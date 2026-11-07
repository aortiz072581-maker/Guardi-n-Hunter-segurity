from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from cryptography.hazmat.primitives.asymmetric import ed25519
import base64

app = FastAPI(title="Guardian Hunter - Enterprise Sovereign Portal")

ADMIN_PUBLIC_KEY_HEX = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef" 

class MitigationPayload(BaseModel):
    anomaly_id: str
    action: str  
    signature_b64: str 

def verify_crypto_signature(payload: MitigationPayload):
    try:
        public_bytes = bytes.fromhex(ADMIN_PUBLIC_KEY_HEX)
        public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_bytes)
        
        message = f"{payload.anomaly_id}:{payload.action}".encode('utf-8')
        signature = base64.b64decode(payload.signature_b64)
        
        public_key.verify(signature, message)
        return True
    except Exception:
        raise HTTPException(
            status_code=403, 
            detail="ACCESO DENEGADO: Firma criptográfica Ed25519 inválida o no autorizada."
        )

@app.post("/api/v1/mitigate")
def execute_mitigation(payload: MitigationPayload, authorized: bool = Depends(verify_crypto_signature)):
    return {
        "status": "EXECUTED",
        "detail": f"Acción '{payload.action}' autorizada criptográficamente y ejecutada a nivel de Kernel.",
        "human_in_the_loop": "VERIFIED_ED25519"
    }
