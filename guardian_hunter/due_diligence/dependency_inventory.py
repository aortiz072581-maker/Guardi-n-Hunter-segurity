"""Phase 152 — dependency inventory contract."""

from dataclasses import dataclass


@dataclass(frozen=True)
class DependencyRecord:
    name: str
    version: str
    ecosystem: str
    license_status: str


def validate_dependency(record: DependencyRecord) -> bool:
    if not record.name:
        return False

    if not record.version:
        return False

    if not record.ecosystem:
        return False

    if not record.license_status:
        return False

    return True
