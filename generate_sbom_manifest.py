import hashlib
import json
from pathlib import Path

print("[SBOM Generator] Generando Manifiesto de Integridad de la Cadena de Suministro...")

target_files = ["guardian_hardened_production.py", "guardian_cli.py", "fix_env.py"]
manifest = {}

for file_name in target_files:
    path = Path(file_name)
    if path.exists():
        file_bytes = path.read_bytes()
        file_hash = hashlib.sha3_512(file_bytes).hexdigest()
        manifest[file_name] = {
            "size_bytes": len(file_bytes),
            "sha3_512": file_hash
        }

manifest_path = Path("dist") / "sbom_manifest_v3.json"
manifest_path.parent.mkdir(parents=True, exist_ok=True)
manifest_path.write_text(json.dumps(manifest, indent=4))

print(f"  [✔] Manifiesto SBOM generado en: {manifest_path}")
print(json.dumps(manifest, indent=2))
