"""Guardian Hunter operational entry point.

Runs the existing defensive operational cycle and reports actionable state.
This entry point cannot commit, merge, promote the trusted baseline, or
self-authorize protected repairs.
"""

from __future__ import annotations

import argparse
import json
from typing import Any

from guardian_hunter.integration.operational_cycle import run_operational_cycle


def _summary(result: dict[str, Any]) -> dict[str, Any]:
    audit = result.get("audit", {})
    repair = result.get("repair", {})
    ai = result.get("ai", {})
    nuclei = result.get("nuclei", {})

    return {
        "status": result.get("status", "UNKNOWN"),
        "health": result.get("health", {}).get("status", "UNKNOWN"),
        "findings": audit.get("finding_count", 0),
        "repair_proposals": repair.get("proposal_count", 0),
        "ai": ai,
        "nuclei": nuclei,
        "authority": {
            "automatic_commit": False,
            "automatic_merge": False,
            "automatic_baseline_update": False,
            "protected_repairs_require_human": True,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="guardian-hunter",
        description="Run one Guardian Hunter defensive operational cycle.",
    )
    parser.add_argument(
        "--target",
        default=None,
        help="Optional defensive Nuclei target.",
    )
    parser.add_argument(
        "--authorized-target",
        action="store_true",
        help="Confirm that the supplied target is authorized for defensive testing.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the complete operational result as JSON.",
    )

    args = parser.parse_args()

    if args.authorized_target and not args.target:
        parser.error("--authorized-target requires --target")

    result = run_operational_cycle(
        target=args.target,
        target_authorized=bool(args.target and args.authorized_target),
    )

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True, default=str))
    else:
        summary = _summary(result)

        print("=== GUARDIAN HUNTER OPERATIONAL CYCLE ===")
        print(f"STATUS: {summary['status']}")
        print(f"HEALTH: {summary['health']}")
        print(f"FINDINGS: {summary['findings']}")
        print(f"REPAIR PROPOSALS: {summary['repair_proposals']}")
        print()
        print("AI:")
        print(json.dumps(summary["ai"], indent=2, sort_keys=True, default=str))
        print()
        print("NUCLEI:")
        print(json.dumps(summary["nuclei"], indent=2, sort_keys=True, default=str))
        print()
        print("AUTHORITY:")
        print("  AUTOMATIC COMMIT: FALSE")
        print("  AUTOMATIC MERGE: FALSE")
        print("  AUTOMATIC BASELINE UPDATE: FALSE")
        print("  PROTECTED REPAIR: HUMAN APPROVAL REQUIRED")

    return 0 if result.get("status") == "HEALTHY" else 2


if __name__ == "__main__":
    raise SystemExit(main())
