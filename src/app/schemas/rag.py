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