from apscheduler.schedulers.background import BackgroundScheduler

from backend.app.db.session import SessionLocal
from backend.app.models.user import User
from backend.app.workers.tasks import discover_jobs_for_user


def run_discovery_for_active_users() -> None:
    """Schedule-trigger entrypoint to queue discovery for all users."""
    db = SessionLocal()
    try:
        users = db.query(User).all()
        for user in users:
            discover_jobs_for_user.delay(user.id)
    finally:
        db.close()


def create_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(
        run_discovery_for_active_users,
        "interval",
        minutes=30,
        id="discover_jobs_for_active_users",
        replace_existing=True,
    )
    return scheduler

