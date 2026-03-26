from backend.app.db.session import SessionLocal
from backend.app.integrations.base import ProviderJob
from backend.app.integrations.registry import get_providers
from backend.app.models.application import JobApplication
from backend.app.models.job import Job
from backend.app.models.user import User
from backend.app.services.matching import score_job_for_user
from backend.app.workers.queue import celery_app


@celery_app.task(name="health.ping")
def ping() -> str:
    """Minimal worker task used to verify Celery wiring."""
    return "pong"


def _user_profile(user: User) -> dict:
    prefs = user.preferences or {}
    return {
        "target_roles": prefs.get("target_roles", []),
        "locations": prefs.get("locations", []),
        "job_types": prefs.get("job_types", []),
        "aggressiveness": prefs.get("aggressiveness", 50),
    }


@celery_app.task(name="jobs.discover_for_user")
def discover_jobs_for_user(user_id: int) -> dict:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"created_jobs": 0, "message": "user not found"}

        profile = _user_profile(user)
        created = 0
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
                    created += 1
                db.flush()

                app_exists = (
                    db.query(JobApplication)
                    .filter(JobApplication.user_id == user.id, JobApplication.job_id == job.id)
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
        return {"created_jobs": created, "providers": len(get_providers())}
    finally:
        db.close()


@celery_app.task(name="jobs.auto_apply_for_user")
def auto_apply_for_user(user_id: int, threshold: float = 0.75) -> dict:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"applied": 0, "message": "user not found"}

        provider_map = {p.provider_name: p for p in get_providers()}
        apps = (
            db.query(JobApplication)
            .join(Job, Job.id == JobApplication.job_id)
            .filter(JobApplication.user_id == user_id, JobApplication.status == "queued")
            .all()
        )
        applied = 0
        profile = _user_profile(user)
        for app in apps:
            job = db.query(Job).filter(Job.id == app.job_id).first()
            if not job or (job.relevance_score or 0) < threshold:
                continue
            provider = provider_map.get(app.provider)
            if not provider or not provider.can_auto_apply():
                continue
            result = provider.apply_to_job(
                job=ProviderJob(
                    external_id=job.external_id,
                    title=job.title,
                    company=job.company,
                    location=job.location or "",
                    description=job.description or "",
                    url=job.url or "",
                    source=job.source,
                ),
                user_profile=profile,
            )
            app.status = result.status
            applied += 1

        db.commit()
        return {"applied": applied}
    finally:
        db.close()

