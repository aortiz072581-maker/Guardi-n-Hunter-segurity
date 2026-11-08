# Guardian Hunter - Modelo de Amenazas (1-Página)

## 1. Supuestos del Atacante
* **Acceso**: El atacante puede tener acceso local como usuario no privilegiado o enviar cargas maliciosas (prompts/red) al entorno.
* **Capacidad**: Intenta inyección de instrucciones en LLM, derivación de sandbox, y bypass de controles RBAC.

## 2. Ataques Bloqueados
* **Inyección de Prompts & Jailbreaks**: Filtrados por entropía y patrones maliciosos en `AIThreatDetectionEngine`.
* **Modificaciones no autorizadas**: Bloqueadas por `require()` y `TransactionalExecutor` si carecen de firma HMAC válida.
* **Escalación de Privilegios**: Interceptada por políticas Seccomp/eBPF y comprobación estricta de roles RBAC.

## 3. Ataques Fuera de Alcance (No Bloqueados)
* Compromiso físico directo del hardware del dispositivo sin TEE/Hardware Root of Trust activo.
* Ataques de denegación de servicio distribuido (DDoS) a nivel de proveedor de red exterior.
