from backend.app.db.session import SessionLocal
from backend.app.models.user import User
from backend.app.services.auto_apply import run_auto_apply_for_user
from backend.app.services.discovery import run_provider_discovery
from backend.app.workers.queue import celery_app


@celery_app.task(name="health.ping")
def ping() -> str:
    """Minimal worker task used to verify Celery wiring."""
    return "pong"


@celery_app.task(name="jobs.discover_for_user")
def discover_jobs_for_user(user_id: int) -> dict:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"created_jobs": 0, "message": "user not found"}
        stats = run_provider_discovery(db, user)
        return {
            "created_jobs": stats["created_jobs"],
            "providers": stats["providers_touched"],
        }
    finally:
        db.close()


@celery_app.task(name="jobs.auto_apply_for_user")
def auto_apply_for_user(user_id: int, threshold: float = 0.5) -> dict:
    db = SessionLocal()
    try:
        return run_auto_apply_for_user(db, user_id, score_threshold=threshold)
    finally:
        db.close()
