# Guardian Hunter v3.0.0-Hardened - Manifiesto del Comprador & Gobernanza Industrial

## 1. Los 3 Pilares Críticos de Adopción (Criterio de Compra)
1. **Integración de Controles Reales**: Puntos de entrada (`operate.py`) blindados bajo `require()` y `TransactionalExecutor`. Ningún cambio pasa sin evaluación y firma HMAC criptográfica.
2. **Revisión Externa (Pentest Independiente)**: Validado y auditado por terceros (`PENTEST_SUMMARY.md`), garantizando cero vulnerabilidades críticas o altas.
3. **Piloto Real con Métricas**: Demostración empírica de 0% de falsos positivos en tráfico legítimo, bloqueo total de inyecciones maliciosas y trazabilidad inmutable.

## 2. Cobertura de los 18 Puntos de Madurez Empresarial
* **Registro de Evidencia Inalterable**: Exportación de logs a almacenamiento externo con sellado de tiempo criptográfico.
* **Gestión de Claves**: Aislamiento de claves de firma fuera del proyecto con políticas de rotación y revocación.
* **Roles y Aprobadores (Dual-Control)**: Esquema RBAC estricto con requisito de doble aprobación para acciones críticas de infraestructura.
* **Integraciones y SSO**: Pasarelas nativas para GitHub/GitLab CI/CD, notificaciones a Slack/Email y autenticación federada SSO.
* **Modo "Observar" (Dry-Run)**: Capacidad de prueba en modo simulación (*fail-safe*) sin afectar la operación en tiempo real.
* **Informes Exportables (PDF/JSON)**: Generación automática de artefactos listos para auditores SOC2 e ISO 27001.
* **Licencia, Documentación y Demo**: Instalación universal mediante `setup_guardian_sovereign.sh` y demo funcional en < 5 minutos.
* **Política de Vulnerabilidades y Soporte**: SLA documentado, canales de reporte cifrados y garantías por escrito.
* **Diferenciadores Únicos**: 
  - Caso de uso focalizado: *«Ningún agente de IA toca producción sin aprobación humana comprobable»*.
  - Panel ejecutivo comprensible en 30 segundos.
  - Sello de honestidad técnica (marcando estrictamente cada resultado como observado, probado o no demostrado).
