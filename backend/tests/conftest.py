"""Use an isolated SQLite DB per test session so migrations match models."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from sqlalchemy.engine.url import URL

_tmp = tempfile.NamedTemporaryFile(prefix="jobauto_pytest_", suffix=".db", delete=False)
_tmp.close()
_db_path = Path(_tmp.name).resolve()
os.environ["DATABASE_URL"] = str(URL.create("sqlite", database=str(_db_path)))

# TestClient may not run FastAPI lifespan; ensure schema exists before tests hit the API.
from backend.app.db.session import init_db  # noqa: E402

init_db()
