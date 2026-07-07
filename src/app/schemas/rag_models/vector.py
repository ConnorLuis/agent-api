from pydantic import BaseModel, Field


class RagVectorStoreIndexStats(BaseModel):
    index_key: str
    source_filter: str | None = None
    max_chars: int
    embedding_dim: int
    embedding_provider: str
    embedding_model: str
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


class RagVectorStoreDebugRequest(BaseModel):
    query: str
    top_k: int = 3
    source_filter: str | None = None
    max_chars: int = 500
    embedding_dim: int = 64
    embedding_provider: str = "deterministic"
    embedding_model: str | None = None
    rebuild_index: bool = True


class RagVectorStoreDebugResponse(BaseModel):
    query: str
    top_k: int
    source_filter: str | None = None
    max_chars: int
    embedding_dim: int
    embedding_provider: str
    embedding_model: str
    index_key: str
    total_indexed_chunks: int
    rebuild_index: bool
    index_stats: RagVectorStoreIndexStats
    results: list[RagVectorStoreDebugResult]
    trace_id: str | None = None


class RagEmbeddingDebugDocument(BaseModel):
    text: str
    embedding_dim: int
    embedding_preview: list[float]
    embedding_norm: float


class RagEmbeddingDebugRequest(BaseModel):
    query: str
    documents: list[str] = Field(default_factory=list)
    provider: str = "deterministic"
    model_name: str | None = None
    embedding_dim: int = 64


class RagEmbeddingDebugResponse(BaseModel):
    query: str
    provider: str
    model: str
    requested_embedding_dim: int
    actual_embedding_dim: int
    query_embedding_preview: list[float]
    query_embedding_norm: float
    documents_count: int
    documents: list[RagEmbeddingDebugDocument]
    trace_id: str | None = None


class RagChromaSearchDebugRequest(BaseModel):
    query: str
    top_k: int = 3
    source_filter: str | None = None
    max_chars: int = 500
    embedding_dim: int = 64
    embedding_provider: str = "deterministic"
    embedding_model: str | None = None
    rebuild_index: bool = True


class RagChromaIndexStats(BaseModel):
    collection_name: str
    persist_dir: str
    source_filter: str | None = None
    max_chars: int
    embedding_dim: int
    embedding_provider: str
    embedding_model: str
    rebuild_index: bool
    loaded_chunks: int
    upserted_count: int
    stored_count: int


class RagChromaSearchDebugResult(BaseModel):
    rank: int
    chunk_id: str
    source: str
    index: int
    distance: float
    score: float
    content: str
    preview: str
    content_length: int


class RagChromaSearchDebugResponse(BaseModel):
    query: str
    top_k: int
    source_filter: str | None = None
    max_chars: int
    embedding_dim: int
    embedding_provider: str
    embedding_model: str
    collection_name: str
    persist_dir: str
    total_indexed_chunks: int
    rebuild_index: bool
    index_stats: RagChromaIndexStats
    results: list[RagChromaSearchDebugResult]
    trace_id: str | None = None