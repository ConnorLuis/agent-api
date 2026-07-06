from pathlib import Path
import json
import os
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from src.app.evaluation.rag_eval import compare_rag_retrieval_backends


DEFAULT_MODEL_PATH = "/mnt/f/LLM/maidalun/bce-embedding-base_v1"
DEFAULT_OUTPUT_PATH = "reports/day41_semantic_extended_backend_eval.json"


def main() -> None:
    model_path = os.getenv("SEMANTIC_EMBEDDING_MODEL", DEFAULT_MODEL_PATH)
    embedding_dim = int(os.getenv("SEMANTIC_EMBEDDING_DIM", "768"))
    output_path = Path(
        os.getenv("DAY41_SEMANTIC_EVAL_OUTPUT", DEFAULT_OUTPUT_PATH)
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)

    print("== Day41 semantic extended backend evaluation ==")
    print("eval_file =", "eval_cases/rag_agentic_eval_extended.jsonl")
    print("embedding_provider =", "sentence_transformers")
    print("embedding_model =", model_path)
    print("embedding_dim =", embedding_dim)
    print("output_path =", output_path)

    comparison = compare_rag_retrieval_backends(
        eval_file="eval_cases/rag_agentic_eval_extended.jsonl",
        backends=["hybrid", "chroma", "chroma_rerank"],
        source_filter="agent_basics",
        max_chars=300,
        embedding_dim=embedding_dim,
        keyword_weight=0.6,
        vector_weight=0.4,
        embedding_provider="sentence_transformers",
        embedding_model=model_path,
        rebuild_index=True,
    )

    output_path.write_text(
        json.dumps(comparison, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    report = comparison["evaluation_report"]

    print()
    print("== summary ==")
    print("best_backend_by_pass_rate =", comparison["best_backend_by_pass_rate"])
    print(
        "best_backend_by_average_relevance =",
        comparison["best_backend_by_average_relevance"],
    )
    print("recommended_backend =", report["recommended_backend"])
    print("default_backend =", report["default_backend"])
    print(
        "default_backend_should_change =",
        report["default_backend_should_change"],
    )
    print("selection_policy =", report["selection_policy"])
    print("eval_case_count =", report["eval_case_count"])

    print()
    print("== backend metrics ==")
    for item in comparison["results"]:
        metrics = item["metrics"]
        print(
            item["retrieval_backend"],
            "passed_cases =",
            f"{metrics['passed_cases']}/{metrics['total_cases']}",
            "pass_rate =",
            metrics["pass_rate"],
            "expected_terms_hit_rate =",
            metrics["expected_terms_hit_rate"],
            "average_relevance_score =",
            metrics["average_relevance_score"],
        )

    print()
    print("== failure analysis ==")
    failure_analysis = report["failure_analysis"]
    print("common_failed_cases =", failure_analysis["common_failed_cases"])
    print(
        "failure_count_by_backend =",
        failure_analysis["failure_count_by_backend"],
    )
    print(
        "unique_failed_cases_by_backend =",
        failure_analysis["unique_failed_cases_by_backend"],
    )

    print()
    print("== policy ==")
    policy = report["selection_policy_evaluation"]
    print("supporting_reasons =", policy["supporting_reasons"])
    print("blocking_reasons =", policy["blocking_reasons"])

    print()
    print("wrote:", output_path)


if __name__ == "__main__":
    main()
