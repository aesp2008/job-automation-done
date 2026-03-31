from backend.app.integrations.careerbuilder import CareerBuilderProvider
from backend.app.integrations.fake_board import FakeBoardProvider
from backend.app.integrations.glassdoor import GlassdoorProvider
from backend.app.integrations.indeed import IndeedProvider
from backend.app.integrations.linkedin import LinkedInProvider
from backend.app.integrations.naukri import NaukriProvider
from backend.app.integrations.unstop import UnstopProvider
from backend.app.integrations.wellfound import WellfoundProvider
from backend.app.integrations.workday_stub import WorkdayStubProvider
from backend.app.integrations.ziprecruiter import ZipRecruiterProvider


def get_providers():
    return [
        FakeBoardProvider(),
        LinkedInProvider(),
        UnstopProvider(),
        IndeedProvider(),
        GlassdoorProvider(),
        ZipRecruiterProvider(),
        NaukriProvider(),
        WellfoundProvider(),
        CareerBuilderProvider(),
        WorkdayStubProvider(),
    ]
