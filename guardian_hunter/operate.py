"""Guardian Hunter operational entry point.

from guardian_hunter.integration.operational_cycle import run_supervised_automatic_repair
Runs the existing defensive operational cycle and reports actionable state.
This entry point cannot commit, merge, promote the trusted baseline, or
self-authorize protected repairs.
"""

from __future__ import annotations

import argparse
import json
import time
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

    parser.add_argument(
        "--watch",
        action="store_true",
        help="Run Guardian Hunter continuously in controlled operational mode.",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=300,
        help="Seconds between operational cycles in --watch mode (minimum 60).",
    )

    parser.add_argument(
        "--auto-repair",
        action="store_true",
        help=(
            "Enable processing of exact pre-authorized ordinary repair "
            "candidates. Protected repairs remain human-gated."
        ),
    )

    parser.add_argument(
        "--codex-supervised",
        action="store_true",
        help=(
            "Use read-only ephemeral Codex to prepare exact "
            "ordinary repair candidates."
        ),
    )

    args = parser.parse_args()

    if args.authorized_target and not args.target:
        parser.error("--authorized-target requires --target")

    def execute_cycle() -> tuple[dict, int]:
        baseline = None
        repair_candidates = ()

        if args.auto_repair:
            from pathlib import Path

            baseline_path = Path(".guardian/trusted-baseline")

            if baseline_path.is_file():
                baseline = baseline_path.read_text(
                    encoding="utf-8"
                ).strip()

        result = run_operational_cycle(
            target=args.target,
            target_authorized=bool(args.target and args.authorized_target),
            repair_candidates=repair_candidates,
            baseline=baseline,
            supervised_codex=(args.codex_supervised or args.auto_repair),
            automatic_repair_enabled=args.auto_repair,
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

        rc = 0 if result.get("status") == "HEALTHY" else 2
        return result, rc

    if not args.watch:
        _, rc = execute_cycle()
        return rc

    if args.interval < 60:
        parser.error("--interval must be at least 60 seconds")

    print("=== GUARDIAN HUNTER CONTINUOUS OPERATION ===")
    print(f"INTERVAL: {args.interval} seconds")
    print("AUTOMATIC REVIEW: ENABLED")
    print("AUTOMATIC DIAGNOSIS: ENABLED")
    print("AUTOMATIC REPAIR PROPOSALS: ENABLED")
    print(
        "AUTOMATIC ORDINARY REPAIR: "
        + ("ENABLED" if args.auto_repair else "DISABLED")
    )
    print(
        "SUPERVISED CODEX: "
        + ("ENABLED" if args.codex_supervised else "DISABLED")
    )
    print("AUTOMATIC COMMIT: FALSE")
    print("AUTOMATIC MERGE: FALSE")
    print("AUTOMATIC BASELINE UPDATE: FALSE")
    print("PROTECTED REPAIR: HUMAN APPROVAL REQUIRED")
    print("STOP: Ctrl-C")
    print()

    try:
        while True:
            started = time.strftime("%Y-%m-%d %H:%M:%S")
            print(f"--- CYCLE {started} ---", flush=True)

            try:
                _, rc = execute_cycle()
                print(f"CYCLE EXIT: {rc}", flush=True)
            except Exception as exc:
                # Fail closed: one failed cycle must never grant authority.
                print(
                    f"CYCLE ERROR: {type(exc).__name__}: {exc}",
                    flush=True,
                )

            print(
                f"NEXT REVIEW IN: {args.interval} seconds",
                flush=True,
            )
            time.sleep(args.interval)

    except KeyboardInterrupt:
        print()
        print("GUARDIAN HUNTER CONTINUOUS OPERATION STOPPED")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
