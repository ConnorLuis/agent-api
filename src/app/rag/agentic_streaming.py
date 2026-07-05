from collections.abc import Iterator
from typing import Any

from src.app.core.sse import sse_event
from src.app.observability.trace_store import record_trace_event
from src.app.rag.agentic_graph import invoke_agentic_rag
from src.app.rag.chunking import DEFAULT_MAX_CHARS
from src.app.rag.vector_index import DEFAULT_EMBEDDING_DIM


def _build_agentic_stream_payload(
    query: str,
    top_k: int,
    source_filter: str | None,
    max_chars: int,
    embedding_dim: int,
    keyword_weight: float,
    vector_weight: float,
    retrieval_backend: str,
    embedding_provider: str,
    embedding_model: str | None,
    rebuild_index: bool,
    trace_id: str,
) -> dict[str, Any]:
    result = invoke_agentic_rag(
        query=query,
        top_k=top_k,
        source_filter=source_filter,
        max_chars=max_chars,
        embedding_dim=embedding_dim,
        keyword_weight=keyword_weight,
        vector_weight=vector_weight,
        retrieval_backend=retrieval_backend,
        embedding_provider=embedding_provider,
        embedding_model=embedding_model,
        rebuild_index=rebuild_index,
    )

    return {
        **result,
        "trace_id": trace_id,
        "top_k": top_k,
        "source_filter": source_filter,
        "max_chars": max_chars,
        "embedding_dim": embedding_dim,
        "keyword_weight": keyword_weight,
        "vector_weight": vector_weight,
        "retrieval_backend": result.get("retrieval_backend", retrieval_backend),
        "retrieval_metadata": result.get("retrieval_metadata", {}),
        "embedding_provider": embedding_provider,
        "embedding_model": embedding_model,
        "rebuild_index": rebuild_index,
    }


def stream_agentic_rag_events(
    query: str,
    trace_id: str,
    top_k: int = 3,
    source_filter: str | None = None,
    max_chars: int = DEFAULT_MAX_CHARS,
    embedding_dim: int = DEFAULT_EMBEDDING_DIM,
    keyword_weight: float = 0.6,
    vector_weight: float = 0.4,
    retrieval_backend: str = "hybrid",
    embedding_provider: str = "deterministic",
    embedding_model: str | None = None,
    rebuild_index: bool = True,
) -> Iterator[str]:
    payload = _build_agentic_stream_payload(
        query=query,
        top_k=top_k,
        source_filter=source_filter,
        max_chars=max_chars,
        embedding_dim=embedding_dim,
        keyword_weight=keyword_weight,
        vector_weight=vector_weight,
        retrieval_backend=retrieval_backend,
        embedding_provider=embedding_provider,
        embedding_model=embedding_model,
        rebuild_index=rebuild_index,
        trace_id=trace_id,
    )

    record_trace_event(
        trace_id=trace_id,
        event_type="rag_agentic_stream",
        payload={
            "query": payload["query"],
            "rewritten_query": payload["rewritten_query"],
            "retrieval_needed": payload["retrieval_needed"],
            "relevance_score": payload["relevance_score"],
            "citations": payload["citations"],
            "steps": payload["steps"],
            "retrieval_results_count": len(payload["retrieval_results"]),
            "retrieval_backend": payload["retrieval_backend"],
            "retrieval_metadata": payload["retrieval_metadata"],
        },
    )

    yield sse_event(
        event="metadata",
        data={
            "trace_id": trace_id,
            "query": payload["query"],
            "top_k": payload["top_k"],
            "source_filter": payload["source_filter"],
            "retrieval_backend": payload["retrieval_backend"],
            "retrieval_metadata": payload["retrieval_metadata"],
        },
    )

    yield sse_event(
        event="decision",
        data={
            "trace_id": trace_id,
            "retrieval_needed": payload["retrieval_needed"],
            "steps": payload["steps"],
        },
    )

    if payload["retrieval_needed"]:
        yield sse_event(
            event="rewrite",
            data={
                "trace_id": trace_id,
                "query": payload["query"],
                "rewritten_query": payload["rewritten_query"],
            },
        )

        yield sse_event(
            event="retrieval",
            data={
                "trace_id": trace_id,
                "total_results": len(payload["retrieval_results"]),
                "results": payload["retrieval_results"],
                "retrieval_backend": payload["retrieval_backend"],
                "retrieval_metadata": payload["retrieval_metadata"],
            },
        )

        yield sse_event(
            event="relevance",
            data={
                "trace_id": trace_id,
                "relevance_score": payload["relevance_score"],
            },
        )

        yield sse_event(
            event="citation",
            data={
                "trace_id": trace_id,
                "citations": payload["citations"],
            },
        )

    yield sse_event(
        event="answer_chunk",
        data={
            "trace_id": trace_id,
            "answer_chunk": payload["final_answer"],
        },
    )

    yield sse_event(
        event="final",
        data={
            "trace_id": trace_id,
            "query": payload["query"],
            "rewritten_query": payload["rewritten_query"],
            "retrieval_needed": payload["retrieval_needed"],
            "relevance_score": payload["relevance_score"],
            "citations": payload["citations"],
            "retrieval_results": payload["retrieval_results"],
            "final_answer": payload["final_answer"],
            "steps": payload["steps"],
            "retrieval_backend": payload["retrieval_backend"],
            "retrieval_metadata": payload["retrieval_metadata"],
        },
    )

    yield sse_event(
        event="done",
        data={
            "trace_id": trace_id,
        },
    )