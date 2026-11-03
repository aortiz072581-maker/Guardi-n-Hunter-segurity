"""
Central Safety Policy - reemplaza los 117 DRY_RUN=True
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class SafetyPolicy:
    READ_ONLY: bool = True
    DRY_RUN: bool = True
    REAL_EXECUTION_BLOCKED: bool = True
    HUMAN_REVIEW_REQUIRED: bool = True
    RESPONSE_LOCKED: bool = True

    def holds(self) -> bool:
        return all([self.READ_ONLY, self.DRY_RUN, self.REAL_EXECUTION_BLOCKED, self.HUMAN_REVIEW_REQUIRED, self.RESPONSE_LOCKED])

POLICY = SafetyPolicy()
READ_ONLY = POLICY.READ_ONLY
DRY_RUN = POLICY.DRY_RUN
REAL_EXECUTION_BLOCKED = POLICY.REAL_EXECUTION_BLOCKED
HUMAN_REVIEW_REQUIRED = POLICY.HUMAN_REVIEW_REQUIRED
RESPONSE_LOCKED = POLICY.RESPONSE_LOCKED
