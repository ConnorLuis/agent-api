from fastapi import FastAPI

from src.app.core.logging import setup_logging
from src.app.core.middleware import TraceLoggingMiddleware
from src.app.routes.routes_agent import router as agent_router

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