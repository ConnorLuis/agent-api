from __future__ import annotations

from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "tests"

MOVE_RULES: list[tuple[str, str]] = [
    # Core
    ("test_health.py", "core"),
    ("test_trace.py", "observability"),
    ("test_observability.py", "observability"),

    # LLM
    ("test_llm.py", "llm"),

    # Agent core
    ("test_agent_chat.py", "agent/core"),
    ("test_agent_memory.py", "agent/core"),
    ("test_agent_debug.py", "agent/core"),
    ("test_stream.py", "agent/streaming"),

    # Router / Smart Chat
    ("test_router_agent.py", "agent/router"),
    ("test_router_delegation.py", "agent/router"),
    ("test_router_stream.py", "agent/router"),
    ("test_llm_router.py", "agent/router"),
    ("test_smart_chat.py", "agent/router"),
    ("test_smart_stream.py", "agent/router"),
    ("test_route_validation.py", "agent/router"),

    # GraphRAG
    ("test_graph_schema.py", "graph"),
    ("test_graph_debug.py", "graph"),
    ("test_graph_extraction.py", "graph"),
    ("test_graph_extract_debug.py", "graph"),
    ("test_graph_ingestion.py", "graph"),
    ("test_graph_ingest_debug.py", "graph"),
    ("test_graph_retrieval.py", "graph"),
    ("test_graph_retrieval_debug.py", "graph"),
    ("test_graph_fusion.py", "graph"),
    ("test_graph_fusion_debug.py", "graph"),

    # RAG retrieval / chunks
    ("test_rag.py", "rag/retrieval"),
    ("test_rag_debug.py", "rag/retrieval"),
    ("test_rag_chunks.py", "rag/retrieval"),
    ("test_rag_vector_search.py", "rag/retrieval"),
    ("test_rag_hybrid_search.py", "rag/retrieval"),

    # Agentic RAG
    ("test_rag_agentic_debug.py", "rag/agentic"),
    ("test_rag_agentic_backend.py", "rag/agentic"),
    ("test_rag_agentic_graph_fusion_backend.py", "rag/agentic"),

    # RAG streaming
    ("test_rag_agentic_stream.py", "rag/streaming"),
    ("test_rag_agentic_stream_backend.py", "rag/streaming"),

    # RAG verification
    ("test_rag_answer_verify.py", "rag/verification"),
    ("test_rag_answer_verify_graph_fusion.py", "rag/verification"),

    # Vector store / embedding / Chroma / rerank
    ("test_rag_vector_store.py", "rag/vector_store"),
    ("test_rag_embedding_provider.py", "rag/vector_store"),
    ("test_rag_chroma_store.py", "rag/vector_store"),
    ("test_rag_reranker.py", "rag/vector_store"),
    ("test_rag_semantic_embedding_provider.py", "rag/vector_store"),

    # RAG evaluation
    ("test_rag_eval.py", "rag/evaluation"),
    ("test_rag_backend_eval.py", "rag/evaluation"),
    ("test_rag_backend_pairwise_eval.py", "rag/evaluation"),
    ("test_rag_backend_comparison_summary.py", "rag/evaluation"),
    ("test_rag_backend_report.py", "rag/evaluation"),
    ("test_rag_eval_extended_dataset.py", "rag/evaluation"),
    ("test_rag_backend_extended_analysis.py", "rag/evaluation"),
    ("test_semantic_backend_review.py", "rag/evaluation"),
    ("test_rag_graph_fusion_eval.py", "rag/evaluation"),
    ("test_rag_graph_fusion_observability.py", "rag/evaluation"),
]

def move_file(filename: str, target_dir: str) -> None:
    src = TESTS / filename
    if not src.exists():
        return

    dst_dir = TESTS / target_dir
    dst_dir.mkdir(parents=True, exist_ok=True)

    dst = dst_dir / filename
    if dst.exists():
        raise FileExistsError(f"Target already exists: {dst}")

    print(f"move {src.relative_to(ROOT)} -> {dst.relative_to(ROOT)}")
    shutil.move(str(src), str(dst))


def main() -> None:
    for filename, target_dir in MOVE_RULES:
        move_file(filename, target_dir)

    remaining = sorted(
        p.name
        for p in TESTS.glob("test_*.py")
        if p.is_file()
    )

    if remaining:
        print("\nRemaining top-level test files:")
        for name in remaining:
            print(f"  - {name}")
        raise SystemExit(
            "Some top-level tests were not classified. Move them manually or update MOVE_RULES."
        )

    print("\nDone. tests/conftest.py remains at tests/conftest.py")


if __name__ == "__main__":
    main()
