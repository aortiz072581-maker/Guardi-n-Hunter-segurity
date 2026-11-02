"""Independent offline verifier; keys are never generated or trusted automatically."""
import base64, hashlib, json, re
from .security import canonical, digest
FIELDS={'record_id','schema_version','asset_id','agent_identity','assessment_type','proposal_hash','candidate_hash','policy_hash','baseline_hash','evidence_hash','authorization_id','target','decision','execution_result','timestamp','signing_key_id','signature','previous_hash','record_type'}
HEX=re.compile(r'^[0-9a-f]{64}$')
def verify_record(record, trusted_keys):
    if type(record) is not dict or set(record)!=FIELDS:return False
    if record['schema_version']!=1 or record['record_type'] not in ('DECISION','EXECUTION','RESULT'):return False
    if record['decision'] not in ('ALLOW','DENY','REQUIRE_APPROVAL'):return False
    if any(type(record[k]) is not str for k in FIELDS-{'schema_version'}):return False
    if any(not HEX.fullmatch(record[k]) for k in ('proposal_hash','candidate_hash','policy_hash','baseline_hash','evidence_hash','previous_hash')):return False
    if not all(record[k] for k in ('record_id','asset_id','agent_identity','assessment_type','target','timestamp','signing_key_id')):return False
    key=trusted_keys.get(record['signing_key_id'])
    if key is None:return False
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        public=Ed25519PublicKey.from_public_bytes(bytes.fromhex(key))
        payload={k:v for k,v in record.items() if k!='signature'}
        public.verify(base64.b64decode(record['signature'],validate=True),canonical(payload))
        return True
    except (ImportError,ValueError,TypeError,Exception):return False

def verify_export(records, trusted_keys):
    if type(records) is not list or not records:return False
    prev='0'*64
    for rec in records:
        if rec.get('previous_hash')!=prev or not verify_record(rec,trusted_keys):return False
        prev=digest(rec)
    return True
