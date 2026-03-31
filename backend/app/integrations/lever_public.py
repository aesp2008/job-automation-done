"""Public Lever Postings API — read-only JSON, no API key."""

from __future__ import annotations

import logging
import re

import httpx

from backend.app.integrations.base import ApplicationResult, ProviderJob

logger = logging.getLogger(__name__)

LEVER_POSTINGS_URL = "https://api.lever.co/v0/postings/{company}"
REQUEST_TIMEOUT = 20.0
MAX_COMPANIES_PER_RUN = 10
MAX_POSTINGS = 60

_SLUG_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9\-]{0,63}$")


def _sanitize_companies(companies: list[str]) -> list[str]:
    out: list[str] = []
    for c in companies[:MAX_COMPANIES_PER_RUN]:
        if not isinstance(c, str):
            continue
        s = c.strip().lower()
        if s and _SLUG_RE.match(s):
            out.append(s)
    return out


class LeverPublicProvider:
    provider_name = "lever_api"

    def search_jobs(self, user_profile: dict) -> list[ProviderJob]:
        raw = user_profile.get("lever_companies") or []
        companies = _sanitize_companies(list(raw))
        if not companies:
            return []

        jobs: list[ProviderJob] = []
        try:
            with httpx.Client(timeout=REQUEST_TIMEOUT, follow_redirects=True) as client:
                for company in companies:
                    url = f"{LEVER_POSTINGS_URL.format(company=company)}?mode=json"
                    try:
                        resp = client.get(url)
                        resp.raise_for_status()
                        body = resp.json()
                    except Exception as exc:
                        logger.warning("Lever fetch failed %s: %s", company, exc)
                        continue

                    postings = body if isinstance(body, list) else body.get("data") or []

                    for p in postings[:MAX_POSTINGS]:
                        pid = p.get("id")
                        if not pid:
                            continue
                        title = str(p.get("text") or "Open role").strip()[:250]
                        cats = p.get("categories") if isinstance(p.get("categories"), dict) else {}
                        loc_name = ""
                        if isinstance(cats.get("location"), str):
                            loc_name = cats["location"].strip()[:255]
                        desc = ""
                        for key in ("descriptionPlain", "description"):
                            v = p.get(key)
                            if isinstance(v, str) and v.strip():
                                desc = v.strip()[:8000]
                                break
                        apply_url = str(
                            p.get("hostedUrl")
                            or p.get("hosted_url")
                            or p.get("applyUrl")
                            or ""
                        ).strip()[:1024]

                        jobs.append(
                            ProviderJob(
                                external_id=f"lever-{company}-{pid}",
                                title=title,
                                company=company.replace("-", " ").title(),
                                location=loc_name,
                                description=desc or title,
                                url=apply_url,
                                source=self.provider_name,
                            )
                        )
        except Exception as exc:
            logger.warning("Lever client error: %s", exc)
        return jobs

    def can_auto_apply(self) -> bool:
        return False

    def apply_to_job(self, job: ProviderJob, user_profile: dict) -> ApplicationResult:
        _ = (job, user_profile)
        return ApplicationResult(status="manual_only", details="Apply via the Lever posting URL.")

    def get_status(self) -> dict:
        return {
            "provider": self.provider_name,
            "connected": False,
            "mode": "configure",
            "details": "Add Lever site slugs (subdomain before jobs.lever.co) under Connections.",
        }
