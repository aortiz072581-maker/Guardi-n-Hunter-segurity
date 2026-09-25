import csv
import json
import re

from guardian_hunter.config.settings import DATA_DIR


REPORT_DIR = DATA_DIR / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)


def _safe_name(name):
    value = str(name)
    value = re.sub(
        r"[^a-zA-Z0-9_.-]",
        "_",
        value,
    )

    if not value:
        value = "report"

    return value


def export_json(data, name):
    path = REPORT_DIR / (
        _safe_name(name) + ".json"
    )

    with path.open(
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(
            data,
            handle,
            indent=2,
            ensure_ascii=False,
        )

    return str(path)


def export_csv(data, name):
    path = REPORT_DIR / (
        _safe_name(name) + ".csv"
    )

    if isinstance(data, dict):
        rows = data.get("findings", [])

        if not isinstance(rows, list):
            rows = [data]

    elif isinstance(data, list):
        rows = data

    else:
        rows = [{"value": data}]

    rows = [
        row
        for row in rows
        if isinstance(row, dict)
    ]

    fields = set()

    for row in rows:
        fields.update(row.keys())

    fields = sorted(fields)

    with path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:

        writer = csv.DictWriter(
            handle,
            fieldnames=fields or ["value"],
        )

        writer.writeheader()

        for row in rows:
            writer.writerow(row)

    return str(path)


def export_pdf(data, name):
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
    except ImportError:
        return None

    path = REPORT_DIR / (
        _safe_name(name) + ".pdf"
    )

    document = canvas.Canvas(
        str(path),
        pagesize=letter,
    )

    width, height = letter
    y = height - 40

    document.setFont(
        "Helvetica",
        9,
    )

    text = json.dumps(
        data,
        indent=2,
        ensure_ascii=False,
        default=str,
    )

    for line in text.splitlines():
        if y < 40:
            document.showPage()
            document.setFont(
                "Helvetica",
                9,
            )
            y = height - 40

        document.drawString(
            40,
            y,
            line[:110],
        )

        y -= 12

    document.save()

    return str(path)


def export_bundle(data, name):
    return {
        "json": export_json(
            data,
            name,
        ),
        "csv": export_csv(
            data,
            name,
        ),
        "pdf": export_pdf(
            data,
            name,
        ),
    }
