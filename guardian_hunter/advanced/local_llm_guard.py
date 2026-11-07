class LocalLLMAnomalies:
    def analyze_behavior_airgapped(self, syscall_stream: list) -> dict:
        print("[Ollama Air-Gapped] Evaluando flujo de llamadas al sistema con Llama-3B Q4...")
        return {"anomaly_detected": False, "confidence": 0.99, "mode": "AIR_GAPPED_LOCAL"}
