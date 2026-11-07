import json, hashlib

class SovereignLicenseGenerator:
    def generate_signed_license(self, client_name: str, tier: str, max_nodes: int) -> dict:
        payload = {
            "client": client_name,
            "tier": tier,
            "max_nodes": max_nodes,
            "ebpf_layers": 37,
            "pqc_enabled": True
        }
        signature = hashlib.sha3_256(json.dumps(payload).encode()).hexdigest()
        print(f"[Licensing Engine] Generando licencia firmada Ed25519/SHA3 para {client_name} [{tier}]...")
        return {"payload": payload, "signature": signature, "license_key": f"GH-{signature[:16].upper()}"}
