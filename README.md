# Job Automation (LinkedIn-first)

Monorepo for a **LinkedIn-focused** job workflow: preferences, resume parsing, JD-tailored drafts, application tracking, and a **stub** LinkedIn discovery path until real **LinkedIn Developer + OAuth + approved APIs** are wired in.

Stack: **FastAPI** + **Celery**, **Next.js (App Router)**, Docker, GitHub Actions.

## Important: what “LinkedIn-only” means

- LinkedIn does **not** offer a public RSS/JSON URL for “my recommendations” like some ATS boards.
- This repo deliberately registers **only** a `LinkedInProvider` for discovery. It returns **one demo listing** driven by your **target role** in Preferences so you can exercise matching, tailoring, and manual-apply UX.
- **Next engineering step** for real data: [LinkedIn Developers](https://www.linkedin.com/developers/) app, OAuth 2.0, store tokens in `integration_connections`, call only APIs your app is approved for, comply with LinkedIn terms.

Other boards (Greenhouse, Lever, RSS, Adzuna, etc.) were **removed** to keep the product scope narrow.

## Current features

- Auth (Argon2), preferences, resume upload (PDF/DOCX/text) + parsing
- **Discover LinkedIn (stub)** + optional **demo fake jobs** (local only)
- Match scoring, applications with **manual apply** fallback, **tailored resume** `.txt` / `.docx`
- Alembic migrations; CI runs backend + frontend checks

## Local development

### 1) Dependencies

```bash
python -m pip install -r backend/requirements.txt
cd frontend && npm install && cd ..
```

### 2) Migrations

```bash
python -m alembic -c backend/alembic.ini upgrade head
```

### 3) Backend & frontend

```bash
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
cd frontend && npm run dev
```

- App: `http://localhost:3000`
- Health: `http://127.0.0.1:8000/health`

### 4) Try the flow

1. Register / log in  
2. **Preferences** — set **target roles**, upload resume  
3. **Dashboard** — **Discover LinkedIn (stub)**  
4. Tailor resume / download drafts; use **manual apply** for real postings on linkedin.com when you implement OAuth

## Tests

```bash
python -m pytest backend/tests -q
cd frontend && npm run lint && npm run test
```

## Docker

```bash
docker compose -f infrastructure/docker-compose.yml --env-file infrastructure/env.example up --build
```

## Repo layout

```text
backend/app/   — FastAPI, models, workers, integrations (linkedin.py)
frontend/      — Next.js App Router
infrastructure/
.github/workflows/
```

## Notes

- `uploads/` is gitignored.  
- Old rows in `integration_connections` (e.g. from earlier RSS experiments) may still exist in your SQLite DB; they are ignored by discovery until you add LinkedIn OAuth storage.
