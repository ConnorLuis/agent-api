import logging
import time
from uuid import uuid4

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from src.app.core.request_context import trace_id_ctx

logger = logging.getLogger("agent-api.request")


class TraceLoggingMiddleware(BaseHTTPMiddleware):
    """
    Add x-trace-id and request latency logging.

    Behavior:
    - If request has x-trace-id, reuse it.
    - If request does not have x-trace-id, generate a new one.
    - Add x-trace-id to response headers.
    - Log method, path, status_code, latency_ms, trace_id.
    """
    async def dispatch(self, request: Request, call_next) -> Response:
        trace_id = request.headers.get("x-trace-id") or f"trace-{uuid4().hex[:12]}"

        token = trace_id_ctx.set(trace_id)
        start_time = time.perf_counter()
        status_code = 500

        try:
            response = await call_next(request)
            status_code = response.status_code
            response.headers["x-trace-id"] = trace_id
            return response
        finally:
            latency_ms = int((time.perf_counter() - start_time) * 1000)
            logger.info(
                "request_completed method=%s path=%s status_code=%s latency_ms=%.2f trace_id=%s",
                request.method,
                request.url.path,
                status_code,
                latency_ms,
                trace_id,
            )

            trace_id_ctx.reset(token)