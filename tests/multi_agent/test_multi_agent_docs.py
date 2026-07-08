from pathlib import Path


DOC_PATH = Path("docs/MULTI_AGENT.md")


def _read_doc() -> str:
    assert DOC_PATH.exists(), "docs/MULTI_AGENT.md should exist."
    return DOC_PATH.read_text(encoding="utf-8")


def test_multi_agent_docs_cover_day52_to_day61_scope():
    doc = _read_doc()

    assert "Day52: Multi-Agent state foundation" in doc
    assert "Day53: Deterministic Planner Agent" in doc
    assert "Day54: Deterministic Research Agent" in doc
    assert "Day55: Deterministic Tool Agent" in doc
    assert "Day56: Deterministic Critic Agent" in doc
    assert "Day57: Deterministic Memory Agent" in doc
    assert "Day58: Deterministic Reflection Agent" in doc
    assert "Day59: Deterministic Supervisor graph" in doc
    assert "Day60: Deterministic Multi-Agent streaming" in doc
    assert "Day61: Deterministic Multi-Agent eval / trace" in doc


def test_multi_agent_docs_describe_roles_and_debug_endpoints():
    doc = _read_doc()

    expected_roles = [
        "Planner",
        "Researcher",
        "Tool",
        "Critic",
        "Memory",
        "Reflection",
        "Supervisor",
    ]
    for role in expected_roles:
        assert f"### {role}" in doc

    expected_endpoints = [
        "POST /multi-agent/state-debug",
        "POST /multi-agent/plan-debug",
        "POST /multi-agent/research-debug",
        "POST /multi-agent/tool-debug",
        "POST /multi-agent/critic-debug",
        "POST /multi-agent/memory-debug",
        "POST /multi-agent/reflection-debug",
        "POST /multi-agent/supervisor-debug",
        "POST /multi-agent/stream",
        "POST /multi-agent/eval-debug",
    ]
    for endpoint in expected_endpoints:
        assert endpoint in doc


def test_multi_agent_docs_describe_stream_contract():
    doc = _read_doc()

    assert "## Streaming contract" in doc
    assert "text/event-stream" in doc
    assert "metadata x1" in doc
    assert "graph x1" in doc
    assert "node x6" in doc
    assert "edge x5" in doc
    assert "role x7" in doc
    assert "artifact x7" in doc
    assert "final x1" in doc
    assert "done x1" in doc

    expected_events = [
        "event: metadata",
        "event: graph",
        "event: node",
        "event: edge",
        "event: role",
        "event: artifact",
        "event: final",
        "event: done",
    ]
    for event_name in expected_events:
        assert event_name in doc

    expected_roles = [
        "planner",
        "researcher",
        "tool",
        "critic",
        "memory",
        "reflection",
        "supervisor",
    ]
    for role in expected_roles:
        assert role in doc


def test_multi_agent_docs_describe_eval_trace_and_boundaries():
    doc = _read_doc()

    assert "## Eval / trace contract" in doc
    assert "eval_report" in doc
    assert "trace_report" in doc
    assert "multi_agent_eval_trace_only" in doc
    assert "eval_report.eval_pass = true" in doc
    assert "eval_report.failed_check_count = 0" in doc

    expected_checks = [
        "supervisor_orchestration_pass",
        "stream_graph_matches_supervisor",
        "stream_event_sequence",
        "node_coverage",
        "edge_coverage",
        "role_stream_sequence",
        "role_readiness_consistency",
        "artifact_coverage",
        "terminal_stream_events",
        "trace_identity_consistency",
        "boundary_flags",
        "debug_endpoint_contracts",
        "state_event_completion_coverage",
        "trace_report_consistency",
    ]
    for check_name in expected_checks:
        assert check_name in doc

    assert "## CI-safe and LLM-free boundaries" in doc
    assert "No LLM call." in doc
    assert "No external tool execution." in doc
    assert "No Neo4j connection from Multi-Agent role execution." in doc
    assert "## Why graph_fusion remains non-default" in doc
    assert "DEFAULT_RETRIEVAL_BACKEND = hybrid" in doc
    assert "graph_fusion remains a non-default retrieval backend." in doc
    assert "graph_fusion_default_changed = false" in doc
