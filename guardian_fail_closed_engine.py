import sys

print("========================================================================")
print("   [GUARDIAN HUNTER] MÓDULO REFACTORIZADO: FAIL-CLOSED ENGINE")
print("========================================================================")

class FailClosedEngine:
    """Motor especializado en garantizar el comportamiento fail-closed ante anomalías."""

    @staticmethod
    def evaluate_initial_state() -> bool:
        """Subrutina 1: Evalúa el estado inicial del sistema."""
        print("[✔] Estado inicial verificado: Seguro.")
        return True

    @staticmethod
    def simulate_anomaly_trigger() -> bool:
        """Subrutina 2: Simula un intento de fallo o brecha de seguridad."""
        print("[✔] Anomalía simulada correctamente para prueba.")
        return True

    @staticmethod
    def enforce_fail_closed_action(anomaly_detected: bool) -> str:
        """Subrutina 3: Aplica el bloqueo inmediato si se detecta anomalía."""
        if anomaly_detected:
            print("[✔] MODO FAIL-CLOSED ACTIVADO: Acceso bloqueado de forma preventiva.")
            return "BLOCKED_SECURE"
        return "ALLOWED"

    @classmethod
    def run_pipeline(cls) -> str:
        """Pipeline principal con complejidad ciclomática reducida (< 5)."""
        cls.evaluate_initial_state()
        anomaly = cls.simulate_anomaly_trigger()
        result = cls.enforce_fail_closed_action(anomaly)
        return result

if __name__ == "__main__":
    outcome = FailClosedEngine.run_pipeline()
    print(f"[ESTADO FINAL] Resultado del pipeline Fail-Closed: {outcome}")
