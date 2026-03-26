from backend.app.integrations.indeed import IndeedProvider
from backend.app.integrations.linkedin import LinkedInProvider
from backend.app.integrations.unstop import UnstopProvider


def get_providers():
    return [LinkedInProvider(), UnstopProvider(), IndeedProvider()]

