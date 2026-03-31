from backend.app.integrations.base import ApplicationResult, ProviderJob


class FakeBoardProvider:
    """Matches applications with source=fake from /jobs/discover/fake."""

    provider_name = "fake"

    def search_jobs(self, user_profile: dict) -> list[ProviderJob]:
        _ = user_profile
        return []

    def can_auto_apply(self) -> bool:
        return False

    def apply_to_job(self, job: ProviderJob, user_profile: dict) -> ApplicationResult:
        _ = (job, user_profile)
        return ApplicationResult(
            status="manual_only",
            details="Demo jobs use manual applications only.",
        )

    def get_status(self) -> dict:
        return {
            "provider": self.provider_name,
            "connected": False,
            "mode": "stub",
            "details": "Local demo postings only.",
        }
