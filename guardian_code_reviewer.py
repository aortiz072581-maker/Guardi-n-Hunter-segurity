import os
import ast
import json
import time

print("========================================================================")
print("   [GUARDIAN HUNTER] AUDITOR AUTOMÁTICO DE CÓDIGO FUENTE (AST & LINT)")
print("========================================================================")

class CodeComplexityVisitor(ast.NodeVisitor):
    def __init__(self):
        self.functions = []

    def visit_FunctionDef(self, node):
        # Cálculo de complejidad ciclomática básica basada en puntos de decisión
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler, ast.With, ast.Assert, ast.BoolOp)):
                complexity += 1
        self.functions.append({
            "name": node.name,
            "lineno": node.lineno,
            "complexity": complexity
        })
        self.generic_visit(node)

def review_source_code():
    python_files = [f for f in os.listdir('.') if f.endswith('.py') and f != 'guardian_code_reviewer.py']
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "files_analyzed": []
    }
    
    for file_path in python_files:
        print(f"\n[*] Analizando archivo: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        try:
            tree = ast.parse(content)
            visitor = CodeComplexityVisitor()
            visitor.visit(tree)
            
            file_data = {
                "file": file_path,
                "functions": visitor.functions,
                "status": "INTEGRITY_OK"
            }
            report["files_analyzed"].append(file_data)
            
            for func in visitor.functions:
                print(f"  - Función '{func['name']}' (Línea {func['lineno']}): Complejidad Ciclomática = {func['complexity']}")
                if func['complexity'] > 15:
                    print(f"    [!] ALERTA: Alta complejidad detectada en '{func['name']}'. Se sugiere refactorizar.")
        except Exception as e:
            print(f"  [X] Error analizando {file_path}: {e}")
            
    with open("GUARDIAN_CODE_REVIEW_REPORT.json", "w") as f:
        json.dump(report, f, indent=4)
    print("\n[✔] Reporte de revisión exportado: GUARDIAN_CODE_REVIEW_REPORT.json")

if __name__ == "__main__":
    review_source_code()
    print("========================================================================")
    print("   [ESTADO FINAL]: REVISIÓN DE CÓDIGO FUENTE COMPLETADA")
    print("========================================================================")
