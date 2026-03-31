from unittest.mock import MagicMock, patch

from backend.app.integrations.greenhouse_public import GreenhousePublicProvider
from backend.app.integrations.lever_public import LeverPublicProvider

_GREENHOUSE_JSON = {
    "name": "Demo Co",
    "jobs": [
        {
            "id": 99,
            "title": "Backend Engineer",
            "absolute_url": "https://boards.greenhouse.io/demo/jobs/99",
            "location": {"name": "Remote"},
            "content": "<p>Python and APIs</p>",
        }
    ],
}

_LEVER_JSON = {
    "data": [
        {
            "id": "a1b2",
            "text": "Product Engineer",
            "hostedUrl": "https://jobs.lever.co/acme/a1b2",
            "categories": {"location": "Berlin"},
            "descriptionPlain": "Build features with TypeScript.",
        }
    ]
}


@patch("backend.app.integrations.greenhouse_public.httpx.Client")
def test_greenhouse_provider(mock_cls: MagicMock) -> None:
    mock_resp = MagicMock()
    mock_resp.json = MagicMock(return_value=_GREENHOUSE_JSON)
    mock_resp.raise_for_status = MagicMock()
    mock_client = MagicMock()
    mock_client.get.return_value = mock_resp
    mock_client.__enter__.return_value = mock_client
    mock_client.__exit__.return_value = False
    mock_cls.return_value = mock_client

    p = GreenhousePublicProvider()
    jobs = p.search_jobs({"greenhouse_board_tokens": ["demo"]})
    assert len(jobs) == 1
    assert jobs[0].title == "Backend Engineer"
    assert "python" in jobs[0].description.lower()
    assert jobs[0].source == "greenhouse_api"


@patch("backend.app.integrations.lever_public.httpx.Client")
def test_lever_provider(mock_cls: MagicMock) -> None:
    mock_resp = MagicMock()
    mock_resp.json = MagicMock(return_value=_LEVER_JSON)
    mock_resp.raise_for_status = MagicMock()
    mock_client = MagicMock()
    mock_client.get.return_value = mock_resp
    mock_client.__enter__.return_value = mock_client
    mock_client.__exit__.return_value = False
    mock_cls.return_value = mock_client

    p = LeverPublicProvider()
    jobs = p.search_jobs({"lever_companies": ["acme"]})
    assert len(jobs) == 1
    assert jobs[0].title == "Product Engineer"
    assert jobs[0].source == "lever_api"
