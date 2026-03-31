"""Adzuna Jobs API — aggregator search; requires server env keys (free dev tier)."""

from __future__ import annotations

import logging

import httpx

from backend.app.core.config import get_settings
from backend.app.integrations.base import ApplicationResult, ProviderJob

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT = 25.0
MAX_RESULTS = 30


class AdzunaApiProvider:
    provider_name = "adzuna_api"

    def search_jobs(self, user_profile: dict) -> list[ProviderJob]:
        settings = get_settings()
        app_id = (settings.ADZUNA_APP_ID or "").strip()
        app_key = (settings.ADZUNA_APP_KEY or "").strip()
        if not app_id or not app_key:
            return []

        country = (settings.ADZUNA_COUNTRY or "gb").strip().lower()
        roles = user_profile.get("target_roles") or []
        what = str(roles[0]).strip() if roles else "software engineer"
        url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/1"
        params = {
            "app_id": app_id,
            "app_key": app_key,
            "results_per_page": MAX_RESULTS,
            "what": what,
        }

        jobs: list[ProviderJob] = []
        try:
            with httpx.Client(timeout=REQUEST_TIMEOUT, follow_redirects=True) as client:
                resp = client.get(url, params=params)
                resp.raise_for_status()
                data = resp.json()
        except Exception as exc:
            logger.warning("Adzuna API error: %s", exc)
            return []

        for r in (data.get("results") or [])[:MAX_RESULTS]:
            rid = r.get("id")
            if rid is None:
                continue
            title = str(r.get("title") or "Role").strip()[:250]
            co = r.get("company")
            if isinstance(co, dict):
                company = str(co.get("display_name") or "").strip()[:255] or "Company"
            else:
                company = str(co or "Company").strip()[:255]
            loc_parts = []
            lad = r.get("location") or {}
            if isinstance(lad, dict):
                for key in ("display_name", "area", "city"):
                    v = lad.get(key)
                    if isinstance(v, list):
                        loc_parts.extend(str(x) for x in v if x)
                    elif isinstance(v, str) and v:
                        loc_parts.append(v)
            location = ", ".join(loc_parts)[:255] if loc_parts else ""
            desc = str(r.get("description") or r.get("snippet") or title).strip()[:8000]
            redir = str(r.get("redirect_url") or r.get("adref") or "").strip()[:1024]

            jobs.append(
                ProviderJob(
                    external_id=f"adzuna-{country}-{rid}",
                    title=title,
                    company=company,
                    location=location,
                    description=desc,
                    url=redir,
                    source=self.provider_name,
                )
            )
        return jobs

    def can_auto_apply(self) -> bool:
        return False

    def apply_to_job(self, job: ProviderJob, user_profile: dict) -> ApplicationResult:
        _ = (job, user_profile)
        return ApplicationResult(status="manual_only", details="Open the Adzuna redirect URL to apply on the employer site.")

    def get_status(self) -> dict:
        settings = get_settings()
        configured = bool((settings.ADZUNA_APP_ID or "").strip() and (settings.ADZUNA_APP_KEY or "").strip())
        return {
            "provider": self.provider_name,
            "connected": configured,
            "mode": "env" if configured else "unconfigured",
            "details": (
                f"Adzuna aggregation ({settings.ADZUNA_COUNTRY or 'gb'}). "
                "Set ADZUNA_APP_ID and ADZUNA_APP_KEY in server environment (see developer.adzuna.com)."
                if configured
                else "Optional: add ADZUNA_APP_ID and ADZUNA_APP_KEY to .env for live aggregation search."
            ),
        }
