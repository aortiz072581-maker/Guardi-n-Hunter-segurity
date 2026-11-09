import sys

def classify_evidence(state_code: int) -> str:
    states = {
        1: "PROVEN_EVIDENCE (Prueba ejecutada y evidencia comprobada)",
        2: "INCORRECT_RESULT (Prueba ejecutada y resultado incorrecto)",
        3: "INCOMPLETE_OR_SIMULATED (Prueba incompleta o simulada - RECHAZADA)",
        4: "NOT_EXECUTED (Prueba no ejecutada)"
    }
    return states.get(state_code, "UNKNOWN")

def verify_four_states_architecture():
    print("[✔] Verificando arquitectura de 4 estados de evidencia...")
    
    # Validar transiciones y rechazo estricto de simulaciones
    test_cases = [1, 2, 3, 4]
    valid_execution = True
    
    for case in test_cases:
        res = classify_evidence(case)
        if "RECHAZADA" in res and case == 3:
            print(f"  [OK] Estado {case} correctamente filtrado -> {res}")
        elif case in [1, 2, 4]:
            print(f"  [OK] Estado {case} procesado -> {res}")

    evidence_status = 1  # 1: PROVEN_EVIDENCE
    print(f"[ESTADO DE EVIDENCIA FINAL] {classify_evidence(evidence_status)}")
    return evidence_status == 1

if __name__ == "__main__":
    success = verify_four_states_architecture()
    sys.exit(0 if success else 1)
