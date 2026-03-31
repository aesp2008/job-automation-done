"""Public Greenhouse Job Board API — no API key (company board token only)."""

from __future__ import annotations

import html as html_lib
import logging
import re

import httpx

from backend.app.integrations.base import ApplicationResult, ProviderJob

logger = logging.getLogger(__name__)

GREENHOUSE_JOBS_URL = "https://boards-api.greenhouse.io/v1/boards/{token}/jobs"
REQUEST_TIMEOUT = 20.0
MAX_BOARDS_PER_RUN = 10
MAX_JOBS_PER_BOARD = 60

_SLUG_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9\-]{0,63}$")


def _sanitize_board_tokens(tokens: list[str]) -> list[str]:
    out: list[str] = []
    for t in tokens[:MAX_BOARDS_PER_RUN]:
        if not isinstance(t, str):
            continue
        s = t.strip().lower()
        if s and _SLUG_RE.match(s):
            out.append(s)
    return out


def _strip_html(raw: str) -> str:
    if not raw:
        return ""
    text = re.sub(r"<[^>]+>", " ", raw)
    text = html_lib.unescape(text)
    return re.sub(r"\s+", " ", text).strip()[:8000]


class GreenhousePublicProvider:
    provider_name = "greenhouse_api"

    def search_jobs(self, user_profile: dict) -> list[ProviderJob]:
        raw_tokens = user_profile.get("greenhouse_board_tokens") or []
        tokens = _sanitize_board_tokens(list(raw_tokens))
        if not tokens:
            return []

        jobs: list[ProviderJob] = []
        try:
            with httpx.Client(timeout=REQUEST_TIMEOUT, follow_redirects=True) as client:
                for token in tokens:
                    url = GREENHOUSE_JOBS_URL.format(token=token)
                    try:
                        resp = client.get(url)
                        resp.raise_for_status()
                        data = resp.json()
                    except Exception as exc:
                        logger.warning("Greenhouse fetch failed %s: %s", token, exc)
                        continue

                    for j in (data.get("jobs") or [])[:MAX_JOBS_PER_BOARD]:
                        jid = j.get("id")
                        if jid is None:
                            continue
                        title = str(j.get("title") or "Role").strip()[:250]
                        loc = j.get("location") or {}
                        location = str(loc.get("name") or "").strip()[:255] or ""
                        desc = _strip_html(str(j.get("content") or "")) or title
                        absolute = str(j.get("absolute_url") or "").strip()[:1024]
                        company = str(j.get("company_name") or data.get("name") or token).strip()[:255]
                        jobs.append(
                            ProviderJob(
                                external_id=f"greenhouse-{token}-{jid}",
                                title=title,
                                company=company,
                                location=location,
                                description=desc,
                                url=absolute,
                                source=self.provider_name,
                            )
                        )
        except Exception as exc:
            logger.warning("Greenhouse client error: %s", exc)
        return jobs

    def can_auto_apply(self) -> bool:
        return False

    def apply_to_job(self, job: ProviderJob, user_profile: dict) -> ApplicationResult:
        _ = (job, user_profile)
        return ApplicationResult(
            status="manual_only",
            details="Apply via the Greenhouse posting URL.",
        )

    def get_status(self) -> dict:
        return {
            "provider": self.provider_name,
            "connected": False,
            "mode": "configure",
            "details": "Add one or more board tokens (e.g. company slug from jobs.site.com) under Connections.",
        }
