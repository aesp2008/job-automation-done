from backend.app.workers.queue import celery_app


@celery_app.task(name="health.ping")
def ping() -> str:
    """Minimal worker task used to verify Celery wiring."""
    return "pong"

