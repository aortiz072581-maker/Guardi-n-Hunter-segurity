class NetworkC2Detector:
    def inspect_socket_connection(self, dest_ip: str, port: int):
        print(f"[Network eBPF] Analizando conexion saliente hacia {dest_ip}:{port}...")
        if port in [4444, 1337, 6667]:
            return {"verdict": "DROP", "reason": "SUSPICIOUS_C2_BEACON"}
        return {"verdict": "ALLOW", "reason": "AUTHORIZED_TRAFFIC"}
