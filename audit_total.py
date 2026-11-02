#!/usr/bin/env python3
# AUDITORIA TOTAL - Guardian Hunter - Termux
# Busca estructura, archivos, tools, skills

import os
import pathlib
import re

ROOT = pathlib.Path(".").resolve()
print(f"=== GUARDIAN HUNTER - AUDITORIA TOTAL ===")
print(f"ROOT: {ROOT}\n")

# 1. ESTRUCTURA
print("--- 1. ESTRUCTURA DE DIRECTORIOS ---")
for r, dirs, files in os.walk(ROOT):
    level = r.count(os.sep) - str(ROOT).count(os.sep)
    if level > 4: # no profundizar demasiado
        continue
    # ignorar backups muy grandes
    if ".guardian/local-backups" in r or "__pycache__" in r:
        continue
    indent = "  " * level
    print(f"{indent}{os.path.basename(r)}/ - {len(files)} archivos")

# 2. CONTEO GENERAL
print("\n--- 2. CONTEO DE ARCHIVOS ---")
all_files = list(ROOT.rglob("*"))
py_files = [f for f in all_files if f.suffix == ".py" and f.is_file()]
print(f"Total archivos: {len([f for f in all_files if f.is_file()])}")
print(f"Total .py: {len(py_files)}")
print(f"Total directorios: {len([d for d in all_files if d.is_dir()])}")

# 3. BUSCAR TOOLS / SKILLS
print("\n--- 3. TOOLS Y SKILLS DETECTADOS ---")
patterns = ["tool", "skill", "operate", "audit", "guardian"]
tools_found = []
for f in py_files:
    path_str = str(f).lower()
    if any(p in path_str for p in patterns):
        if ".guardian/local-backups" not in path_str and "__pycache__" not in path_str:
            tools_found.append(f)

for f in sorted(tools_found):
    print(f"- {f.relative_to(ROOT)}")

# 4. REVISION DE CODIGO PELIGROSO (lo del informe 18-10-2026)
print("\n--- 4. REVISION DE PATRONES CRITICOS ---")
checks = {
    "default=str": re.compile(r"default\s*=\s*str"),
    "shell=True": re.compile(r"shell\s*=\s*True"),
    "eval(": re.compile(r"\beval\s*\("),
    "exec(": re.compile(r"\bexec\s*\("),
    "canonical_hash": re.compile(r"canonical_hash"),
    "DEPLOYMENT": re.compile(r"DEPLOYMENT"),
}

report = []
for f in py_files:
    if ".guardian/local-backups" in str(f) or "__pycache__" in str(f):
        continue
    try:
        text = f.read_text(errors="ignore")
        for name, regex in checks.items():
            if regex.search(text):
                report.append(f"[{name}] -> {f.relative_to(ROOT)}")
    except:
        pass

for line in sorted(set(report)):
    print(line)

# 5. LISTADO DE ARCHIVOS CORE
print("\n--- 5. ARCHIVOS CORE PRINCIPALES ---")
core_files = [
    "guardian_hunter/operate.py",
    "guardian_hunter/audit/authorization_hardening.py",
    "guardian_hunter/audit/authorization_integration_audit.py",
    "guardian_hunter/audit/phase18_interface_audit.py",
    "guardian_hunter/evidence/incident.py",
    "guardian_hunter/hardening/phase26.py",
]
for cf in core_files:
    p = ROOT / cf
    if p.exists():
        size = p.stat().st_size
        print(f"OK {cf} - {size} bytes")
    else:
        print(f"FALTA {cf}")

print("\n=== FIN AUDITORIA - Guarda este log ===")
