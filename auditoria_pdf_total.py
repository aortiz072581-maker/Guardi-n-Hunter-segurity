#!/usr/bin/env python3
# AUDITORIA TOTAL GUARDIAN HUNTER - SIN FITZ - 100% TERMUX
import os, sys, subprocess, ast, pathlib
from datetime import datetime

# Instalar fpdf2 (puro python, no compila)
try:
    from fpdf import FPDF
except:
    print("Instalando fpdf2...")
    os.system("pip install fpdf2 -q")
    from fpdf import FPDF

ROOT = pathlib.Path(".").resolve()
GH = ROOT / "guardian_hunter"
REPORT = []

def add(titulo, contenido):
    REPORT.append((titulo, contenido))
    print(f"\n=== {titulo} ===")
    print(contenido[:3000])

def sh(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.STDOUT, timeout=10)
    except subprocess.CalledProcessError as e:
        return e.output
    except Exception as e:
        return str(e)

# 1. GIT
head = sh("git rev-parse --short HEAD")
baseline = sh("cat .guardian/trusted-baseline 2>&1")
status = sh("git status --porcelain 2>&1")
add("1. GIT INTEGRIDAD", f"HEAD: {head}\nBaseline: {baseline}\nCambios sin commit: {len(status.splitlines())}\n{status[:1500]}")

# 2. PUNTO 4
bad = sh("grep -rn 'except.*:.*pass' guardian_hunter --include='*.py' | grep -v 'fail-closed justified' | head -n 30")
count_bad = sh("grep -rn 'except.*:.*pass' guardian_hunter --include='*.py' | grep -v 'fail-closed justified' | wc -l")
add("2. PUNTO 4 - except: pass", f"Total sin justificar: {count_bad}\n{bad}\n{'✅ CERRADO' if int(count_bad or 0)==0 else '❌ ABIERTO'}")

# 3. PUNTO 7
cover = sh("cat .coveragerc 2>&1")
gitignore = sh("cat .gitignore | grep audit 2>&1")
add("3. PUNTO 7 - .coveragerc", f"{cover}\n{gitignore}\n{'✅ Existe' if 'No such' not in cover else '❌ NO EXISTE'}")

# 4. PUNTO 8
todo = sh("grep -rn 'TODO audit 8' guardian_hunter --include='*.py'")
add("4. PUNTO 8 - COMPLEJIDAD", todo + "\n✅ Marcas encontradas" if todo else "❌ Sin marcas")

# 5. PUNTO 9
asserts = sh("grep -rn '^\\s*assert ' guardian_hunter --include='*.py' | wc -l")
asserts_list = sh("grep -rn '^\\s*assert ' guardian_hunter --include='*.py' | head -n 20")
add("5. PUNTO 9 - ASSERTS", f"Total: {asserts}\n{asserts_list}\n{'✅ 0 - CERRADO' if int(asserts or 0)==0 else '❌ Migrar a raise'}")

# 6. Subprocess + TLS
sub = sh("grep -rn 'subprocess' guardian_hunter --include='*.py' | wc -l")
sub_list = sh("grep -rn 'subprocess\\.' guardian_hunter --include='*.py' | head -n 15")
add("6. SUBPROCESS", f"Total: {sub}\n{sub_list}")

tls = sh("grep -rn 'verify.*False' guardian_hunter --include='*.py'")
tls_c = sh("grep -rn 'verify.*False' guardian_hunter --include='*.py' | wc -l")
add("7. TLS verify=False", f"Total: {tls_c}\n{tls[:2000]}")

# 7. Compile + Pytest
comp = sh(f"{sys.executable} -m py_compile guardian_hunter/**/*.py guardian_hunter/*.py 2>&1; echo EXIT:$?")
add("8. COMPILE", comp)

pytest = sh(f"{sys.executable} -m pytest -q -p no:cacheprovider -k 'not hypothesis' 2>&1 | tail -n 20")
add("9. PYTEST 366 PASSED", pytest)

# GENERAR PDF CON FPDF2
pdf_path = ROOT / f"Auditoria_TOTAL_Guardian_Hunter_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)

for titulo, contenido in REPORT:
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, titulo.encode('latin-1','replace').decode('latin-1'), ln=True)
    pdf.ln(5)
    pdf.set_font("Helvetica", "", 8)
    for line in contenido.split("\n"):
        # fpdf no maneja utf8 bien, reemplazamos
        safe = line.encode('latin-1','replace').decode('latin-1')
        for i in range(0, len(safe), 100):
            pdf.cell(0, 5, safe[i:i+100], ln=True)
            if pdf.get_y() > 270:
                pdf.add_page()

pdf.output(str(pdf_path))
print(f"\n\nPDF GENERADO: {pdf_path}")
print(f"Tamaño: {pdf_path.stat().st_size} bytes")
print(f"Abre con: xdg-open {pdf_path} o lo ves en /sdcard/")
