from backend.app.integrations.base import ApplicationResult, ProviderJob


class WorkdayStubProvider:
    """Simulates an ATS that allows auto-apply attempts but fails (manual fallback path)."""

    provider_name = "workday_ats"

    def search_jobs(self, user_profile: dict) -> list[ProviderJob]:
        role = (user_profile.get("target_roles") or ["Software Engineer"])[0]
        loc = (user_profile.get("locations") or ["Remote"])[0]
        return [
            ProviderJob(
                external_id=f"workday-{role.lower().replace(' ', '-')}-1",
                title=f"{role} (Workday posting)",
                company="Workday Stub Enterprise",
                location=loc,
                description=(
                    "Enterprise role: Python, FastAPI, AWS, Terraform, and PostgreSQL. "
                    "Kubernetes platform team."
                ),
                url="https://example.com/careers/workday-stub",
                source=self.provider_name,
            )
        ]

    def can_auto_apply(self) -> bool:
        return True

    def apply_to_job(self, job: ProviderJob, user_profile: dict) -> ApplicationResult:
        _ = (job, user_profile)
        return ApplicationResult(
            status="failed",
            details=(
                "Simulated ATS failure (session/expired). "
                "Complete your application manually on the employer site."
            ),
        )

    def get_status(self) -> dict:
        return {
            "provider": self.provider_name,
            "connected": False,
            "mode": "stub",
            "details": "Stub ATS with intentional failed auto-apply for testing manual fallback.",
        }
