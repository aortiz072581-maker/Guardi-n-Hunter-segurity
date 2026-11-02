"""Fail-closed, read-only security decision adapter. No execution privileges."""
import hashlib, json, re
from pathlib import Path

def canonical(obj):
    def valid(x):
        if x is None or type(x) in (bool,int,str): return x
        if type(x) is list: return [valid(y) for y in x]
        if type(x) is dict and all(type(k) is str for k in x): return {k:valid(v) for k,v in x.items()}
        raise ValueError('NON_CANONICAL_VALUE')
    return json.dumps(valid(obj),sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def digest(obj):return hashlib.sha256(canonical(obj)).hexdigest()
def decide(request, policy, verified_identity=None, approval=None):
    """Only cryptographically verified identities/approvals passed by trusted caller count."""
    try:
        if not isinstance(request,dict) or not isinstance(policy,dict):return 'DENY'
        if policy.get('mode')!='ENFORCE' or policy.get('deployment')!='DENY':return 'DENY'
        if not isinstance(verified_identity,dict) or verified_identity.get('verified') is not True:return 'DENY'
        if verified_identity.get('subject')!=request.get('agent_identity'):return 'DENY'
        if not isinstance(request.get('tool'),str) or request['tool'] not in policy.get('tools',[]):return 'DENY'
        if request.get('resource') not in policy.get('resources',[]):return 'DENY'
        if request.get('risk') not in ('LOW','MEDIUM','HIGH'):return 'DENY'
        if type(request.get('parameters')) is not dict:return 'DENY'
        allowed=policy.get('parameters',{}).get(request['tool'],{})
        if any(k not in allowed or v not in allowed[k] for k,v in request['parameters'].items()):return 'DENY'
        if any(k not in request for k in ('proposal_hash','candidate_hash','baseline_hash')):return 'DENY'
        if any(not isinstance(request[k],str) or not re.fullmatch('[a-f0-9]{64}',request[k]) for k in ('proposal_hash','candidate_hash','baseline_hash')):return 'DENY'
        if request['risk']!='LOW':
            if not isinstance(approval,dict) or approval.get('independently_verified') is not True:return 'REQUIRE_APPROVAL'
            if approval.get('binding_hash')!=digest({'request':request,'policy':policy,'subject':verified_identity['subject']}):return 'DENY'
        return 'ALLOW_READ_ONLY' if request['tool'] in policy.get('read_only_tools',[]) else 'DENY'
    except (ValueError,TypeError,KeyError):return 'DENY'

def validate_target(root, relative):
    """Deny absolute paths, symlinks, traversal and missing targets."""
    root=Path(root).resolve(strict=True)
    p=Path(relative)
    if p.is_absolute() or not p.parts or any(x in ('.','..') for x in p.parts):raise PermissionError('INVALID_PATH')
    current=root
    for part in p.parts:
        current=current/part
        if current.is_symlink():raise PermissionError('SYMLINK_DENIED')
    resolved=current.resolve(strict=True)
    if not resolved.is_relative_to(root) or not resolved.is_file():raise PermissionError('RESOURCE_DENIED')
    return resolved
