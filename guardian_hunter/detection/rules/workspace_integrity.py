
def detect_workspace_drift(baseline_hashes: dict, current_hashes: dict):
    return [k for k in baseline_hashes if baseline_hashes[k]!=current_hashes.get(k)]
