
"""Fail-closed read-only adapter for Guardian Hunter. Never calls a tool."""
from .core import decide, sha
from .evidence import verify

def assess_tool_request(request, policy, *, trusted_policy_hash, evidence=None, trusted_keys=None):
    if not isinstance(trusted_policy_hash,str) or sha(policy)!=trusted_policy_hash:
        return {"decision":"DENY","reason":"TRUSTED_POLICY_MISMATCH","execution_allowed":False}
    try:
        decision, reason=decide(request,policy)
    except (TypeError,ValueError,KeyError):
        return {"decision":"DENY","reason":"INVALID_INPUT","execution_allowed":False}
    if evidence is not None:
        if not trusted_keys or not verify(evidence,trusted_keys):
            return {"decision":"DENY","reason":"EVIDENCE_UNTRUSTED","execution_allowed":False}
        if evidence['proposal_hash']!=request.get('proposal_hash') or evidence['policy_hash']!=trusted_policy_hash or evidence['authorization_id']!=request.get('authorization_id'):
            return {"decision":"DENY","reason":"EVIDENCE_CONTEXT_MISMATCH","execution_allowed":False}
    if decision=='ALLOW':
        return {"decision":"REQUIRE_APPROVAL","reason":"BROKER_AND_HUMAN_APPROVAL_NOT_CONFIGURED","execution_allowed":False}
    return {"decision":decision,"reason":reason,"execution_allowed":False}

def execute(*args,**kwargs):
    raise PermissionError('TRUSTED_EXECUTION_BROKER_NOT_CONFIGURED')
