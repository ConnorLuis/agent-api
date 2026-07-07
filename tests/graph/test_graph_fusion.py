from src.app.graph.fusion import (
    fuse_graph_and_vector_results,
    run_graph_vector_fusion_debug,
)


def test_fuse_graph_and_vector_results_merges_same_chunk_id():
    graph_chunks = [
        {
            "chunk_id": "chunk-1",
            "source": "knowledge/doc.md",
            "index": 1,
            "content": "graph content",
            "preview": "graph preview",
            "content_length": 13,
            "matched_entities": [{"name": "RAG"}],
            "mentions": [{"entity_id": "Entity:concept:rag"}],
        }
    ]

    vector_results = [
        {
            "chunk_id": "chunk-1",
            "source": "knowledge/doc.md",
            "index": 1,
            "content": "vector content",
            "preview": "vector preview",
            "content_length": 14,
            "hybrid_score": 0.8,
            "keyword_score": 1.0,
            "vector_score": 0.5,
            "matched_terms": ["rag"],
        }
    ]

    fused = fuse_graph_and_vector_results(
        graph_chunks=graph_chunks,
        vector_results=vector_results,
        top_k=5,
        fusion_graph_weight=0.5,
        fusion_vector_weight=0.5,
    )

    assert len(fused) == 1

    result = fused[0]

    assert result["chunk_id"] == "chunk-1"
    assert result["rank"] == 1
    assert result["graph_score"] == 1.0
    assert result["vector_score"] == 0.8
    assert result["fusion_score"] == 0.9
    assert result["retrieval_sources"] == ["graph", "vector"]
    assert result["matched_entities"] == [{"name": "RAG"}]
    assert result["vector_metadata"]["matched_terms"] == ["rag"]


def test_fuse_graph_and_vector_results_keeps_graph_only_and_vector_only_chunks():
    graph_chunks = [
        {
            "chunk_id": "graph-only",
            "source": "knowledge/doc.md",
            "index": 1,
            "content": "graph only",
            "preview": "graph only",
            "content_length": 10,
        }
    ]

    vector_results = [
        {
            "chunk_id": "vector-only",
            "source": "knowledge/doc.md",
            "index": 2,
            "content": "vector only",
            "preview": "vector only",
            "content_length": 11,
            "hybrid_score": 0.7,
        }
    ]

    fused = fuse_graph_and_vector_results(
        graph_chunks=graph_chunks,
        vector_results=vector_results,
        top_k=5,
        fusion_graph_weight=0.6,
        fusion_vector_weight=0.4,
    )

    chunk_ids = {item["chunk_id"] for item in fused}

    assert chunk_ids == {"graph-only", "vector-only"}

    graph_only = next(item for item in fused if item["chunk_id"] == "graph-only")
    vector_only = next(item for item in fused if item["chunk_id"] == "vector-only")

    assert graph_only["retrieval_sources"] == ["graph"]
    assert vector_only["retrieval_sources"] == ["vector"]


def test_fuse_graph_and_vector_results_respects_top_k():
    vector_results = [
        {
            "chunk_id": f"chunk-{index}",
            "source": "knowledge/doc.md",
            "index": index,
            "content": f"content {index}",
            "preview": f"content {index}",
            "content_length": 10,
            "hybrid_score": 1.0 / index,
        }
        for index in range(1, 6)
    ]

    fused = fuse_graph_and_vector_results(
        graph_chunks=[],
        vector_results=vector_results,
        top_k=2,
    )

    assert len(fused) == 2
    assert [item["rank"] for item in fused] == [1, 2]


def test_run_graph_vector_fusion_debug_defaults_to_graph_dry_run():
    result = run_graph_vector_fusion_debug(
        query="RAG 是什么？",
        top_k=3,
        source_filter="agent_basics",
        max_chars=300,
        embedding_dim=64,
    )

    assert result["query"] == "RAG 是什么？"
    assert result["graph_dry_run"] is True
    assert result["graph_retrieval"]["status"] == "dry_run"
    assert result["vector_retrieval"]["result_count"] >= 1
    assert result["fusion"]["result_count"] >= 1
    assert result["fusion"]["strategy"] == "chunk_id_union_weighted_score"

    assert "Entity:concept:rag" in [
        item["entity_id"]
        for item in result["query_entity_matches"]
    ]


def test_run_graph_vector_fusion_debug_handles_no_query_entity_match():
    result = run_graph_vector_fusion_debug(
        query="今天天气怎么样？",
        top_k=3,
        source_filter="agent_basics",
        max_chars=300,
    )

    assert result["query_entity_matches"] == []
    assert result["graph_retrieval"]["status"] == "no_query_entity_match"
    assert result["vector_retrieval"]["result_count"] >= 0
    assert "results" in result


def test_run_graph_vector_fusion_debug_can_use_mocked_live_graph(monkeypatch):
    def fake_run_graph_retrieval_debug(
        query,
        chunk_limit=5,
        related_entity_limit=10,
        dry_run=True,
    ):
        return {
            "query": query,
            "query_entity_matches": [
                {
                    "entity_id": "Entity:concept:rag",
                    "name": "RAG",
                }
            ],
            "execution": {
                "ok": True,
                "status": "retrieved",
                "matched_entities": [
                    {
                        "entity_id": "Entity:concept:rag",
                        "name": "RAG",
                    }
                ],
                "chunks": [
                    {
                        "chunk_id": "mock-graph-chunk",
                        "source": "knowledge/doc.md",
                        "index": 1,
                        "content": "mock graph chunk",
                        "preview": "mock graph chunk",
                        "content_length": 16,
                        "matched_entities": [
                            {
                                "entity_id": "Entity:concept:rag",
                                "name": "RAG",
                            }
                        ],
                        "mentions": [],
                    }
                ],
                "related_entities": [],
                "counts": {
                    "matched_entities": 1,
                    "chunks": 1,
                    "related_entities": 0,
                },
            },
        }

    monkeypatch.setattr(
        "src.app.graph.fusion.run_graph_retrieval_debug",
        fake_run_graph_retrieval_debug,
    )

    result = run_graph_vector_fusion_debug(
        query="RAG 是什么？",
        top_k=5,
        graph_dry_run=False,
    )

    assert result["graph_dry_run"] is False
    assert result["graph_retrieval"]["status"] == "retrieved"
    assert result["graph_retrieval"]["chunk_count"] == 1

    chunk_ids = {item["chunk_id"] for item in result["results"]}

    assert "mock-graph-chunk" in chunk_ids
