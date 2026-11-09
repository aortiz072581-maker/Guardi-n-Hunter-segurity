import sys

print("========================================================================")
print("   [GUARDIAN HUNTER] CLASIFICADOR ESTRICTO DE EVIDENCIA Y PRUEBAS")
print("========================================================================")

class EvidenceEvaluationError(Exception):
    """Excepción lanzada cuando una prueba no cumple con los criterios de evidencia real."""
    pass

def classify_and_validate_test(status_code: int, has_real_evidence: bool, executed: bool) -> str:
    """
    Clasifica y valida el estado de una prueba según los 4 criterios soberanos:
    1. 1 = Prueba ejecutada y evidencia comprobada.
    2. 2 = Prueba ejecutada y resultado incorrecto.
    3. 3 = Prueba incompleta, simulada o sin evidencia suficiente.
    4. 4 = Prueba no ejecutada.
    """
    if not executed:
        raise EvidenceEvaluationError("[ESTADO 4] BLOQUEO: Prueba no ejecutada. No se puede certificar.")
    
    if simulated_or_incomplete(has_real_evidence, status_code):
        raise EvidenceEvaluationError("[ESTADO 3] BLOQUEO: Prueba incompleta, simulada o sin evidencia suficiente.")
        
    if status_code != 200:
        print("[ESTADO 2] ADVERTENCIA: Prueba ejecutada y resultado incorrecto (Fallo detectado).")
        return "TEST_FAILED_INCORRECT_RESULT"
        
    print("[ESTADO 1] EXITO: Prueba ejecutada y evidencia comprobada satisfactoriamente.")
    return "TEST_SUCCESS_VERIFIED"

def simulated_or_incomplete(evidence: bool, code: int) -> bool:
    # Retorna True si carece de evidencia real o el código de estado denota simulación/incompletitud
    return not evidence or code not in [200, 403, 500]

if __name__ == "__main__":
    try:
        # Prueba de ejemplo con estado 1 (Ejecutada y evidencia comprobada)
        result = classify_and_validate_test(status_code=200, has_real_evidence=True, executed=True)
        print(f"Resultado clasificado: {result}")
    except EvidenceEvaluationError as e:
        print(f"[X] {e}")
        sys.exit(1)
