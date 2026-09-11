from __future__ import annotations

import sqlite3
from pathlib import Path

from langgraph.checkpoint.sqlite import SqliteSaver


PROJECT_ROOT = Path(__file__).resolve().parents[4]
ERP_DIAGNOSIS_CHECKPOINT_DB_PATH = (
    PROJECT_ROOT / "data" / "erp_diagnosis_checkpoints.sqlite"
)


def build_erp_diagnosis_checkpointer(
    db_path: Path | str = ERP_DIAGNOSIS_CHECKPOINT_DB_PATH,
) -> SqliteSaver:
    """Build a dedicated SQLite checkpointer for the ERP diagnosis workflow."""
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, check_same_thread=False)
    return SqliteSaver(connection)
