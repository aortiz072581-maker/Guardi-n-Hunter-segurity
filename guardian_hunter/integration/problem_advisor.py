"""Fail-closed problem recognition and recovery advice."""

def analyze_problem(name, ok):
    if ok:
        return None

    knowledge = {
        "python_modules": (
            "Dependencia o módulo no disponible",
            "Instalación incompleta o entorno Python alterado",
            "Revisar las dependencias antes de continuar",
        ),
        "integrity_baseline": (
            "Baseline de integridad ausente",
            "Baseline eliminado, movido o no inicializado",
            "Verificar o regenerar un baseline autorizado",
        ),
        "integrity_tamper": (
            "Cambio detectado en archivos protegidos",
            "Archivo protegido añadido, modificado o eliminado",
            "Revisar el cambio y restaurar desde un checkpoint verificado si no fue autorizado",
        ),
        "hardware": (
            "Cambio detectado en hardware",
            "Inventario o dispositivo local cambió respecto al estado anterior",
            "Revisar el dispositivo y confirmar si el cambio fue autorizado",
        ),
        "network": (
            "Cambio detectado en red",
            "Interfaz, dirección, ruta o vecino cambió respecto al estado anterior",
            "Revisar el cambio de red y confirmar si corresponde al estado esperado",
        ),
        "hardware": (
            "Cambio detectado en hardware",
            "Inventario o dispositivo local cambió respecto al estado anterior",
            "Revisar el dispositivo y confirmar si el cambio fue autorizado",
        ),
        "network": (
            "Cambio detectado en red",
            "Interfaz, dirección, ruta o vecino cambió respecto al estado anterior",
            "Revisar el cambio de red y confirmar si corresponde al estado esperado",
        ),
        "storage": (
            "Espacio de almacenamiento insuficiente",
            "Poco espacio libre disponible",
            "Liberar espacio antes de continuar",
        ),
        "defensive_components": (
            "Componente defensivo ausente",
            "Archivo eliminado, modificado o instalación incompleta",
            "Restaurar desde un checkpoint verificado",
        ),
    }

    problem, cause, solution = knowledge.get(
        name,
        (
            "Problema no clasificado",
            "La causa requiere revisión",
            "Mantener bloqueo y realizar revisión humana",
        ),
    )

    return {
        "problem": problem,
        "probable_cause": cause,
        "recommended_solution": solution,
        "automatic_repair": False,
        "human_review": True,
    }


def advise_health_result(health):
    findings = []

    for check in health.get("checks", []):
        finding = analyze_problem(check["name"], check["ok"])
        if finding:
            finding["sensor"] = check["name"]
            findings.append(finding)

    return {
        "findings": findings,
        "problem_count": len(findings),
        "automatic_repair": False,
        "execution_allowed": False,
        "response_locked": True,
    }
