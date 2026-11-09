import json
import time

class HumanApprovalRequiredError(Exception):
    """Excepción lanzada cuando una acción crítica requiere aprobación humana obligatoria."""
    pass

class GuardianEnterpriseCore:
    """Núcleo empresarial de Guardian Hunter con control de gobierno estricto."""
    def __init__(self, enterprise_name: str):
        self.enterprise_name = enterprise_name
        self.timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())

    def execute_critical_action(self, action: str, approved: bool = False):
        if not approved:
            raise HumanApprovalRequiredError(f"BLOQUEO DE GOBIERNO: La accion critica '{action}' requiere aprobacion humana expresa.")
        return f"Accion '{action}' ejecutada con exito."

if __name__ == "__main__":
    core = GuardianEnterpriseCore("SovereignCorp Global")
    try:
        core.execute_critical_action("REVOKE_DB_ACCESS", approved=False)
    except HumanApprovalRequiredError as e:
        print(f"[✔] Excepción capturada correctamente: {e}")
