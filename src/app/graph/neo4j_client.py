from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

try:
    from neo4j import GraphDatabase
except ImportError:  # pragma: no cover - defensive for optional local installs
    GraphDatabase = None  # type: ignore[assignment]


TRUE_VALUES = {"1", "true", "yes", "y", "on"}


@dataclass(frozen=True)
class Neo4jSettings:
    uri: str
    username: str
    password: str
    database: str
    enabled: bool

    def safe_public_dict(self) -> dict[str, Any]:
        return {
            "uri": self.uri,
            "username": self.username,
            "database": self.database,
            "enabled": self.enabled,
            "password_configured": bool(self.password),
        }


def get_neo4j_settings() -> Neo4jSettings:
    return Neo4jSettings(
        uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        username=os.getenv("NEO4J_USERNAME", "neo4j"),
        password=os.getenv("NEO4J_PASSWORD", "password"),
        database=os.getenv("NEO4J_DATABASE", "neo4j"),
        enabled=os.getenv("NEO4J_ENABLED", "false").strip().lower() in TRUE_VALUES,
    )


def check_neo4j_connection(settings: Neo4jSettings | None = None) -> dict[str, Any]:
    current_settings = settings or get_neo4j_settings()

    if GraphDatabase is None:
        return {
            "ok": False,
            "status": "driver_missing",
            "reason": "neo4j Python driver is not installed.",
            "settings": current_settings.safe_public_dict(),
        }

    try:
        driver = GraphDatabase.driver(
            current_settings.uri,
            auth=(current_settings.username, current_settings.password),
        )

        try:
            with driver.session(database=current_settings.database) as session:
                record = session.run("RETURN 1 AS ok").single()
                ok = bool(record and record.get("ok") == 1)

            return {
                "ok": ok,
                "status": "connected" if ok else "unexpected_response",
                "reason": None if ok else "Neo4j returned an unexpected health-check result.",
                "settings": current_settings.safe_public_dict(),
            }
        finally:
            driver.close()

    except Exception as exc:  # pragma: no cover - depends on local Neo4j runtime
        return {
            "ok": False,
            "status": "connection_failed",
            "reason": exc.__class__.__name__,
            "detail": str(exc),
            "settings": current_settings.safe_public_dict(),
        }


def skipped_neo4j_connection_check() -> dict[str, Any]:
    settings = get_neo4j_settings()

    return {
        "ok": None,
        "status": "skipped",
        "reason": "Set check_connection=true to verify a live Neo4j connection.",
        "settings": settings.safe_public_dict(),
    }
