"""Sync job discovery from registered providers into DB + application rows."""

from sqlalchemy.orm import Session

from backend.app.integrations.registry import get_providers
from backend.app.models.application import JobApplication
from backend.app.models.integration_connection import IntegrationConnection
from backend.app.models.job import Job
from backend.app.models.user import User
from backend.app.services.matching import score_job_for_user


def _user_profile(db: Session, user: User) -> dict:
    prefs = user.preferences or {}
    profile: dict = {
        "target_roles": prefs.get("target_roles", []),
        "locations": prefs.get("locations", []),
        "job_types": prefs.get("job_types", []),
        "aggressiveness": prefs.get("aggressiveness", 50),
    }
    rss_urls: list[str] = []
    for row in (
        db.query(IntegrationConnection)
        .filter(
            IntegrationConnection.user_id == user.id,
            IntegrationConnection.provider == "rss_feed",
        )
        .all()
    ):
        cfg = row.config or {}
        url = cfg.get("rss_url")
        if isinstance(url, str) and url.strip():
            rss_urls.append(url.strip())
    profile["rss_feed_urls"] = rss_urls
    return profile


def run_provider_discovery(db: Session, user: User) -> dict[str, int]:
    """Pull jobs from all providers; upsert Job rows and ensure JobApplication per user."""
    profile = _user_profile(db, user)
    created_jobs = 0
    for provider in get_providers():
        for item in provider.search_jobs(profile):
            existing = db.query(Job).filter(Job.external_id == item.external_id).first()
            score, explanation = score_job_for_user(
                user,
                {
                    "title": item.title,
                    "location": item.location,
                    "description": item.description,
                },
            )
            if existing:
                existing.relevance_score = score
                existing.relevance_explanation = explanation
                existing.title = item.title
                existing.company = item.company
                existing.location = item.location
                existing.description = item.description
                existing.url = item.url
                existing.source = item.source
                job = existing
            else:
                job = Job(
                    external_id=item.external_id,
                    title=item.title,
                    company=item.company,
                    location=item.location,
                    description=item.description,
                    source=item.source,
                    url=item.url,
                    relevance_score=score,
                    relevance_explanation=explanation,
                )
                db.add(job)
                created_jobs += 1
            db.flush()

            app_exists = (
                db.query(JobApplication)
                .filter(
                    JobApplication.user_id == user.id,
                    JobApplication.job_id == job.id,
                )
                .first()
            )
            if not app_exists:
                db.add(
                    JobApplication(
                        user_id=user.id,
                        job_id=job.id,
                        status="queued",
                        provider=item.source,
                    )
                )

    db.commit()
    return {
        "created_jobs": created_jobs,
        "providers_touched": len(get_providers()),
    }
