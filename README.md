# Job Automation MVP

Monorepo for a job automation platform with:
- `backend/` FastAPI API + Celery workers
- `frontend/` Next.js (App Router, TypeScript) UI
- `infrastructure/` Docker compose stack
- `.github/workflows/` CI checks

## Current MVP scope

- **Authentication:** register, login (Argon2), JWT, current-user profile
- **User settings:** preferences CRUD; resume upload with **PDF / DOCX / text** parsing (skills, emails, preview)
- **Jobs:** demo discovery, **multi-board stub discovery**, match scoring, applications with job title/URL
- **Apply flow:** **auto-apply** where a connector supports it; otherwise **`manual_required`** with `status_detail`; **mark manual complete** when you applied on the site
- **Resume tailoring:** JD-aware **skill order, bullets, summary**; download **`.txt`** or **`.docx`** draft
- **Integrations:** stubs plus **modern read-only JSON**: **Greenhouse** public board API and **Lever** postings API (configure tokens in Connections), optional **Adzuna** aggregation via `ADZUNA_*` env keys; **RSS/Atom** still supported where feeds exist; data stored in `integration_connections` (except Adzuna, server env)
- **Workers:** Celery tasks call the same discovery/auto-apply logic as the HTTP API
- **Database:** Alembic migrations (run `python -m alembic -c backend/alembic.ini upgrade head` after pull)
- **CI:** backend tests (isolated SQLite + migrations); frontend lint, build, tests

## Repo structure

```text
backend/
  app/
    api/
    core/
    db/
    integrations/
    models/
    services/
    workers/
frontend/
  src/app/
infrastructure/
.github/workflows/
```

## Prerequisites

- Python 3.10+
- Node.js 22+
- npm 10+
- Docker Desktop (optional, for compose workflow)

## Local development

### 1) Install dependencies

Backend:

```bash
python -m pip install -r backend/requirements.txt
```

Frontend:

```bash
cd frontend
npm install
cd ..
```

### 2) Database migrations (local SQLite or Postgres)

From the repo root:

```bash
python -m alembic -c backend/alembic.ini upgrade head
```

### 3) Run backend

```bash
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

### 4) Run frontend

```bash
cd frontend
npm run dev
```

### Optional: Live job sources (recommended)

1. **Greenhouse / Lever** — **Settings → Connections**: add board tokens (e.g. `stripe`) or Lever slugs (e.g. `shopify`), then **Discover all boards**. Uses public HTTPS JSON APIs ([Greenhouse Job Board API](https://developers.greenhouse.io/job-board.html), [Lever Postings](https://github.com/lever/postings-api)).
2. **Adzuna** — register at [developer.adzuna.com](https://developer.adzuna.com), set `ADZUNA_APP_ID`, `ADZUNA_APP_KEY`, and optionally `ADZUNA_COUNTRY` (e.g. `gb`, `us`) in backend `.env`. Discovery runs a search from your profile **target role**.
3. **RSS/Atom** — same Connections page; public `http`/`https` only (localhost blocked). Less common on large boards today.

Open:
- Frontend: `http://localhost:3000`
- Backend health: `http://127.0.0.1:8000/health`

## Docker development

Use the compose stack with env file:

```bash
docker compose -f infrastructure/docker-compose.yml --env-file infrastructure/env.example up --build
```

Services:
- frontend on `localhost:3000`
- backend on `localhost:8000`
- postgres on `localhost:5432`
- redis on `localhost:6379`
- celery worker in same compose project

## Running tests

Backend:

```bash
python -m pytest backend/tests -q
```

Frontend:

```bash
cd frontend
npm run test
```

## CI

GitHub Actions workflow at `.github/workflows/ci.yml` runs:
- backend dependency install + import validation + backend tests
- frontend install + lint + build + frontend tests

## Notes local

- Uploaded resumes are stored under `uploads/` (gitignored).
- Provider integrations are mostly **stubs** for flow testing; replace with real APIs and stored credentials when ready.
