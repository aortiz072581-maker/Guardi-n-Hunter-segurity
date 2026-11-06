#!/bin/bash

echo "=== AUDITORÍA DE REQUERIMIENTOS DE KERNEL DE LINUX ==="
echo "[*] Verificando privilegios necesarios para eBPF..."
echo "  1. CAP_BPF        : Requerido para cargar mapas e eBPF programs (Kernel 5.8+)"
echo "  2. CAP_SYS_ADMIN  : Requerido para operaciones legacy de tracer/kernel"
echo "  3. CAP_NET_ADMIN  : Requerido para inspección de paquetes en interfaces de red"
echo ""

# Simulación de verificación de permisos
if [ $(id -u) -eq 0 ]; then
    echo "[✔] Permisos de superusuario detectados (ROOT). Capacidades activables."
else
    echo "[i] Entorno de prueba (Modo Unprivileged/Termux). En produccion Enterprise Linux se requiere ejecutar bajo CAP_BPF / CAP_SYS_ADMIN."
fi
