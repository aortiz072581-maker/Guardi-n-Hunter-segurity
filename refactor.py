from typing import Dict, Any, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GuardianHunterRefactor")

def _extract_candidate_metadata(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": raw_data.get("candidate_id"),
        "timestamp": raw_data.get("timestamp"),
        "source": raw_data.get("source", "unknown")
    }

def _validate_candidate_schema(metadata: Dict[str, Any]) -> bool:
    return bool(metadata.get("id") and metadata.get("timestamp"))

def prepare_codex_candidate(raw_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not raw_data:
        logger.warning("Datos vacíos recibidos.")
        return {"status": "INVALID", "reason": "empty_data"}
    metadata = _extract_candidate_metadata(raw_data)
    if not _validate_candidate_schema(metadata):
        return {"status": "REJECTED", "reason": "schema_validation_failed"}
    return {"status": "APPROVED", "metadata": metadata, "integrity_check": True}

def _filter_sensor_metrics(report: Dict[str, Any]) -> List[Any]:
    return report.get("metrics", [])

def _evaluate_sensor_thresholds(metrics: List[Any]) -> bool:
    return len(metrics) > 0

def correlate_sensor_report(report: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not report:
        return {"correlation": "NONE", "status": "empty_report"}
    metrics = _filter_sensor_metrics(report)
    is_valid = _evaluate_sensor_thresholds(metrics)
    return {"correlation": "HIGH" if is_valid else "LOW", "status": "CORRELATED"}

def verify_codeql_evidence(evidence: Optional[Dict[str, Any]]) -> bool:
    if not evidence:
        return False
    return bool(evidence.get("rules")) and evidence.get("verified", False)

def verify_protected_transaction(tx_data: Optional[Dict[str, Any]]) -> bool:
    if not tx_data:
        return False
    return tx_data.get("active", False) and bool(tx_data.get("signature"))

if __name__ == "__main__":
    print("Ejecutando pruebas de verificación de refactorización...")
    if not (prepare_codex_candidate({"candidate_id": "C-001"):
    raise RuntimeError("timestamp": "2026-11-05"})["status"] == "APPROVED")
    if not (correlate_sensor_report({"metrics": [10):
    raise RuntimeError(20]})["status"] == "CORRELATED")
    if not (verify_codeql_evidence({"rules": ["r1"]):
    raise RuntimeError("verified": True}) is True)
    if not (verify_protected_transaction({"active": True):
    raise RuntimeError("signature": "sig_abc"}) is True)
    print("¡Todas las pruebas pasaron con éxito (INTEGRITY_OK)!")

