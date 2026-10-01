"""CLI adapter for Guardian Hunter diagnostic defensive flow."""

from __future__ import annotations

from uuid import uuid4
from pathlib import Path

from guardian_hunter.assets import AssetManager
from guardian_hunter.config.settings import DATA_DIR
from guardian_hunter.evidence.persistence import EvidenceStore
from guardian_hunter.integration.e2e_diagnostic_flow import (
    run_diagnostic_defensive_flow,
)
from guardian_hunter.pipeline.engine import SecurityPipeline
from guardian_hunter.integration.integrity_tamper import inspect_integrity_tamper


EVIDENCE_FILE = DATA_DIR / "diagnostic_evidence.jsonl"


def execute_diagnostic(domain: str) -> dict:
    """Run the existing fail-closed diagnostic defensive flow."""

    assets = AssetManager()
    evidence = EvidenceStore(EVIDENCE_FILE)
    pipeline = SecurityPipeline(
        asset_manager=assets,
    )

    trace_id = uuid4().hex

    result = run_diagnostic_defensive_flow(
        target=domain,
        asset_manager=assets,
        evidence_store=evidence,
        pipeline=pipeline,
        actor_id="guardian-hunter-cli",
        request_id=f"diagnostic-{trace_id}",
        authorization_id=f"diagnostic-auth-{trace_id}",
        nonce=f"diagnostic-nonce-{trace_id}",
    )

    print()
    print("=" * 60)
    print("           GUARDIAN HUNTER DIAGNOSTIC")
    print("=" * 60)
    print(f"Target          : {domain}")
    print(f"Status          : {result.get('status')}")
    print(f"Execution       : {result.get('execution_allowed', False)}")
    print(f"Read only       : {result.get('read_only', True)}")
    print(f"Dry run         : {result.get('dry_run', True)}")
    print(f"Response locked : {result.get('response_locked', True)}")

    baseline = DATA_DIR / "integrity_baseline.json"
    if baseline.exists():
        security = inspect_integrity_tamper(
            baseline,
            Path.cwd(),
        )
        result["integrity_tamper"] = security

        # Fail closed regardless of diagnostic outcome.
        result["execution_allowed"] = False
        result["response_locked"] = True

        print()
        print("SELF PROTECTION")
        print(f"Integrity       : {security['integrity_state']}")
        print(f"Tamper          : {security['tamper']['risk_level']}")
        print(f"Integrity gate  : {security['integrity_fail_closed']}")
        print(f"Tamper gate     : {security['tamper_fail_closed']}")

    diagnosis = result.get("diagnosis")

    if diagnosis:
        print()
        print("DIAGNOSIS")
        print(f"Risk level      : {diagnosis.get('risk_level')}")
        print(f"Risk score      : {diagnosis.get('risk_score')}")
        print(f"Confidence      : {diagnosis.get('confidence')}")
        print(
            f"Human review    : "
            f"{diagnosis.get('requires_human_review')}"
        )

        recommendations = diagnosis.get(
            "recommendations",
            [],
        )

        if recommendations:
            print()
            print("RECOMMENDATIONS")
            for item in recommendations:
                print(f"  - {item}")

    reason = result.get("reason")

    if reason:
        print()
        print(f"Reason          : {reason}")

    print()
    print("=" * 60)

    return result
