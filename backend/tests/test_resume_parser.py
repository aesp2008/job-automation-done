from io import BytesIO
from unittest.mock import MagicMock, patch

from docx import Document

from backend.app.services.resume_parser import parse_resume_bytes


def test_plain_text_extracts_skills() -> None:
    body = b"I build APIs with Python, FastAPI, and PostgreSQL."
    out = parse_resume_bytes("resume.txt", body)
    assert "python" in out["skills_detected"]
    assert "fastapi" in out["skills_detected"]
    assert "postgresql" in out["skills_detected"]


def test_pdf_extracts_text_via_pypdf() -> None:
    fake_page = MagicMock()
    fake_page.extract_text.return_value = "Senior Python developer with AWS and Docker."
    fake_reader = MagicMock()
    fake_reader.pages = [fake_page]
    with patch("backend.app.services.resume_parser.PdfReader", return_value=fake_reader):
        out = parse_resume_bytes("cv.pdf", b"%PDF-1.4 fake")
    assert "python" in out["skills_detected"]
    assert "aws" in out["skills_detected"]
    assert "docker" in out["skills_detected"]


def test_pdf_no_text_sets_note() -> None:
    fake_page = MagicMock()
    fake_page.extract_text.return_value = ""
    fake_reader = MagicMock()
    fake_reader.pages = [fake_page]
    with patch("backend.app.services.resume_parser.PdfReader", return_value=fake_reader):
        out = parse_resume_bytes("scan.pdf", b"%PDF-1.4 fake")
    assert out["skills_detected"] == []
    assert "scan" in out["summary"].lower() or "extractable" in out["summary"].lower()


def test_docx_round_trip() -> None:
    buf = BytesIO()
    doc = Document()
    doc.add_paragraph("Full stack: React, TypeScript, and Node.js.")
    doc.save(buf)
    raw = buf.getvalue()
    out = parse_resume_bytes("profile.docx", raw)
    assert "react" in out["skills_detected"]
    assert "typescript" in out["skills_detected"]
    assert "node.js" in out["skills_detected"]


def test_legacy_doc_rejected() -> None:
    out = parse_resume_bytes("old.doc", b"binary stuff")
    assert "not supported" in out["summary"].lower()
    assert out["skills_detected"] == []


def test_emails_deduped() -> None:
    body = b"Contact a@example.com and A@example.com plus b@test.org"
    out = parse_resume_bytes("c.txt", body)
    assert len(out["emails_found"]) >= 2
    lower = [e.lower() for e in out["emails_found"]]
    assert "a@example.com" in lower
