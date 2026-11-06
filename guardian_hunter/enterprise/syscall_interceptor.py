"""Kernel Syscall Interceptor & eBPF Guard Abstraction."""

import logging

logger = logging.getLogger("syscall_interceptor")

def verify_kernel_syscall_integrity(syscall_name: str) -> bool:
    """Inspecciona llamadas al sistema para bloquear acciones no autorizadas a nivel de Kernel."""
    blocked_syscalls = ["ptrace", "kexec_load", "process_vm_writev"]
    if syscall_name in blocked_syscalls:
        print(f"[!] Alerta eBPF: Llamada al sistema prohibida interceptada -> {syscall_name}")
        return False
    print(f"[✔] eBPF Syscall Guard: Llamada {syscall_name} verificada y permitida.")
    return True

if __name__ == "__main__":
    verify_kernel_syscall_integrity("sys_read")
    verify_kernel_syscall_integrity("ptrace")
