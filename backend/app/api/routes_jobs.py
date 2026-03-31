from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.core.security import get_current_user
from backend.app.db.session import get_db
from backend.app.models.application import JobApplication
from backend.app.models.job import Job
from backend.app.models.user import User
from backend.app.services.auto_apply import run_auto_apply_for_user
from backend.app.services.discovery import run_provider_discovery
from backend.app.services.matching import score_job_for_user
from backend.app.services.resume_tailoring import build_tailoring_payload, load_user_resume_plain_text

router = APIRouter(prefix="/jobs", tags=["jobs"])


class JobMatchResponse(BaseModel):
    id: int
    title: str
    company: str
    location: str | None = None
    score: float | None = None
    explanation: str | None = None
    source: str


class ApplicationResponse(BaseModel):
    id: int
    job_id: int
    status: str
    provider: str
    status_detail: str | None = None
    job_title: str | None = None
    company: str | None = None
    job_url: str | None = None


FAKE_JOBS = [
    {
        "external_id": "fake-1",
        "title": "Backend Engineer",
        "company": "Acme Tech",
        "location": "Pune",
        "description": "Build APIs with Python and FastAPI.",
    },
    {
        "external_id": "fake-2",
        "title": "Full Stack Developer",
        "company": "Orbit Labs",
        "location": "Remote",
        "description": "React + Python product development.",
    },
]


@router.post("/discover/fake")
def discover_fake_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, int]:
    created_count = 0
    for item in FAKE_JOBS:
        score, explanation = score_job_for_user(current_user, item)
        existing = db.query(Job).filter(Job.external_id == item["external_id"]).first()
        if existing:
            existing.relevance_score = score
            existing.relevance_explanation = explanation
            job = existing
        else:
            job = Job(
                external_id=item["external_id"],
                title=item["title"],
                company=item["company"],
                location=item["location"],
                description=item["description"],
                source="fake",
                relevance_score=score,
                relevance_explanation=explanation,
                url=f"https://example.com/jobs/{item['external_id']}",
            )
            db.add(job)
            created_count += 1
        db.flush()

        existing_app = (
            db.query(JobApplication)
            .filter(
                JobApplication.user_id == current_user.id,
                JobApplication.job_id == job.id,
            )
            .first()
        )
        if not existing_app:
            db.add(
                JobApplication(
                    user_id=current_user.id,
                    job_id=job.id,
                    status="queued",
                    provider="fake",
                )
            )

    db.commit()
    return {"created_jobs": created_count, "total_fake_jobs": len(FAKE_JOBS)}


@router.post("/discover/providers")
def discover_provider_feeds(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, int]:
    """Pull stub jobs from all registered boards (expand with real APIs later)."""
    return run_provider_discovery(db, current_user)


@router.post("/applications/auto-apply/run")
def run_my_auto_apply(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, int | str]:
    """Attempt automation; failures become manual_required with an explanation."""
    return run_auto_apply_for_user(db, current_user.id)


@router.post("/applications/{application_id}/manual-complete")
def mark_manual_application_complete(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str | int]:
    app_row = (
        db.query(JobApplication)
        .filter(
            JobApplication.id == application_id,
            JobApplication.user_id == current_user.id,
        )
        .first()
    )
    if not app_row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    suffix = "User confirmed application submitted manually via posting link."
    if app_row.status_detail:
        app_row.status_detail = app_row.status_detail.strip() + " | " + suffix
    else:
        app_row.status_detail = suffix
    app_row.status = "manual_completed"
    db.add(app_row)
    db.commit()
    return {"id": app_row.id, "status": app_row.status}


@router.get("/matches", response_model=list[JobMatchResponse])
def list_job_matches(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[JobMatchResponse]:
    _ = current_user
    jobs = db.query(Job).order_by(Job.relevance_score.desc().nullslast()).all()
    return [
        JobMatchResponse(
            id=j.id,
            title=j.title,
            company=j.company,
            location=j.location,
            score=j.relevance_score,
            explanation=j.relevance_explanation,
            source=j.source,
        )
        for j in jobs
    ]


@router.get("/applications", response_model=list[ApplicationResponse])
def list_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ApplicationResponse]:
    rows = (
        db.query(JobApplication, Job)
        .join(Job, Job.id == JobApplication.job_id)
        .filter(JobApplication.user_id == current_user.id)
        .order_by(JobApplication.created_at.desc())
        .all()
    )
    return [
        ApplicationResponse(
            id=a.id,
            job_id=a.job_id,
            status=a.status,
            provider=a.provider,
            status_detail=a.status_detail,
            job_title=j.title,
            company=j.company,
            job_url=j.url,
        )
        for a, j in rows
    ]


@router.get("/{job_id}/tailoring")
def get_job_resume_tailoring(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    text, note = load_user_resume_plain_text(current_user.resume_path)
    if note and not text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=note,
        )

    return build_tailoring_payload(
        text,
        job_title=job.title,
        company=job.company,
        jd_description=job.description or "",
        resume_extraction_note=note,
    )


@router.get("/{job_id}/tailored-resume.txt")
def download_tailored_resume_text(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PlainTextResponse:
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    text, note = load_user_resume_plain_text(current_user.resume_path)
    if note and not text.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=note)

    payload = build_tailoring_payload(
        text,
        job_title=job.title,
        company=job.company,
        jd_description=job.description or "",
        resume_extraction_note=note,
    )
    body = payload["full_text_draft"]
    filename = f"tailored-resume-{job_id}.txt"
    return PlainTextResponse(
        body,
        media_type="text/plain; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
