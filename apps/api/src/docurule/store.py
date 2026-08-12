import sqlite3
from pathlib import Path
from threading import Lock

from .models import CaseRecord


class CaseStore:
    """Tiny SQLite repository; the JSON boundary keeps the MVP easy to migrate."""

    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path
        self._lock = Lock()
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path, timeout=10)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS cases (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    payload TEXT NOT NULL
                )
                """
            )

    def save(self, case: CaseRecord) -> CaseRecord:
        payload = case.model_dump_json()
        with self._lock, self._connect() as connection:
            connection.execute(
                """
                INSERT INTO cases (id, name, status, created_at, updated_at, payload)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    status = excluded.status,
                    updated_at = excluded.updated_at,
                    payload = excluded.payload
                """,
                (
                    case.id,
                    case.name,
                    case.status.value,
                    case.created_at.isoformat(),
                    case.updated_at.isoformat(),
                    payload,
                ),
            )
        return case

    def get(self, case_id: str) -> CaseRecord | None:
        with self._connect() as connection:
            row = connection.execute("SELECT payload FROM cases WHERE id = ?", (case_id,)).fetchone()
        return CaseRecord.model_validate_json(row["payload"]) if row else None

    def list(self) -> list[CaseRecord]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT payload FROM cases ORDER BY created_at DESC"
            ).fetchall()
        return [CaseRecord.model_validate_json(row["payload"]) for row in rows]

    def delete_all(self) -> None:
        with self._lock, self._connect() as connection:
            connection.execute("DELETE FROM cases")
