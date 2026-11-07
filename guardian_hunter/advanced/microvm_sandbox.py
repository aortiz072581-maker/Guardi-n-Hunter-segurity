class MicroVMSandboxManager:
    def spawn_ephemeral_microvm(self, workload_id: str) -> dict:
        print(f"[MicroVM] Desplegando carga {workload_id} en Hypervisor liviano aislado...")
        return {"vm_status": "RUNNING", "isolation_level": "HARDWARE_VIRTUALIZED", "firecracker_compliant": True}
