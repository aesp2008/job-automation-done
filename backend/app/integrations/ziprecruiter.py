from backend.app.integrations.base import ApplicationResult, ProviderJob


class ZipRecruiterProvider:
    provider_name = "ziprecruiter"

    def search_jobs(self, user_profile: dict) -> list[ProviderJob]:
        role = (user_profile.get("target_roles") or ["Software Engineer"])[0]
        loc = (user_profile.get("locations") or ["Remote"])[0]
        return [
            ProviderJob(
                external_id=f"ziprecruiter-{role.lower().replace(' ', '-')}-1",
                title=f"{role} (Direct Hire)",
                company="ZipRecruiter Sample Corp",
                location=loc,
                description=(
                    "Full stack with React, TypeScript, FastAPI, and Redis. "
                    "CI/CD with Jenkins and Docker. Elasticsearch experience a plus."
                ),
                url="https://www.ziprecruiter.com/jobs-search",
                source=self.provider_name,
            )
        ]

    def can_auto_apply(self) -> bool:
        return False

    def apply_to_job(self, job: ProviderJob, user_profile: dict) -> ApplicationResult:
        _ = (job, user_profile)
        return ApplicationResult(status="queued", details="ZipRecruiter apply is stubbed.")

    def get_status(self) -> dict:
        return {
            "provider": self.provider_name,
            "connected": False,
            "mode": "stub",
            "details": "Stub provider. Partner API pending.",
        }
