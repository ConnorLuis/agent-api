# Multi-Agent Architecture

This document describes the deterministic Multi-Agent workflow implemented in `agent-api` from Day52 through Day61.

The Multi-Agent system is intentionally built as a CI-safe, LLM-free engineering layer first. It focuses on explicit state, role boundaries, artifacts, streaming, and eval / trace consistency before introducing real LLM-driven planning or dynamic orchestration.

## Current status

```text
Day52: Multi-Agent state foundation
Day53: Deterministic Planner Agent
Day54: Deterministic Research Agent
Day55: Deterministic Tool Agent
Day56: Deterministic Critic Agent
Day57: Deterministic Memory Agent
Day58: Deterministic Reflection Agent
Day59: Deterministic Supervisor graph
Day60: Deterministic Multi-Agent streaming
Day61: Deterministic Multi-Agent eval / trace
```

Current execution chain:

```text
Planner
  ↓
Researcher
  ↓
Tool
  ↓
Critic
  ↓
Memory
  ↓
Reflection
  ↓
Supervisor
  ↓
Streaming
  ↓
Eval / Trace
```

The current implementation is deterministic by design:

```text
No LLM call.
No external tool execution.
No shell command execution.
No filesystem mutation from the Agent roles.
No external storage write.
No Neo4j connection from the Multi-Agent workflow.
No graph_fusion default switch.
```

## Design goals

The Multi-Agent stage is designed to prove the following engineering abilities:

```text
1. Explicit multi-role state modeling.
2. Deterministic role execution.
3. Structured task, event, artifact, and memory tracking.
4. Clear role boundaries.
5. Supervisor graph orchestration.
6. SSE streaming contract for Multi-Agent execution replay.
7. Eval / trace layer for validating graph and stream consistency.
8. CI-safe regression coverage.
```

The goal is not to immediately build an autonomous LLM agent. The current goal is to build a reliable, observable, and testable Multi-Agent backend foundation.

## State foundation

Day52 introduced the shared Multi-Agent state model.

Core state shape:

```text
MultiAgentState:
  task
  thread_id
  trace_id
  current_role
  tasks
  events
  artifacts
  memory
  final_answer
  status
```

Task shape:

```text
MultiAgentTask:
  task_id
  title
  description
  assigned_role
  status
  depends_on
  result
  metadata
```

Supported task statuses:

```text
pending
running
completed
failed
skipped
```

Event shape:

```text
MultiAgentEvent:
  event_id
  event_type
  role
  message
  metadata
```

Artifact shape:

```text
MultiAgentArtifact:
  artifact_id
  name
  artifact_type
  content
  created_by
  metadata
```

Memory shape:

```text
memory:
  planner
  researcher
  tool
  critic
  memory
  reflection
  supervisor
```

The state foundation is exposed through:

```text
POST /multi-agent/state-debug
```

This endpoint initializes the Multi-Agent state and returns the tasks, events, artifacts, memory, and state summary.

## Role responsibilities

### Planner

Endpoint:

```text
POST /multi-agent/plan-debug
```

Implementation module:

```text
src/app/multi_agent/planner.py
```

Responsibilities:

```text
1. Infer planning_mode.
2. Convert the initial user task into deterministic role-assigned tasks.
3. Store planner output in memory["planner"].
4. Create deterministic_multi_agent_plan artifact.
5. Keep execution boundary as planning_only.
```

Planner does not execute Researcher, Tool, Critic, Memory, Reflection, or Supervisor logic.

Key output fields:

```text
planner_role
planning_mode
objective
task_ids
constraints
next_role
execution_boundary
llm_used
```

Boundary:

```text
execution_boundary = planning_only
llm_used = false
```

### Researcher

Endpoint:

```text
POST /multi-agent/research-debug
```

Implementation module:

```text
src/app/multi_agent/researcher.py
```

Responsibilities:

```text
1. Consume the planner-generated researcher task.
2. Inspect planner context.
3. Produce deterministic research findings.
4. Store researcher output in memory["researcher"].
5. Create deterministic_research_notes artifact.
6. Keep execution boundary as research_only.
```

Researcher does not execute Tool, Critic, Memory, Reflection, or Supervisor logic.

Key output fields:

```text
researcher_role
planning_mode
objective
source_task_id
findings
constraints_checked
next_role
execution_boundary
llm_used
note
```

Boundary:

```text
execution_boundary = research_only
llm_used = false
```

### Tool

Endpoint:

```text
POST /multi-agent/tool-debug
```

Implementation module:

```text
src/app/multi_agent/tool_agent.py
```

Responsibilities:

```text
1. Consume the planner-generated tool task.
2. Produce deterministic tool execution records.
3. Simulate implementation steps in a CI-safe way.
4. Store tool output in memory["tool"].
5. Create deterministic_tool_execution_notes artifact.
6. Keep execution boundary as tool_simulation_only.
```

Tool Agent does not run real shell commands and does not modify repository files.

Key output fields:

```text
tool_role
planning_mode
objective
source_task_id
execution_records
constraints_checked
next_role
execution_boundary
llm_used
external_tools_used
note
```

Boundary:

```text
execution_boundary = tool_simulation_only
llm_used = false
external_tools_used = false
filesystem_modified = false
shell_commands_executed = false
```

### Critic

Endpoint:

```text
POST /multi-agent/critic-debug
```

Implementation module:

```text
src/app/multi_agent/critic.py
```

Responsibilities:

```text
1. Consume the planner-generated critic task.
2. Validate Planner / Researcher / Tool task transitions.
3. Validate Planner / Researcher / Tool memory outputs.
4. Validate artifact chain coverage.
5. Validate boundary flags.
6. Validate graph_fusion non-default boundary.
7. Store critic output in memory["critic"].
8. Create deterministic_critic_review artifact.
```

Critic validates previous outputs but does not execute Memory, Reflection, or Supervisor graph logic.

Key output fields:

```text
critic_role
planning_mode
objective
source_task_id
checks
passed_check_count
warning_check_count
failed_check_count
validation_pass
constraints_checked
next_role
execution_boundary
llm_used
note
```

Important checks:

```text
planner_initial_task_completed
researcher_task_completed
tool_task_completed
planner_memory_boundary
researcher_memory_boundary
tool_memory_boundary
artifact_chain_exists
future_agents_not_executed
supervisor_graph_not_started
graph_fusion_non_default_boundary
non_blocking_pending_planner_task
critic_task_available
```

Boundary:

```text
execution_boundary = critic_validation_only
llm_used = false
validation_pass = true
```

### Memory

Endpoint:

```text
POST /multi-agent/memory-debug
```

Implementation module:

```text
src/app/multi_agent/memory_agent.py
```

Responsibilities:

```text
1. Read critic.validation_pass.
2. Persist only Critic-approved memory.
3. Summarize Planner / Researcher / Tool / Critic outputs.
4. Store memory output in memory["memory"].
5. Create deterministic_memory_snapshot artifact.
6. Use only MultiAgentState memory and artifacts.
```

Memory Agent does not write to a real database, file system, vector store, or external storage.

Key output fields:

```text
memory_role
planning_mode
objective
source_task_id
approved
approval_source
memory_items
persisted_summary
storage_backend
persistence_mode
constraints_checked
next_role
execution_boundary
llm_used
external_storage_used
note
```

Boundary:

```text
execution_boundary = memory_snapshot_only
storage_backend = multi_agent_state_memory
persistence_mode = ci_safe_state_snapshot_only
llm_used = false
external_storage_used = false
```

### Reflection

Endpoint:

```text
POST /multi-agent/reflection-debug
```

Implementation module:

```text
src/app/multi_agent/reflection_agent.py
```

Responsibilities:

```text
1. Reflect on Planner / Researcher / Tool / Critic / Memory outputs.
2. Produce deterministic reflection items.
3. Build readiness_summary for the future Supervisor graph.
4. Store reflection output in memory["reflection"].
5. Create deterministic_reflection_report artifact.
```

Reflection Agent reviews prior outputs but does not start Supervisor graph by itself.

Key output fields:

```text
reflection_role
planning_mode
objective
source_task_id
reviewed_roles
reflection_items
readiness_summary
constraints_checked
next_role
execution_boundary
llm_used
external_tools_used
note
```

Reflection categories:

```text
planning_quality
research_grounding
tool_execution_safety
critic_validation
memory_snapshot
supervisor_readiness
```

Boundary:

```text
execution_boundary = reflection_only
llm_used = false
external_tools_used = false
```

### Supervisor

Endpoint:

```text
POST /multi-agent/supervisor-debug
```

Implementation module:

```text
src/app/multi_agent/supervisor_graph.py
```

Responsibilities:

```text
1. Build deterministic Supervisor graph.
2. Represent Planner / Researcher / Tool / Critic / Memory / Reflection as explicit graph nodes.
3. Represent graph edges explicitly.
4. Record execution_order.
5. Record role_readiness.
6. Validate orchestration_pass.
7. Store supervisor output in memory["supervisor"].
8. Create deterministic_supervisor_graph_report artifact.
9. Preserve existing role-specific debug endpoints.
```

Supervisor graph nodes:

```text
planner
researcher
tool
critic
memory
reflection
```

Supervisor graph edges:

```text
planner -> researcher
researcher -> tool
tool -> critic
critic -> memory
memory -> reflection
```

Execution order:

```text
planner
researcher
tool
critic
memory
reflection
```

Supervisor output fields:

```text
supervisor_role
planning_mode
objective
source_task_id
graph_name
graph_version
nodes
edges
execution_order
role_readiness
orchestration_pass
completed_role_count
constraints_checked
preserved_debug_endpoints
next_role
execution_boundary
llm_used
note
```

Boundary:

```text
execution_boundary = supervisor_orchestration_only
llm_used = false
orchestration_pass = true
```

## Endpoint overview

Role-specific debug endpoints:

```text
POST /multi-agent/state-debug
POST /multi-agent/plan-debug
POST /multi-agent/research-debug
POST /multi-agent/tool-debug
POST /multi-agent/critic-debug
POST /multi-agent/memory-debug
POST /multi-agent/reflection-debug
POST /multi-agent/supervisor-debug
```

Streaming endpoint:

```text
POST /multi-agent/stream
```

Eval / trace endpoint:

```text
POST /multi-agent/eval-debug
```

The role-specific endpoints are intentionally preserved after introducing Supervisor graph, streaming, and eval / trace.

## Streaming contract

Day60 introduced deterministic Multi-Agent streaming through:

```text
POST /multi-agent/stream
```

Implementation module:

```text
src/app/multi_agent/streaming.py
```

The streaming endpoint uses Server-Sent Events. The stream is a deterministic replay of Supervisor graph output. It does not perform token-level LLM streaming.

SSE content type:

```text
text/event-stream
```

SSE event format:

```text
event: <event_name>
data: <json_payload>
```

Expected event sequence:

```text
event: metadata
event: graph
event: node
event: node
event: node
event: node
event: node
event: node
event: edge
event: edge
event: edge
event: edge
event: edge
event: role
event: role
event: role
event: role
event: role
event: role
event: role
event: artifact
event: artifact
event: artifact
event: artifact
event: artifact
event: artifact
event: artifact
event: final
event: done
```

Compact form:

```text
metadata x1
graph x1
node x6
edge x5
role x7
artifact x7
final x1
done x1
```

### metadata event

Purpose:

```text
Stream-level identity and safety metadata.
```

Key fields:

```text
task
thread_id
trace_id
current_role
status
streaming_mode
llm_used
graph_fusion_default_changed
```

Expected values:

```text
streaming_mode = deterministic_replay
llm_used = false
graph_fusion_default_changed = false
```

### graph event

Purpose:

```text
Supervisor graph metadata.
```

Key fields:

```text
graph_name
graph_version
planning_mode
execution_order
orchestration_pass
completed_role_count
execution_boundary
```

Expected values:

```text
graph_name = deterministic_multi_agent_supervisor_graph
graph_version = day59_supervisor_graph_v1
orchestration_pass = true
completed_role_count = 6
execution_boundary = supervisor_orchestration_only
```

### node events

Purpose:

```text
Replay Supervisor graph nodes.
```

There are six node events:

```text
planner
researcher
tool
critic
memory
reflection
```

Key fields:

```text
node_id
role
status
memory_key
artifact_expected
summary
```

Expected value:

```text
status = completed
```

### edge events

Purpose:

```text
Replay explicit Supervisor graph edges.
```

There are five edge events:

```text
planner -> researcher
researcher -> tool
tool -> critic
critic -> memory
memory -> reflection
```

Key fields:

```text
source
target
condition
```

### role events

Purpose:

```text
Replay role readiness and role-level execution boundary.
```

There are seven role events:

```text
planner
researcher
tool
critic
memory
reflection
supervisor
```

Key fields:

```text
sequence
role
memory_present
artifact_count
completed_task_count
llm_used
execution_boundary
status
orchestration_pass   # supervisor role event only
```

Expected values:

```text
status = completed
llm_used = false
memory_present = true
artifact_count >= 1
completed_task_count >= 1
```

### artifact events

Purpose:

```text
Replay artifacts created by each deterministic role.
```

There are seven artifact events:

```text
planner
researcher
tool
critic
memory
reflection
supervisor
```

Key fields:

```text
artifact_id
name
artifact_type
created_by
```

Expected artifact names:

```text
deterministic_multi_agent_plan
deterministic_research_notes
deterministic_tool_execution_notes
deterministic_critic_review
deterministic_memory_snapshot
deterministic_reflection_report
deterministic_supervisor_graph_report
```

### final event

Purpose:

```text
Final stream summary.
```

Key fields:

```text
task
thread_id
trace_id
current_role
status
orchestration_pass
completed_role_count
artifact_count
event_count
preserved_debug_endpoints
llm_used
graph_fusion_default_changed
```

Expected values:

```text
status = completed
orchestration_pass = true
completed_role_count = 6
artifact_count = 7
llm_used = false
graph_fusion_default_changed = false
```

### done event

Purpose:

```text
Terminal stream marker.
```

Key fields:

```text
trace_id
status
```

Expected value:

```text
status = done
```

## Eval / trace contract

Day61 introduced deterministic Multi-Agent eval / trace through:

```text
POST /multi-agent/eval-debug
```

Implementation module:

```text
src/app/multi_agent/evaluation.py
```

The eval / trace layer validates that Supervisor graph output and streaming output are consistent.

The endpoint returns:

```text
task
thread_id
trace_id
current_role
status
planning_mode
eval_report
trace_report
supervisor
stream_events
tasks
events
artifacts
memory
summary
```

### eval_report

Purpose:

```text
Structured validation report for Supervisor graph output and stream output.
```

Key fields:

```text
eval_role
objective
planning_mode
eval_pass
checks
passed_check_count
warning_check_count
failed_check_count
constraints_checked
preserved_endpoints
execution_boundary
llm_used
note
```

Expected values:

```text
eval_role = multi_agent_eval_trace
eval_pass = true
failed_check_count = 0
execution_boundary = multi_agent_eval_trace_only
llm_used = false
```

Current checks:

```text
supervisor_orchestration_pass
stream_graph_matches_supervisor
stream_event_sequence
node_coverage
edge_coverage
role_stream_sequence
role_readiness_consistency
artifact_coverage
terminal_stream_events
trace_identity_consistency
boundary_flags
debug_endpoint_contracts
state_event_completion_coverage
trace_report_consistency
```

Each check has:

```text
check_name
status
summary
evidence
```

Supported check statuses:

```text
passed
failed
warning
```

### trace_report

Purpose:

```text
Compact trace summary for graph, stream, role, artifact, and boundary inspection.
```

Key fields:

```text
trace_id
thread_id
task
graph_name
graph_version
stream_event_count
state_event_count
stream_event_counts
execution_order
streamed_roles
artifact_creators
role_readiness_summary
boundary_flags
```

Expected values:

```text
graph_name = deterministic_multi_agent_supervisor_graph
graph_version = day59_supervisor_graph_v1
stream_event_count = 29
streamed_roles = planner / researcher / tool / critic / memory / reflection / supervisor
artifact_creators = planner / researcher / tool / critic / memory / reflection / supervisor
```

Boundary flags:

```text
llm_used = false
default_retrieval_backend = hybrid
graph_fusion_default_changed = false
streaming_mode = deterministic_replay
```

### supervisor

Purpose:

```text
The same Supervisor graph output used as the source of truth for eval / trace checks.
```

Important fields:

```text
orchestration_pass = true
completed_role_count = 6
execution_order = planner / researcher / tool / critic / memory / reflection
llm_used = false
```

### stream_events

Purpose:

```text
The deterministic stream event list used by eval / trace checks.
```

Expected sequence:

```text
metadata x1
graph x1
node x6
edge x5
role x7
artifact x7
final x1
done x1
```

## CI-safe and LLM-free boundaries

The Multi-Agent implementation is intentionally CI-safe.

Global boundaries:

```text
No LLM call.
No OpenAI call.
No Ollama call.
No model inference.
No real shell command execution.
No repository file mutation by Agent roles.
No external tool execution.
No external storage write.
No database write.
No Neo4j connection from Multi-Agent role execution.
No graph_fusion default switch.
```

Role boundary summary:

```text
Planner:
  planning_only

Researcher:
  research_only

Tool:
  tool_simulation_only

Critic:
  critic_validation_only

Memory:
  memory_snapshot_only

Reflection:
  reflection_only

Supervisor:
  supervisor_orchestration_only

Eval / Trace:
  multi_agent_eval_trace_only
```

All role-level outputs should include:

```text
llm_used = false
```

Tool Agent additionally includes:

```text
external_tools_used = false
filesystem_modified = false
shell_commands_executed = false
```

Memory Agent additionally includes:

```text
external_storage_used = false
```

## Why graph_fusion remains non-default

The project already supports GraphRAG through the explicit Agentic RAG retrieval backend:

```text
retrieval_backend = graph_fusion
```

However, the default retrieval backend remains:

```text
DEFAULT_RETRIEVAL_BACKEND = hybrid
```

Reason:

```text
1. graph_fusion is an explicit GraphRAG-capable backend, not the default path.
2. graph_fusion may depend on live Neo4j for full graph retrieval behavior.
3. CI-safe paths use graph_dry_run=true or deterministic fallbacks.
4. The hybrid backend remains the safest deterministic default for broad regression tests.
5. GraphRAG evaluation and manual validation exist, but default switching should require larger and more representative evaluation.
6. Multi-Agent should not silently change RAG backend behavior.
```

The Multi-Agent layer therefore validates this boundary repeatedly:

```text
graph_fusion remains a non-default retrieval backend.
graph_fusion_default_changed = false
default_retrieval_backend = hybrid
```

Day61 eval / trace checks also validate:

```text
DEFAULT_RETRIEVAL_BACKEND = hybrid
```

## Preserved endpoint contracts

Day61 validates that these endpoints remain preserved:

```text
/multi-agent/stream
/multi-agent/supervisor-debug
/multi-agent/plan-debug
/multi-agent/research-debug
/multi-agent/tool-debug
/multi-agent/critic-debug
/multi-agent/memory-debug
/multi-agent/reflection-debug
```

The purpose is to ensure that adding eval / trace does not break the role-specific debug workflow or the Day60 streaming contract.

## Manual validation commands

Run Multi-Agent tests:

```bash
pytest tests/multi_agent -q
```

Run full tests:

```bash
pytest -q
```

Check graph_fusion default boundary:

```bash
grep -R --exclude-dir=__pycache__ "DEFAULT_RETRIEVAL_BACKEND" -n src/app/rag

grep -R --exclude-dir=__pycache__ \
  "graph_fusion.*default\|DEFAULT_RETRIEVAL_BACKEND.*graph_fusion" \
  -n src/app tests || true
```

Expected default:

```text
src/app/rag/retrieval_backend_modules/normalization.py:1:DEFAULT_RETRIEVAL_BACKEND = "hybrid"
```

Validate streaming:

```bash
curl -N -X POST http://localhost:8000/multi-agent/stream \
  -H "Content-Type: application/json" \
  -H "x-trace-id: multi-agent-stream-doc-check-001" \
  -d '{"task":"验证 Multi-Agent stream 文档契约","thread_id":"multi-agent-doc-stream-thread"}'
```

Validate eval / trace:

```bash
curl -s -X POST http://localhost:8000/multi-agent/eval-debug \
  -H "Content-Type: application/json" \
  -H "x-trace-id: multi-agent-eval-doc-check-001" \
  -d '{"task":"验证 Multi-Agent eval trace 文档契约","thread_id":"multi-agent-doc-eval-thread"}' \
  | python -m json.tool --no-ensure-ascii
```

Expected eval / trace result:

```text
eval_report.eval_pass = true
eval_report.failed_check_count = 0
trace_report.boundary_flags.default_retrieval_backend = hybrid
trace_report.boundary_flags.graph_fusion_default_changed = false
```

## Current limitations

Current limitations are intentional:

```text
1. The role chain is deterministic.
2. The current stream is deterministic replay, not token-level generation.
3. Supervisor graph is explicit and fixed, not dynamic.
4. Tool Agent simulates tool execution instead of running real tools.
5. Memory Agent writes only to MultiAgentState memory and artifacts.
6. Eval / trace is a deterministic consistency check, not a live benchmark suite.
7. graph_fusion remains non-default.
```

These limitations make the system stable for CI and suitable as a foundation for later LLM-backed and production-grade Multi-Agent orchestration.

## Next milestone

Recommended next milestone:

```text
Day63: Multi-Agent interview material.
```

Day63 should convert this architecture into Chinese interview material:

```text
1. Multi-Agent project explanation.
2. Role-by-role implementation explanation.
3. Supervisor graph explanation.
4. SSE streaming explanation.
5. Eval / trace explanation.
6. CI-safe / LLM-free design rationale.
7. Common interview Q&A.
```
