from pydantic import BaseModel, Field


class RAGReaderRequest(BaseModel):
    query: str = Field(..., description="Search query")
    k: int = Field(default=3, ge=1, le=10, description="Number of results")


class RAGSearchResult(BaseModel):
    source: str
    content: str
    score: int


class RAGSearchResponse(BaseModel):
    query: str
    results: list[RAGSearchResult]
    trace_id: str | None = None


class RagSearchDebugRequest(BaseModel):
    query: str
    k: int = 3


class RagSearchDebugResult(BaseModel):
    rank: int
    source: str
    score: int
    content: str
    preview: str
    matched_terms: list[str]
    content_length: int


class RagSearchDebugResponse(BaseModel):
    query: str
    normalized_query: str
    k: int
    results: list[RagSearchDebugResult]
    trace_id: str | None = None


class RagChunksDebugRequest(BaseModel):
    source_filter: str | None = None
    max_chars: int = 500


class RagChunkInfo(BaseModel):
    chunk_id: str
    source: str
    index: int
    content: str
    preview: str
    content_length: int


class RagChunksDebugResponse(BaseModel):
    source_filter: str | None = None
    max_chars: int
    total_chunks: int
    chunks: list[RagChunkInfo]
    trace_id: str | None = None


class RagVectorSearchDebugRequest(BaseModel):
    query: str
    top_k: int = 3
    source_filter: str | None = None
    max_chars: int = 500
    embedding_dim: int = 64


class RagVectorSearchDebugResult(BaseModel):
    rank: int
    chunk_id: str
    source: str
    index: int
    score: float
    content: str
    preview: str
    matched_terms: list[str]
    content_length: int


class RagVectorSearchDebugResponse(BaseModel):
    query: str
    top_k: int
    source_filter: str | None = None
    max_chars: int
    embedding_dim: int
    total_chunks: int
    results: list[RagVectorSearchDebugResult]
    trace_id: str | None = None


class RagHybridSearchDebugRequest(BaseModel):
    query: str
    top_k: int = 3
    source_filter: str | None = None
    max_chars: int = 500
    embedding_dim: int = 64
    keyword_weight: float = 0.5
    vector_weight: float = 0.5


class RagHybridSearchDebugResult(BaseModel):
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


class RagHybridSearchDebugResponse(BaseModel):
    query: str
    top_k: int
    source_filter: str | None = None
    max_chars: int
    embedding_dim: int
    keyword_weight: float
    vector_weight: float
    total_chunks: int
    results: list[RagHybridSearchDebugResult]
    trace_id: str | None = None


class RagAgenticDebugRequest(BaseModel):
    query: str
    top_k: int = 3
    source_filter: str | None = None
    max_chars: int = 500
    embedding_dim: int = 64
    keyword_weight: float = 0.6
    vector_weight: float = 0.4


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


class RagEvalDebugRequest(BaseModel):
    eval_file: str = "eval_cases/rag_agentic_eval.jsonl"
    source_filter: str | None = "agent_basics"
    max_chars: int = 500
    embedding_dim: int = 64
    keyword_weight: float = 0.6
    vector_weight: float = 0.4


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
    steps: list[str]
    final_answer_preview: str
    passed: bool


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



class RagAnswerVerifyDebugRequest(BaseModel):
    query: str
    top_k: int = 3
    source_filter: str | None = None
    max_chars: int = 500
    embedding_dim: int = 64
    keyword_weight: float = 0.6
    vector_weight: float = 0.4


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
    citations: list[str]
    retrieval_results: list[RagAgenticDebugResult]
    final_answer: str
    steps: list[str]
    verification: RagAnswerVerificationResult
    trace_id: str | None = None


class RagVectorStoreDebugRequest(BaseModel):
    query: str
    top_k: int = 3
    source_filter: str | None = None
    max_chars: int = 500
    embedding_dim: int = 64
    rebuild_index: bool = True


class RagVectorStoreIndexStats(BaseModel):
    index_key: str
    source_filter: str | None = None
    max_chars: int
    embedding_dim: int
    rebuild_index: bool
    loaded_chunks: int
    inserted_count: int
    stored_count: int
    db_path: str


class RagVectorStoreDebugResult(BaseModel):
    rank: int
    chunk_id: str
    source: str
    index: int
    score: float
    content: str
    preview: str
    content_length: int


class RagVectorStoreDebugResponse(BaseModel):
    query: str
    top_k: int
    source_filter: str | None = None
    max_chars: int
    embedding_dim: int
    index_key: str
    total_indexed_chunks: int
    rebuild_index: bool
    index_stats: RagVectorStoreIndexStats
    results: list[RagVectorStoreDebugResult]
    trace_id: str | None = None


