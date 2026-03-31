from backend.app.integrations.base import ApplicationResult, ProviderJob


class LinkedInProvider:
    """LinkedIn-only product scope. Live job search requires LinkedIn-approved API + OAuth (not public RSS)."""

    provider_name = "linkedin"

    def search_jobs(self, user_profile: dict) -> list[ProviderJob]:
        role = (user_profile.get("target_roles") or ["Software Engineer"])[0]
        loc = (user_profile.get("locations") or ["Remote"])[0]
        return [
            ProviderJob(
                external_id=f"linkedin-{role.lower().replace(' ', '-')}-sample-1",
                title=f"{role}",
                company="Sample employer (LinkedIn flow placeholder)",
                location=loc,
                description=(
                    f"Placeholder listing aligned to your saved role “{role}”. "
                    "When LinkedIn OAuth + Jobs API access is implemented, this will be replaced by "
                    "real search results. Skills emphasis: Python, APIs, collaboration, ownership."
                ),
                url="https://www.linkedin.com/jobs/",
                source=self.provider_name,
            )
        ]

    def can_auto_apply(self) -> bool:
        return False

    def apply_to_job(self, job: ProviderJob, user_profile: dict) -> ApplicationResult:
        _ = (job, user_profile)
        return ApplicationResult(
            status="manual_only",
            details="Apply on LinkedIn at the job URL. Auto-apply is not enabled.",
        )

    def get_status(self) -> dict:
        return {
            "provider": self.provider_name,
            "connected": False,
            "mode": "linkedin_stub",
            "details": (
                "LinkedIn-first app: live search needs LinkedIn Developer app + OAuth + approved API "
                "products (subject to LinkedIn terms). This row is a single demo listing until then."
            ),
        }
