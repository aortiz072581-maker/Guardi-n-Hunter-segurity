"""135 → 138 OmniRoute preflight tests."""

from guardian_hunter.omniroute.phase135_138_preflight import (
    DRY_RUN,
    HUMAN_REVIEW_REQUIRED,
    READ_ONLY,
    REAL_EXECUTION_BLOCKED,
    RESPONSE_LOCKED,
    security_contract,
    security_invariants,
    validate_contract,
)


def test_security_invariants():
    state = security_invariants()

    assert state["READ_ONLY"] is True
    assert state["DRY_RUN"] is True
    assert state["REAL_EXECUTION_BLOCKED"] is True
    assert state["HUMAN_REVIEW_REQUIRED"] is True
    assert state["RESPONSE_LOCKED"] is True

    assert READ_ONLY is True
    assert DRY_RUN is True
    assert REAL_EXECUTION_BLOCKED is True
    assert HUMAN_REVIEW_REQUIRED is True
    assert RESPONSE_LOCKED is True


def test_gateway_contract():
    contract = security_contract()

    assert contract.input_validation is True
    assert contract.output_validation is True
    assert contract.prompt_injection_detection is True
    assert contract.secret_redaction is True
    assert contract.rate_limiting is True
    assert contract.authentication_required is True
    assert contract.audit_logging is True
    assert contract.fail_closed is True
    assert contract.real_execution_blocked is True


def test_contract_validation():
    assert validate_contract(security_contract()) is True
