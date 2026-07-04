import json
import sqlite3
import time
from pathlib import Path
from typing import Any

DEFAULT_TRACE_DB_PATH = Path("data/observablity.sqlite")


def _connect(db_path: Path | str = DEFAULT_TRACE_DB_PATH) -> sqlite3.Connection:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row

    return connection


def init_trace_store(db_path: Path | str = DEFAULT_TRACE_DB_PATH) -> None:
    with _connect(db_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS trace_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trace_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                created_at_ms INTEGER NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_trace_events_trace_id
            ON trace_events(trace_id)
            """
        )
        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_trace_events_created_at
            ON trace_events(created_at_ms)
            """
        )


def record_trace_event(trace_id: str, event_type: str, payload: dict[str, Any] |  None =  None, db_path: Path | str = DEFAULT_TRACE_DB_PATH) -> dict[str, Any]:
    init_trace_store(db_path=db_path)

    created_at_ms = int(time.time() * 1000)
    payload_json = json.dumps(payload or {}, ensure_ascii=False, sort_keys=True, default=str)

    with _connect(db_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO trace_events (
                trace_id,
                event_type,
                payload_json,
                created_at_ms
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                trace_id,
                event_type,
                payload_json,
                created_at_ms,
            ),
        )

        event_id = int(cursor.lastrowid)

    return {
        "event_id": event_id,
        "trace_id": trace_id,
        "event_type": event_type,
        "payload": payload or {},
        "created_at_ms": created_at_ms,
    }


def get_trace_events(trace_id: str, db_path: Path | str = DEFAULT_TRACE_DB_PATH) -> list[dict[str, Any]]:
    init_trace_store(db_path=db_path)

    with _connect(db_path) as connection:
        rows = connection.execute(
            """
            SELECT
                id,
                trace_id,
                event_type,
                payload_json,
                created_at_ms
            FROM trace_events
            WHERE trace_id = ?
            ORDER BY id ASC
            """,
            (trace_id,),
        ).fetchall()

    return [
        {
            "event_id": int(row["id"]),
            "trace_id": str(row["trace_id"]),
            "event_type": str(row["event_type"]),
            "payload": json.loads(str(row["payload_json"])),
            "created_at_ms": int(row["created_at_ms"]),
        }
        for row in rows
    ]


def list_recent_trace_ids(limit: int = 20, db_path: Path | str = DEFAULT_TRACE_DB_PATH) -> list[dict[str, Any]]:
    init_trace_store(db_path=db_path)

    safe_limit = max(1, min(limit, 100))
    with _connect(db_path) as connection:
        rows = connection.execute(
            """
            SELECT
                trace_id,
                COUNT(*) AS event_count,
                MAX(created_at_ms) AS last_event_at_ms
            FROM trace_events
            GROUP BY trace_id
            ORDER BY last_event_at_ms DESC
            LIMIT ?
            """,
            (safe_limit,),
        ).fetchall()

    return [
        {
            "trace_id": str(row["trace_id"]),
            "event_count": int(row["event_count"]),
            "last_event_at_ms": int(row["last_event_at_ms"]),
        }
        for row in rows
    ]
