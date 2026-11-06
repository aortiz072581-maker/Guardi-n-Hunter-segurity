# Política de Seguridad y Gobernanza - Guardian Hunter

## 1. Visión General y Propósito
El proyecto **Guardian Hunter** (rama `seguridad-autorizaciones-2026`) está diseñado bajo un estándar de calidad e integridad de grado industrial (*Enterprise-Grade*). Su objetivo es garantizar la seguridad perimetral, la auditoría inalterable y el cumplimiento normativo estricto.

## 2. Modelo de Control Estricto (HITL - Human-in-the-Loop)
* **Autoridad Exclusiva:** Ninguna modificación, refactorización o cambio de código es aplicado de forma autónoma sin la revisión y autorización explícita del operador humano.
* **Compuertas Automatizadas:** Las herramientas de IA y análisis actúan como consultores de diagnóstico preventivo, pero el veredicto final recae bajo la aprobación humana.

## 3. Mecanismos de Blindaje e Integridad
* **Tipado Estricto (Mypy):** Validación continua de contratos de tipos estáticos para prevenir errores lógicos en tiempo de compilación.
* **Análisis AST de Complejidad:** Detección y control de funciones con alta complejidad ciclomática para mantener un código limpio y mantenible.
* **Ganchos de Pre-commit Automatizados:** Restricción a nivel local de Git que bloquea cualquier commit que no supere las auditorías de seguridad e integridad (`ci_audit_check.py`).
* **Bitácoras Criptográficas (Tamper-Evident Logging):** Los eventos del sistema se registran en una cadena de bloques basada en hashes incrementales (`SHA-256`), asegurando que cualquier intento de alteración rompa de inmediato la cadena de confianza.
