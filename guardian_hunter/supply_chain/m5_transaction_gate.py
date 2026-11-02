"""Fail-closed gate for transactional repair; no local identity can authorize execution."""
from __future__ import annotations
from pathlib import Path

def enforce_transaction(*, proposal, action, baseline, approval, root):
    """Require independent cryptographic identity and approval, not configured in Termux."""
    if not isinstance(baseline, str) or len(baseline) != 64 or any(c not in '0123456789abcdef' for c in baseline):
        raise PermissionError('M5_INVALID_BASELINE')
    if not isinstance(root, Path):
        raise PermissionError('M5_INVALID_ROOT')
    if not isinstance(action.relative_path, str) or action.relative_path not in proposal.affected_files:
        raise PermissionError('M5_PROPOSAL_ACTION_MISMATCH')
    p=Path(action.relative_path)
    if p.is_absolute() or '..' in p.parts or not p.parts or '\\' in action.relative_path:
        raise PermissionError('M5_INVALID_TARGET')
    # No trusted external verifier or independently authenticated human approval configured.
    raise PermissionError('M5_EXTERNAL_AUTHORIZATION_UNAVAILABLE')
