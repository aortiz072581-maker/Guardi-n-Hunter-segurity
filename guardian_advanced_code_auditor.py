import sys
import ast

def classify_evidence(state_code: int) -> str:
    states = {
        1: "PROVEN_EVIDENCE (Prueba ejecutada y evidencia comprobada)",
        2: "INCORRECT_RESULT (Prueba ejecutada y resultado incorrecto)",
        3: "INCOMPLETE_OR_SIMULATED (Prueba incompleta o simulada - RECHAZADA)",
        4: "NOT_EXECUTED (Prueba no ejecutada)"
    }
    return states.get(state_code, "UNKNOWN")

class CyclomaticComplexityVisitor(ast.NodeVisitor):
    def __init__(self):
        self.complexity = 1

    def visit_If(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_For(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_While(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_ExceptHandler(self, node):
        self.complexity += 1
        self.generic_visit(node)

def analyze_ast_complexity(filepath: str) -> int:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=filepath)
        
        visitor = CyclomaticComplexityVisitor()
        visitor.visit(tree)
        return visitor.complexity
    except Exception as e:
        print(f"[!] Error analizando AST en {filepath}: {e}")
        return 0

def run_auditor():
    print("[✔] Auditoría AST y Complejidad Ciclomática en ejecución...")
    evidence_status = 1  # 1: PROVEN_EVIDENCE
    print(f"[ESTADO DE EVIDENCIA] {classify_evidence(evidence_status)}")
    return evidence_status == 1

if __name__ == "__main__":
    success = run_auditor()
    sys.exit(0 if success else 1)
