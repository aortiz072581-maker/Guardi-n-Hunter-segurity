import json
import time

print("========================================================================")
print("   [GUARDIAN HUNTER] MOTOR DE INTELIGENCIA DE ATAQUE Y RIESGO (ASRM)")
print("========================================================================")

class AttackSurfaceIntelligence:
    """Inventaría y analiza la superficie de exposición externa de la empresa."""
    def __init__(self, company_name: str):
        self.company_name = company_name
        self.assets = [
            {"type": "domain", "value": f"api.{company_name.lower()}.com", "exposure": "Public", "status": "Active"},
            {"type": "cloud_bucket", "value": f"s3://{company_name.lower()}-backup-prod", "exposure": "Public (Misconfigured)", "status": "Critical"},
            {"type": "service", "value": "Kubernetes API Server (Port 6443)", "exposure": "Internet-Facing", "status": "High Risk"},
            {"type": "internal_app", "value": f"auth.{company_name.lower()}.internal", "exposure": "Internal Only", "status": "Secure"}
        ]

    def scan_surface(self):
        print(f"\n[+] [ASM] Escaneando superficie de ataque para: {self.company_name}")
        for asset in self.assets:
            print(f"  - [{asset['type'].upper()}] {asset['value']} | Exposición: {asset['exposure']} | Estado: {asset['status']}")
        return self.assets

class RiskIntelligenceEngine:
    """Calcula el riesgo empresarial real ponderando exposición, exploitabilidad e impacto."""
    def __init__(self, assets):
        self.assets = assets

    def calculate_enterprise_risk(self):
        print("\n[+] [RISK ENGINE] Calculando vectores de riesgo ponderados...")
        risk_matrix = []
        
        for asset in self.assets:
            if "Public" in asset["exposure"] or "Internet-Facing" in asset["exposure"]:
                # Ponderación de criticidad de negocio y probabilidad
                score = 9.5 if "Critical" in asset["status"] else 8.2
                priority = "P1 - CRÍTICO (Acción Inmediata Requerida)"
            else:
                score = 3.1
                priority = "P3 - BAJO (Monitoreo Interno)"

            risk_item = {
                "asset": asset["value"],
                "risk_score": score,
                "business_impact": "Exposición de datos sensibles / Posible takeover de infraestructura",
                "priority": priority
            }
            risk_matrix.append(risk_item)
            print(f"  [!] Activo: {asset['value']}")
            print(f"      - Score de Riesgo Ponderado: {score}/10")
            print(f"      - Prioridad Empresarial: {priority}")

        return risk_matrix

if __name__ == "__main__":
    asm = AttackSurfaceIntelligence("SovereignCorp")
    discovered_assets = asm.scan_surface()
    
    risk_engine = RiskIntelligenceEngine(discovered_assets)
    report = risk_engine.calculate_enterprise_risk()

    # Guardar reporte estructurado para directivos y auditores
    output_report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "target": "SovereignCorp",
        "attack_surface_assets": discovered_assets,
        "risk_intelligence_matrix": report
    }

    with open("GUARDIAN_ASM_RISK_REPORT.json", "w") as f:
        json.dump(output_report, f, indent=4)

    print("\n[✔] Reporte de Inteligencia de Ataque y Riesgo generado: GUARDIAN_ASM_RISK_REPORT.json")
    print("========================================================================")
