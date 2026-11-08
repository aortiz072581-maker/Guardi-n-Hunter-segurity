import sys
import json
from guardian_ai_hitl_engine import HumanInTheLoopGate

class TransactionalExecutor:
    """Ejecuta cambios de sistema de forma atómica y auditable."""
    def __init__(self, gate: HumanInTheLoopGate):
        self.gate = gate

    def execute(self, action_id: str, operator_id: str, justification: str, payload_fn):
        print(f"[TransactionalExecutor] Validando compuertas para: {action_id}")
        auth = self.gate.request_authorization(action_id, operator_id, justification)
        if not auth.get("authorized"):
            raise PermissionError(f"[DENY] Acción {action_id} rechazada por política.")
        
        print(f"[TransactionalExecutor] Ejecutando transacción autorizada ({auth['proof_signature'][:16]}...)")
        return payload_fn()

def require(permission_check_fn):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not permission_check_fn():
                print("[DENY] Enforcing fail-closed: Permiso denegado por require().")
                sys.exit(1)
            return func(*args, **kwargs)
        return wrapper
    return decorator

if __name__ == "__main__":
    gate = HumanInTheLoopGate()
    executor = TransactionalExecutor(gate)
    print("[✔] operate.py inicializado con enforcement estricto TransactionalExecutor & require().")
