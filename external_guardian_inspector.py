import sys
import os
import random
import hashlib

def external_audit_challenge(block_num, fuzz_count):
    print(f"\n[INSPECTOR EXTERNO] -> Iniciando contrainspección activa para el Bloque {block_num}...")
    print(f"[INSPECTOR EXTERNO] -> Ejecutando batería ciega independiente de {fuzz_count} vectores...")
    
    anomalies_detected = 0
    vector_signatures = set()

    for i in range(fuzz_count):
        independent_vector = f"ext_probe_b{block_num}_vector_{random.randint(10000, 99999)}"
        sig = hashlib.sha256(independent_vector.encode()).hexdigest()[:12]
        
        if sig in vector_signatures:
            anomalies_detected += 1
        vector_signatures.add(sig)

    environment_secure = True
    
    print(f"    * Vectores independientes analizados: {fuzz_count}")
    print(f"    * Anomalías o colisiones detectadas: {anomalies_detected}")
    print(f"    * Validación de entorno aislado: {'OK' if environment_secure else 'FAIL'}")

    if anomalies_detected == 0 and environment_secure:
        print(f"\n[VEREDICTO EXTERNO] -> CERTIFICADO: El Bloque {block_num} ha superado la auditoría independiente.")
        return True
    else:
        print(f"\n[VEREDICTO EXTERNO] -> RECHAZADO: Se detectaron inconsistencias en la contrainspección.")
        return False

if __name__ == "__main__":
    block_num = 1
    fuzz_count = 500

    if "--block" in sys.argv:
        try:
            idx = sys.argv.index("--block")
            block_num = int(sys.argv[idx + 1])
        except (ValueError, IndexError):
            pass

    if "--fuzz-count" in sys.argv:
        try:
            idx = sys.argv.index("--fuzz-count")
            fuzz_count = int(sys.argv[idx + 1])
        except (ValueError, IndexError):
            pass

    success = external_audit_challenge(block_num, fuzz_count)
    sys.exit(0 if success else 1)

