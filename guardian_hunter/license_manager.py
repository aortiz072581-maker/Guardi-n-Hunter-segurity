import json, sys

TIERS_CONFIG = {
    "ESSENTIAL_SHIELD": {"ebpf_level": "BASIC", "human_in_the_loop": True, "custom_rules": False, "max_nodes": 50},
    "ENTERPRISE_SOVEREIGN": {"ebpf_level": "FULL_37_LAYERS", "human_in_the_loop": True, "custom_rules": True, "max_nodes": 500},
    "CRITICAL_INFRASTRUCTURE": {"ebpf_level": "CUSTOM_KERNEL_SLA", "human_in_the_loop": True, "custom_rules": True, "max_nodes": 999999}
}

class GuardianLicense:
    def __init__(self, tier_name: str = "ENTERPRISE_SOVEREIGN"):
        self.tier_name = tier_name
        self.features = TIERS_CONFIG.get(tier_name, TIERS_CONFIG["ENTERPRISE_SOVEREIGN"])

    def get_license_summary(self) -> dict:
        return {"tier": self.tier_name, "status": "ACTIVE", "capabilities": self.features}
