import json
import sqlite3
import time
from pathlib import Path
from typing import Any

from src.app.rag.chunking import DEFAULT_MAX_CHARS, load_knowledge_chunks
from src.app.rag.vector_index import DEFAULT_EMBEDDING_DIM, build_deterministic_embedding, cosine_similarity


DEFAULT_VECTOR_STORE_DB_PATH = Path("data/rag_vector_store.sqlite")


def _connect(db_path: Path | str = DEFAULT_VECTOR_STORE_DB_PATH) -> sqlite3.Connection:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row

    return  connection


def init_vector_store(db_path: Path | str = DEFAULT_VECTOR_STORE_DB_PATH) -> None:
    with _connect(db_path=db_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS rag_chunk_vectors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                index_key TEXT NOT NULL,
                chunk_id TEXT NOT NULL,
                source TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                content TEXT NOT NULL,
                preview TEXT NOT NULL,
                content_length INTEGER NOT NULL,
                embedding_dim INTEGER NOT NULL,
                embedding_json TEXT NOT NULL,
                created_at_ms INTEGER NOT NULL,
                UNIQUE(index_key, chunk_id)
            )
            """
        )
        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_rag_chunk_vectors_index_key ON rag_chunk_vectors(index_key)
            """
        )
        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_rag_chunk_vectors_index_key ON rag_chunk_vectors(chunk_id)
            """
        )


def _build_index_key(source_filter: str | None, max_chars: int, embedding_dim: int) -> str:
    normalized_source_filter = source_filter or "__all__"

    return (
        f"source_filter={normalized_source_filter}|"
        f"max_chars={max_chars}|"
        f"embedding_dim={embedding_dim}"
    )


def build_vector_store_index(
        source_filter: str | None =  None,
        max_chars: int = DEFAULT_MAX_CHARS,
        embedding_dim: int = DEFAULT_EMBEDDING_DIM,
        rebuild_index: bool = True,
        db_path: Path | str = DEFAULT_VECTOR_STORE_DB_PATH,
) -> dict[str, Any]:
    safe_dim = max(embedding_dim, 8)
    index_key = _build_index_key(source_filter=source_filter, max_chars=max_chars, embedding_dim=safe_dim)

    init_vector_store(db_path=db_path)

    chunks = load_knowledge_chunks(source_filter=source_filter, max_chars=max_chars)

    created_at_ms = int(time.time() * 1000)

    with _connect(db_path=db_path) as connection:
        if rebuild_index:
            connection.execute(
                "DELETE FROM rag_chunk_vectors WHERE index_key = ?",
                (index_key,),
            )

        inserted_count = 0

        for chunk in chunks:
            embedding = build_deterministic_embedding(text=chunk["content"], embedding_dim=safe_dim)

            connection.execute(
                """
                INSERT OR REPLACE INTO rag_chunk_vectors (
                    index_key,
                    chunk_id,
                    source,
                    chunk_index,
                    content,
                    preview,
                    content_length,
                    embedding_dim,
                    embedding_json,
                    created_at_ms
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (index_key, chunk["chunk_id"], chunk["source"], int(chunk["index"]), chunk["content"], chunk["preview"], int(chunk["content_length"]), safe_dim, json.dumps(embedding), created_at_ms),
            )
            inserted_count += 1

        stored_count = connection.execute(
            """
            SELECT COUNT(*) AS count FROM rag_chunk_vectors WHERE index_key = ?
            """,
            (index_key, ),
        ).fetchone()["count"]

    return {
        "index_key": index_key,
        "source_filter": source_filter,
        "max_chars": max_chars,
        "embedding_dim": safe_dim,
        "rebuild_index": rebuild_index,
        "loaded_chunks": len(chunks),
        "inserted_count": inserted_count,
        "stored_count": int(stored_count),
        "db_path": str(db_path),
    }


def query_vector_store(
        query: str,
        top_k: int = 3,
        source_filter: str | None = None,
        max_chars: int = DEFAULT_MAX_CHARS,
        embedding_dim: int = DEFAULT_EMBEDDING_DIM,
        db_path: Path | str = DEFAULT_VECTOR_STORE_DB_PATH,
) -> dict[str, Any]:
    safe_top_k = max(top_k, 1)
    safe_dim = max(embedding_dim, 8)
    index_key = _build_index_key(source_filter=source_filter, max_chars=max_chars, embedding_dim=safe_dim)

    init_vector_store(db_path=db_path)

    query_embedding = build_deterministic_embedding(text=query, embedding_dim=safe_dim)

    with _connect(db_path=db_path) as connection:
        rows = connection.execute(
            """
            SELECT
                chunk_id,
                source,
                chunk_index,
                content,
                preview,
                content_length,
                embedding_json
            FROM rag_chunk_vectors
            WHERE index_key = ?
            order by chunk_index ASC
            """,
            (index_key,),
        ).fetchall()

    scored_items = []

    for row in rows:
        chunk_embedding = json.loads(str(row["embedding_json"]))
        score = round(cosine_similarity(query_embedding, chunk_embedding), 6,)

        scored_items.append({
            "chunk_id": str(row["chunk_id"]),
            "source": str(row["source"]),
            "index": int(row["chunk_index"]),
            "score": score,
            "content": str(row["content"]),
            "preview": str(row["preview"]),
            "content_length": int(row["content_length"]),
        })

    scored_items.sort(
        key=lambda item: (
            item["score"],
            -item["index"],
        ),
        reverse=True,
    )

    results = []

    for rank, item in enumerate(scored_items[:safe_top_k], start=1):
        results.append({
            "rank": rank,
            **item,
        })

    return {
        "query": query,
        "top_k": safe_top_k,
        "source_filter": source_filter,
        "max_chars": max_chars,
        "embedding_dim": safe_dim,
        "index_key": index_key,
        "total_indexed_chunks": len(rows),
        "results": results,
    }


def debug_vector_store_search(query: str, top_k: int = 3, source_filter: str | None = None, max_chars: int = DEFAULT_MAX_CHARS, embedding_dim: int = DEFAULT_EMBEDDING_DIM, rebuild_index: bool = True, db_path: Path | str = DEFAULT_VECTOR_STORE_DB_PATH):
    index_stats = build_vector_store_index(source_filter=source_filter, max_chars=max_chars, embedding_dim=embedding_dim, rebuild_index=rebuild_index, db_path=db_path)

    search_result = query_vector_store(query=query, top_k=top_k, source_filter=source_filter, max_chars=max_chars, embedding_dim=embedding_dim, db_path=db_path)

    return {
        **search_result,
        "rebuild_index": rebuild_index,
        "index_stats": index_stats,
    }