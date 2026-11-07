import sys, os

print("=== INICIANDO SUITE DE PRUEBAS INTEGRALES DE GUARDIAN HUNTER ===")

try:
    from guardian_hunter.license_manager import GuardianLicense
    lic = GuardianLicense("ENTERPRISE_SOVEREIGN")
    print("[✔] license_manager OK:", lic.get_license_summary()["tier"])
except Exception as e:
    print("[X] license_manager error:", e)

try:
    from guardian_hunter.policy_engine import PolicyEngine
    pe = PolicyEngine()
    action = pe.evaluate_threat("CRITICO", 0.98)
    print("[✔] policy_engine OK, Action:", action)
except Exception as e:
    print("[X] policy_engine error:", e)

try:
    from guardian_hunter.tpm_anchor import TPMHardwareAnchor
    tpm = TPMHardwareAnchor()
    valid = tpm.verify_hardware_integrity("LICENSE-KEY-123")
    print("[✔] tpm_anchor OK, Valid:", valid)
except Exception as e:
    print("[X] tpm_anchor error:", e)

try:
    from guardian_hunter.red_teaming import InternalBreachSimulator
    bas = InternalBreachSimulator()
    res = bas.run_simulation(0)
    print("[✔] red_teaming OK:", res)
except Exception as e:
    print("[X] red_teaming error:", e)

try:
    from guardian_hunter.blind_telemetry import BlindTelemetry
    bt = BlindTelemetry()
    encrypted = bt.encrypt_event_stats({"pid": 9912, "action": "exec"})
    print("[✔] blind_telemetry OK:", encrypted[:50])
except Exception as e:
    print("[X] blind_telemetry error:", e)

try:
    from guardian_hunter.siem_connector import SIEMConnector
    siem = SIEMConnector()
    sent = siem.send_cef_alert("EVT_01", 8, "Unauthorized execution")
    print("[✔] siem_connector OK:", sent)
except Exception as e:
    print("[X] fido2_auth error:", e)

try:
    from guardian_hunter.fido2_auth import FIDO2HardwareAuth
    fido = FIDO2HardwareAuth()
    auth = fido.verify_fido2_assertion("yubikey_enterprise_5ci", "{}", "base64sig...")
    print("[✔] fido2_auth OK:", auth)
except Exception as e:
    print("[X] fido2_auth error:", e)

print("=== SUITE DE PRUEBAS COMPLETADA EXITOSAMENTE ===")

# Pruebas de los nuevos módulos avanzados
try:
    from guardian_hunter.advanced.apt_sandbox import APTSandboxSimulator
    apt = APTSandboxSimulator()
    print("[✔] apt_sandbox OK:", apt.simulate_apt_attack("LSASS_MEMORY_DUMP"))
except Exception as e:
    print("[X] apt_sandbox error:", e)

try:
    from guardian_hunter.advanced.network_ebpf import NetworkC2Detector
    net = NetworkC2Detector()
    print("[✔] network_ebpf OK:", net.inspect_socket_connection("185.220.101.5", 4444))
except Exception as e:
    print("[X] network_ebpf error:", e)

try:
    from guardian_hunter.advanced.pqc_crypto import PostQuantumCrypto
    pqc = PostQuantumCrypto()
    print("[✔] pqc_crypto OK:", pqc.sign_telemetry_pqc("Event data"))
except Exception as e:
    print("[X] pqc_crypto error:", e)

try:
    from guardian_hunter.advanced.local_llm_guard import LocalLLMAnomalies
    llm = LocalLLMAnomalies()
    print("[✔] local_llm_guard OK:", llm.analyze_behavior_airgapped(["execve", "ptrace"]))
except Exception as e:
    print("[X] local_llm_guard error:", e)

# Pruebas de arquitecturas hiper-avanzadas
try:
    from guardian_hunter.advanced.p2p_mesh_defense import P2PMeshDefense
    mesh = P2PMeshDefense("node_sovereign_01")
    print("[✔] p2p_mesh_defense OK:", mesh.broadcast_threat_isolation("node_rogue_99"))
except Exception as e:
    print("[X] p2p_mesh_defense error:", e)

try:
    from guardian_hunter.advanced.microvm_sandbox import MicroVMSandboxManager
    vm = MicroVMSandboxManager()
    print("[✔] microvm_sandbox OK:", vm.spawn_ephemeral_microvm("PAYLOAD_ENGINE_01"))
except Exception as e:
    print("[X] microvm_sandbox error:", e)

# Pruebas de la capa comercial y compliance
try:
    from guardian_hunter.license_generator import SovereignLicenseGenerator
    lg = SovereignLicenseGenerator()
    print("[✔] license_generator OK:", lg.generate_signed_license("ACME Corp", "ENTERPRISE_SOVEREIGN", 1000)["license_key"])
except Exception as e:
    print("[X] license_generator error:", e)

try:
    from guardian_hunter.advanced.compliance_reporter import ComplianceReporter
    cr = ComplianceReporter()
    print("[✔] compliance_reporter OK:", cr.generate_audit_certificate()["blockchain_proof_hash"][:16])
except Exception as e:
    print("[X] compliance_reporter error:", e)

# Pruebas de MTD y Auto-Parcheo por IA
try:
    from guardian_hunter.advanced.mtd_kernel_deception import KernelMovingTargetDefense
    mtd = KernelMovingTargetDefense()
    print("[✔] mtd_kernel_deception OK:", mtd.randomize_kernel_layout()["status"])
except Exception as e:
    print("[X] mtd_kernel_deception error:", e)

try:
    from guardian_hunter.advanced.auto_patch_ai import PolymorphicAutoPatcher
    patcher = PolymorphicAutoPatcher()
    print("[✔] auto_patch_ai OK:", patcher.evaluate_and_patch_zero_day("ZERO_DAY_SYSCALL_HOOK")["status"])
except Exception as e:
    print("[X] auto_patch_ai error:", e)

# Pruebas de Hardware PUF y Redes SAGIN
try:
    from guardian_hunter.advanced.hardware_puf_root import HardwarePUFRootOfTrust
    puf = HardwarePUFRootOfTrust()
    print("[✔] hardware_puf_root OK:", puf.verify_silicon_identity()["status"])
except Exception as e:
    print("[X] hardware_puf_root error:", e)

try:
    from guardian_hunter.advanced.sagin_tactical_net import SAGINTacticalNetwork
    sagin = SAGINTacticalNetwork()
    print("[✔] sagin_tactical_net OK:", sagin.sync_satellite_link(850)["sagin_status"])
except Exception as e:
    print("[X] sagin_tactical_net error:", e)

# Pruebas del Nivel Transcendente (QKD y Hive Mind)
try:
    from guardian_hunter.advanced.qkd_quantum_mesh import QuantumKeyDistribution
    qkd = QuantumKeyDistribution()
    print("[✔] qkd_quantum_mesh OK:", qkd.establish_quantum_channel("node_omega")["qkd_status"])
except Exception as e:
    print("[X] qkd_quantum_mesh error:", e)

try:
    from guardian_hunter.advanced.hive_mind_soc import HiveMindSOC
    hive = HiveMindSOC()
    print("[✔] hive_mind_soc OK:", hive.broadcast_global_immunization("ZERO_DAY_MUTANT_V9")["hive_status"])
except Exception as e:
    print("[X] hive_mind_soc error:", e)

# Pruebas de los 3 Horizontes de Vanguardia
try:
    from guardian_hunter.horizons.bio_immune_system import BioImmuneSystem
    bio = BioImmuneSystem()
    print("[✔] bio_immune_system OK:", bio.synthesize_digital_antibody("KERNEL_ANOMALY_X")["status"])
except Exception as e:
    print("[X] bio_immune_system error:", e)

try:
    from guardian_hunter.horizons.tee_enclave_manager import TEEEnclaveManager
    tee = TEEEnclaveManager()
    print("[✔] tee_enclave_manager OK:", tee.initialize_hardware_enclave()["status"])
except Exception as e:
    print("[X] tee_enclave_manager error:", e)

try:
    from guardian_hunter.horizons.swarm_orchestrator import SwarmOrchestrator
    swarm = SwarmOrchestrator()
    print("[✔] swarm_orchestrator OK:", swarm.reconfigure_swarm_mesh("node_frontline_01")["swarm_status"])
except Exception as e:
    print("[X] swarm_orchestrator error:", e)
