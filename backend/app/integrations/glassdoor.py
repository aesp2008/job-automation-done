from backend.app.integrations.base import ApplicationResult, ProviderJob


class GlassdoorProvider:
    provider_name = "glassdoor"

    def search_jobs(self, user_profile: dict) -> list[ProviderJob]:
        role = (user_profile.get("target_roles") or ["Software Engineer"])[0]
        loc = (user_profile.get("locations") or ["Remote"])[0]
        return [
            ProviderJob(
                external_id=f"glassdoor-{role.lower().replace(' ', '-')}-1",
                title=f"{role} — Platform",
                company="Glassdoor Sample Employer",
                location=loc,
                description=(
                    "Own microservices on AWS with Docker and Kubernetes. "
                    "Python, PostgreSQL, Kafka, and Terraform required."
                ),
                url="https://www.glassdoor.com/Job/index.htm",
                source=self.provider_name,
            )
        ]

    def can_auto_apply(self) -> bool:
        return False

    def apply_to_job(self, job: ProviderJob, user_profile: dict) -> ApplicationResult:
        _ = (job, user_profile)
        return ApplicationResult(status="queued", details="Glassdoor apply is stubbed.")

    def get_status(self) -> dict:
        return {
            "provider": self.provider_name,
            "connected": False,
            "mode": "stub",
            "details": "Stub provider. OAuth/API integration pending.",
        }
