"""Automated apply attempt with explicit fallback to manual when unsupported or failed."""

from sqlalchemy.orm import Session

from backend.app.integrations.base import ProviderJob
from backend.app.integrations.registry import get_providers
from backend.app.models.application import JobApplication
from backend.app.models.job import Job
from backend.app.models.user import User

AUTO_SUCCESS_STATUSES = frozenset({"submitted", "auto_applied", "applied", "success"})


def _user_profile(user: User) -> dict:
    prefs = user.preferences or {}
    return {
        "target_roles": prefs.get("target_roles", []),
        "locations": prefs.get("locations", []),
        "job_types": prefs.get("job_types", []),
        "aggressiveness": prefs.get("aggressiveness", 50),
    }


def run_auto_apply_for_user(
    db: Session,
    user_id: int,
    *,
    score_threshold: float = 0.5,
) -> dict[str, int | str]:
    """Try automation for queued applications; otherwise mark manual_required with reason."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"processed": 0, "message": "user not found"}

    provider_map = {p.provider_name: p for p in get_providers()}
    profile = _user_profile(user)

    apps = (
        db.query(JobApplication)
        .join(Job, Job.id == JobApplication.job_id)
        .filter(JobApplication.user_id == user_id, JobApplication.status == "queued")
        .all()
    )

    auto_ok = 0
    manual = 0
    skipped_low_score = 0

    for app in apps:
        job = db.query(Job).filter(Job.id == app.job_id).first()
        if not job:
            app.status = "manual_required"
            app.status_detail = "Job record missing; cannot apply."
            manual += 1
            continue

        if (job.relevance_score or 0) < score_threshold:
            skipped_low_score += 1
            continue

        provider = provider_map.get(app.provider)
        if not provider:
            app.status = "manual_required"
            app.status_detail = (
                "No automation connector for this job source. Open the posting link to apply manually."
            )
            manual += 1
            continue

        if not provider.can_auto_apply():
            app.status = "manual_required"
            app.status_detail = (
                "Automated apply is not available for this site. "
                "Use “Open posting” and submit your application manually."
            )
            manual += 1
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

        if result.status in AUTO_SUCCESS_STATUSES:
            app.status = "auto_applied"
            app.status_detail = result.details
            auto_ok += 1
        else:
            app.status = "manual_required"
            app.status_detail = (
                result.details
                or "Automated apply did not succeed. Complete your application on the job site."
            )
            manual += 1

    db.commit()
    return {
        "auto_applied": auto_ok,
        "manual_required": manual,
        "skipped_low_score": skipped_low_score,
    }
