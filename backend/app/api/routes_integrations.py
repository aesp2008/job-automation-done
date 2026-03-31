from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, HttpUrl
from sqlalchemy.orm import Session

from backend.app.core.security import get_current_user
from backend.app.db.session import get_db
from backend.app.integrations.registry import get_providers
from backend.app.integrations.rss_jobs import RSS_PROVIDER_NAME, _public_http_url
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


class RssFeedUpsert(BaseModel):
    rss_url: HttpUrl


@router.get("/status", response_model=list[ProviderStatus])
def get_provider_statuses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ProviderStatus]:
    out: list[ProviderStatus] = []
    for provider in get_providers():
        st = dict(provider.get_status())
        if provider.provider_name == RSS_PROVIDER_NAME:
            conn = (
                db.query(IntegrationConnection)
                .filter(
                    IntegrationConnection.user_id == current_user.id,
                    IntegrationConnection.provider == RSS_PROVIDER_NAME,
                )
                .first()
            )
            url = (conn.config or {}).get("rss_url") if conn else None
            if isinstance(url, str) and url.strip():
                st["connected"] = True
                st["mode"] = "rss"
                display = url.strip()
                if len(display) > 96:
                    display = display[:93] + "..."
                st["details"] = f"Feed URL: {display}"
        out.append(ProviderStatus(**st))
    return out


@router.get("/connections", response_model=list[ConnectionOut])
def list_my_connections(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ConnectionOut]:
    rows = (
        db.query(IntegrationConnection)
        .filter(IntegrationConnection.user_id == current_user.id)
        .order_by(IntegrationConnection.provider.asc())
        .all()
    )
    return [ConnectionOut(provider=r.provider, config=dict(r.config or {})) for r in rows]


@router.put("/connections/rss_feed")
def upsert_rss_feed(
    payload: RssFeedUpsert,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    url = str(payload.rss_url)
    if not _public_http_url(url):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only public http(s) URLs are allowed (localhost is blocked).",
        )
    row = (
        db.query(IntegrationConnection)
        .filter(
            IntegrationConnection.user_id == current_user.id,
            IntegrationConnection.provider == RSS_PROVIDER_NAME,
        )
        .first()
    )
    if row:
        row.config = {"rss_url": url}
    else:
        db.add(
            IntegrationConnection(
                user_id=current_user.id,
                provider=RSS_PROVIDER_NAME,
                config={"rss_url": url},
            )
        )
    db.commit()
    return {"provider": RSS_PROVIDER_NAME, "rss_url": url}


@router.delete("/connections/rss_feed")
def delete_rss_feed(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, bool]:
    row = (
        db.query(IntegrationConnection)
        .filter(
            IntegrationConnection.user_id == current_user.id,
            IntegrationConnection.provider == RSS_PROVIDER_NAME,
        )
        .first()
    )
    if row:
        db.delete(row)
        db.commit()
    return {"ok": True}
