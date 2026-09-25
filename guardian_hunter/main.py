from guardian_hunter.alerts import AlertHistory
from guardian_hunter.assets import AssetManager
from guardian_hunter.config.settings import APP_NAME
from guardian_hunter.core.logger import setup_logger
from guardian_hunter.reports import export_json
from guardian_hunter.risk import calculate_risk
from guardian_hunter.system import system_state


def main():
    logger = setup_logger()

    logger.info("%s iniciado", APP_NAME)
    logger.info("Entorno cargado correctamente")

    assets = AssetManager()
    alerts = AlertHistory()

    state = system_state(assets)

    logger.info(
        "System: %s | modo=%s",
        state["status"],
        state["mode"],
    )

    logger.info(
        "Assets: %s autorizados | %s descubiertos",
        len(assets.get_authorized()),
        len(assets.get_discovered()),
    )

    logger.info("Hunter disponible: pasivo/autorizado")
    logger.info("Assessment disponible: análisis seguro")
    logger.info("Risk Engine disponible")
    logger.info("Intelligence catalog disponible")
    logger.info("Reports disponible: JSON/CSV/PDF")
    logger.info(
        "Alerts disponible: %s eventos",
        alerts.count(),
    )

    risk = calculate_risk([])

    logger.info(
        "Risk Engine operativo: %s findings",
        risk["total"],
    )

    report = {
        "system": state,
        "risk": risk,
        "assets": {
            "authorized": assets.get_authorized(),
            "discovered": assets.get_discovered(),
            "changes": assets.get_changes(),
        },
        "alerts": {
            "count": alerts.count(),
            "recent": alerts.recent(10),
        },
    }

    report_path = export_json(
        report,
        "system_status",
    )

    logger.info(
        "Reporte JSON generado: %s",
        report_path,
    )


if __name__ == "__main__":
    main()
