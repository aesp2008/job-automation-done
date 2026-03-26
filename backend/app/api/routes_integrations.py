from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend.app.core.security import get_current_user
from backend.app.models.user import User


router = APIRouter(prefix="/integrations", tags=["integrations"])


class ProviderStatus(BaseModel):
    provider: str
    connected: bool
    mode: str
    details: str


@router.get("/status", response_model=list[ProviderStatus])
def get_provider_statuses(current_user: User = Depends(get_current_user)) -> list[ProviderStatus]:
    _ = current_user
    return [
        ProviderStatus(
            provider="linkedin",
            connected=False,
            mode="stub",
            details="Connection setup is not configured yet.",
        ),
        ProviderStatus(
            provider="unstop",
            connected=False,
            mode="stub",
            details="Connection setup is not configured yet.",
        ),
        ProviderStatus(
            provider="indeed",
            connected=False,
            mode="stub",
            details="Connection setup is not configured yet.",
        ),
    ]

