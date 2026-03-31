from backend.app.services.resume_tailoring import (
    build_tailoring_payload,
    tailoring_payload_to_docx_bytes,
)


def test_tailoring_orders_skills_and_matches_jd() -> None:
    resume = "10 years Python, FastAPI, PostgreSQL, Docker in production."
    jd = "Need strong Python, AWS, Kubernetes, and Terraform experience."
    out = build_tailoring_payload(
        resume,
        job_title="Platform Engineer",
        company="Example Co",
        jd_description=jd,
    )
    assert "python" in out["skills_matched_with_jd"]
    assert "aws" in out["skills_gaps_vs_jd"]
    assert out["skills_section_ordered"][0] in out["jd_skills_highlighted"]
    assert "Platform Engineer" in out["full_text_draft"]


def test_tailoring_docx_is_valid_zip() -> None:
    out = build_tailoring_payload(
        "Python developer.",
        job_title="Engineer",
        company="Co",
        jd_description="Need Python.",
    )
    raw = tailoring_payload_to_docx_bytes(out)
    assert raw[:2] == b"PK"
