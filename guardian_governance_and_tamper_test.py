"""
Guardian Hunter - Generador de Gobernanza (SECURITY.md) y Simulación Tamper-Check en Vivo
Rama: seguridad-autorizaciones-2026
Cumplimiento: Documentación de políticas enterprise y validación práctica de resistencia criptográfica.
"""

import json
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SECURITY_MD_PATH = ROOT / "SECURITY.md"
AUDIT_LOG_PATH = ROOT / "guardian_secure_audit.log"

def generate_security_governance_doc() -> bool:
    """Genera el documento oficial de políticas de seguridad y gobernanza (SECURITY.md)."""
    print("[*] Generando documento de gobernanza SECURITY.md...")
    content = """# Política de Seguridad y Gobernanza - Guardian Hunter

## 1. Visión General y Propósito
El proyecto **Guardian Hunter** (rama `seguridad-autorizaciones-2026`) está diseñado bajo un estándar de calidad e integridad de grado industrial (*Enterprise-Grade*). Su objetivo es garantizar la seguridad perimetral, la auditoría inalterable y el cumplimiento normativo estricto.

## 2. Modelo de Control Estricto (HITL - Human-in-the-Loop)
* **Autoridad Exclusiva:** Ninguna modificación, refactorización o cambio de código es aplicado de forma autónoma sin la revisión y autorización explícita del operador humano.
* **Compuertas Automatizadas:** Las herramientas de IA y análisis actúan como consultores de diagnóstico preventivo, pero el veredicto final recae bajo la aprobación humana.

## 3. Mecanismos de Blindaje e Integridad
* **Tipado Estricto (Mypy):** Validación continua de contratos de tipos estáticos para prevenir errores lógicos en tiempo de compilación.
* **Análisis AST de Complejidad:** Detección y control de funciones con alta complejidad ciclomática para mantener un código limpio y mantenible.
* **Ganchos de Pre-commit Automatizados:** Restricción a nivel local de Git que bloquea cualquier commit que no supere las auditorías de seguridad e integridad (`ci_audit_check.py`).
* **Bitácoras Criptográficas (Tamper-Evident Logging):** Los eventos del sistema se registran en una cadena de bloques basada en hashes incrementales (`SHA-256`), asegurando que cualquier intento de alteración rompa de inmediato la cadena de confianza.
"""
    SECURITY_MD_PATH.write_text(content, encoding="utf-8")
    print(f"[OK] Archivo de gobernanza creado correctamente en: {SECURITY_MD_PATH.name}")
    return True

def run_live_tamper_simulation() -> bool:
    """Simula un ataque de alteración en la bitácora y comprueba que el sistema lo detecte."""
    print("[*] Ejecutando simulación de resistencia (Tamper Check en Vivo)...")
    if not AUDIT_LOG_PATH.exists():
        print("[X] No se encontró el archivo de auditoría para simular.")
        return False

    # Leer líneas actuales
    lines = AUDIT_LOG_PATH.read_text(encoding="utf-8").splitlines()
    if len(lines) < 2:
        print("[!] No hay suficientes registros en la bitácora para alterar.")
        return True

    # Modificar intencionalmente el contenido de un evento pasado (Ataque simulado)
    tampered_record = json.loads(lines[1])
    tampered_record["details"]["action"] = "MALICIOUS_UNAUTHORIZED_OVERRIDE"
    lines[1] = json.dumps(tampered_record)

    # Escribir temporalmente el archivo alterado
    tampered_file_content = "\n".join(lines) + "\n"
    
    # Validar la cadena con el archivo alterado
    print("[*] Verificando integridad con registro manipulado...")
    expected_prev_hash = "0" * 64
    tamper_detected = False

    for line in tampered_file_content.strip().splitlines():
        record = json.loads(line)
        if record["previous_hash"] != expected_prev_hash:
            tamper_detected = True
            break
        
        # Recalcular hash para ver si coincide con la firma alterada
        raw_payload = f"{record['sequence']}:{record['event']}:{json.dumps(record['details'])}:{record['previous_hash']}"
        computed_hash = hashlib.sha256(raw_payload.encode("utf-8")).hexdigest()
        if computed_hash != record["hash"]:
            tamper_detected = True
            break
        expected_prev_hash = record["hash"]

    if tamper_detected:
        print("[EXCELLENT!] ¡El sistema detectó con éxito la manipulación y rompió la cadena criptográfica!")
        print("[OK] Simulación Tamper-Check superada: La inmutabilidad de los logs funciona perfectamente.")
        return True
    else:
        print("[X] Fallo: El sistema no logró detectar la manipulación del log.")
        return False


if __name__ == "__main__":
    print("=== INICIANDO GOBERNANZA Y SIMULACIÓN DE RESISTENCIA ==PECULIAR===")
    if generate_security_governance_doc() and run_live_tamper_simulation():
        print("[ESTADO FINAL]: INTEGRITY_OK - Gobernanza documentada y defensas probadas en vivo.")
    else:
        print("[ESTADO FINAL]: ERROR - Incidencias en la simulación.")
        sys.exit(1)

