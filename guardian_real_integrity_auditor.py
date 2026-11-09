import os
import sys
import ast
import py_compile

def classify_evidence(state_code: int) -> str:
    states = {
        1: "PROVEN_EVIDENCE (Prueba ejecutada y evidencia comprobada)",
        2: "INCORRECT_RESULT (Prueba ejecutada y resultado incorrecto)",
        3: "INCOMPLETE_OR_SIMULATED (Prueba incompleta o simulada - RECHAZADA)",
        4: "NOT_EXECUTED (Prueba no ejecutada)"
    }
    return states.get(state_code, "UNKNOWN")

def audit_real_integrity():
    print("=== INICIANDO AUDITORÍA DE INTEGRIDAD REAL OPTIMIZADA ===")
    
    py_files = [f for f in os.listdir('.') if f.endswith('.py') and f != __file__]
    print(f"[*] Total de módulos detectados en el inventario local: {len(py_files)}")
    
    syntax_errors = 0
    defined_modules = set(f[:-3] for f in py_files)
    imported_relations = set()
    broken_imports = set()

    # 1. Compilación sintáctica y extracción de importaciones reales via AST
    for filepath in py_files:
        mod_name = filepath[:-3]
        try:
            py_compile.compile(filepath, doraise=True)
        except Exception as e:
            print(f"[!] Error de compilación en {filepath}: {e}")
            syntax_errors += 1

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=filepath)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imported_name = alias.name.split('.')[0]
                        imported_relations.add(imported_name)
                        if imported_name.startswith("guardian_") and imported_name not in defined_modules:
                            broken_imports.add((mod_name, imported_name))
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imported_name = node.module.split('.')[0]
                        imported_relations.add(imported_name)
                        if imported_name.startswith("guardian_") and imported_name not in defined_modules:
                            broken_imports.add((mod_name, imported_name))
        except Exception as e:
            print(f"[!] Error analizando AST en {filepath}: {e}")

    print(f"[-] Errores de compilación sintáctica: {syntax_errors}")
    print(f"[-] Importaciones locales rotas: {len(broken_imports)}")
    if broken_imports:
        for src, target in broken_imports:
            print(f"    * {src}.py importa '{target}' pero el archivo no existe.")

    if syntax_errors == 0 and len(broken_imports) == 0:
        print("[OK] Integridad Real del Código Superada: Sintaxis y dependencias validadas con éxito.")
        evidence_status = 1  # 1: PROVEN_EVIDENCE
    else:
        evidence_status = 2  # 2: INCORRECT_RESULT

    print(f"[ESTADO DE EVIDENCIA] {classify_evidence(evidence_status)}")
    return evidence_status == 1

if __name__ == "__main__":
    success = audit_real_integrity()
    sys.exit(0 if success else 1)
