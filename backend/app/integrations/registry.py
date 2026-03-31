"""Job providers registered for discovery. Product scope: LinkedIn-first (stub until OAuth)."""

from backend.app.integrations.linkedin import LinkedInProvider


def get_providers():
    return [LinkedInProvider()]
