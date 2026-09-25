import socket


SAFE_PORTS = {
    22: "ssh",
    53: "dns",
    80: "http",
    443: "https",
    8080: "http-alt",
    8443: "https-alt",
}


def assess_services(hostname, ports=None, timeout=1.0):
    selected_ports = ports or SAFE_PORTS.keys()
    results = []

    for port in selected_ports:
        if port not in SAFE_PORTS:
            continue

        status = "closed"

        try:
            with socket.create_connection(
                (hostname, port),
                timeout=timeout,
            ):
                status = "open"

        except (OSError, TimeoutError):
            status = "closed"

        results.append({
            "port": port,
            "service": SAFE_PORTS[port],
            "status": status,
        })

    return {
        "hostname": hostname,
        "services": results,
        "error": None,
    }
