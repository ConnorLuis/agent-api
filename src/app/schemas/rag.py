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