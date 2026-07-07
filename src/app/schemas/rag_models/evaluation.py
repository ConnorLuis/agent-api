from typing import Any

from pydantic import BaseModel, Field


class RagEvalMetrics(BaseModel):
    total_cases: int
    passed_cases: int
    pass_rate: float
    retrieval_decision_accuracy: float
    expected_terms_hit_rate: float
    citation_hit_rate: float
    average_relevance_score: float


class RagEvalCaseResult(BaseModel):
    case_id: str
    query: str
    expected_retrieval_needed: bool
    actual_retrieval_needed: bool
    retrieval_decision_pass: bool
    expected_terms: list[str]
    matched_expected_terms: list[str]
    expected_terms_pass: bool
    expected_citation_keywords: list[str]
    citations: list[str]
    citation_pass: bool
    relevance_score: float
    retrieval_backend: str | None = None
    retrieval_metadata: dict = Field(default_factory=dict)
    graph_vector_contribution: dict[str, Any] = Field(default_factory=dict)
    steps: list[str] = Field(default_factory=list)
    final_answer_preview: str
    passed: bool


class RagEvalDebugRequest(BaseModel):
    eval_file: str = "eval_cases/rag_agentic_eval.jsonl"
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

class RagEvalDebugResponse(BaseModel):
    eval_file: str
    source_filter: str | None = None
    max_chars: int
    embedding_dim: int
    keyword_weight: float
    vector_weight: float
    metrics: RagEvalMetrics
    cases: list[RagEvalCaseResult]
    trace_id: str | None = None
    retrieval_backend: str = "hybrid"
    embedding_provider: str = "deterministic"
    embedding_model: str | None = None
    rebuild_index: bool = True
    graph_dry_run: bool = True
    fusion_graph_weight: float = 0.5
    fusion_vector_weight: float = 0.5
    graph_chunk_limit: int = 5
    related_entity_limit: int = 10
    graph_evaluation_metadata: dict[str, Any] = Field(default_factory=dict)


class RagBackendEvalDebugRequest(BaseModel):
    eval_file: str = "eval_cases/rag_agentic_eval.jsonl"
    backends: list[str] = Field(default_factory=lambda: ["hybrid", "chroma"])
    source_filter: str | None = None
    max_chars: int = 500
    embedding_dim: int = 64
    keyword_weight: float = 0.6
    vector_weight: float = 0.4
    embedding_provider: str = "deterministic"
    embedding_model: str | None = None
    rebuild_index: bool = True
    graph_dry_run: bool = True
    fusion_graph_weight: float = 0.5
    fusion_vector_weight: float = 0.5
    graph_chunk_limit: int = 5
    related_entity_limit: int = 10


class RagBackendEvalDebugResponse(BaseModel):
    eval_file: str
    backends: list[str]
    source_filter: str | None = None
    max_chars: int
    embedding_dim: int
    keyword_weight: float
    vector_weight: float
    embedding_provider: str
    embedding_model: str | None = None
    rebuild_index: bool
    best_backend_by_pass_rate: str
    best_backend_by_average_relevance: str
    metric_deltas: dict = Field(default_factory=dict)
    pairwise_metric_deltas: list[dict] = Field(default_factory=list)
    case_comparisons: list[dict] = Field(default_factory=list)
    comparison_summary: dict = Field(default_factory=dict)
    evaluation_report: dict[str, Any]
    results: list[RagEvalDebugResponse]
    trace_id: str | None = None
    graph_dry_run: bool = True
    fusion_graph_weight: float = 0.5
    fusion_vector_weight: float = 0.5
    graph_chunk_limit: int = 5
    related_entity_limit: int = 10
    graph_evaluation_metadata: dict[str, Any] = Field(default_factory=dict)