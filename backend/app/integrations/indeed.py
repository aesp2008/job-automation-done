from backend.app.integrations.base import ApplicationResult, ProviderJob


class IndeedProvider:
    provider_name = "indeed"

    def search_jobs(self, user_profile: dict) -> list[ProviderJob]:
        role = (user_profile.get("target_roles") or ["Software Engineer"])[0]
        return [
            ProviderJob(
                external_id=f"indeed-{role.lower().replace(' ', '-')}-1",
                title=f"{role} II",
                company="Indeed Sample Co",
                location=(user_profile.get("locations") or ["Remote"])[0],
                description="Indeed stub search result for MVP flow.",
                url="https://www.indeed.com/jobs",
                source=self.provider_name,
            )
        ]

    def can_auto_apply(self) -> bool:
        return False

    def apply_to_job(self, job: ProviderJob, user_profile: dict) -> ApplicationResult:
        _ = (job, user_profile)
        return ApplicationResult(status="queued", details="Indeed apply is stubbed for now.")

    def get_status(self) -> dict:
        return {
            "provider": self.provider_name,
            "connected": False,
            "mode": "stub",
            "details": "Using stub provider. Session/OAuth integration pending.",
        }

