from src.app.rag.chunking import debug_knowledge_chunks, split_text_into_chunks


def test_split_text_into_chunks_by_blank_lines():
    text = "第一段内容\n\n第二段内容\n\n第三段内容"

    chunks = split_text_into_chunks(
        text=text,
        max_chars=80,
    )

    assert len(chunks) >= 1
    assert "第一段内容" in chunks[0]
    assert all(chunk.strip() for chunk in chunks)


def test_debug_knowledge_chunks_loads_agent_basics():
    result = debug_knowledge_chunks(
        source_filter="agent_basics",
        max_chars=300,
    )

    assert result["source_filter"] == "agent_basics"
    assert result["max_chars"] == 300
    assert result["total_chunks"] >= 1
    assert len(result["chunks"]) == result["total_chunks"]

    first = result["chunks"][0]

    assert first["chunk_id"].startswith("knowledge/agent_basics.md::chunk-")
    assert first["source"] == "knowledge/agent_basics.md"
    assert first["index"] == 1
    assert first["content"]
    assert first["preview"]
    assert first["content_length"] > 0


def test_rag_chunks_debug_endpoint(client):
    trace_id = "rag-chunks-debug-001"

    response = client.post(
        "/rag/chunks-debug",
        headers={"x-trace-id": trace_id},
        json={
            "source_filter": "agent_basics",
            "max_chars": 300,
        },
    )

    assert response.status_code == 200
    assert response.headers["x-trace-id"] == trace_id

    data = response.json()

    assert data["source_filter"] == "agent_basics"
    assert data["max_chars"] == 300
    assert data["trace_id"] == trace_id
    assert data["total_chunks"] >= 1
    assert len(data["chunks"]) == data["total_chunks"]

    first = data["chunks"][0]

    assert first["chunk_id"].startswith("knowledge/agent_basics.md::chunk-")
    assert first["source"] == "knowledge/agent_basics.md"
    assert first["index"] == 1
    assert first["content"]
    assert first["preview"]
    assert first["content_length"] > 0