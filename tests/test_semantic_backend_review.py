from src.app.evaluation.semantic_review import (
    build_semantic_backend_review,
    render_semantic_backend_review_markdown,
)


def _sample_semantic_comparison():
    return {
        "eval_file": "eval_cases/rag_agentic_eval_extended.jsonl",
        "best_backend_by_pass_rate": "chroma",
        "best_backend_by_average_relevance": "chroma_rerank",
        "results": [
            {
                "retrieval_backend": "hybrid",
                "metrics": {
                    "total_cases": 12,
                    "passed_cases": 10,
                    "pass_rate": 0.833333,
                    "expected_terms_hit_rate": 0.833333,
                    "citation_hit_rate": 1.0,
                    "average_relevance_score": 0.354141,
                },
            },
            {
                "retrieval_backend": "chroma",
                "metrics": {
                    "total_cases": 12,
                    "passed_cases": 11,
                    "pass_rate": 0.916667,
                    "expected_terms_hit_rate": 0.916667,
                    "citation_hit_rate": 1.0,
                    "average_relevance_score": 0.519489,
                },
            },
            {
                "retrieval_backend": "chroma_rerank",
                "metrics": {
                    "total_cases": 12,
                    "passed_cases": 11,
                    "pass_rate": 0.916667,
                    "expected_terms_hit_rate": 0.916667,
                    "citation_hit_rate": 1.0,
                    "average_relevance_score": 0.604476,
                },
            },
        ],
        "case_comparisons": [
            {
                "case_id": "agent_graph_flow",
                "winner_by_pass": "none",
                "winner_by_relevance": "chroma_rerank",
                "backend_results": [
                    {
                        "retrieval_backend": "hybrid",
                        "passed": False,
                        "expected_terms_pass": False,
                        "matched_expected_terms": ["tools"],
                        "citation_pass": True,
                        "retrieval_decision_pass": True,
                        "relevance_score": 0.42,
                        "citations": ["knowledge/agent_basics.md::chunk-1"],
                        "steps": [
                            "query_analyzer",
                            "query_rewriter",
                            "hybrid_retrieve",
                            "relevance_grade",
                            "answer_with_citations",
                        ],
                    },
                    {
                        "retrieval_backend": "chroma",
                        "passed": False,
                        "expected_terms_pass": False,
                        "matched_expected_terms": ["tools"],
                        "citation_pass": True,
                        "retrieval_decision_pass": True,
                        "relevance_score": 0.51,
                        "citations": ["knowledge/agent_basics.md::chunk-1"],
                        "steps": [
                            "query_analyzer",
                            "query_rewriter",
                            "chroma_retrieve",
                            "relevance_grade",
                            "answer_with_citations",
                        ],
                    },
                    {
                        "retrieval_backend": "chroma_rerank",
                        "passed": False,
                        "expected_terms_pass": False,
                        "matched_expected_terms": ["tools"],
                        "citation_pass": True,
                        "retrieval_decision_pass": True,
                        "relevance_score": 0.62,
                        "citations": ["knowledge/agent_basics.md::chunk-1"],
                        "steps": [
                            "query_analyzer",
                            "query_rewriter",
                            "chroma_rerank_retrieve",
                            "relevance_grade",
                            "answer_with_citations",
                        ],
                    },
                ],
            }
        ],
        "evaluation_report": {
            "recommended_backend": "chroma_rerank",
            "default_backend": "hybrid",
            "default_backend_should_change": False,
            "selection_policy": "keep_default_hybrid_until_failure_cases_are_reviewed",
            "embedding_provider": "sentence_transformers",
            "embedding_model": "/mnt/f/LLM/maidalun/bce-embedding-base_v1",
            "eval_file": "eval_cases/rag_agentic_eval_extended.jsonl",
            "eval_case_count": 12,
            "failure_analysis": {
                "common_failed_cases": ["agent_graph_flow"],
                "failure_count_by_backend": {
                    "hybrid": 2,
                    "chroma": 1,
                    "chroma_rerank": 1,
                },
                "unique_failed_cases_by_backend": {
                    "hybrid": ["agent_components"],
                    "chroma": [],
                    "chroma_rerank": [],
                },
            },
            "selection_policy_evaluation": {
                "candidate_backend": "chroma_rerank",
                "default_backend": "hybrid",
                "default_backend_should_change": False,
                "pass_rate_winners": ["chroma", "chroma_rerank"],
                "best_relevance_backend": "chroma_rerank",
                "supporting_reasons": [
                    "chroma_rerank is in the top pass-rate group.",
                    "chroma_rerank has the best average relevance score.",
                ],
                "blocking_reasons": [
                    "Common failed cases must be reviewed before changing the default backend: agent_graph_flow."
                ],
            },
        },
    }


def test_build_semantic_backend_review_marks_candidate_validated_but_blocked():
    review = build_semantic_backend_review(_sample_semantic_comparison())

    assert review["semantic_candidate_validated"] is True
    assert (
        review["review_decision"]
        == "review_common_failure_cases_before_default_switch"
    )
    assert review["candidate_backend"] == "chroma_rerank"
    assert review["default_backend"] == "hybrid"
    assert review["common_failed_cases"] == ["agent_graph_flow"]
    assert review["candidate_in_top_pass_rate_group"] is True
    assert review["candidate_best_by_relevance"] is True


def test_render_semantic_backend_review_markdown_contains_key_sections():
    review = build_semantic_backend_review(_sample_semantic_comparison())
    markdown = render_semantic_backend_review_markdown(review)

    assert "# Day41 Semantic Backend Review" in markdown
    assert "Semantic candidate validated" in markdown
    assert "agent_graph_flow" in markdown
    assert "chroma_rerank" in markdown
    assert "Blocking Reasons" in markdown
