"""Immutable Audit Ledger using Cryptographic Hash Chains (Merkle Tree style)."""

import hashlib
import json
import os
import time

class ImmutableLedger:
    def __init__(self, ledger_file=".guardian/immutable_ledger.json"):
        self.ledger_file = ledger_file
        os.makedirs(os.path.dirname(self.ledger_file), exist_ok=True)
        if not os.path.exists(self.ledger_file):
            self._create_genesis_block()

    def _create_genesis_block(self):
        genesis = {
            "index": 0,
            "timestamp": time.time(),
            "event": "GENESIS_BLOCK_INITIALIZED",
            "previous_hash": "0" * 64,
            "hash": ""
        }
        genesis["hash"] = self._compute_hash(genesis)
        with open(self.ledger_file, "w") as f:
            json.dump([genesis], f, indent=4)

    def _compute_hash(self, block: dict) -> str:
        block_string = f"{block['index']}{block['timestamp']}{block['event']}{block['previous_hash']}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    def append_event(self, event_data: str) -> str:
        with open(self.ledger_file, "r") as f:
            chain = json.load(f)
        
        last_block = chain[-1]
        new_block = {
            "index": len(chain),
            "timestamp": time.time(),
            "event": event_data,
            "previous_hash": last_block["hash"],
            "hash": ""
        }
        new_block["hash"] = self._compute_hash(new_block)
        chain.append(new_block)
        
        with open(self.ledger_file, "w") as f:
            json.dump(chain, f, indent=4)
        
        print(f"[✔] Immutable Ledger: Evento de seguridad sellado en el bloque #{new_block['index']}.")
        return new_block["hash"]

if __name__ == "__main__":
    ledger = ImmutableLedger()
    ledger.append_event("AUDIT_CHECKPOINT_PASSED")
