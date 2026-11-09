# Guardian Hunter - NIST Compliance & Governance Blueprint

Este documento establece el mapeo oficial entre las capacidades autónomas de Guardian Hunter y los marcos de referencia de ciberseguridad e inteligencia artificial del NIST (**National Institute of Standards and Technology**).

---

## 1. Alineación con NIST Cybersecurity Framework (CSF) 2.0
El CSF 2.0 organiza la gestión de riesgos en funciones nucleares que Guardian Hunter automatiza y valida de forma empírica:

* **Govern (Gobernanza)**: 
  - *Implementación*: Control de acceso basado en roles, registros de auditoría inalterables (WORM) y puertas de aprobación humana obligatorias (**HITL** con firmas HMAC).
* **Identify (Identificación)**:
  - *Implementación*: Descubrimiento profundo de superficie de ataque, detección de Shadow IT y análisis de riesgos en activos expuestos (`guardian_attack_and_risk_engine.py`).
* **Protect (Protección)**:
  - *Implementación*: Blindaje de aplicaciones, infraestructura cloud y APIs mediante parches atómicos y políticas de seguridad preventivas.
* **Detect (Detección)**:
  - *Implementación*: Inteligencia de amenazas activa, simulación de ataques en tiempo real y cálculo continuo de métricas operativas (**MTTD**).
* **Respond & Recover (Respuesta y Recuperación)**:
  - *Implementación*: Motores de auto-remediación asistida, validación empírica post-parche de 8 pasos y reducción garantizada del riesgo residual.

---

## 2. Alineación con NIST AI Risk Management Framework (AI RMF)
El AI RMF guía la gestión responsable, confiable y segura de los sistemas de Inteligencia Artificial mediante cuatro pilares clave cubiertos por **Guardian AI Defense**:

* **Govern (Gobernar la IA)**:
  - *Implementación*: Políticas corporativas personalizadas para el uso de modelos, auditoría de permisos de agentes autónomos y trazabilidad de decisiones algorítmicas.
* **Map (Mapear el Riesgo)**:
  - *Implementación*: Evaluación profunda de pesos, tuberías de inferencia (*pipelines*) y identificación de vulnerabilidades específicas en entornos de IA.
* **Measure (Medir el Riesgo)**:
  - *Implementación*: Pruebas automatizadas y continuas contra *Prompt Injection*, *Jailbreaks* y fugas de datos sensibles (PII), cuantificando la entropía y anomalías en interacciones con LLMs.
* **Manage (Gestionar el Riesgo)**:
  - *Implementación*: Mitigación activa, aislamiento multi-tenant y simulación controlada de ataques impulsados por IA para asegurar la resiliencia operativa continua.
