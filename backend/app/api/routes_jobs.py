from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.core.security import get_current_user
from backend.app.db.session import get_db
from backend.app.models.application import JobApplication
from backend.app.models.job import Job
from backend.app.models.user import User


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


FAKE_JOBS = [
    {
        "external_id": "fake-1",
        "title": "Backend Engineer",
        "company": "Acme Tech",
        "location": "Pune",
        "description": "Build APIs with Python and FastAPI.",
        "score": 0.89,
        "explanation": "Matches backend Python experience and API focus.",
    },
    {
        "external_id": "fake-2",
        "title": "Full Stack Developer",
        "company": "Orbit Labs",
        "location": "Remote",
        "description": "React + Python product development.",
        "score": 0.81,
        "explanation": "Strong overlap with React and backend stack.",
    },
]


@router.post("/discover/fake")
def discover_fake_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, int]:
    created_count = 0
    for item in FAKE_JOBS:
        existing = db.query(Job).filter(Job.external_id == item["external_id"]).first()
        if existing:
            existing.relevance_score = item["score"]
            existing.relevance_explanation = item["explanation"]
            job = existing
        else:
            job = Job(
                external_id=item["external_id"],
                title=item["title"],
                company=item["company"],
                location=item["location"],
                description=item["description"],
                source="fake",
                relevance_score=item["score"],
                relevance_explanation=item["explanation"],
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
    apps = (
        db.query(JobApplication)
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
        )
        for a in apps
    ]

