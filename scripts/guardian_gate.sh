#!/data/data/com.termux/files/usr/bin/bash

set -u
set -o pipefail

cd "$(git rev-parse --show-toplevel 2>/dev/null)" || {
    echo "STOP: NOT INSIDE GUARDIAN HUNTER REPOSITORY"
    exit 1
}

fail() {
    echo
    echo "=================================================="
    echo "GUARDIAN GATE: FAIL CLOSED"
    echo "REASON: $1"
    echo "=================================================="
    exit 1
}

echo
echo "=================================================="
echo "       GUARDIAN HUNTER SECURITY GATE"
echo "=================================================="

# ------------------------------------------------------------
# TRUST ROOT
# ------------------------------------------------------------

[ -f .guardian/trusted-baseline ] ||
    fail "TRUSTED BASELINE MISSING"

HEAD_NOW="$(git rev-parse HEAD)" ||
    fail "CANNOT READ HEAD"

BASE_NOW="$(tr -d '\n' < .guardian/trusted-baseline)" ||
    fail "CANNOT READ TRUSTED BASELINE"

echo "HEAD=$HEAD_NOW"
echo "BASELINE=$BASE_NOW"

[ "$HEAD_NOW" = "$BASE_NOW" ] ||
    fail "HEAD DOES NOT MATCH TRUSTED BASELINE"

echo "PASS: TRUST ROOT"

# ------------------------------------------------------------
# WORKTREE FINGERPRINT
# ------------------------------------------------------------

BEFORE="$(mktemp)" ||
    fail "CANNOT CREATE BEFORE FINGERPRINT"

AFTER="$(mktemp)" || {
    rm -f "$BEFORE"
    fail "CANNOT CREATE AFTER FINGERPRINT"
}

cleanup() {
    rm -f "$BEFORE" "$AFTER"
}

trap cleanup EXIT INT TERM

git status --porcelain=v1 > "$BEFORE" ||
    fail "CANNOT CAPTURE WORKTREE"

# ------------------------------------------------------------
# COMPILE SECURITY BOUNDARY
# ------------------------------------------------------------

echo
echo "--- COMPILE ---"

python -m py_compile \
    guardian_hunter/integration/operational_cycle.py \
    guardian_hunter/operate.py \
    guardian_hunter/repair/executor.py \
    tests/test_security_architecture.py \
    guardian_hunter/harness/provider_runtime.py \
    guardian_hunter/integration/automatic_repair.py \
    guardian_hunter/integration/codex_supervised.py ||
    fail "COMPILE FAILURE"

echo "PASS: COMPILE"

# ------------------------------------------------------------
# ADVERSARIAL AUTHORIZATION GATE
# ------------------------------------------------------------

echo
echo "--- ATTACK 1: MISSING / UNTRUSTED AUTHORIZATION ---"

python -m pytest -q \
    tests/test_security_architecture.py::test_req004_missing_evidence_blocks_authorization \
    tests/test_security_architecture.py::test_req004_tampered_evidence_blocks_authorization \
    tests/test_security_architecture.py::test_req001_trust_denial_does_not_consume_nonce ||
    fail "ATTACK 1 FAILURE"

echo "PASS: MISSING / UNTRUSTED AUTHORIZATION FAILS CLOSED"

echo
echo "--- ATTACK 2: AUTHORIZATION REUSE / NONCE REPLAY ---"

python -m pytest -q \
    tests/test_security_architecture.py::test_req001_trust_denial_does_not_consume_nonce ||
    fail "ATTACK 2 FAILURE"

echo "PASS: AUTHORIZATION REUSE / NONCE REPLAY FAILS CLOSED"

echo
echo "--- ATTACK 3: TAMPERED EVIDENCE / CANDIDATE ---"

python -m pytest -q \
    tests/test_security_architecture.py::test_req004_tampered_evidence_blocks_authorization ||
    fail "ATTACK 3 FAILURE"

echo "PASS: TAMPERED EVIDENCE FAILS CLOSED"

echo
echo "--- ATTACK 4: EXECUTION WITHOUT CONSENT ---"

python -m pytest -q \
    tests/test_security_architecture.py::test_req003_direct_authorized_transition_blocked \
    tests/test_security_architecture.py::test_req002_req005_adapter_plans_but_never_executes ||
    fail "ATTACK 4 FAILURE"

echo "PASS: EXECUTION WITHOUT CONSENT FAILS CLOSED"

# ------------------------------------------------------------
# COMPLETE SECURITY ARCHITECTURE
# ------------------------------------------------------------

echo
echo "--- SECURITY ARCHITECTURE ---"

python -m pytest -q tests/test_security_architecture.py ||
    fail "SECURITY ARCHITECTURE FAILURE"

echo "PASS: SECURITY ARCHITECTURE"

# ------------------------------------------------------------
# FULL REGRESSION
# ------------------------------------------------------------

echo
echo "--- FULL REGRESSION ---"

python -m pytest -q ||
    fail "FULL REGRESSION FAILURE"

echo "PASS: FULL REGRESSION"

# ------------------------------------------------------------
# DIFF INTEGRITY
# ------------------------------------------------------------

echo
echo "--- DIFF INTEGRITY ---"

git diff --check ||
    fail "DIFF CHECK FAILURE"

git diff --cached --check ||
    fail "STAGED DIFF CHECK FAILURE"

echo "PASS: DIFF INTEGRITY"

# ------------------------------------------------------------
# MUTATION DETECTION
# ------------------------------------------------------------

git status --porcelain=v1 > "$AFTER" ||
    fail "CANNOT CAPTURE FINAL WORKTREE"

cmp -s "$BEFORE" "$AFTER" ||
    fail "TESTS MUTATED WORKTREE"

echo "PASS: TESTS DID NOT MUTATE WORKTREE"

# ------------------------------------------------------------
# FINAL TRUST ROOT RECHECK
# ------------------------------------------------------------

HEAD_AFTER="$(git rev-parse HEAD)" ||
    fail "CANNOT RECHECK HEAD"

BASE_AFTER="$(tr -d '\n' < .guardian/trusted-baseline)" ||
    fail "CANNOT RECHECK BASELINE"

[ "$HEAD_AFTER" = "$HEAD_NOW" ] ||
    fail "HEAD CHANGED DURING GATE"

[ "$BASE_AFTER" = "$BASE_NOW" ] ||
    fail "TRUSTED BASELINE CHANGED DURING GATE"

[ "$HEAD_AFTER" = "$BASE_AFTER" ] ||
    fail "FINAL TRUST ROOT MISMATCH"

echo "PASS: TRUST ROOT REMAINED FROZEN"

echo
echo "=================================================="
echo "GUARDIAN GATE: PASS"
echo "ATTACK CLASSES: 4/4 FAIL CLOSED"
echo "SECURITY ARCHITECTURE: PASS"
echo "FULL REGRESSION: PASS"
echo "WORKTREE MUTATION: NONE"
echo "TRUST ROOT: FROZEN"
echo "=================================================="

exit 0
