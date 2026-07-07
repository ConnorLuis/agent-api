from typing import Any

from pydantic import BaseModel, Field


class RagAgenticDebugResult(BaseModel):
    rank: int
    chunk_id: str
    source: str
    index: int
    hybrid_score: float
    keyword_score: float
    vector_score: float
    content: str
    preview: str
    matched_terms: list[str]
    content_length: int

    # Chroma-compatible optional fields.
    score: float | None = None
    distance: float | None = None
    retrieval_backend: str | None = None

    # Day35 reranker-compatible optional fields.
    original_rank: int | None = None
    original_score: float | None = None
    rerank_score: float | None = None
    rerank_keyword_score: float | None = None
    rerank_matched_terms: list[str] = Field(default_factory=list)

    # Day47 GraphRAG fusion-compatible optional fields.
    fusion_score: float | None = None
    graph_score: float | None = None
    retrieval_sources: list[str] = Field(default_factory=list)
    matched_entities: list[dict[str, Any]] = Field(default_factory=list)
    mentions: list[dict[str, Any]] = Field(default_factory=list)
    graph_metadata: dict[str, Any] = Field(default_factory=dict)
    vector_metadata: dict[str, Any] = Field(default_factory=dict)


class RagAgenticDebugResponse(BaseModel):
    query: str
    rewritten_query: str
    retrieval_needed: bool
    relevance_score: float
    citations: list[str]
    retrieval_results: list[RagAgenticDebugResult]
    final_answer: str
    steps: list[str]
    trace_id: str | None = None
    retrieval_backend: str = "hybrid"
    retrieval_metadata: dict = Field(default_factory=dict)
    graph_vector_contribution: dict[str, Any] = Field(default_factory=dict)


class RagAgenticDebugRequest(BaseModel):
    query: str
    top_k: int = 3
    source_filter: str | None = None
    max_chars: int = 500
    embedding_dim: int = 64
    keyword_weight: float = 0.6
    vector_weight: float = 0.4
    retrieval_backend: str = "hybrid"
    embedding_provider: str = "deterministic"
    embedding_model: str | None = None
    rebuild_index: bool = True
    graph_dry_run: bool = True
    fusion_graph_weight: float = 0.5
    fusion_vector_weight: float = 0.5
    graph_chunk_limit: int = 5
    related_entity_limit: int = 10