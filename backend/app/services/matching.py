from __future__ import annotations

from typing import Any

from backend.app.models.user import User


def _normalize(text: str | None) -> str:
    return (text or "").strip().lower()


def _token_overlap_score(a: str, b: str) -> float:
    a_tokens = set(_normalize(a).replace("/", " ").replace("-", " ").split())
    b_tokens = set(_normalize(b).replace("/", " ").replace("-", " ").split())
    if not a_tokens or not b_tokens:
        return 0.0
    intersection = len(a_tokens.intersection(b_tokens))
    return intersection / max(len(a_tokens), 1)


def score_job_for_user(user: User, job_payload: dict[str, Any]) -> tuple[float, str]:
    """
    Compute a deterministic MVP relevance score + explanation.
    This is intentionally simple and can be replaced by LLM scoring later.
    """
    title = _normalize(str(job_payload.get("title", "")))
    location = _normalize(str(job_payload.get("location", "")))
    description = _normalize(str(job_payload.get("description", "")))

    prefs = user.preferences or {}
    target_roles = [str(x).strip() for x in prefs.get("target_roles", []) if str(x).strip()]
    target_locations = [str(x).strip() for x in prefs.get("locations", []) if str(x).strip()]

    role_score = 0.0
    if target_roles:
        role_score = max(_token_overlap_score(role, title) for role in target_roles)

    location_score = 0.0
    if target_locations:
        location_score = max(_token_overlap_score(loc, location) for loc in target_locations)

    # Lightweight bonus for basic backend/fullstack keywords in description.
    keyword_bonus = 0.0
    if any(k in description for k in ["python", "fastapi", "react", "api", "backend"]):
        keyword_bonus = 0.08

    base = 0.45
    score = min(0.99, round(base + (0.35 * role_score) + (0.12 * location_score) + keyword_bonus, 2))

    explanation_parts = []
    if target_roles:
        explanation_parts.append(f"role overlap {round(role_score, 2)}")
    if target_locations:
        explanation_parts.append(f"location overlap {round(location_score, 2)}")
    if keyword_bonus > 0:
        explanation_parts.append("keyword bonus from description")
    if not explanation_parts:
        explanation_parts.append("default MVP score (no user preferences set)")

    explanation = " | ".join(explanation_parts)
    return score, explanation

