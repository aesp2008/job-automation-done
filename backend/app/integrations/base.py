from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass
class ProviderJob:
    external_id: str
    title: str
    company: str
    location: str
    description: str
    url: str
    source: str


@dataclass
class ApplicationResult:
    status: str
    details: str


class JobProvider(Protocol):
    provider_name: str

    def search_jobs(self, user_profile: dict) -> list[ProviderJob]:
        ...

    def can_auto_apply(self) -> bool:
        ...

    def apply_to_job(self, job: ProviderJob, user_profile: dict) -> ApplicationResult:
        ...

    def get_status(self) -> dict:
        ...

