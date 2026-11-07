class PolicyEngine:
    def evaluate_threat(self, risk_level: str, confidence: float) -> str:
        if risk_level == "CRITICO" and confidence > 0.95:
            return "AUTO_ISOLATE_NODE"
        return "REQUIRE_ED25519_SIGNATURE"
