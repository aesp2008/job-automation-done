# Job Automation MVP

Monorepo for a job automation platform with:
- `backend/` FastAPI API + Celery workers
- `frontend/` Next.js (App Router, TypeScript) UI
- `infrastructure/` Docker compose stack
- `.github/workflows/` CI checks

## Current MVP scope

- Authentication:
  - register, login, current-user profile
- User settings:
  - preferences create/update/get
  - resume upload to local disk with parsed summary (keyword-based MVP parser)
- Jobs:
  - fake discovery endpoint
  - match scoring via centralized matching service
  - applications list
- Integrations:
  - provider status endpoint for LinkedIn, Unstop, Indeed (stub implementations)
- Workers and scheduling:
  - Celery tasks for discover and auto-apply skeleton flows
  - APScheduler service skeleton for periodic discovery
- CI:
  - backend import + tests
  - frontend lint + build + tests

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

### 2) Run backend

```bash
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

### 3) Run frontend

```bash
cd frontend
npm run dev
```

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

## Notes

- Local uploaded resume files are stored under `uploads/` and ignored by git.
- Current provider integrations are stubs; real session/OAuth automation is planned next.
