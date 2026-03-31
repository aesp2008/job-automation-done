from unittest.mock import MagicMock, patch

from backend.app.integrations.rss_jobs import RssJobsProvider, _jobs_from_feed_xml, _public_http_url


_MINIMAL_RSS = """<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0"><channel><title>Example Jobs</title>
<item><title>Senior Python Engineer</title>
<link>https://example.com/jobs/1</link>
<description>Build APIs with FastAPI</description>
</item>
</channel></rss>"""


def test_public_http_url_blocks_localhost() -> None:
    assert _public_http_url("https://jobs.example.com/feed.xml") is True
    assert _public_http_url("http://127.0.0.1/feed") is False
    assert _public_http_url("file:///etc/passwd") is False


def test_jobs_from_feed_xml() -> None:
    jobs = _jobs_from_feed_xml(_MINIMAL_RSS, "https://example.com/jobs.xml")
    assert len(jobs) == 1
    assert jobs[0].title == "Senior Python Engineer"
    assert jobs[0].source == "rss_feed"
    assert "fastapi" in jobs[0].description.lower()


@patch("backend.app.integrations.rss_jobs.httpx.Client")
def test_rss_provider_fetches_feed(mock_cls: MagicMock) -> None:
    mock_resp = MagicMock()
    mock_resp.text = _MINIMAL_RSS
    mock_resp.raise_for_status = MagicMock()
    mock_client = MagicMock()
    mock_client.get.return_value = mock_resp
    mock_client.__enter__.return_value = mock_client
    mock_client.__exit__.return_value = False
    mock_cls.return_value = mock_client

    p = RssJobsProvider()
    jobs = p.search_jobs({"rss_feed_urls": ["https://example.com/feed.xml"]})
    assert len(jobs) == 1
    mock_client.get.assert_called_once()
