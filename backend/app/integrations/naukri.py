from backend.app.integrations.base import ApplicationResult, ProviderJob


class NaukriProvider:
    provider_name = "naukri"

    def search_jobs(self, user_profile: dict) -> list[ProviderJob]:
        role = (user_profile.get("target_roles") or ["Software Engineer"])[0]
        loc = (user_profile.get("locations") or ["Bangalore"])[0]
        return [
            ProviderJob(
                external_id=f"naukri-{role.lower().replace(' ', '-')}-1",
                title=f"{role}",
                company="Naukri Sample IT Services",
                location=loc,
                description=(
                    "Java, Spring, microservices on Azure. "
                    "MongoDB, RabbitMQ, Kubernetes, and Linux production support."
                ),
                url="https://www.naukri.com/jobs",
                source=self.provider_name,
            )
        ]

    def can_auto_apply(self) -> bool:
        return False

    def apply_to_job(self, job: ProviderJob, user_profile: dict) -> ApplicationResult:
        _ = (job, user_profile)
        return ApplicationResult(status="queued", details="Naukri apply is stubbed.")

    def get_status(self) -> dict:
        return {
            "provider": self.provider_name,
            "connected": False,
            "mode": "stub",
            "details": "Stub provider. Session integration pending.",
        }
