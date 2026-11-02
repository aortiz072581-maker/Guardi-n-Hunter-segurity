"""Strict evidence schema and external-key Ed25519 verification; no key provisioning."""
import base64,datetime
from .core import sha,canonical
FIELDS={'record_id','schema_version','asset_id','agent_identity','assessment_type','proposal_hash','candidate_hash','policy_hash','baseline_hash','evidence_hash','authorization_id','target','decision','execution_result','timestamp','signing_key_id','signature'}
def validate(record):
    if not isinstance(record,dict) or set(record)!=FIELDS:raise ValueError('Invalid schema')
    if record['schema_version']!='1.0':raise ValueError('Unsupported schema')
    for k in FIELDS-{'signature'}:
        if not isinstance(record[k],str) or not record[k]:raise ValueError('Invalid '+k)
    for k in ('proposal_hash','candidate_hash','policy_hash','baseline_hash','evidence_hash'):
        if len(record[k])!=64 or any(c not in '0123456789abcdef' for c in record[k]):raise ValueError('Invalid hash '+k)
    if record['assessment_type'] not in ('DECISION','EXECUTION','RESULT'):raise ValueError('Invalid evidence type')
    if record['decision'] not in ('ALLOW','DENY','REQUIRE_APPROVAL'):raise ValueError('Invalid decision')
    datetime.datetime.fromisoformat(record['timestamp'].replace('Z','+00:00'))
    return True
def verify(record,trusted_public_keys):
    validate(record)
    if record['signing_key_id'] not in trusted_public_keys:return False
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        public=Ed25519PublicKey.from_public_bytes(trusted_public_keys[record['signing_key_id']])
        public.verify(base64.b64decode(record['signature'],validate=True),canonical({k:v for k,v in record.items() if k!='signature'}))
        return True
    except (ImportError,ValueError,TypeError,Exception):return False
