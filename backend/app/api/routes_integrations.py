from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, HttpUrl, validator
from sqlalchemy.orm import Session

from backend.app.core.security import get_current_user
from backend.app.db.session import get_db
from backend.app.integrations.greenhouse_public import _sanitize_board_tokens
from backend.app.integrations.lever_public import _sanitize_companies
from backend.app.integrations.registry import get_providers
from backend.app.integrations.rss_jobs import RSS_PROVIDER_NAME, _public_http_url
from backend.app.models.integration_connection import IntegrationConnection
from backend.app.models.user import User


router = APIRouter(prefix="/integrations", tags=["integrations"])

GREENHOUSE_PROVIDER = "greenhouse_api"
LEVER_PROVIDER = "lever_api"


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


class GreenhouseUpsert(BaseModel):
    board_tokens: List[str] = Field(..., min_items=1, max_items=10)

    @validator("board_tokens")
    def validate_tokens(cls, v: List[str]) -> List[str]:
        cleaned = _sanitize_board_tokens(list(v))
        if not cleaned:
            raise ValueError("No valid board tokens (use lowercase slugs: letters, numbers, hyphens).")
        return cleaned


class LeverUpsert(BaseModel):
    companies: List[str] = Field(..., min_items=1, max_items=10)

    @validator("companies")
    def validate_companies(cls, v: List[str]) -> List[str]:
        cleaned = _sanitize_companies(list(v))
        if not cleaned:
            raise ValueError("No valid Lever slugs (subdomain before .jobs.lever.co).")
        return cleaned


def _merge_connection_status(
    db: Session,
    user: User,
    provider_name: str,
    st: dict,
) -> dict:
    if provider_name == RSS_PROVIDER_NAME:
        conn = (
            db.query(IntegrationConnection)
            .filter(
                IntegrationConnection.user_id == user.id,
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
    elif provider_name == GREENHOUSE_PROVIDER:
        conn = (
            db.query(IntegrationConnection)
            .filter(
                IntegrationConnection.user_id == user.id,
                IntegrationConnection.provider == GREENHOUSE_PROVIDER,
            )
            .first()
        )
        tokens = (conn.config or {}).get("board_tokens") if conn else []
        if isinstance(tokens, list) and tokens:
            st["connected"] = True
            st["mode"] = "api"
            preview = ", ".join(str(t) for t in tokens[:6])
            st["details"] = f"Greenhouse boards: {preview}"
    elif provider_name == LEVER_PROVIDER:
        conn = (
            db.query(IntegrationConnection)
            .filter(
                IntegrationConnection.user_id == user.id,
                IntegrationConnection.provider == LEVER_PROVIDER,
            )
            .first()
        )
        companies = (conn.config or {}).get("companies") if conn else []
        if isinstance(companies, list) and companies:
            st["connected"] = True
            st["mode"] = "api"
            preview = ", ".join(str(c) for c in companies[:6])
            st["details"] = f"Lever sites: {preview}"
    return st


@router.get("/status", response_model=list[ProviderStatus])
def get_provider_statuses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ProviderStatus]:
    out: list[ProviderStatus] = []
    for provider in get_providers():
        st = dict(provider.get_status())
        st = _merge_connection_status(db, current_user, provider.provider_name, st)
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


@router.put("/connections/greenhouse")
def upsert_greenhouse(
    payload: GreenhouseUpsert,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    row = (
        db.query(IntegrationConnection)
        .filter(
            IntegrationConnection.user_id == current_user.id,
            IntegrationConnection.provider == GREENHOUSE_PROVIDER,
        )
        .first()
    )
    cfg = {"board_tokens": payload.board_tokens}
    if row:
        row.config = cfg
    else:
        db.add(
            IntegrationConnection(
                user_id=current_user.id,
                provider=GREENHOUSE_PROVIDER,
                config=cfg,
            )
        )
    db.commit()
    return {"provider": GREENHOUSE_PROVIDER, "board_tokens": payload.board_tokens}


@router.delete("/connections/greenhouse")
def delete_greenhouse(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, bool]:
    row = (
        db.query(IntegrationConnection)
        .filter(
            IntegrationConnection.user_id == current_user.id,
            IntegrationConnection.provider == GREENHOUSE_PROVIDER,
        )
        .first()
    )
    if row:
        db.delete(row)
        db.commit()
    return {"ok": True}


@router.put("/connections/lever")
def upsert_lever(
    payload: LeverUpsert,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    row = (
        db.query(IntegrationConnection)
        .filter(
            IntegrationConnection.user_id == current_user.id,
            IntegrationConnection.provider == LEVER_PROVIDER,
        )
        .first()
    )
    cfg = {"companies": payload.companies}
    if row:
        row.config = cfg
    else:
        db.add(
            IntegrationConnection(
                user_id=current_user.id,
                provider=LEVER_PROVIDER,
                config=cfg,
            )
        )
    db.commit()
    return {"provider": LEVER_PROVIDER, "companies": payload.companies}


@router.delete("/connections/lever")
def delete_lever(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, bool]:
    row = (
        db.query(IntegrationConnection)
        .filter(
            IntegrationConnection.user_id == current_user.id,
            IntegrationConnection.provider == LEVER_PROVIDER,
        )
        .first()
    )
    if row:
        db.delete(row)
        db.commit()
    return {"ok": True}
