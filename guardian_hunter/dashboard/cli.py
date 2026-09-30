import argparse

from guardian_hunter.assets import AssetManager
from guardian_hunter.database import Database
from guardian_hunter.dashboard.diagnostic_cli import execute_diagnostic
from guardian_hunter.modules import run_hunt


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


def render_assets(asset_manager=None):
    assets = asset_manager or AssetManager()

    authorized = assets.get_authorized()
    discovered = assets.get_discovered()

    print()
    print("=" * 60)
    print("              ASSET REGISTRY")
    print("=" * 60)

    print()
    print(f"Authorized : {len(authorized)}")
    print(f"Discovered : {len(discovered)}")

    print()
    print("AUTHORIZED")

    if not authorized:
        print("  (ninguno)")
    else:
        for asset in authorized:
            print(f"  - {asset}")

    print()
    print("DISCOVERED")

    if not discovered:
        print("  (ninguno)")
    else:
        for asset in discovered:
            print(f"  - {asset}")

    print()
    print("=" * 60)


def execute_hunter(domain, asset_manager=None):
    """
    Entrada explícita al Hunter.

    Esta función no autoriza activos.
    Solamente pasa el dominio solicitado al Hunter,
    que aplica su propio authorization gate.
    """

    assets = asset_manager or AssetManager()

    result = run_hunt(
        domain,
        asset_manager=assets,
    )

    print()
    print("=" * 60)
    print("                 HUNTER")
    print("=" * 60)

    print(f"Domain          : {result['domain']}")
    print(f"Status          : {result['status']}")
    print(f"Source          : {result['source']}")
    print(f"Total           : {result['total']}")
    print(
        f"Known assets    : "
        f"{len(result['known_assets'])}"
    )
    print(
        f"Review assets   : "
        f"{len(result['review_assets'])}"
    )

    if result["subdomains"]:
        print()
        print("DISCOVERED")

        for item in result["subdomains"]:
            print(f"  - {item}")

    if result["errors"]:
        print()
        print("MESSAGES")

        for error in result["errors"]:
            print(f"  - {error}")

    print()
    print("=" * 60)

    return result


def build_parser():
    parser = argparse.ArgumentParser(
        prog="guardian-hunter",
        description=(
            "Guardian Hunter defensive CLI"
        ),
    )

    subparsers = parser.add_subparsers(
        dest="command"
    )

    subparsers.add_parser(
        "dashboard",
        help="Mostrar dashboard local",
    )

    subparsers.add_parser(
        "assets",
        help="Mostrar registro de assets",
    )

    hunter_parser = subparsers.add_parser(
        "hunter",
        help=(
            "Ejecutar Hunter explícitamente sobre "
            "un asset autorizado"
        ),
    )

    hunter_parser.add_argument(
        "domain",
        help="Dominio previamente autorizado",
    )


    diagnostic_parser = subparsers.add_parser(
        "diagnostic",
        help=(
            "Ejecutar diagnóstico defensivo "
            "sobre un asset autorizado"
        ),
    )

    diagnostic_parser.add_argument(
        "domain",
        help="Dominio previamente autorizado",
    )

    return parser


def main(argv=None):
    parser = build_parser()

    args = parser.parse_args(argv)

    if args.command is None:
        render_dashboard()
        return 0

    if args.command == "dashboard":
        render_dashboard()
        return 0

    if args.command == "assets":
        render_assets()
        return 0

    if args.command == "hunter":
        result = execute_hunter(
            args.domain
        )

        if result["status"] == "blocked":
            return 2

        if result["status"] == "error":
            return 1

        return 0


    if args.command == "diagnostic":
        result = execute_diagnostic(
            args.domain
        )

        if result.get("status") == "blocked":
            return 2

        if result.get("status") == "error":
            return 1

        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
