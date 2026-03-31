from backend.app.integrations.base import ApplicationResult, ProviderJob


class CareerBuilderProvider:
    provider_name = "careerbuilder"

    def search_jobs(self, user_profile: dict) -> list[ProviderJob]:
        role = (user_profile.get("target_roles") or ["Software Engineer"])[0]
        loc = (user_profile.get("locations") or ["Remote"])[0]
        return [
            ProviderJob(
                external_id=f"careerbuilder-{role.lower().replace(' ', '-')}-1",
                title=f"Senior {role}",
                company="CareerBuilder Sample Industry",
                location=loc,
                description=(
                    "C#, Azure, SQL Server, and Angular frontend. "
                    "Experience with dockerized services appreciated."
                ),
                url="https://www.careerbuilder.com/jobs",
                source=self.provider_name,
            )
        ]

    def can_auto_apply(self) -> bool:
        return False

    def apply_to_job(self, job: ProviderJob, user_profile: dict) -> ApplicationResult:
        _ = (job, user_profile)
        return ApplicationResult(status="queued", details="CareerBuilder apply is stubbed.")

    def get_status(self) -> dict:
        return {
            "provider": self.provider_name,
            "connected": False,
            "mode": "stub",
            "details": "Stub provider. Feed/API pending.",
        }
