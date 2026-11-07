import requests
import json
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("AirGappedAI")

class AirGappedThreatAnalyzer:
    def __init__(self, ollama_url: str = "http://127.0.0.1:11434"):
        self.endpoint = f"{ollama_url}/api/generate"
        self.model = "llama3:3b-instruct-q4_K_M"

    def analyze_event(self, pid: int, comm: str, filename: str) -> dict:
        prompt = f"""
[SISTEMA DE SEGURIDAD CRÍTICO GUARDIAN HUNTER]
Analiza este evento interceptado a nivel de Kernel (eBPF):
- PID: {pid}
- Proceso: {comm}
- Ruta Ejecutable: {filename}

Proporciona un reporte conciso:
1. Nivel de Riesgo (BAJO, MEDIO, ALTO, CRÍTICO)
2. Recomendación técnica (Ej: Aislar proceso, Bloquear Red)
"""
        logger.info(f"[*] Enviando evento PID {pid} al LLM Local (Air-Gapped Q4)...")
        try:
            response = requests.post(
                self.endpoint,
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=5
            )
            if response.status_code == 200:
                result = response.json().get("response", "")
                return {"status": "SUCCESS", "analysis": result}
        except Exception as e:
            logger.warning(f"[!] Ollama offline. Usando motor analítico estático de respaldo. Error: {e}")
        
        return {
            "status": "FALLBACK",
            "analysis": f"ALERTA PREVENTIVA: Ejecución sospechosa en {filename} por {comm} (PID: {pid}). Requiere revisión."
        }

if __name__ == "__main__":
    analyzer = AirGappedThreatAnalyzer()
    report = analyzer.analyze_event(pid=4092, comm="nc", filename="/usr/bin/nc")
    print("\n--- REPORTE SOBERANO DE IA ---")
    print(report["analysis"])
