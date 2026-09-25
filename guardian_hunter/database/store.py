import json
import sqlite3
from pathlib import Path

from guardian_hunter.config.settings import DATA_DIR


DEFAULT_DB = DATA_DIR / "guardian_hunter.db"


class Database:
    def __init__(self, path=None):
        self.path = Path(path or DEFAULT_DB)
        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.connection = sqlite3.connect(
            str(self.path)
        )

        self.connection.row_factory = (
            sqlite3.Row
        )

        self.initialize()

    def initialize(self):
        cursor = self.connection.cursor()

        cursor.executescript(
            """
            CREATE TABLE IF NOT EXISTS executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                target TEXT,
                status TEXT NOT NULL,
                summary TEXT
            );

            CREATE TABLE IF NOT EXISTS assets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                status TEXT NOT NULL,
                first_seen TEXT,
                last_seen TEXT
            );

            CREATE TABLE IF NOT EXISTS findings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                execution_id INTEGER,
                fingerprint TEXT,
                category TEXT,
                title TEXT,
                severity TEXT,
                score INTEGER,
                confidence REAL,
                evidence TEXT,
                recommendation TEXT,
                first_seen TEXT,
                last_seen TEXT,
                status TEXT,
                FOREIGN KEY(execution_id)
                    REFERENCES executions(id)
            );

            CREATE TABLE IF NOT EXISTS technologies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                version TEXT,
                source TEXT,
                first_seen TEXT,
                last_seen TEXT,
                UNIQUE(name, version)
            );

            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                execution_id INTEGER,
                timestamp TEXT,
                severity TEXT,
                title TEXT,
                message TEXT,
                source TEXT
            );
            """
        )

        self.connection.commit()

    def add_execution(
        self,
        timestamp,
        target,
        status="completed",
        summary=None,
    ):
        cursor = self.connection.cursor()

        cursor.execute(
            """
            INSERT INTO executions
            (timestamp, target, status, summary)
            VALUES (?, ?, ?, ?)
            """,
            (
                timestamp,
                target,
                status,
                json.dumps(
                    summary or {},
                    ensure_ascii=False,
                ),
            ),
        )

        self.connection.commit()

        return cursor.lastrowid

    def add_asset(
        self,
        name,
        status,
        timestamp,
    ):
        cursor = self.connection.cursor()

        cursor.execute(
            """
            INSERT INTO assets
            (name, status, first_seen, last_seen)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(name)
            DO UPDATE SET
                status=excluded.status,
                last_seen=excluded.last_seen
            """,
            (
                name,
                status,
                timestamp,
                timestamp,
            ),
        )

        self.connection.commit()

    def add_finding(
        self,
        execution_id,
        finding,
        fingerprint,
        timestamp,
        status="open",
    ):
        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT id
            FROM findings
            WHERE fingerprint = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (fingerprint,),
        )

        previous = cursor.fetchone()

        first_seen = timestamp

        if previous:
            cursor.execute(
                """
                SELECT first_seen
                FROM findings
                WHERE id = ?
                """,
                (previous["id"],),
            )

            row = cursor.fetchone()

            if row and row["first_seen"]:
                first_seen = row["first_seen"]

        cursor.execute(
            """
            INSERT INTO findings (
                execution_id,
                fingerprint,
                category,
                title,
                severity,
                score,
                confidence,
                evidence,
                recommendation,
                first_seen,
                last_seen,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                execution_id,
                fingerprint,
                finding.get("category"),
                finding.get("title"),
                finding.get("severity"),
                int(finding.get("score", 0)),
                float(finding.get("confidence", 1.0)),
                finding.get("evidence", ""),
                finding.get(
                    "recommendation",
                    "",
                ),
                first_seen,
                timestamp,
                status,
            ),
        )

        self.connection.commit()

        return cursor.lastrowid

    def add_technology(
        self,
        name,
        version=None,
        source="local",
        timestamp=None,
    ):
        cursor = self.connection.cursor()

        cursor.execute(
            """
            INSERT INTO technologies (
                name,
                version,
                source,
                first_seen,
                last_seen
            )
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(name, version)
            DO UPDATE SET
                source=excluded.source,
                last_seen=excluded.last_seen
            """,
            (
                name,
                version,
                source,
                timestamp,
                timestamp,
            ),
        )

        self.connection.commit()

    def add_alert(
        self,
        execution_id,
        timestamp,
        alert,
    ):
        cursor = self.connection.cursor()

        cursor.execute(
            """
            INSERT INTO alerts (
                execution_id,
                timestamp,
                severity,
                title,
                message,
                source
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                execution_id,
                timestamp,
                alert.get("severity"),
                alert.get("title"),
                alert.get("message"),
                alert.get("source"),
            ),
        )

        self.connection.commit()

    def counts(self):
        cursor = self.connection.cursor()

        result = {}

        for table in (
            "executions",
            "assets",
            "findings",
            "technologies",
            "alerts",
        ):
            cursor.execute(
                f"SELECT COUNT(*) AS total FROM {table}"
            )

            result[table] = cursor.fetchone()["total"]

        return result

    def recent_findings(self, limit=10):
        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM findings
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        )

        return [
            dict(row)
            for row in cursor.fetchall()
        ]

    def close(self):
        self.connection.close()
