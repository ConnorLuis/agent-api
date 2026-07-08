from fastapi import FastAPI

from src.app.core.logging import setup_logging
from src.app.core.middleware import TraceLoggingMiddleware
from src.app.routes.routes_agent import router as agent_router
from src.app.routes.routes_llm import router as llm_router
from src.app.routes.routes_rag import router as rag_router
from src.app.routes.routes_observability import router as observability_router
from src.app.routes.routes_multi_agent import router as multi_agent_router
from src.app.routes import routes_graph

setup_logging()

app = FastAPI(
    title="agent-api",
    description="FastAPI + LangGraph based Agent backend service",
    version="0.1.0",
)

app.add_middleware(TraceLoggingMiddleware)

@app.get("/health")
def heath_check() -> dict:
    return {"status": "ok"}

app.include_router(agent_router, prefix="/agent", tags=["agent"])
app.include_router(llm_router, prefix="/llm", tags=["llm"])
app.include_router(rag_router, prefix="/rag", tags=["rag"])
app.include_router(observability_router)
app.include_router(routes_graph.router)
app.include_router(multi_agent_router)
