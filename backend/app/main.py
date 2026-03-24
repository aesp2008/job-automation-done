from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes_users import router as users_router
from .core.config import get_settings
from .db.session import init_db


settings = get_settings()

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(users_router)


@app.on_event("startup")
def on_startup() -> None:
    """Initialize DB tables for the MVP."""
    init_db()


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    """Simple health check endpoint."""
    return {"status": "ok"}


@app.get("/", tags=["root"])
async def root() -> dict[str, str]:
    """Placeholder root endpoint."""
    return {"message": "Job Automation Backend is running"}

