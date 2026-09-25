from guardian_hunter.alerts import AlertHistory, generate_alerts
from guardian_hunter.assessment import (
    assess_dns,
    assess_http,
    assess_services,
    assess_tls,
)
from guardian_hunter.correlation import correlate_findings
from guardian_hunter.database import Database
from guardian_hunter.normalizer import normalize_assessment
from guardian_hunter.reports import export_bundle
from guardian_hunter.risk import calculate_risk
from guardian_hunter.system import utc_now


class SecurityPipeline:
    def __init__(self, asset_manager, database=None):
        self.assets = asset_manager
        self.database = database or Database()
        self.alerts = AlertHistory()

    def assess(
        self,
        target,
        url=None,
        run_services=False,
        technologies=None,
        cves=None,
        kev=None,
    ):
        if not self.assets.is_authorized(target):
            raise PermissionError("El objetivo no está autorizado.")

        timestamp = utc_now()
        findings = []

        dns_result = assess_dns(target)
        findings.extend(dns_result.get("findings", []))

        http_result = None
        tls_result = None
        services_result = None

        if url:
            http_result = assess_http(url)
            findings.extend(http_result.get("findings", []))

            if url.lower().startswith("https://"):
                tls_result = assess_tls(target)
                findings.extend(tls_result.get("findings", []))

        if run_services:
            services_result = assess_services(target)

        normalized = normalize_assessment(findings)

        correlated = correlate_findings(
            target,
            normalized,
            technologies=technologies or [],
            cves=cves or [],
            kev=kev or [],
        )

        risk = calculate_risk(correlated)

        alerts = generate_alerts(
            risk,
            history=self.alerts,
        )

        execution_id = self.database.add_execution(
            timestamp=timestamp,
            target=target,
            status="completed",
            summary=risk["summary"],
        )

        self.database.add_asset(
            target,
            "authorized",
            timestamp,
        )

        for finding in risk["findings"]:
            fingerprint = finding.get(
                "fingerprint",
                finding.get("title", "finding"),
            )

            self.database.add_finding(
                execution_id,
                finding,
                fingerprint,
                timestamp,
            )

        for technology in technologies or []:
            if isinstance(technology, dict):
                self.database.add_technology(
                    technology.get("name"),
                    technology.get("version"),
                    technology.get("source", "local"),
                    timestamp,
                )

        for alert in alerts:
            self.database.add_alert(
                execution_id,
                timestamp,
                alert,
            )

        report = {
            "pipeline_version": "2.0",
            "execution_id": execution_id,
            "timestamp": timestamp,
            "target": target,
            "dns": dns_result,
            "http": http_result,
            "tls": tls_result,
            "services": services_result,
            "findings": risk["findings"],
            "risk": risk,
            "alerts": alerts,
            "correlation": {
                "technologies": technologies or [],
                "cves": cves or [],
                "kev": kev or [],
            },
        }

        reports = export_bundle(
            report,
            "pipeline_assessment",
        )

        return {
            "report": report,
            "reports": reports,
            "alerts": alerts,
            "execution_id": execution_id,
        }
