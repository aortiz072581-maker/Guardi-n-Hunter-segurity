import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_pdf(filename="Guardian_Hunter_Technical_Manual.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=40, leftMargin=40,
        topMargin=40, bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    # Estilos personalizados de nivel corporativo
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        textColor=colors.HexColor('#1A202C'),
        spaceAfter=6,
        alignment=1
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        textColor=colors.HexColor('#4A5568'),
        spaceAfter=15,
        alignment=1
    )
    
    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        textColor=colors.HexColor('#2B6CB0'),
        spaceBefore=12,
        spaceAfter=6
    )
    
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        textColor=colors.HexColor('#2D3748'),
        spaceAfter=6,
        leading=13
    )
    
    bullet_style = ParagraphStyle(
        'BulletText',
        parent=body_style,
        leftIndent=15,
        spaceAfter=4
    )

    story = []

    # Encabezado del Documento
    story.append(Paragraph("GUARDIAN HUNTER ENTERPRISE", title_style))
    story.append(Paragraph("Manual de Arquitectura y Especificación Técnica Soberana (v3.0.0-Hardened)", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2B6CB0'), spaceAfter=12))

    # 1. Resumen Ejecutivo
    story.append(Paragraph("1. Resumen Ejecutivo e Intento del Sistema", h1_style))
    story.append(Paragraph(
        "<b>Guardian Hunter</b> es una plataforma de seguridad soberana de grado industrial diseñada para operar en entornos "
        "completamente aislados (air-gapped) o críticos. Su arquitectura combina un motor determinista en Python, interceptación "
        "de bajo nivel mediante eBPF/LSM Seccomp, atestación criptográfica de hardware y un registro de auditoría inmutable de doble quorum.",
        body_style
    ))

    # 2. Núcleo y Lógica de Decisión
    story.append(Paragraph("2. Núcleo de Detección y Lógica de Decisión", h1_style))
    story.append(Paragraph("• <b>Motor Híbrido Z-Score + Llama-3B:</b> Análisis cuantitativo estricto mediante Z-score para veredictos duros (CLEAN/ANOMALY), aislando la inteligencia artificial (Llama-3B local) exclusivamente para la summarización semántica.", bullet_style))
    story.append(Paragraph("• <b>Principio Fail-Closed:</b> Arquitectura de denegación por defecto ante cualquier fallo de privilegios o anomalía detectada.", bullet_style))

    # 3. Blindaje de Kernel y Hardware
    story.append(Paragraph("3. Blindaje de Kernel y Hardware", h1_style))
    story.append(Paragraph("• <b>TPM 2.0 / vTPM Attestation:</b> Verificación de registros PCR mediante hardware físico o mediante un protocolo vTPM con semillas criptográficas y firmas estrictas de respaldo.", bullet_style))
    story.append(Paragraph("• <b>LSM Seccomp Real:</b> Restricción estricta sobre llamadas al sistema (syscalls) a través de la interfaz del kernel para bloquear comportamientos no autorizados.", bullet_style))
    story.append(Paragraph("• <b>Soporte eBPF con Fallback:</b> Trazas de kernel con conmutación automática a Seccomp en entornos restringidos (como Termux).", bullet_style))

    # 4. Ledger Distribuido e Inmutabilidad
    story.append(Paragraph("4. Ledger Distribuido con Quorum e Inmutabilidad", h1_style))
    story.append(Paragraph("• <b>Ledger Append-Only:</b> Registro criptográfico de eventos usando hashes SHA3-512 con sincronización atómica mediante llamadas directas a os.fsync().", bullet_style))
    story.append(Paragraph("• <b>Quorum de Respaldo (Primary + Replica):</b> Replicación síncrona en dos archivos independientes (ledger_primary.jsonl y ledger_replica_quorum.jsonl) para resistir auditorías de partición (Split-Brain).", bullet_style))

    # 5. Observabilidad y SIEM
    story.append(Paragraph("5. Observabilidad, Telemetría y SIEM", h1_style))
    story.append(Paragraph("• <b>Métricas Prometheus:</b> Exportación automatizada de contadores y latencias p95 inferiores al 2%.", bullet_style))
    story.append(Paragraph("• <b>Conector SIEM HMAC-SHA256:</b> Envíos de telemetría y alertas firmadas criptográficamente para integración con colectores corporativos (Splunk, Datadog, Elastic).", bullet_style))

    # 6. Cadena de Suministro y CI/CD
    story.append(Paragraph("6. Aseguramiento, CI/CD y SBOM", h1_style))
    story.append(Paragraph("• <b>Compuertas de Integridad:</b> Bloqueo automático ante el uso de aserciones (assert) en código fuente productivo, exigiendo excepciones empresariales explícitas.", bullet_style))
    story.append(Paragraph("• <b>Auditorías AST, Diff y Fuzzing:</b> Análisis de complejidad ciclomática y simulaciones de entradas extremas para garantizar cero fallos fatales.", bullet_style))
    story.append(Paragraph("• <b>Manifiesto SBOM (SHA3-512):</b> Control de suministro mediante el archivo sbom_manifest_v3.json que garantiza la inmutabilidad de los artefactos.", bullet_style))

    # 7. Interfaz de Control (CLI)
    story.append(Paragraph("7. Interfaz de Control Soberano (CLI)", h1_style))
    story.append(Paragraph("• <b>Panel de Comandos (guardian_cli.py):</b> Interfaz unificada para consultar el estado del sistema en modo seguro, ejecutar auditorías de subsistemas y gestionar rollbacks de parches de kernel.", bullet_style))

    doc.build(story)
    print(f"[✔] PDF generado con éxito: {filename}")

if __name__ == "__main__":
    generate_pdf()
