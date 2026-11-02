"""Fail-closed, non-executing policy assessment for tool calls."""
import hashlib,json,re

def canonical(obj):
    def validate(x):
        if x is None or type(x) in (bool,int,str): return
        if isinstance(x,list):
            for v in x:validate(v)
            return
        if isinstance(x,dict) and all(isinstance(k,str) for k in x):
            for v in x.values():validate(v)
            return
        raise ValueError('Noncanonical type')
    validate(obj)
    return json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def sha(obj):return hashlib.sha256(canonical(obj)).hexdigest()
def decide(request,policy):
    required={'identity','tool','parameters','resource','proposal_hash','policy_hash','baseline_hash','authorization_id'}
    if not isinstance(request,dict) or not required.issubset(request):return 'DENY','MISSING_FIELDS'
    if not isinstance(policy,dict) or request['policy_hash']!=sha(policy):return 'DENY','POLICY_MISMATCH'
    if not policy.get('authenticated_identity_verified_externally'):return 'DENY','IDENTITY_UNVERIFIED'
    if not isinstance(request['identity'],str) or request['identity'] not in policy.get('allowed_identities',[]):return 'DENY','IDENTITY_DENIED'
    if request['tool'] not in policy.get('allowed_tools',[]):return 'DENY','TOOL_DENIED'
    if request['resource'] not in policy.get('allowed_resources',[]):return 'DENY','RESOURCE_DENIED'
    if not isinstance(request['parameters'],dict):return 'DENY','PARAMETERS_INVALID'
    if set(request['parameters'])-set(policy.get('allowed_parameters',{}).get(request['tool'],[])):return 'DENY','PARAMETERS_DENIED'
    if not all(isinstance(request[k],str) and re.fullmatch('[0-9a-f]{64}',request[k]) for k in ('proposal_hash','baseline_hash')):return 'DENY','HASH_INVALID'
    if not isinstance(request['authorization_id'],str) or not request['authorization_id']:return 'DENY','AUTH_ID_INVALID'
    return 'REQUIRE_APPROVAL','INDEPENDENT_APPROVAL_AND_BROKER_REQUIRED'
def execute(*args,**kwargs):raise PermissionError('TRUSTED_BROKER_NOT_CONFIGURED')
