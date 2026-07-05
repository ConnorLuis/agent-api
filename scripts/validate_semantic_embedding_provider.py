from pathlib import Path
import sys
import os

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.app.evaluation.rag_eval import compare_rag_retrieval_backends
from src.app.rag.embedding_provider import get_embedding_provider
from src.app.rag.agentic_graph import invoke_agentic_rag
from src.app.rag.chroma_store import debug_chroma_search


def main() -> None:
    provider_name = "sentence_transformers"
    model_name = os.getenv(
        "SEMANTIC_EMBEDDING_MODEL",
        "/mnt/f/LLM/maidalun/bce-embedding-base_v1",
    )
    embedding_dim = int(os.getenv("SEMANTIC_EMBEDDING_DIM", "768"))

    print("== provider ==")
    print("model_path =", model_name)
    print("expected_embedding_dim =", embedding_dim)

    provider = get_embedding_provider(
        provider=provider_name,
        embedding_model=model_name,
    )

    query_embedding = provider.embed_text("LangGraph 是什么？")

    print("provider =", provider.provider)
    print("model =", getattr(provider, "model", model_name))
    print("actual_embedding_dim =", len(query_embedding))
    print("embedding_preview =", query_embedding[:5])

    print("\n== chroma search ==")
    chroma_result = debug_chroma_search(
        query="LangGraph 是什么？",
        top_k=2,
        source_filter="agent_basics",
        max_chars=300,
        embedding_dim=embedding_dim,
        embedding_provider=provider_name,
        embedding_model=model_name,
        rebuild_index=True,
    )

    print("collection_name =", chroma_result["collection_name"])
    print("embedding_provider =", chroma_result["embedding_provider"])
    print("embedding_model =", chroma_result["embedding_model"])
    print("embedding_dim =", chroma_result["embedding_dim"])
    print("total_indexed_chunks =", chroma_result["total_indexed_chunks"])

    for item in chroma_result["results"]:
        print(
            item["rank"],
            item["chunk_id"],
            item["score"],
            item["preview"][:80].replace("\n", " "),
        )

    print("\n== agentic rag chroma semantic ==")
    agentic_result = invoke_agentic_rag(
        query="请搜索知识库：LangGraph 是什么？",
        top_k=2,
        source_filter="agent_basics",
        max_chars=300,
        embedding_dim=embedding_dim,
        retrieval_backend="chroma",
        embedding_provider=provider_name,
        embedding_model=model_name,
        rebuild_index=True,
    )

    print("retrieval_backend =", agentic_result["retrieval_backend"])
    print("retrieval_metadata =", agentic_result["retrieval_metadata"])
    print("steps =", agentic_result["steps"])
    print("citations =", agentic_result["citations"])
    print("relevance_score =", agentic_result["relevance_score"])
    print("final_answer_preview =", agentic_result["final_answer"][:200])

    print("\n== backend comparison ==")
    comparison = compare_rag_retrieval_backends(
        backends=["hybrid", "chroma", "chroma_rerank"],
        source_filter="agent_basics",
        max_chars=300,
        embedding_dim=embedding_dim,
        keyword_weight=0.6,
        vector_weight=0.4,
        embedding_provider=provider_name,
        embedding_model=model_name,
        rebuild_index=True,
    )

    print("best_backend_by_pass_rate =", comparison["best_backend_by_pass_rate"])
    print(
        "best_backend_by_average_relevance =",
        comparison["best_backend_by_average_relevance"],
    )
    print("comparison_summary =", comparison["comparison_summary"])

    for item in comparison["results"]:
        print(
            item["retrieval_backend"],
            item["embedding_provider"],
            item["embedding_model"],
            item["metrics"],
        )


if __name__ == "__main__":
    main()