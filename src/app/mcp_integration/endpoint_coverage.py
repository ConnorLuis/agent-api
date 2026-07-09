from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class MCPEndpointCoverageSpec:
    endpoint_id: str
    method: str
    path: str
    domain: str
    existing_capability: str
    mcp_coverage_type: str
    ci_safe: bool
    dry_run_default: bool
    risk_flags: tuple[str, ...] = field(default_factory=tuple)
    mapped_mcp_tools: tuple[str, ...] = field(default_factory=tuple)
    mapped_mcp_resources: tuple[str, ...] = field(default_factory=tuple)
    notes: str = ""


def list_mcp_endpoint_coverage_specs() -> list[MCPEndpointCoverageSpec]:
    return [
        MCPEndpointCoverageSpec(
            endpoint_id="rag_agentic_debug",
            method="POST",
            path="/rag/agentic-debug",
            domain="rag",
            existing_capability="Agentic RAG debug graph with retrieval backend selection.",
            mcp_coverage_type="tool_adapter_existing",
            ci_safe=True,
            dry_run_default=True,
            risk_flags=("read_only", "rag_access"),
            mapped_mcp_tools=("agentic_rag_query",),
            notes="Already covered by the existing agentic_rag_query MCP tool.",
        ),
        MCPEndpointCoverageSpec(
            endpoint_id="rag_agentic_stream",
            method="POST",
            path="/rag/agentic-stream",
            domain="rag",
            existing_capability="Agentic RAG SSE streaming endpoint.",
            mcp_coverage_type="planned_stream_summary_wrapper",
            ci_safe=True,
            dry_run_default=True,
            risk_flags=("read_only", "rag_access", "streaming"),
            mapped_mcp_tools=(),
            notes="Day71 should expose a CI-safe stream summary wrapper rather than raw SSE streaming.",
        ),
        MCPEndpointCoverageSpec(
            endpoint_id="rag_eval_debug",
            method="POST",
            path="/rag/eval-debug",
            domain="rag",
            existing_capability="Single-backend RAG evaluation debug endpoint.",
            mcp_coverage_type="tool_adapter_existing",
            ci_safe=True,
            dry_run_default=True,
            risk_flags=("read_only", "evaluation"),
            mapped_mcp_tools=("rag_backend_eval",),
            notes="Partially covered through rag_backend_eval; direct single-backend wrapper is planned.",
        ),
        MCPEndpointCoverageSpec(
            endpoint_id="rag_backend_eval_debug",
            method="POST",
            path="/rag/backend-eval-debug",
            domain="rag",
            existing_capability="Multi-backend RAG evaluation comparison endpoint.",
            mcp_coverage_type="tool_adapter_existing",
            ci_safe=True,
            dry_run_default=True,
            risk_flags=("read_only", "evaluation"),
            mapped_mcp_tools=("rag_backend_eval",),
            notes="Already covered by rag_backend_eval.",
        ),
        MCPEndpointCoverageSpec(
            endpoint_id="rag_answer_verify_debug",
            method="POST",
            path="/rag/answer-verify-debug",
            domain="rag",
            existing_capability="Agentic RAG answer verification debug endpoint.",
            mcp_coverage_type="tool_adapter_existing",
            ci_safe=True,
            dry_run_default=True,
            risk_flags=("read_only", "verification"),
            mapped_mcp_tools=("answer_verify",),
            notes="Already covered by answer_verify.",
        ),
        MCPEndpointCoverageSpec(
            endpoint_id="graph_schema_debug",
            method="GET",
            path="/graph/schema-debug",
            domain="graph",
            existing_capability="GraphRAG schema debug endpoint.",
            mcp_coverage_type="resource_existing",
            ci_safe=True,
            dry_run_default=True,
            risk_flags=("read_only", "graph_access"),
            mapped_mcp_resources=("agent-api://graph/schema",),
            notes="Already covered as an MCP resource; Day71 can add a tool probe if useful.",
        ),
        MCPEndpointCoverageSpec(
            endpoint_id="graph_extract_debug",
            method="POST",
            path="/graph/extract-debug",
            domain="graph",
            existing_capability="Deterministic graph entity / relation extraction debug endpoint.",
            mcp_coverage_type="planned_tool_wrapper",
            ci_safe=True,
            dry_run_default=True,
            risk_flags=("read_only", "graph_access"),
            mapped_mcp_tools=(),
            notes="Planned Day71 wrapper should call extraction without Neo4j writes.",
        ),
        MCPEndpointCoverageSpec(
            endpoint_id="graph_retrieval_debug",
            method="POST",
            path="/graph/retrieval-debug",
            domain="graph",
            existing_capability="Neo4j graph retrieval debug endpoint.",
            mcp_coverage_type="planned_tool_wrapper",
            ci_safe=True,
            dry_run_default=True,
            risk_flags=("read_only", "graph_access", "live_neo4j_capable"),
            mapped_mcp_tools=(),
            notes="Planned Day71 wrapper must enforce dry_run under CI-safe principal.",
        ),
        MCPEndpointCoverageSpec(
            endpoint_id="graph_fusion_debug",
            method="POST",
            path="/graph/fusion-debug",
            domain="graph",
            existing_capability="GraphRAG + VectorRAG fusion debug endpoint.",
            mcp_coverage_type="tool_adapter_existing",
            ci_safe=True,
            dry_run_default=True,
            risk_flags=("read_only", "graph_access", "live_neo4j_capable"),
            mapped_mcp_tools=("graph_fusion_retrieve",),
            notes="Already covered by graph_fusion_retrieve with graph_dry_run safety.",
        ),
        MCPEndpointCoverageSpec(
            endpoint_id="multi_agent_supervisor_debug",
            method="POST",
            path="/multi-agent/supervisor-debug",
            domain="multi_agent",
            existing_capability="Deterministic Multi-Agent Supervisor graph debug endpoint.",
            mcp_coverage_type="planned_tool_wrapper",
            ci_safe=True,
            dry_run_default=True,
            risk_flags=("read_only", "multi_agent"),
            mapped_mcp_tools=(),
            notes="Planned Day71 wrapper should expose Supervisor graph output directly.",
        ),
        MCPEndpointCoverageSpec(
            endpoint_id="multi_agent_stream",
            method="POST",
            path="/multi-agent/stream",
            domain="multi_agent",
            existing_capability="Deterministic Multi-Agent SSE streaming endpoint.",
            mcp_coverage_type="planned_stream_summary_wrapper",
            ci_safe=True,
            dry_run_default=True,
            risk_flags=("read_only", "multi_agent", "streaming"),
            mapped_mcp_tools=(),
            notes="Day71 should expose a stream summary wrapper rather than raw SSE streaming.",
        ),
        MCPEndpointCoverageSpec(
            endpoint_id="multi_agent_eval_debug",
            method="POST",
            path="/multi-agent/eval-debug",
            domain="multi_agent",
            existing_capability="Deterministic Multi-Agent eval / trace endpoint.",
            mcp_coverage_type="tool_adapter_existing",
            ci_safe=True,
            dry_run_default=True,
            risk_flags=("read_only", "multi_agent", "evaluation"),
            mapped_mcp_tools=("multi_agent_eval_trace",),
            notes="Already covered by multi_agent_eval_trace.",
        ),
        MCPEndpointCoverageSpec(
            endpoint_id="observability_traces",
            method="GET",
            path="/observability/traces",
            domain="observability",
            existing_capability="Recent observability trace list endpoint.",
            mcp_coverage_type="tool_adapter_existing",
            ci_safe=True,
            dry_run_default=True,
            risk_flags=("read_only", "observability"),
            mapped_mcp_tools=("mcp_endpoint_probe",),
            notes="Covered by mcp_endpoint_probe as a CI-safe read-only trace-list probe.",
        ),
        MCPEndpointCoverageSpec(
            endpoint_id="observability_trace_detail",
            method="GET",
            path="/observability/traces/{trace_id}",
            domain="observability",
            existing_capability="Single trace event lookup endpoint.",
            mcp_coverage_type="tool_adapter_existing",
            ci_safe=True,
            dry_run_default=True,
            risk_flags=("read_only", "observability"),
            mapped_mcp_tools=("mcp_endpoint_probe",),
            notes="Covered by mcp_endpoint_probe as a CI-safe read-only trace-detail probe.",
        ),
    ]


def serialize_endpoint_coverage_spec(
    spec: MCPEndpointCoverageSpec,
) -> dict[str, Any]:
    return {
        "endpoint_id": spec.endpoint_id,
        "method": spec.method,
        "path": spec.path,
        "domain": spec.domain,
        "existing_capability": spec.existing_capability,
        "mcp_coverage_type": spec.mcp_coverage_type,
        "ci_safe": spec.ci_safe,
        "dry_run_default": spec.dry_run_default,
        "risk_flags": list(spec.risk_flags),
        "mapped_mcp_tools": list(spec.mapped_mcp_tools),
        "mapped_mcp_resources": list(spec.mapped_mcp_resources),
        "notes": spec.notes,
    }


def build_mcp_endpoint_coverage_report() -> dict[str, Any]:
    specs = list_mcp_endpoint_coverage_specs()
    serialized = [serialize_endpoint_coverage_spec(spec) for spec in specs]

    by_domain: dict[str, int] = {}
    by_coverage_type: dict[str, int] = {}
    ci_safe_count = 0
    dry_run_default_count = 0
    already_covered_count = 0
    planned_wrapper_count = 0

    for item in serialized:
        by_domain[item["domain"]] = by_domain.get(item["domain"], 0) + 1
        by_coverage_type[item["mcp_coverage_type"]] = (
            by_coverage_type.get(item["mcp_coverage_type"], 0) + 1
        )
        if item["ci_safe"]:
            ci_safe_count += 1
        if item["dry_run_default"]:
            dry_run_default_count += 1
        if item["mapped_mcp_tools"] or item["mapped_mcp_resources"]:
            already_covered_count += 1
        if item["mcp_coverage_type"].startswith("planned"):
            planned_wrapper_count += 1

    already_covered_endpoint_ids = [
        item["endpoint_id"]
        for item in serialized
        if item["mapped_mcp_tools"] or item["mapped_mcp_resources"]
    ]
    planned_endpoint_ids = [
        item["endpoint_id"]
        for item in serialized
        if item["mcp_coverage_type"].startswith("planned")
    ]

    return {
        "report_name": "agent-api MCP endpoint coverage report",
        "report_version": "day71_mcp_endpoint_coverage_report_v1",
        "scope": {
            "milestone": "Day71",
            "goal": "Broader MCP endpoint coverage",
            "rest_endpoints_preserved": True,
            "mcp_is_additive_protocol_layer": True,
            "main_agent_default_path_changed": False,
            "graph_fusion_default_changed": False,
        },
        "summary": {
            "endpoint_count": len(serialized),
            "ci_safe_endpoint_count": ci_safe_count,
            "dry_run_default_endpoint_count": dry_run_default_count,
            "already_covered_endpoint_count": already_covered_count,
            "planned_wrapper_endpoint_count": planned_wrapper_count,
            "domain_counts": by_domain,
            "coverage_type_counts": by_coverage_type,
            "already_covered_endpoint_ids": already_covered_endpoint_ids,
            "planned_endpoint_ids": planned_endpoint_ids,
        },
        "coverage": serialized,
        "safety": {
            "ci_safe": True,
            "external_servers_executed_in_ci": False,
            "write_tools_enabled_in_ci": False,
            "destructive_tools_allowed_in_ci": False,
            "live_neo4j_required_in_ci": False,
            "graph_mutation_allowed_in_ci": False,
            "rest_endpoint_behavior_changed": False,
        },
        "next_stage": {
            "stage": "Day71 Stage 2",
            "goal": "Add CI-safe endpoint probe / wrapper execution for selected covered endpoints.",
            "candidate_wrappers": planned_endpoint_ids,
        },
    }
