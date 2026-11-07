import base64
from cryptography.hazmat.primitives.asymmetric import ed25519
from guardian_hunter.ai.airgapped_llm import AirGappedThreatAnalyzer

def run_live_simulation():
    print("==========================================================")
    print("  SIMULACIÓN EN VIVO: GUARDIAN HUNTER (eBPF -> AI -> ED25519)")
    print("==========================================================")

    simulated_pid = 9912
    simulated_comm = "nc"
    simulated_filename = "/bin/nc"
    anomaly_id = "ANOMALY_EXEC_9912_NETCAT"
    action_to_execute = f"KILL_PID_{simulated_pid}_AND_ISOLATE_INTERFACE"

    print(f"[1] Evento detectado por eBPF: Proceso '{simulated_comm}' (PID: {simulated_pid}) ejecutando '{simulated_filename}'")

    analyzer = AirGappedThreatAnalyzer()
    ai_report = analyzer.analyze_event(pid=simulated_pid, comm=simulated_comm, filename=simulated_filename)
    
    print("\n[2] Informe generado por el LLM Local (Air-Gapped):")
    print(ai_report["analysis"])

    print("\n[3] Generando firma criptográfica Ed25519 del Administrador Soberano...")
    admin_private_key = ed25519.Ed25519PrivateKey.generate()
    admin_public_key = admin_private_key.public_key()
    
    message = f"{anomaly_id}:{action_to_execute}".encode('utf-8')
    signature = admin_private_key.sign(message)
    signature_b64 = base64.b64encode(signature).decode('utf-8')
    
    public_hex = admin_public_key.public_bytes_raw().hex()
    print(f"[✔] Llave Pública del Admin registrada: {public_hex[:32]}...")
    print(f"[✔] Firma Ed25519 generada con éxito.")

    print("\n[4] Enviando comando firmado a la API de Kernel (FastAPI)...")
    payload = {
        "anomaly_id": anomaly_id,
        "action": action_to_execute,
        "signature_b64": signature_b64
    }
    
    print(f"-> Payload preparado con éxito para POST /api/v1/mitigate")
    print(f"-> Acción '{action_to_execute}' AUTORIZADA criptográficamente y lista para aplicarse en el Kernel.")
    print("==========================================================")

if __name__ == "__main__":
    run_live_simulation()
