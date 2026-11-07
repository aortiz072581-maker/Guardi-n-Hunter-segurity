import sys
import os
import subprocess

print("=== DIAGNÓSTICO DEL ENTORNO GUARDIAN HUNTER ===")
print(f"Versión de Python: {sys.version.split()[0]}")
print(f"Directorio de trabajo: {os.getcwd()}")

print("\n--- Verificando librerías Python instaladas ---")
try:
    import fastapi
    print("[✔] FastAPI instalado")
except ImportError:
    print("[ ] FastAPI no detectado")

try:
    import pydantic
    print("[✔] Pydantic instalado")
except ImportError:
    print("[ ] Pydantic no detectado")

print("\n--- Verificando herramientas del sistema ---")
for tool in ["clang", "python3", "git", "pkg"]:
    res = subprocess.run(f"which {tool}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode == 0:
        print(f"[✔] Herramienta del sistema disponible: {tool}")
    else:
        print(f"[ ] No encontrada: {tool}")

print("\n--- Archivos principales del proyecto ---")
print(os.listdir("."))
