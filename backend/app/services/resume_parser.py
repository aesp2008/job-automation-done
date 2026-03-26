from pathlib import Path


KNOWN_SKILLS = [
    "python",
    "java",
    "javascript",
    "typescript",
    "react",
    "next.js",
    "fastapi",
    "django",
    "sql",
    "postgresql",
    "docker",
    "kubernetes",
    "aws",
    "azure",
    "git",
]


def parse_resume_bytes(filename: str, content: bytes) -> dict:
    """Return a lightweight parsed summary for MVP use."""
    text = content.decode("utf-8", errors="ignore").lower()
    found_skills = [skill for skill in KNOWN_SKILLS if skill in text]

    return {
        "filename": Path(filename).name,
        "file_size_kb": round(len(content) / 1024, 2),
        "extension": Path(filename).suffix.lower(),
        "skills_detected": found_skills[:12],
        "summary": "MVP parser: basic keyword extraction from uploaded file content.",
    }

