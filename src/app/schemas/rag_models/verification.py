from typing import Any

from pydantic import BaseModel, Field


class RagAnswerVerifyDebugRequest(BaseModel):
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


class RagAnswerVerificationResult(BaseModel):
    verification_mode: str
    answer_supported: bool
    verification_pass: bool
    confidence: str
    answer_has_citation: bool
    citation_coverage_pass: bool
    cited_in_answer: list[str]
    unsupported_citations: list[str]
    grounding_terms: list[str]
    matched_grounding_terms: list[str]
    risk_flags: list[str]


class RagAnswerVerifyDebugResponse(BaseModel):
    query: str
    rewritten_query: str
    retrieval_needed: bool
    relevance_score: float
    citations: list[str] = Field(default_factory=list)
    retrieval_results: list[dict[str, Any]] = Field(default_factory=list)
    final_answer: str
    steps: list[str] = Field(default_factory=list)

    # Backward-compatible nested Day28 verification payload.
    verification: dict[str, Any] = Field(default_factory=dict)

    # Flattened verification fields for easier Day49 GraphRAG trace / response assertions.
    verification_mode: str
    answer_supported: bool
    verification_pass: bool
    confidence: str
    answer_has_citation: bool
    citation_coverage_pass: bool
    cited_in_answer: list[str] = Field(default_factory=list)
    unsupported_citations: list[str] = Field(default_factory=list)
    grounding_terms: list[str] = Field(default_factory=list)
    matched_grounding_terms: list[str] = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list)

    trace_id: str | None = None

    retrieval_backend: str = "hybrid"
    retrieval_metadata: dict[str, Any] = Field(default_factory=dict)
    graph_vector_contribution: dict[str, Any] = Field(default_factory=dict)
    graph_fusion_verification: dict[str, Any] = Field(default_factory=dict)