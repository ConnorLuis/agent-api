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