#!/usr/bin/env bash
set -u
cd "$(dirname "$0")"
W="-W ignore::DeprecationWarning -W ignore::UserWarning"
echo "[1/3] ruff criticos"
ruff check guardian_hunter --exclude legacy --select F821,F601,F811,E9 || exit 1
echo "[2/3] seguridad"
python -m pytest -q -p no:cacheprovider $W guardian_hunter/tests/test_execution_consolidation.py guardian_hunter/tests/test_final_security_consolidation.py guardian_hunter/tests/test_security_verifier.py || exit 1
echo "[3/3] suite completa"
python -m pytest -q -p no:cacheprovider $W || exit 1
echo VERIFY_OK
