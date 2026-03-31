"""Read-only job discovery from user-configured RSS/Atom feeds."""

from __future__ import annotations

import hashlib
import logging
from urllib.parse import urlparse

import feedparser
import httpx

from backend.app.integrations.base import ApplicationResult, ProviderJob

logger = logging.getLogger(__name__)

MAX_FEEDS_PER_RUN = 5
MAX_ITEMS_PER_FEED = 40
REQUEST_TIMEOUT = 20.0
RSS_PROVIDER_NAME = "rss_feed"


def _public_http_url(url: str) -> bool:
    try:
        p = urlparse(url.strip())
    except Exception:
        return False
    if p.scheme not in ("http", "https") or not p.netloc:
        return False
    host = p.hostname or ""
    if host in ("localhost", "127.0.0.1", "::1") or host.endswith(".local"):
        return False
    return True


def _jobs_from_feed_xml(content: str, feed_url: str) -> list[ProviderJob]:
    parsed = feedparser.parse(content)
    feed_name = (parsed.feed.get("title") if parsed.feed else None) or "RSS feed"
    feed_name = str(feed_name)[:200]
    jobs: list[ProviderJob] = []
    for entry in parsed.entries[:MAX_ITEMS_PER_FEED]:
        title = (entry.get("title") or "Job posting").strip()[:250]
        link = (entry.get("link") or feed_url).strip()
        if not link:
            link = feed_url
        summary = entry.get("summary") or entry.get("description") or ""
        summary = str(summary)[:8000] if summary else title
        company = feed_name
        if entry.get("author"):
            company = str(entry.get("author"))[:200]

        ext_key = f"{feed_url}|{link}"
        ext_hash = hashlib.sha256(ext_key.encode("utf-8", errors="ignore")).hexdigest()[:24]
        jobs.append(
            ProviderJob(
                external_id=f"rss-{ext_hash}",
                title=title,
                company=company,
                location=None,
                description=summary,
                url=link[:1024],
                source=RSS_PROVIDER_NAME,
            )
        )
    return jobs


class RssJobsProvider:
    provider_name = RSS_PROVIDER_NAME

    def search_jobs(self, user_profile: dict) -> list[ProviderJob]:
        urls_raw = user_profile.get("rss_feed_urls") or []
        urls: list[str] = []
        for u in urls_raw[:MAX_FEEDS_PER_RUN]:
            if isinstance(u, str) and _public_http_url(u):
                urls.append(u.strip())
        if not urls:
            return []

        out: list[ProviderJob] = []
        try:
            with httpx.Client(timeout=REQUEST_TIMEOUT, follow_redirects=True) as client:
                for feed_url in urls:
                    try:
                        resp = client.get(feed_url)
                        resp.raise_for_status()
                        ctype = (resp.headers.get("content-type") or "").lower()
                        if "xml" not in ctype and "rss" not in ctype and "atom" not in ctype and "text/plain" not in ctype:
                            # feedparser often still copes; allow missing header
                            pass
                        out.extend(_jobs_from_feed_xml(resp.text, feed_url))
                    except Exception as exc:
                        logger.warning("RSS fetch failed for %s: %s", feed_url, exc)
        except Exception as exc:
            logger.warning("RSS client error: %s", exc)
        return out

    def can_auto_apply(self) -> bool:
        return False

    def apply_to_job(self, job: ProviderJob, user_profile: dict) -> ApplicationResult:
        _ = (job, user_profile)
        return ApplicationResult(
            status="manual_only",
            details="RSS feeds require applying on the employer site.",
        )

    def get_status(self) -> dict:
        return {
            "provider": self.provider_name,
            "connected": False,
            "mode": "configure",
            "details": "Add an RSS or Atom job feed URL under Connections.",
        }
