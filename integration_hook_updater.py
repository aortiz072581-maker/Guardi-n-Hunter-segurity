"""
Guardian Hunter - Actualizador de Gancho Pre-Commit con Suite Avanzada de IA
Rama: seguridad-autorizaciones-2026
"""

from pathlib import Path
import os

ROOT = Path(__file__).resolve().parent

def update_git_pre_commit_hook() -> bool:
    hooks_dir = ROOT / ".git" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    pre_commit_path = hooks_dir / "pre-commit"
    
    hook_content = """#!/bin/sh
# Guardian Hunter - Pre-commit Avanzado con Suite de IA y Auditoría
echo "=== EJECUTANDO AUDITORÍA AVANZADA PRE-COMMIT (AST, DIFF & FUZZING) ==="
python3 guardian_advanced_ai_suite.py
if [ $? -ne 0 ]; then
    echo "[X] ERROR: La suite avanzada de IA detectó bloqueadores. Commit denegado."
    exit 1
fi

echo "=== EJECUTANDO AUDITORÍA CLÁSICA DE INTEGRIDAD ==="
python3 ci_audit_check.py
if [ $? -ne 0 ]; then
    echo "[X] ERROR: Las compuertas de calidad estándar fallaron. Commit bloqueado."
    exit 1
fi

echo "[OK] Todas las validaciones avanzadas superadas con éxito. Aprobado para commit."
"""
    pre_commit_path.write_text(hook_content)
    os.chmod(pre_commit_path, 0o755)
    print("[OK] Gancho de pre-commit actualizado exitosamente con la suite avanzada.")
    return True

if __name__ == "__main__":
    update_git_pre_commit_hook()

