from guardian_hunter.database import Database


def render_dashboard(database=None):
    own_database = database is None

    db = database or Database()

    counts = db.counts()

    findings = db.recent_findings(
        limit=8
    )

    print()
    print("=" * 60)
    print("              GUARDIAN HUNTER")
    print("                 DASHBOARD")
    print("=" * 60)

    print()
    print(
        f"Executions     : {counts['executions']}"
    )
    print(
        f"Assets         : {counts['assets']}"
    )
    print(
        f"Findings       : {counts['findings']}"
    )
    print(
        f"Technologies   : {counts['technologies']}"
    )
    print(
        f"Alerts         : {counts['alerts']}"
    )

    print()
    print("-" * 60)
    print("RECENT FINDINGS")
    print("-" * 60)

    if not findings:
        print("No hay findings registrados.")

    else:
        for item in findings:
            print(
                f"[{item.get('severity', 'unknown').upper():10}] "
                f"{item.get('title', 'Unnamed')}"
            )

    print()
    print("=" * 60)

    if own_database:
        db.close()


def main():
    render_dashboard()


if __name__ == "__main__":
    main()
