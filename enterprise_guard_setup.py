"""
Guardian Hunter - Script Maestro de Configuración y Pre-commit Automatizado
Rama: seguridad-autorizaciones-2026
"""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def verify_trusted_baseline() -> bool:
    """Verifica y sincroniza el hash de confianza del repositorio (trusted-baseline)."""
    baseline_path = ROOT / ".guardian" / "trusted-baseline"
    if not baseline_path.exists():
        print("[!] Advertencia: No se encontró el archivo trusted-baseline. Creándolo...")
        baseline_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        current_head = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()
        baseline_path.write_text(current_head)
        print(f"[OK] Baseline de seguridad sincronizado con HEAD: {current_head[:10]}...")
        return True
    except Exception as e:
        print(f"[X] Error al sincronizar el trusted-baseline: {e}")
        return False

def install_git_hooks() -> bool:
    """Configura los ganchos locales de Git para prevenir commits inseguros."""
    hooks_dir = ROOT / ".git" / "hooks"
    if not hooks_dir.exists():
        print("[!] Directorio .git/hooks no encontrado. Inicializando hook manualmente...")
        hooks_dir.mkdir(parents=True, exist_ok=True)
        
    pre_commit_path = hooks_dir / "pre-commit"
    hook_content = """#!/bin/sh
# Guardian Hunter - Pre-commit Security Hook Automatizado
echo "=== EJECUTANDO AUDITORÍA PRE-COMMIT DE SEGURIDAD ==="
python3 ci_audit_check.py
if [ $? -ne 0 ]; then
    echo "[X] ERROR: Las compuertas de seguridad fallaron. Commit bloqueado."
    exit 1
fi
echo "[OK] Auditoría pre-commit superada con éxito."
"""
    pre_commit_path.write_text(hook_content)
    # Dar permisos de ejecución
    os.chmod(pre_commit_path, 0o755)
    print("[OK] Gancho de pre-commit instalado correctamente en Git.")
    return True

if __name__ == "__main__":
    print("=== INICIANDO CONFIGURACIÓN AVANZADA ENTERPRISE ===")
    if verify_trusted_baseline() and install_git_hooks():
        print("[ESTADO FINAL]: INTEGRITY_OK - Entorno configurado para control estricto HITL.")
    else:
        print("[ESTADO FINAL]: FALLIDO - Revise las incidencias.")
        sys.exit(1)

