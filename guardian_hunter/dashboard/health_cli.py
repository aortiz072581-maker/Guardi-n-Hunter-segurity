from guardian_hunter.integration.health_recovery import run_health_recovery

def main():
    r = run_health_recovery()

    print("=== GUARDIAN HUNTER HEALTH & RECOVERY ===")
    print("STATUS:", r["status"])

    for c in r["checks"]:
        print(("[OK] " if c["ok"] else "[REVIEW] ") + c["name"])
        if c["solution"]:
            print("  Solution:", c["solution"])

    print()
    print("Hardware sensor: INTEGRATED")
    print("Network sensor: INTEGRATED")
    print("Integrity sensor: INTEGRATED")
    print("Tamper sensor: INTEGRATED")
    print("Diagnosis correlation: INTEGRATED")
    print("READ_ONLY:", r["read_only"])
    print("DRY_RUN:", r["dry_run"])
    print("EXECUTION_ALLOWED:", r["execution_allowed"])
    print("RESPONSE_LOCKED:", r["response_locked"])

if __name__ == "__main__":
    main()
