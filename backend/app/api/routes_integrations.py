from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.core.security import get_current_user
from backend.app.db.session import get_db
from backend.app.integrations.registry import get_providers
from backend.app.models.integration_connection import IntegrationConnection
from backend.app.models.user import User


router = APIRouter(prefix="/integrations", tags=["integrations"])


class ProviderStatus(BaseModel):
    provider: str
    connected: bool
    mode: str
    details: str


class ConnectionOut(BaseModel):
    provider: str
    config: dict


@router.get("/status", response_model=list[ProviderStatus])
def get_provider_statuses(
    current_user: User = Depends(get_current_user),
) -> list[ProviderStatus]:
    _ = current_user
    return [ProviderStatus(**dict(p.get_status())) for p in get_providers()]


@router.get("/connections", response_model=list[ConnectionOut])
def list_my_connections(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ConnectionOut]:
    """Reserved for future LinkedIn OAuth token storage; often empty today."""
    rows = (
        db.query(IntegrationConnection)
        .filter(IntegrationConnection.user_id == current_user.id)
        .order_by(IntegrationConnection.provider.asc())
        .all()
    )
    return [ConnectionOut(provider=r.provider, config=dict(r.config or {})) for r in rows]
