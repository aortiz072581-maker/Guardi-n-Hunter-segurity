"""Independent OPA authorization verification.

OPA is an additional verifier.  It grants no execution, commit,
merge, baseline-update, or global-execution authority.

Any engine failure, timeout, malformed output, missing policy,
or invalid input fails closed.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import shutil
import subprocess
from typing import Any


OPA_QUERY = "data.guardian.authorization.allow"
OPA_TIMEOUT_SECONDS = 5.0


@dataclass(frozen=True)
class OPADecision:
    allowed: bool
    reason: str


def policy_path() -> Path:
    return (
        Path(__file__).resolve().parent
        / "opa"
        / "guardian_authorization.rego"
    )


def evaluate_opa(
    context: dict[str, Any],
    *,
    opa_binary: str | None = None,
    timeout: float = OPA_TIMEOUT_SECONDS,
) -> OPADecision:
    """Evaluate independent policy and fail closed on every error."""

    binary = opa_binary or shutil.which("opa")

    if not binary:
        return OPADecision(False, "OPA_NOT_AVAILABLE")

    policy = policy_path()

    if not policy.is_file():
        return OPADecision(False, "OPA_POLICY_MISSING")

    try:
        payload = json.dumps(
            context,
            sort_keys=True,
            separators=(",", ":"),
        )

        completed = subprocess.run(
            [
                binary,
                "eval",
                "--format",
                "raw",
                "--stdin-input",
                "--data",
                str(policy),
                OPA_QUERY,
            ],
            input=payload,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )

    except subprocess.TimeoutExpired:
        return OPADecision(False, "OPA_TIMEOUT")

    except Exception as exc:
        return OPADecision(
            False,
            f"OPA_ENGINE_ERROR:{type(exc).__name__}",
        )

    if completed.returncode != 0:
        return OPADecision(False, "OPA_EVALUATION_FAILED")

    output = completed.stdout.strip()

    if output == "true":
        return OPADecision(True, "OPA_ALLOW")

    if output == "false":
        return OPADecision(False, "OPA_DENY")

    return OPADecision(False, "OPA_INVALID_OUTPUT")
