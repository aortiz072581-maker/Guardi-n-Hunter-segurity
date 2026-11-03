
"""Regla: deriva de red - gateway, MAC por IP, interfaz nueva"""
def detect_network_drift(baseline: dict, current: dict):
    alerts = []
    if baseline.get("gateway") != current.get("gateway"):
        alerts.append({"type":"GATEWAY_DRIFT","baseline":baseline.get("gateway"),"current":current.get("gateway")})
    if set(current.get("interfaces",[])) - set(baseline.get("interfaces",[])):
        alerts.append({"type":"NEW_INTERFACE"})
    return alerts
