DEFAULT_RETRIEVAL_BACKEND = "hybrid"


def normalize_retrieval_backend(
    retrieval_backend: str | None,
) -> str:
    normalized = (retrieval_backend or DEFAULT_RETRIEVAL_BACKEND).strip().lower()

    if normalized in {"default", "deterministic", "hybrid"}:
        return "hybrid"

    if normalized in {"chroma", "chromadb", "vector_db", "vector-db"}:
        return "chroma"

    if normalized in {
        "chroma_rerank",
        "chroma-rerank",
        "chromadb_rerank",
        "vector_db_rerank",
        "vector-db-rerank",
    }:
        return "chroma_rerank"

    if normalized in {
        "graph_fusion",
        "graph-fusion",
        "graphrag",
        "graph_rag",
        "graph-rag",
    }:
        return "graph_fusion"

    raise ValueError(
        f"Unsupported retrieval backend: {retrieval_backend}"
    )