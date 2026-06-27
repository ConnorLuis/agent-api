import sqlite3
from pathlib import Path

from langgraph.checkpoint.sqlite import SqliteSaver

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"
CHECKPOINT_DB_PATH = DATA_DIR / "checkpoints.sqlite"


def build_sqlite_checkpointer() -> SqliteSaver:
    """
    Build a SQLite checkpointer for LangGraph short-term memory.

    The SQLite file is stored at:
        data/checkpoints.sqlite

    This saver is suitable for local demo and small synchronous projects.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(
        CHECKPOINT_DB_PATH,
        check_same_thread=False,
    )

    return SqliteSaver(conn)