from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, UniqueConstraint, func

from backend.app.db.session import Base


class IntegrationConnection(Base):
    """Per-user integration config (e.g. RSS feed URL). Secrets should use dedicated vaulting later."""

    __tablename__ = "integration_connections"
    __table_args__ = (UniqueConstraint("user_id", "provider", name="uq_integration_user_provider"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    provider = Column(String(100), nullable=False)
    config = Column(JSON, nullable=False, default=lambda: {})

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
