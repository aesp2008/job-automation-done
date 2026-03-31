from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from backend.app.core.config import get_settings


settings = get_settings()

engine = create_engine(settings.DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    # Import models to ensure metadata is available for fallback behavior.
    from backend.app.models import (  # noqa: F401
        application,
        integration_connection,
        job,
        user,
    )

    alembic_ini = Path(__file__).resolve().parents[2] / "alembic.ini"
    alembic_cfg = Config(str(alembic_ini))
    try:
        command.upgrade(alembic_cfg, "head")
    except Exception:
        # Safe fallback for environments where Alembic isn't initialized yet.
        Base.metadata.create_all(bind=engine)

