import os
import ast
import json
import sys
import time

print("========================================================================")
print("   [GUARDIAN HUNTER] AUDITOR AVANZADO DE CÓDIGO FUENTE (AST & LINT)")
print("========================================================================")

class AdvancedCodeAuditor(ast.NodeVisitor):
    def __init__(self, filename):
        self.filename = filename
        self.functions = []
        self.has_raw_assert = False

    def visit_FunctionDef(self, node):
        # Cálculo estricto de complejidad ciclomática
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler, ast.With, ast.BoolOp)):
                complexity += 1
        self.functions.append({
            "name": node.name,
            "lineno": node.lineno,
            "complexity": complexity
        })
        self.generic_visit(node)

    def visit_Assert(self, node):
        self.has_raw_assert = True
        self.generic_visit(node)

def audit_repository():
    python_files = [f for f in os.listdir('.') if f.endswith('.py') and f != 'guardian_advanced_code_auditor.py']
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "status": "INTEGRITY_OK",
        "files_analyzed": []
    }
    
    failed = False
    for file_path in python_files:
        print(f"\n[*] Analizando archivo: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        try:
            tree = ast.parse(content)
            auditor = AdvancedCodeAuditor(file_path)
            auditor.visit(tree)
            
            file_data = {
                "file": file_path,
                "functions": auditor.functions,
                "raw_assert_detected": auditor.has_raw_assert,
                "status": "OK"
            }
            report["files_analyzed"].append(file_data)
            
            for func in auditor.functions:
                print(f"  - Función '{func['name']}' (Línea {func['lineno']}): Complejidad = {func['complexity']}")
                if func['complexity'] > 20:
                    print(f"    [!] ADVERTENCIA: Alta complejidad en '{func['name']}'.")
            
            if auditor.has_raw_assert:
                print(f"    [!] ALERTA: Se detectó el uso de 'assert' en {file_path}.")
        except Exception as e:
            print(f"  [X] Error crítico analizando {file_path}: {e}")
            failed = True

    with open("GUARDIAN_ADVANCED_AUDIT_REPORT.json", "w") as f:
        json.dump(report, f, indent=4)
    
    if failed:
        print("\n[X] Estado: FAILED - Se encontraron errores de sintaxis.")
        sys.exit(1)
    else:
        print("\n[✔] Estado: INTEGRITY_OK - Auditoría completada con éxito absoluto.")
        print("[✔] Reporte exportado: GUARDIAN_ADVANCED_AUDIT_REPORT.json")

if __name__ == "__main__":
    audit_repository()
    print("========================================================================")
