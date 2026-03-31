from backend.app.integrations.base import ApplicationResult, ProviderJob


class WellfoundProvider:
    provider_name = "wellfound"

    def search_jobs(self, user_profile: dict) -> list[ProviderJob]:
        role = (user_profile.get("target_roles") or ["Software Engineer"])[0]
        loc = (user_profile.get("locations") or ["Remote"])[0]
        return [
            ProviderJob(
                external_id=f"wellfound-{role.lower().replace(' ', '-')}-1",
                title=f"{role} @ early-stage startup",
                company="Wellfound Sample Startup",
                location=loc,
                description=(
                    "Node.js, GraphQL, React, PostgreSQL, and GCP. "
                    "Small team; Docker and git workflows."
                ),
                url="https://wellfound.com/role/l/software-engineer",
                source=self.provider_name,
            )
        ]

    def can_auto_apply(self) -> bool:
        return False

    def apply_to_job(self, job: ProviderJob, user_profile: dict) -> ApplicationResult:
        _ = (job, user_profile)
        return ApplicationResult(status="queued", details="Wellfound apply is stubbed.")

    def get_status(self) -> dict:
        return {
            "provider": self.provider_name,
            "connected": False,
            "mode": "stub",
            "details": "Stub provider. OAuth pending.",
        }
