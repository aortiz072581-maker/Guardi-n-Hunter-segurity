import sys
import os
import subprocess
import importlib.metadata

print("=== DIAGNÓSTICO SEGURO DEL ENTORNO GUARDIAN HUNTER ===")
print(f"Versión de Python: {sys.version.split()[0]}")
print(f"Directorio de trabajo: {os.getcwd()}")

print("\n--- Verificando paquetes instalados (vía metadatos) ---")
packages = ["fastapi", "pydantic", "uvicorn", "cryptography"]
for pkg in packages:
    try:
        ver = importlib.metadata.version(pkg)
        print(f"[✔] {pkg} instalado (versión {ver})")
    except importlib.metadata.PackageNotFoundError:
        print(f"[ ] {pkg} no encontrado")

print("\n--- Verificando herramientas del sistema ---")
for tool in ["clang", "python3", "git", "pkg"]:
    res = subprocess.run(f"which {tool}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode == 0:
        print(f"[✔] Herramienta del sistema disponible: {tool}")
    else:
        print(f"[ ] No encontrada: {tool}")

print("\n--- Archivos principales del proyecto ---")
print(os.listdir("."))
