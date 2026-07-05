import re
import shutil
import hashlib
from pathlib import Path
from typing import Any

import chromadb

from src.app.rag.chunking import DEFAULT_MAX_CHARS, load_knowledge_chunks
from src.app.rag.embedding_provider import (
    DEFAULT_EMBEDDING_PROVIDER,
    get_embedding_provider,
)
from src.app.rag.vector_index import DEFAULT_EMBEDDING_DIM

DEFAULT_CHROMA_PERSIST_DIR = Path("data/chroma")
DEFAULT_CHROMA_COLLECTION_PREFIX = "agent_api_rag"


def _safe_collection_token(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9_]+", "_", value.strip())
    normalized = re.sub(r"_+", "_", normalized).strip("_").lower()

    return normalized or "default"


def build_chroma_collection_name(
    source_filter: str | None,
    embedding_provider: str,
    embedding_model: str,
    embedding_dim: int,
) -> str:
    safe_dim = max(embedding_dim, 8)

    source_token = _safe_collection_token(source_filter or "all")[:16]
    provider_token = _safe_collection_token(embedding_provider)[:12]
    dim_token = f"d{safe_dim}"

    raw_identity = (
        f"source_filter={source_filter or '__all__'}|"
        f"embedding_provider={embedding_provider}|"
        f"embedding_model={embedding_model}|"
        f"embedding_dim={safe_dim}"
    )

    digest = hashlib.sha1(
        raw_identity.encode("utf-8")
    ).hexdigest()[:8]

    name = (
        f"{DEFAULT_CHROMA_COLLECTION_PREFIX}_"
        f"{source_token}_"
        f"{provider_token}_"
        f"{dim_token}_"
        f"{digest}"
    )

    return name[:63].strip("_")


def _get_chroma_client(
    persist_dir: Path | str = DEFAULT_CHROMA_PERSIST_DIR,
) -> chromadb.PersistentClient:
    path = Path(persist_dir)
    path.mkdir(parents=True, exist_ok=True)

    return chromadb.PersistentClient(path=str(path))


def _reset_collection_if_needed(
    client: chromadb.PersistentClient,
    collection_name: str,
    rebuild_index: bool,
) -> None:
    if not rebuild_index:
        return

    try:
        client.delete_collection(name=collection_name)
    except Exception:
        # Collection may not exist yet.
        return


def build_chroma_index(
    source_filter: str | None = None,
    max_chars: int = DEFAULT_MAX_CHARS,
    embedding_dim: int = DEFAULT_EMBEDDING_DIM,
    embedding_provider: str = DEFAULT_EMBEDDING_PROVIDER,
    embedding_model: str | None = None,
    rebuild_index: bool = True,
    persist_dir: Path | str = DEFAULT_CHROMA_PERSIST_DIR,
) -> dict[str, Any]:
    safe_dim = max(embedding_dim, 8)

    provider_instance = get_embedding_provider(
        provider=embedding_provider,
        embedding_model=embedding_model,
    )

    collection_name = build_chroma_collection_name(
        source_filter=source_filter,
        embedding_provider=provider_instance.provider,
        embedding_model=provider_instance.model,
        embedding_dim=safe_dim,
    )

    client = _get_chroma_client(persist_dir=persist_dir)

    _reset_collection_if_needed(
        client=client,
        collection_name=collection_name,
        rebuild_index=rebuild_index,
    )

    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=None,
        metadata={
            "source_filter": source_filter or "__all__",
            "embedding_provider": provider_instance.provider,
            "embedding_model": provider_instance.model,
            "embedding_dim": safe_dim,
        },
    )

    chunks = load_knowledge_chunks(
        source_filter=source_filter,
        max_chars=max_chars,
    )

    ids: list[str] = []
    documents: list[str] = []
    metadatas: list[dict[str, Any]] = []
    embeddings: list[list[float]] = []

    for chunk in chunks:
        ids.append(str(chunk["chunk_id"]))
        documents.append(str(chunk["content"]))
        metadatas.append(
            {
                "chunk_id": str(chunk["chunk_id"]),
                "source": str(chunk["source"]),
                "chunk_index": int(chunk["index"]),
                "preview": str(chunk["preview"]),
                "content_length": int(chunk["content_length"]),
                "source_filter": source_filter or "__all__",
                "embedding_provider": provider_instance.provider,
                "embedding_model": provider_instance.model,
                "embedding_dim": safe_dim,
            }
        )
        embeddings.append(
            provider_instance.embed_text(
                text=str(chunk["content"]),
                embedding_dim=safe_dim,
            )
        )

    if ids:
        collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
        )

    stored_count = collection.count()

    return {
        "collection_name": collection_name,
        "persist_dir": str(persist_dir),
        "source_filter": source_filter,
        "max_chars": max_chars,
        "embedding_dim": safe_dim,
        "embedding_provider": provider_instance.provider,
        "embedding_model": provider_instance.model,
        "rebuild_index": rebuild_index,
        "loaded_chunks": len(chunks),
        "upserted_count": len(ids),
        "stored_count": int(stored_count),
    }


def query_chroma_store(
    query: str,
    top_k: int = 3,
    source_filter: str | None = None,
    max_chars: int = DEFAULT_MAX_CHARS,
    embedding_dim: int = DEFAULT_EMBEDDING_DIM,
    embedding_provider: str = DEFAULT_EMBEDDING_PROVIDER,
    embedding_model: str | None = None,
    persist_dir: Path | str = DEFAULT_CHROMA_PERSIST_DIR,
) -> dict[str, Any]:
    safe_top_k = max(top_k, 1)
    safe_dim = max(embedding_dim, 8)

    provider_instance = get_embedding_provider(
        provider=embedding_provider,
        embedding_model=embedding_model,
    )

    collection_name = build_chroma_collection_name(
        source_filter=source_filter,
        embedding_provider=provider_instance.provider,
        embedding_model=provider_instance.model,
        embedding_dim=safe_dim,
    )

    client = _get_chroma_client(persist_dir=persist_dir)
    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=None,
    )

    query_embedding = provider_instance.embed_text(
        text=query,
        embedding_dim=safe_dim,
    )

    raw_result = collection.query(
        query_embeddings=[query_embedding],
        n_results=safe_top_k,
        include=["documents", "metadatas", "distances"],
    )

    ids_batch = raw_result.get("ids") or [[]]
    documents_batch = raw_result.get("documents") or [[]]
    metadatas_batch = raw_result.get("metadatas") or [[]]
    distances_batch = raw_result.get("distances") or [[]]

    ids = ids_batch[0] if ids_batch else []
    documents = documents_batch[0] if documents_batch else []
    metadatas = metadatas_batch[0] if metadatas_batch else []
    distances = distances_batch[0] if distances_batch else []

    results = []

    for rank, item_id in enumerate(ids, start=1):
        metadata = metadatas[rank - 1] or {}
        document = documents[rank - 1] or ""
        distance = float(distances[rank - 1]) if rank - 1 < len(distances) else 0.0

        results.append(
            {
                "rank": rank,
                "chunk_id": str(metadata.get("chunk_id") or item_id),
                "source": str(metadata.get("source") or ""),
                "index": int(metadata.get("chunk_index") or 0),
                "distance": round(distance, 6),
                "score": round(1.0 / (1.0 + distance), 6),
                "content": str(document),
                "preview": str(metadata.get("preview") or str(document)[:200]),
                "content_length": int(metadata.get("content_length") or len(str(document))),
            }
        )

    stored_count = collection.count()

    return {
        "query": query,
        "top_k": safe_top_k,
        "source_filter": source_filter,
        "max_chars": max_chars,
        "embedding_dim": safe_dim,
        "embedding_provider": provider_instance.provider,
        "embedding_model": provider_instance.model,
        "collection_name": collection_name,
        "persist_dir": str(persist_dir),
        "total_indexed_chunks": int(stored_count),
        "results": results,
    }


def debug_chroma_search(
    query: str,
    top_k: int = 3,
    source_filter: str | None = None,
    max_chars: int = DEFAULT_MAX_CHARS,
    embedding_dim: int = DEFAULT_EMBEDDING_DIM,
    embedding_provider: str = DEFAULT_EMBEDDING_PROVIDER,
    embedding_model: str | None = None,
    rebuild_index: bool = True,
    persist_dir: Path | str = DEFAULT_CHROMA_PERSIST_DIR,
) -> dict[str, Any]:
    index_stats = build_chroma_index(
        source_filter=source_filter,
        max_chars=max_chars,
        embedding_dim=embedding_dim,
        embedding_provider=embedding_provider,
        embedding_model=embedding_model,
        rebuild_index=rebuild_index,
        persist_dir=persist_dir,
    )

    search_result = query_chroma_store(
        query=query,
        top_k=top_k,
        source_filter=source_filter,
        max_chars=max_chars,
        embedding_dim=embedding_dim,
        embedding_provider=embedding_provider,
        embedding_model=embedding_model,
        persist_dir=persist_dir,
    )

    return {
        **search_result,
        "rebuild_index": rebuild_index,
        "index_stats": index_stats,
    }


def reset_chroma_persist_dir(
    persist_dir: Path | str = DEFAULT_CHROMA_PERSIST_DIR,
) -> None:
    path = Path(persist_dir)

    if path.exists():
        shutil.rmtree(path)