"""Human-readable output for supervised Guardian findings."""

from __future__ import annotations

from guardian_hunter.auditor.engine import audit


def main() -> int:
    findings = audit()

    print("=== GUARDIAN SUPERVISED AUDITOR ===")
    print("MODE: READ_ONLY")
    print("AUTOMATIC REPAIR: FALSE")
    print("AUTOMATIC APPROVAL: FALSE")
    print("EXECUTION ALLOWED: FALSE")
    print("HUMAN APPROVAL REQUIRED: TRUE")
    print("FINDINGS:", len(findings))

    for finding in findings:
        print()
        print(f"[{finding.finding_id}]")
        print("SEVERITY:", finding.severity.value)
        print("CONFIDENCE:", finding.confidence.value)
        print("TITLE:", finding.title)
        print("RISK:", finding.risk)

        print("EVIDENCE:")
        for item in finding.evidence:
            print(" -", item)

        print("AFFECTED FILES:")
        for item in finding.affected_files:
            print(" -", item)

        print("PROPOSED FIX:", finding.proposed_fix)

        print("REQUIRED TESTS:")
        for item in finding.required_tests:
            print(" -", item)

        print("PATCH APPLIED: FALSE")
        print("HUMAN DECISION: REQUIRED")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
