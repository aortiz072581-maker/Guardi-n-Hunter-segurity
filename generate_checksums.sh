#!/bin/bash

echo "=== GENERANDO HUELLA CRIPTOGRÁFICA SHA3-512 (ANTI-TAMPER) ==="

if [ -f "./guardian_native_core" ]; then
    HASH_CPLUSPLUS=$(python3 -c "import hashlib; print(hashlib.sha3_512(open('guardian_native_core', 'rb').read()).hexdigest())")
    echo "NATIVE_CORE_SHA3_512=$HASH_CPLUSPLUS" > CHECKSUMS.txt
    echo "[✔] Hash de NATIVE_CORE generado y guardado en CHECKSUMS.txt:"
    echo "    $HASH_CPLUSPLUS"
else
    echo "[!] Error: No se encontró el ejecutable './guardian_native_core'. Compílalo primero con g++."
fi
