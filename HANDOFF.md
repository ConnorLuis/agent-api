# HANDOFF.md

## Project

agent-api

## Current Status

Project 2 has officially started and is now the main development line.

`chat-api-v2` has been completed. Future review of that project will happen in the separate conversation named **Chat-API项目复习**.

Current `agent-api` status:

```text
Day1-Day27 completed.
Day27 completed: Agentic RAG Streaming.
Local pytest: 66 passed, 1 warning.
Git push: success.
GitHub Actions CI: green.
Next: Day28 answer verification, real embedding/vector DB preparation, or richer observability.
```

## Project Goal

Build an Agent backend service based on FastAPI + LangGraph.

Current direction:

```text
FastAPI
  ↓
LangGraph
  ↓
Tool Calling Agent
  ↓
Short-term memory
  ↓
Debug output
  ↓
pytest + README + CI
  ↓
Request tracing
  ↓
LLM provider abstraction
  ↓
Real LLM tool calling
  ↓
Streaming
  ↓
RAG tool
  ↓
Router Agent
  ↓
GraphRAG / Multi-Agent
```

## Environment

- OS: WSL2 Ubuntu
- Local path: `/home/dministrator/projects/agent-api`
- Windows path: `\\wsl.localhost\Ubuntu\home\dministrator\projects\agent-api`
- Conda env: `agentapi`
- Python: 3.10
- GitHub: `git@github.com:ConnorLuis/agent-api.git`
- Branch: `master`
- Local Ollama model verified: `qwen2.5:7b`

## Tech Stack

Current:

- FastAPI
- Uvicorn
- Pydantic
- LangGraph
- LangChain Core
- LangChain Ollama
- LangGraph prebuilt `ToolNode`
- LangGraph prebuilt `tools_condition`
- SQLite checkpoint saver
- Request logging middleware
- `ContextVar` based request trace context
- LLM provider abstraction
- Mock LLM provider
- Ollama LLM provider
- Real LLM tool calling path
- Server-Sent Events streaming endpoints
- Lightweight keyword-based RAG retriever
- RAG Search Debug endpoint
- Retrieval explainability metadata
- Local Markdown knowledge base
- Deterministic Router Agent
- Router delegation to existing deterministic Agent graph
- Router Agent SSE streaming endpoint
- Initial LLM Router Agent endpoint
- Mock LLM Router for CI-safe routing
- Ollama LLM Router for local manual routing
- Smart Chat unified entry point preview
- Smart Chat SSE streaming endpoint
- Route validation metadata layer
- Route fallback support
- RAG chunk pipeline for vector DB preparation
- RAG Chunks Debug endpoint
- Deterministic RAG vector-search debug endpoint
- Deterministic hashed embedding preview
- Cosine similarity based chunk ranking
- Hybrid Retrieval Debug endpoint
- Hybrid retrieval scoring with keyword_score, vector_score, and hybrid_score
- Agentic RAG Debug Graph
- Agentic RAG query analysis, query rewriting, hybrid retrieval, relevance grading, and citation-aware answering
- RAG Evaluation Debug endpoint
- RAG evaluation JSONL cases and metrics
- Observability Trace Store
- SQLite-backed trace events for Agentic RAG and RAG Evaluation
- Agentic RAG Streaming endpoint
- Agentic RAG SSE events for retrieval and direct paths
- pytest
- GitHub Actions CI

Not yet implemented:

- OpenAI provider
- Replacing `/agent/chat` with the real LLM Agent as the default route
- Making Smart Chat the default production entry point
- Vector database based RAG
- Embedding-based retrieval
- Document upload and parsing pipeline
- GraphRAG
- Multi-Agent Supervisor

---

## Current Project Structure

```text
agent-api/
├── README.md
├── HANDOFF.md
├── requirements.txt
├── pytest.ini
├── .env.example
├── .gitignore
├── .github/
│   └── workflows/
│       └── ci.yml
├── eval_cases/
│   └── rag_agentic_eval.jsonl
├── docs/
│   ├── DAY01.md
│   ├── DAY02.md
│   ├── DAY03.md
│   ├── DAY04.md
│   ├── DAY05.md
│   ├── DAY06.md
│   ├── DAY07.md
│   ├── DAY08.md
│   ├── DAY09.md
│   ├── DAY10.md
│   ├── DAY11.md
│   ├── DAY12.md
│   ├── DAY13.md
│   ├── DAY14.md
│   ├── DAY15.md
│   ├── DAY16.md
│   ├── DAY17.md
│   ├── DAY18.md
│   ├── DAY19.md
│   ├── DAY20.md
│   ├── DAY21.md
│   ├── DAY22.md
│   ├── DAY23.md
│   ├── DAY24.md
│   ├── DAY25.md
│   ├── DAY26.md
│   └── DAY27.md
├── knowledge/
│   └── agent_basics.md
├── data/
│   └── checkpoints.sqlite          # runtime only, ignored by Git
├── src/
│   └── app/
│       ├── main.py
│       ├── core/
│       │   ├── config.py
│       │   ├── logging.py
│       │   ├── middleware.py
│       │   ├── request_context.py
│       │   └── sse.py
│       ├── schemas/
│       │   ├── agent.py
│       │   ├── llm.py
│       │   ├── rag.py
│       │   └── observability.py
│       ├── routes/
│       │   ├── routes_agent.py
│       │   ├── routes_llm.py
│       │   ├── routes_rag.py
│       │   └── routes_observability.py
│       ├── evaluation/
│       │   ├── __init__.py
│       │   └── rag_eval.py
│       ├── observability/
│       │   ├── __init__.py
│       │   └── trace_store.py
│       ├── rag/
│       │   ├── __init__.py
│       │   ├── explain.py
│       │   ├── chunking.py
│       │   ├── vector_index.py
│       │   ├── hybrid.py
│       │   ├── agentic_graph.py
│       │   ├── agentic_streaming.py
│       │   └── retriever.py
│       ├── llm/
│       │   ├── base.py
│       │   ├── factory.py
│       │   ├── mock.py
│       │   └── ollama.py
│       └── agent/
│           ├── graph.py
│           ├── router_graph.py
│           ├── router_streaming.py
│           ├── streaming.py
│           ├── llm_router.py
│           ├── smart_router.py
│           ├── smart_streaming.py
│           ├── route_validation.py
│           ├── llm_graph.py
│           ├── llm_nodes.py
│           ├── state.py
│           ├── nodes.py
│           ├── tools.py
│           └── memory.py
└── tests/
    ├── conftest.py
    ├── test_health.py
    ├── test_agent_chat.py
    ├── test_agent_memory.py
    ├── test_agent_debug.py
    ├── test_trace.py
    ├── test_llm.py
    ├── test_stream.py
    ├── test_rag.py
    ├── test_rag_debug.py
    ├── test_rag_chunks.py
    ├── test_rag_vector_search.py
    ├── test_rag_hybrid_search.py
    ├── test_rag_agentic_debug.py
    ├── test_rag_eval.py
    ├── test_observability.py
    ├── test_rag_agentic_stream.py
    ├── test_router_agent.py
    ├── test_router_delegation.py
    ├── test_router_stream.py
    ├── test_llm_router.py
    ├── test_smart_chat.py
    ├── test_smart_stream.py
    ├── test_route_validation.py
    └── test_rag_chunks.py
```

---

## Current API

### Health

```text
GET /health
```

Expected:

```json
{"status":"ok"}
```

Response header includes:

```text
x-trace-id
```

### Agent Chat - Deterministic

```text
POST /agent/chat
```

Request:

```json
{
  "message": "请计算 3 加 5",
  "thread_id": "demo-thread-001"
}
```

Response:

```json
{
  "answer": "工具 `add` 执行结果：8",
  "thread_id": "demo-thread-001",
  "trace_id": "trace-or-client-provided-id"
}
```

This route now also supports deterministic RAG tool triggering for knowledge-base search questions.

### Agent Debug - Deterministic

```text
POST /agent/debug
```

Expected node path for arithmetic and RAG tool calls:

```text
agent -> tools -> agent
```

### LLM Chat

```text
POST /llm/chat
```

Current providers:

```text
mock
ollama
```

### Real LLM Tool Calling Agent

```text
POST /agent/llm-chat
```

This route uses Ollama + bound tools and lets the model decide whether to call tools.

Response fields:

```text
answer
thread_id
provider
model
trace_id
```

### Real LLM Tool Calling Debug / Stream

```text
POST /agent/llm-debug
POST /agent/stream
POST /agent/llm-stream
```

`/agent/llm-debug` is used to inspect whether the LLM really generated `tool_calls`.

`/agent/stream` is deterministic and covered by CI.

`/agent/llm-stream` depends on local Ollama and is manually verified.

### RAG Search

```text
POST /rag/search
POST /rag/search-debug
POST /rag/chunks-debug
POST /rag/vector-search-debug
POST /rag/hybrid-search-debug
POST /rag/agentic-debug
POST /rag/agentic-stream
POST /rag/eval-debug
GET /observability/traces/{trace_id}
GET /observability/traces
```

### Router Agent

```text
POST /agent/router-chat
POST /agent/router-debug
POST /agent/router-stream
POST /agent/llm-router-chat
POST /agent/smart-chat
POST /agent/smart-stream
```

Routes:

```text
calculator
rag
chat
```

`/agent/router-chat` returns `answer`, `route`, `thread_id`, and `trace_id`.

`/agent/router-debug` returns the selected route and node-level path, such as `router -> rag`.

### RAG Search

```text
POST /rag/search
```

Request:

```json
{
  "query": "RAG 是什么？",
  "k": 2
}
```

Response fields:

```text
query
results
trace_id
```

---

## Current Graph Strategy

### Deterministic graph

Used by:

```text
/agent/chat
/agent/debug
/agent/stream
```

Current message flow:

```text
HumanMessage
  ↓
AIMessage(tool_calls generated by deterministic rules)
  ↓
ToolMessage
  ↓
AIMessage(final answer)
```

Current deterministic tools:

```text
add
multiply
search_knowledge_base
```

Important:

```text
/agent/chat remains deterministic for stable tests and CI.
/agent/chat now supports RAG tool triggering through search_knowledge_base.
/agent/debug can show the RAG tool-call path.
```

### Real LLM Tool Calling graph

Used by:

```text
/agent/llm-chat
/agent/llm-debug
/agent/llm-stream
```

Current message flow:

```text
HumanMessage
  ↓
AIMessage(tool_calls generated by Ollama model)
  ↓
ToolMessage
  ↓
AIMessage(final answer generated by Ollama model)
```

Important:

```text
/agent/llm-chat is the Day10 real LLM tool-calling route.
CI does not test Ollama-dependent behavior.
```

---

## Current Memory Strategy

Current short-term memory strategy:

```text
SqliteSaver + thread_id
```

SQLite checkpoint file:

```text
data/checkpoints.sqlite
```

SQLite runtime files may also appear:

```text
data/checkpoints.sqlite-shm
data/checkpoints.sqlite-wal
```

These files are runtime data and are ignored by Git.

Expected tables:

```text
checkpoints
writes
```

Important:

```text
thread_id is passed through config.configurable.thread_id.
thread_id in State is only for application-level response tracking.
The actual LangGraph checkpoint lookup depends on config.configurable.thread_id.
```

---

## Current Observability Strategy

Current request tracing strategy:

```text
TraceLoggingMiddleware + x-trace-id + ContextVar
```

Rules:

```text
Client provides x-trace-id:
  reuse the client trace id.

Client does not provide x-trace-id:
  generate trace-xxxxxxxxxxxx.
```

Response header:

```text
x-trace-id
```

Agent, LLM, and RAG response body:

```text
trace_id
```

Current log fields:

```text
method
path
status_code
latency_ms
trace_id
```

Example log:

```text
request_completed method=POST path=/rag/search status_code=200 latency_ms=12.34 trace_id=day12-rag-search-001
```

---

## Current LLM Provider Strategy

Current LLM provider strategy:

```text
ChatProvider Protocol
  ↓
MockChatProvider / OllamaChatProvider
  ↓
get_chat_provider()
  ↓
/llm/chat and /agent/llm-chat
```

Current providers:

```text
mock
ollama
```

Current LLM endpoints:

```text
POST /llm/chat
POST /agent/llm-chat
POST /agent/llm-debug
POST /agent/stream
POST /agent/llm-stream
```

Important:

```text
/llm/chat tests provider abstraction.
/agent/llm-chat uses Ollama tool calling.
/agent/llm-debug verifies tool_calls and node path.
CI only tests mock provider and deterministic endpoints.
Ollama provider and real tool calling are verified manually in local WSL/Ollama environment.
```

---

## Current Streaming Strategy

Day11 added Server-Sent Events streaming while keeping stable and Ollama-dependent paths separate.

Current streaming endpoints:

```text
POST /agent/stream
POST /agent/llm-stream
```

`/agent/stream` uses the deterministic Agent path and is covered by pytest/CI.

Expected deterministic SSE events:

```text
metadata
answer_chunk
final
done
```

`/agent/llm-stream` uses the real Ollama-backed LLM Tool Calling Agent graph and is manually verified locally.

Expected real LLM SSE events:

```text
metadata
step(agent)
step(tools)
step(agent)
final
done
```

Important:

```text
SSE data is serialized with ensure_ascii=False, so Chinese text remains readable in terminal output.
CI tests /agent/stream only; it does not depend on local Ollama.
```

---

## Current RAG Strategy

Day12 added a lightweight local RAG search path.

Current RAG files:

```text
knowledge/agent_basics.md
src/app/rag/retriever.py
src/app/routes/routes_rag.py
src/app/schemas/rag.py
tests/test_rag.py
```

Current retriever:

```text
search_knowledge(query, k)
```

Current RAG API:

```text
POST /rag/search
```

Current Agent tool:

```text
search_knowledge_base(query, k)
```

Current Agent RAG flow:

```text
User asks a knowledge-base question
  ↓
agent_node creates AIMessage(tool_calls=[search_knowledge_base])
  ↓
ToolNode executes search_knowledge_base
  ↓
search_knowledge reads knowledge/*.md
  ↓
Agent summarizes ToolMessage as final answer
```

Important:

```text
Day12 intentionally uses keyword retrieval instead of embeddings/vector DB.
This keeps CI deterministic and avoids external services.
Knowledge files are stored under knowledge/ and should be UTF-8 encoded.
Do not put source-controlled knowledge files under data/, because data/ is runtime-only and ignored by Git.
```

---

## Current Router Agent Strategy

Day13 added a separate deterministic Router Agent graph.

Current Router files:

```text
src/app/agent/router_graph.py
tests/test_router_agent.py
```

Current Router endpoints:

```text
POST /agent/router-chat
POST /agent/router-debug
```

Current routes:

```text
calculator
rag
chat
```

Router graph:

```text
START
  ↓
router
  ├── calculator
  ├── rag
  └── chat
```

Important:

```text
Router Agent is deterministic and CI-safe.
It does not depend on Ollama.
It does not replace /agent/chat yet.
Day14 connects `calculator` and `rag` routes to the existing deterministic Agent graph through `invoke_agent()`, so the Router now reuses existing tools and SQLite short-term memory for delegated routes.
```

---

## Current Router Delegation Strategy

Day14 upgraded the Router Agent from simple branch handling to delegation.

Current behavior:

```text
calculator route
  ↓
invoke_agent()
  ↓
existing add / multiply tools
  ↓
existing SQLite short-term memory
```

```text
rag route
  ↓
invoke_agent()
  ↓
existing search_knowledge_base tool
  ↓
existing SQLite short-term memory
```

```text
chat route
  ↓
Router chat response
```

Important:

```text
Router calculator and RAG routes now share the same thread_id with invoke_agent().
This means Router-triggered tool calls can be remembered by /agent/chat.
Router does not duplicate calculator or RAG implementation logic anymore.
```

New Day14 test file:

```text
tests/test_router_delegation.py
```

---

## Current Router Streaming Strategy

Day15 added SSE streaming for the deterministic Router Agent.

Current Router streaming file:

```text
src/app/agent/router_streaming.py
```

Current Router streaming endpoint:

```text
POST /agent/router-stream
```

Current event sequence:

```text
metadata
route
answer_chunk
final
done
```

Supported routes:

```text
calculator
rag
chat
```

Important:

```text
/agent/router-stream is deterministic and CI-safe.
It reuses invoke_router_agent().
answer_chunk currently emits the complete answer as one chunk.
The event contract prepares the project for future token-level LLM streaming.
```

New Day15 test file:

```text
tests/test_router_stream.py
```

---

## Current LLM Router Strategy

Day16 added an initial LLM Router Agent.

Current LLM Router file:

```text
src/app/agent/llm_router.py
```

Current LLM Router endpoint:

```text
POST /agent/llm-router-chat
```

Current router providers:

```text
mock
ollama
```

Provider strategy:

```text
router_provider="mock"
  ↓
CI-safe deterministic route decision
  ↓
mock-router
```

```text
router_provider="ollama"
  ↓
local Ollama route decision
  ↓
qwen2.5:7b
```

Execution strategy after route decision:

```text
calculator -> invoke_agent()
rag        -> invoke_agent()
chat       -> Router chat response
```

Important:

```text
mock provider is covered by pytest and CI.
ollama provider is manually verified locally.
The LLM Router does not replace /agent/router-chat yet.
```

New Day16 test file:

```text
tests/test_llm_router.py
```

---

## Current Smart Chat Strategy

Day17 added Smart Chat as a future unified Agent entry point preview.

Current Smart Chat file:

```text
src/app/agent/smart_router.py
```

Current Smart Chat endpoint:

```text
POST /agent/smart-chat
```

Router mode strategy:

```text
router_mode="deterministic"
  ↓
invoke_router_agent()
  ↓
deterministic Router Agent
```

```text
router_mode="llm"
  ↓
invoke_llm_router_agent()
  ↓
mock or Ollama LLM Router
```

Unified response fields:

```text
answer
route
route_reason
router_mode
router_provider
router_model
thread_id
trace_id
```

Important:

```text
/agent/smart-chat does not replace /agent/chat yet.
It is a compatibility-safe preview of the future unified entry point.
deterministic and llm+mock modes are covered by pytest and CI.
llm+ollama mode is manually verified locally.
```

New Day17 test file:

```text
tests/test_smart_chat.py
```

---

## Current RAG Search Debug Strategy

Day18 added a RAG search-debug endpoint for retrieval explainability.

Current RAG debug file:

```text
src/app/rag/explain.py
```

Current RAG debug endpoint:

```text
POST /rag/search-debug
```

Current debug function:

```text
explain_search_knowledge(query, k)
```

Returned debug fields:

```text
query
normalized_query
k
rank
source
score
content
preview
matched_terms
content_length
trace_id
```

Important:

```text
/rag/search-debug does not replace /rag/search.
It exposes retrieval-level observability.
It helps distinguish retrieval failures from answer-generation failures.
It still uses the existing keyword retriever, so CI remains deterministic.
```

New Day18 test file:

```text
tests/test_rag_debug.py
```

---

## Current Smart Stream Strategy

Day19 added Smart Stream as the SSE streaming version of Smart Chat.

Current Smart Stream file:

```text
src/app/agent/smart_streaming.py
```

Current Smart Stream endpoint:

```text
POST /agent/smart-stream
```

Current streaming function:

```text
stream_smart_agent_events()
```

It reuses:

```text
invoke_smart_agent()
```

Current event sequence:

```text
metadata
route
answer_chunk
final
done
```

Supported modes:

```text
router_mode="deterministic"
router_mode="llm", router_provider="mock"
router_mode="llm", router_provider="ollama"  # local manual verification only
```

Important:

```text
deterministic and llm+mock modes are covered by pytest and CI.
llm+ollama mode is manually verified locally.
answer_chunk currently emits the complete answer as one chunk.
```

New Day19 test file:

```text
tests/test_smart_stream.py
```

---

## Current Route Validation Strategy

Day20 added route validation metadata and fallback support.

Current route validation file:

```text
src/app/agent/route_validation.py
```

Current route validation function:

```text
validate_route_decision()
```

Returned metadata:

```text
route_confidence
route_valid
fallback_used
validation_reason
```

Confidence strategy:

```text
deterministic -> 1.0
mock          -> 1.0
ollama        -> 0.85
unknown       -> 0.5
invalid route -> 0.0
```

Fallback behavior:

```text
invalid route -> fallback to chat
```

Applied endpoints:

```text
POST /agent/llm-router-chat
POST /agent/smart-chat
POST /agent/smart-stream
```

New Day20 test file:

```text
tests/test_route_validation.py
```

---

## Current RAG Chunk Pipeline Strategy

Day21 added a deterministic chunk pipeline for vector DB preparation.

Current chunking file:

```text
src/app/rag/chunking.py
```

Current chunk debug endpoint:

```text
POST /rag/chunks-debug
```

Current chunking functions:

```text
split_text_into_chunks()
load_markdown_documents()
load_knowledge_chunks()
debug_knowledge_chunks()
```

Request fields:

```text
source_filter
max_chars
```

Returned metadata:

```text
source_filter
max_chars
total_chunks
chunk_id
source
index
content
preview
content_length
trace_id
```

Important:

```text
Day21 does not add embeddings or a vector database yet.
It prepares the deterministic document loading and chunk metadata layer.
This keeps CI stable while preparing for vector DB based RAG.
```

New Day21 test file:

```text
tests/test_rag_chunks.py
```

---

## Current Deterministic Vector Search Strategy

Day22 added a deterministic vector-search debug layer.

Current vector search file:

```text
src/app/rag/vector_index.py
```

Current vector-search debug endpoint:

```text
POST /rag/vector-search-debug
```

Current functions:

```text
build_deterministic_embedding()
cosine_similarity()
vector_search_knowledge()
```

It reuses the Day21 chunk pipeline:

```text
load_knowledge_chunks()
```

Request fields:

```text
query
top_k
source_filter
max_chars
embedding_dim
```

Returned metadata:

```text
query
top_k
source_filter
max_chars
embedding_dim
total_chunks
rank
chunk_id
source
index
score
content
preview
matched_terms
content_length
trace_id
```

Important:

```text
Day22 does not add a real embedding model or vector database yet.
It uses deterministic hashed embeddings so tests remain stable.
The API shape prepares the project for later real embeddings or vector DB integration.
```

New Day22 test file:

```text
tests/test_rag_vector_search.py
```

---

## Current Hybrid Retrieval Strategy

Day23 added a hybrid retrieval debug layer.

Current hybrid retrieval file:

```text
src/app/rag/hybrid.py
```

Current hybrid retrieval debug endpoint:

```text
POST /rag/hybrid-search-debug
```

Current function:

```text
hybrid_search_knowledge()
```

It reuses:

```text
load_knowledge_chunks()
build_deterministic_embedding()
cosine_similarity()
```

Request fields:

```text
query
top_k
source_filter
max_chars
embedding_dim
keyword_weight
vector_weight
```

Returned metadata:

```text
query
top_k
source_filter
max_chars
embedding_dim
keyword_weight
vector_weight
total_chunks
rank
chunk_id
source
index
hybrid_score
keyword_score
vector_score
content
preview
matched_terms
content_length
trace_id
```

Important:

```text
Day23 combines keyword retrieval signal and deterministic vector retrieval signal.
It exposes score components for retrieval debugging and future reranking or evaluation.
```

New Day23 test file:

```text
tests/test_rag_hybrid_search.py
```

---

## Current Agentic RAG Strategy

Day24 added an Agentic RAG debug graph.

Current Agentic RAG file:

```text
src/app/rag/agentic_graph.py
```

Current Agentic RAG endpoint:

```text
POST /rag/agentic-debug
```

Current graph state:

```text
AgenticRagState
```

Current graph nodes:

```text
query_analyzer
query_rewriter
hybrid_retrieve
relevance_grade
answer_with_citations
direct_answer
```

Current function:

```text
invoke_agentic_rag()
```

It reuses:

```text
hybrid_search_knowledge()
```

Retrieval path:

```text
query_analyzer -> query_rewriter -> hybrid_retrieve -> relevance_grade -> answer_with_citations
```

Direct path:

```text
query_analyzer -> direct_answer
```

Returned metadata:

```text
query
rewritten_query
retrieval_needed
relevance_score
citations
retrieval_results
final_answer
steps
trace_id
```

Important:

```text
Day24 turns RAG into a debuggable workflow instead of a single retrieval endpoint.
It supports both retrieval and non-retrieval paths.
```

New Day24 test file:

```text
tests/test_rag_agentic_debug.py
```

---

## Current Agentic RAG Streaming Strategy

Day27 added an Agentic RAG SSE streaming endpoint.

Current streaming file:

```text
src/app/rag/agentic_streaming.py
```

Current endpoint:

```text
POST /rag/agentic-stream
```

Current function:

```text
stream_agentic_rag_events()
```

It reuses:

```text
invoke_agentic_rag()
record_trace_event()
```

Retrieval path event sequence:

```text
metadata
decision
rewrite
retrieval
relevance
citation
answer_chunk
final
done
```

Direct path event sequence:

```text
metadata
decision
answer_chunk
final
done
```

Stream observability event:

```text
rag_agentic_stream
```

Stored trace payload:

```text
query
rewritten_query
retrieval_needed
relevance_score
citations
steps
retrieval_results_count
```

Important:

```text
Day27 makes Agentic RAG suitable for real-time frontend display.
It streams the same decision chain that /rag/agentic-debug returns as a single JSON payload.
```

New Day27 test file:

```text
tests/test_rag_agentic_stream.py
```

---

## Day1 - Project Initialization

### Completed

- Created project directory
- Created conda env `agentapi`
- Initialized FastAPI app
- Added `/health`
- Added `/agent/chat` mock endpoint
- Added Pydantic request/response schemas
- Initialized Git repository
- Connected GitHub remote
- Pushed initial commit to `master`

### Verified

```bash
curl http://localhost:8000/health
```

Expected:

```json
{"status":"ok"}
```

---

## Day2 - Minimal LangGraph Agent

### Completed

- Added `AgentState`
- Added minimal `agent_node`
- Added `build_agent_graph()`
- Added compiled `agent_graph`
- Added `invoke_agent()`
- Updated `/agent/chat` to call LangGraph instead of returning mock response

### Graph

```text
START -> agent -> END
```

---

## Day3 - Minimal Tool Calling Agent

### Completed

- Switched `AgentState` to `MessagesState`
- Added `add` tool
- Added `multiply` tool
- Added `ToolNode(tools)`
- Added `tools_condition`
- Updated `agent_node` to generate deterministic mock `tool_calls`
- Verified full message flow:
  - `HumanMessage`
  - `AIMessage(tool_calls)`
  - `ToolMessage`
  - `AIMessage(final answer)`

---

## Day4 - InMemorySaver Short-Term Memory

### Completed

- Added `InMemorySaver`
- Added `config.configurable.thread_id`
- Added automatic `thread_id` generation when request does not provide one
- Added deterministic memory response logic
- Verified same-thread memory
- Verified different-thread memory isolation

### Memory Formula

```text
Short-term memory = checkpointer + thread_id
```

---

## Day5 - SQLite Persistent Short-Term Memory

### Completed

- Installed `langgraph-checkpoint-sqlite`
- Added `src/app/agent/memory.py`
- Replaced `InMemorySaver` with `SqliteSaver`
- SQLite checkpoint file path: `data/checkpoints.sqlite`
- `/agent/chat` keeps using `thread_id` for short-term memory
- Same `thread_id` can restore conversation state after service restart
- Verified SQLite tables: `checkpoints`, `writes`
- Verified memory restoration across new Python process

---

## Day6 - Agent Debug Output

### Completed

- Added `DebugMessage`
- Added `DebugStep`
- Added `AgentDebugResponse`
- Added `serialize_message()`
- Added `debug_agent()`
- Added `/agent/debug`
- Used `graph.stream(..., stream_mode="updates")` to inspect node-level updates
- Used `graph.get_state(config)` to inspect final checkpoint state
- Verified normal debug path: `agent`
- Verified tool-call debug path: `agent -> tools -> agent`
- Verified `/agent/chat` still works

Commit:

```text
9a01e28 add agent debug endpoint
```

---

## Day7 - pytest + README.md + CI

### Completed

- Fixed SQLite runtime files being tracked by Git
- Updated `.gitignore` for runtime SQLite files
- Removed tracked `data/checkpoints.sqlite-shm` and `data/checkpoints.sqlite-wal` from Git
- Added split pytest tests
- Added `tests/conftest.py`
- Added `pytest.ini`
- Added README.md initial version
- Added GitHub Actions CI
- Fixed CI dependency installation issue by replacing `pip freeze` output with a minimal hand-maintained `requirements.txt`
- Verified local pytest
- Verified GitHub Actions CI

### Local pytest Result

```text
8 passed, 1 warning
```

---

## Day8 - Request Logging Middleware + x-trace-id

### Completed

- Added `src/app/core/logging.py` logging setup
- Added `src/app/core/middleware.py`
- Added `TraceLoggingMiddleware`
- Added `src/app/core/request_context.py`
- Added request-scoped `trace_id` context
- Registered middleware in `main.py`
- Added `x-trace-id` response header
- Reused client-provided `x-trace-id`
- Auto-generated `trace-*` when request does not provide one
- Added `trace_id` to `/agent/chat` response body
- Added `trace_id` to `/agent/debug` response body
- Added trace tests in `tests/test_trace.py`
- Expanded pytest from 8 tests to 12 tests
- Verified local pytest
- Verified GitHub Actions CI

### Test Result

```text
12 passed, 1 warning
```

---

## Day9 - Ollama LLM Provider Abstraction

### Completed

- Installed and added `langchain-ollama`
- Updated minimal `requirements.txt`
- Updated LLM-related settings in `src/app/core/config.py`
- Added `ChatProvider` protocol
- Added `MockChatProvider`
- Added `OllamaChatProvider`
- Added `get_chat_provider()`
- Added `LLMChatRequest`
- Added `LLMChatResponse`
- Added `/llm/chat`
- Registered LLM router in `main.py`
- Added `tests/test_llm.py`
- Verified mock provider with curl
- Verified Ollama provider with local `qwen2.5:7b`
- Expanded pytest from 12 tests to 14 tests
- Verified GitHub Actions CI

### Current Providers

```text
mock
ollama
```

### Test Result

```text
14 passed, 1 warning
```

### CI Result

```text
GitHub Actions CI: green
```

### Commit

```text
77cefb0 add ollama llm provider abstraction
```

### Note

`/agent/chat` still uses deterministic tool-call logic. Real LLM tool calling is introduced through `/agent/llm-chat` in Day10.

---

## Day10 - Real LLM Tool Calling Agent

### Completed

- Added real LLM Tool Calling Agent node
- Added `src/app/agent/llm_nodes.py`
- Added `src/app/agent/llm_graph.py`
- Added `OllamaChatProvider.bind_tools()`
- Added `AgentLLMChatResponse`
- Added `/agent/llm-chat`
- Added `/agent/llm-debug`
- Reused existing `add` and `multiply` tools
- Reused `ToolNode(tools)` and `tools_condition`
- Kept `SqliteSaver + thread_id` short-term memory
- Kept `x-trace-id` and response body `trace_id`
- Verified addition tool call through Ollama
- Verified multiplication tool call through Ollama
- Verified debug node path `agent -> tools -> agent`
- Verified `tool_calls` generated by the LLM, not by deterministic rules
- Verified local pytest
- Verified GitHub Actions CI

### New Endpoints

```text
POST /agent/llm-chat
POST /agent/llm-debug
POST /agent/stream
POST /agent/llm-stream
```

### Verified Addition

```bash
curl -s -X POST http://localhost:8000/agent/llm-chat \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day10-llm-add-001" \
  -d '{"message":"请计算 13 加 29，必须使用工具。","thread_id":"day10-llm-add-001"}'
```

Result:

```json
{
  "answer": "计算结果是 42。",
  "thread_id": "day10-llm-add-001",
  "provider": "ollama",
  "model": "qwen2.5:7b",
  "trace_id": "day10-llm-add-001"
}
```

### Verified Multiplication

```bash
curl -s -X POST http://localhost:8000/agent/llm-chat \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day10-llm-mul-001" \
  -d '{"message":"请计算 8 乘 9，必须使用工具。","thread_id":"day10-llm-mul-001"}'
```

Result:

```json
{
  "answer": "计算结果是 72。",
  "thread_id": "day10-llm-mul-001",
  "provider": "ollama",
  "model": "qwen2.5:7b",
  "trace_id": "day10-llm-mul-001"
}
```

### Verified Debug Path

Addition debug showed:

```text
agent -> tools -> agent
```

The LLM-generated tool call was:

```json
{
  "name": "add",
  "args": {
    "a": 13,
    "b": 29
  }
}
```

Multiplication debug showed:

```text
agent -> tools -> agent
```

The LLM-generated tool call was:

```json
{
  "name": "multiply",
  "args": {
    "a": 8,
    "b": 9
  }
}
```

### Test Result

```text
14 passed, 1 warning
```

### CI Result

```text
GitHub Actions CI: green
```

### Notes

Real LLM tool calling is verified manually because CI does not have access to local Ollama.

When using `python -m json.tool`, Chinese characters may be escaped as Unicode sequences. Prefer:

```bash
python -m json.tool --no-ensure-ascii
```

---

## Day11 - Streaming Response / SSE

### Completed

- Added `src/app/core/sse.py`
- Added `sse_event()` helper
- Added `src/app/agent/streaming.py`
- Added deterministic stream generator `stream_agent_events()`
- Added real LLM graph-step stream generator `stream_llm_agent_events()`
- Added `/agent/stream`
- Added `/agent/llm-stream`
- Kept `x-trace-id` response header behavior
- Kept `trace_id` inside SSE payloads
- Kept `thread_id` inside SSE payloads
- Used `ensure_ascii=False` so Chinese output is readable
- Added `tests/test_stream.py`
- Expanded pytest from 14 tests to 16 tests
- Verified deterministic stream manually
- Verified real LLM tool-calling stream manually
- Verified local pytest
- Verified GitHub Actions CI

### New Endpoints

```text
POST /agent/stream
POST /agent/llm-stream
```

### Verified Deterministic Stream

```bash
curl -N -X POST http://localhost:8000/agent/stream \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day11-stream-add-001" \
  -d '{"message":"请计算 3 加 5","thread_id":"day11-stream-add-001"}'
```

Observed events:

```text
event: metadata
event: answer_chunk
event: final
event: done
```

Observed final answer:

```text
工具 `add` 执行结果：8
```

### Verified Real LLM Tool Calling Stream

```bash
curl -N -X POST http://localhost:8000/agent/llm-stream \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day11-llm-stream-add-001" \
  -d '{"message":"请计算 13 加 29，必须使用 add 工具。","thread_id":"day11-llm-stream-add-001"}'
```

Observed event sequence:

```text
metadata -> step(agent) -> step(tools) -> step(agent) -> final -> done
```

Observed tool call:

```json
{
  "name": "add",
  "args": {
    "a": 13,
    "b": 29
  }
}
```

Observed tool result:

```text
42
```

Observed final answer:

```text
计算结果是 42。
```

### Test Result

```text
16 passed, 1 warning
```

### CI Result

```text
GitHub Actions CI: green
```

### Notes

`/agent/stream` is deterministic and covered by CI.

`/agent/llm-stream` depends on local Ollama and is verified manually.

---

## Day12 - Lightweight RAG Search Tool

### Completed

- Added `knowledge/agent_basics.md`
- Added `src/app/rag/__init__.py`
- Added `src/app/rag/retriever.py`
- Added lightweight keyword-based retriever `search_knowledge()`
- Added `src/app/schemas/rag.py`
- Added `src/app/routes/routes_rag.py`
- Added `/rag/search`
- Registered RAG router in `main.py`
- Added `search_knowledge_base` tool
- Updated deterministic `agent_node` to trigger `search_knowledge_base`
- Updated RAG ToolMessage summarization
- Added `tests/test_rag.py`
- Expanded pytest from 16 tests to 19 tests
- Verified `/rag/search`
- Verified `/agent/chat` RAG tool path
- Verified `/agent/debug` RAG tool path
- Moved knowledge base from `data/knowledge` to `knowledge/` so CI can track it
- Converted `knowledge/agent_basics.md` to UTF-8 to avoid `UnicodeDecodeError`
- Verified local pytest
- Verified GitHub Actions CI

### New Endpoint

```text
POST /rag/search
```

### New Tool

```text
search_knowledge_base
```

### Verified RAG Search

```bash
curl -s -X POST http://localhost:8000/rag/search \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day12-rag-search-001" \
  -d '{"query":"RAG 是什么？","k":2}' \
  | python -m json.tool --no-ensure-ascii
```

Observed result:

```text
source: knowledge/agent_basics.md
content includes: RAG 是 Retrieval-Augmented Generation 的缩写
```

### Verified Agent RAG Tool

```bash
curl -s -X POST http://localhost:8000/agent/chat \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day12-agent-rag-001" \
  -d '{"message":"请搜索知识库：RAG 是什么？","thread_id":"day12-agent-rag-001"}' \
  | python -m json.tool --no-ensure-ascii
```

Observed answer starts with:

```text
根据知识库检索结果：
```

### Verified Debug Path

```bash
curl -s -X POST http://localhost:8000/agent/debug \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day12-debug-rag-001" \
  -d '{"message":"请搜索知识库：LangGraph 是什么？","thread_id":"day12-debug-rag-001"}' \
  | python -m json.tool --no-ensure-ascii
```

Observed node path:

```text
agent -> tools -> agent
```

Observed tool call:

```json
{
  "name": "search_knowledge_base",
  "args": {
    "query": "请搜索知识库：LangGraph 是什么？",
    "k": 3
  }
}
```

### Test Result

```text
57 passed, 1 warning
```

### CI Result

```text
GitHub Actions CI: green
```

### Notes

Day12 intentionally uses keyword retrieval instead of embedding/vector DB based retrieval.

This keeps local tests and GitHub Actions deterministic.

Knowledge base files should stay under:

```text
knowledge/
```

and must be UTF-8 encoded.

---

## Day13 - Deterministic Router Agent

### Completed

- Added `src/app/agent/router_graph.py`
- Added deterministic route classification
- Added `calculator` route
- Added `rag` route
- Added `chat` route
- Added `/agent/router-chat`
- Added `/agent/router-debug`
- Added `AgentRouterChatResponse`
- Added `AgentRouterDebugResponse`
- Added `tests/test_router_agent.py`
- Verified calculator route
- Verified RAG route
- Verified chat route
- Verified debug route path `router -> rag`
- Fixed router condition behavior by classifying from the input message instead of depending on unstable graph state propagation
- Fixed `debug_router_agent()` handling for `None` node updates from LangGraph stream
- Expanded pytest from 19 tests to 23 tests
- Verified local pytest
- Verified GitHub Actions CI

### New Endpoints

```text
POST /agent/router-chat
POST /agent/router-debug
```

### Test Result

```text
57 passed, 1 warning
```

### CI Result

```text
GitHub Actions CI: green
```

---

## Day14 - Router Agent Delegation

### Completed

- Updated `src/app/agent/router_graph.py`
- Added delegation helper for Router branches
- Changed `calculator_node` to call existing `invoke_agent()`
- Changed `rag_node` to call existing `invoke_agent()`
- Kept `chat_node` deterministic and local to the Router Agent
- Preserved same `thread_id` when delegating to `invoke_agent()`
- Verified Router calculator route still returns `工具 `multiply` 执行结果：36`
- Verified Router RAG route still returns `根据知识库检索结果：`
- Verified Router calculator route writes into existing Agent memory
- Verified `/agent/chat` can recall a Router-triggered calculation with the same `thread_id`
- Added `tests/test_router_delegation.py`
- Expanded pytest from 23 tests to 25 tests
- Verified local pytest
- Verified GitHub Actions CI

### New Test File

```text
tests/test_router_delegation.py
```

### Verified Memory Delegation

Router call:

```text
POST /agent/router-chat
message: 请计算 4 乘 9
thread_id: day14-router-memory-001
```

Response:

```text
工具 `multiply` 执行结果：36
```

Follow-up normal Agent call:

```text
POST /agent/chat
message: 我刚才计算了什么？
thread_id: day14-router-memory-001
```

Response:

```text
我记得上一轮工具 `multiply` 的执行结果是：36
```

### Test Result

```text
57 passed, 1 warning
```

### CI Result

```text
GitHub Actions CI: green
```

### Notes

Day14 proves that Router Agent can reuse existing Agent capabilities instead of duplicating calculator and RAG logic.

This makes Router Agent closer to a future unified entry point.

---

## Day15 - Router Agent SSE Streaming

### Completed

- Added `src/app/agent/router_streaming.py`
- Added `stream_router_agent_events()`
- Added `/agent/router-stream`
- Reused existing `invoke_router_agent()`
- Added SSE event sequence: `metadata -> route -> answer_chunk -> final -> done`
- Verified calculator route streaming
- Verified RAG route streaming
- Verified chat route streaming
- Fixed early stream event naming from `final_answer` to `answer_chunk`
- Fixed stream completion so `final` and `done` are emitted
- Added `tests/test_router_stream.py`
- Expanded pytest from 25 tests to 28 tests
- Verified local pytest
- Verified GitHub Actions CI

### New Endpoint

```text
POST /agent/router-stream
```

### New Files

```text
src/app/agent/router_streaming.py
tests/test_router_stream.py
```

### Verified Event Sequence

```text
metadata -> route -> answer_chunk -> final -> done
```

### Test Result

```text
57 passed, 1 warning
```

### CI Result

```text
GitHub Actions CI: green
```

### Notes

Day15 gives the Router Agent a complete API surface:

```text
/agent/router-chat
/agent/router-debug
/agent/router-stream
```

The stream currently emits the full answer as a single `answer_chunk`, because the deterministic Router does not generate token-level output.

---

## Day16 - Initial LLM Router Agent

### Completed

- Added `src/app/agent/llm_router.py`
- Added `RouterDecision`
- Added mock LLM Router classification
- Added Ollama LLM Router classification for local manual verification
- Added route output parsing for JSON and fallback text
- Added `/agent/llm-router-chat`
- Added `AgentLLMRouterChatRequest`
- Added `AgentLLMRouterChatResponse`
- Preserved calculator route delegation to `invoke_agent()`
- Preserved RAG route delegation to `invoke_agent()`
- Kept chat route deterministic
- Added `route_reason`, `router_provider`, and `router_model` response fields
- Fixed provider selection so `router_provider="mock"` always uses mock-router
- Manually verified `router_provider="ollama"` with local `qwen2.5:7b`
- Added `tests/test_llm_router.py`
- Expanded pytest from 28 tests to 31 tests
- Verified local pytest
- Verified GitHub Actions CI

### New Endpoint

```text
POST /agent/llm-router-chat
```

### New Files

```text
src/app/agent/llm_router.py
tests/test_llm_router.py
```

### Test Result

```text
57 passed, 1 warning
```

### CI Result

```text
GitHub Actions CI: green
```

### Notes

Day16 introduces LLM-based routing without making CI depend on local Ollama.

The mock router is used for deterministic tests and CI.

The Ollama router is available for local manual verification through:

```text
router_provider="ollama"
```

---

## Day17 - Smart Chat Unified Entry Point Preview

### Completed

- Added `src/app/agent/smart_router.py`
- Added `invoke_smart_agent()`
- Added router mode normalization
- Added `/agent/smart-chat`
- Added `AgentSmartChatRequest`
- Added `AgentSmartChatResponse`
- Supported `router_mode="deterministic"`
- Supported `router_mode="llm"`
- Reused `invoke_router_agent()` for deterministic mode
- Reused `invoke_llm_router_agent()` for LLM mode
- Preserved mock provider for CI-safe LLM Router tests
- Manually verified Ollama provider through Smart Chat
- Added unified response fields: `route`, `route_reason`, `router_mode`, `router_provider`, `router_model`
- Added `tests/test_smart_chat.py`
- Expanded pytest from 31 tests to 34 tests
- Verified local pytest
- Verified GitHub Actions CI

### New Endpoint

```text
POST /agent/smart-chat
```

### New Files

```text
src/app/agent/smart_router.py
tests/test_smart_chat.py
```

### Test Result

```text
57 passed, 1 warning
```

### CI Result

```text
GitHub Actions CI: green
```

### Notes

Day17 does not replace existing endpoints.

It adds a stable compatibility layer for a future default Agent entry point.

Current interface family:

```text
/agent/chat
/agent/router-chat
/agent/llm-router-chat
/agent/smart-chat
```

---

## Day18 - RAG Search Debug / Retrieval Explainability

### Completed

- Added `src/app/rag/explain.py`
- Added `explain_search_knowledge()`
- Added `/rag/search-debug`
- Added `RagSearchDebugRequest`
- Added `RagSearchDebugResult`
- Added `RagSearchDebugResponse`
- Returned `normalized_query`
- Returned ranked results
- Returned `source`
- Returned `score`
- Returned `content`
- Returned `preview`
- Returned `matched_terms`
- Returned `content_length`
- Preserved `trace_id`
- Added `tests/test_rag_debug.py`
- Expanded pytest from 34 tests to 37 tests
- Verified local pytest
- Verified GitHub Actions CI

### New Endpoint

```text
POST /rag/search-debug
```

### New Files

```text
src/app/rag/explain.py
tests/test_rag_debug.py
```

### Test Result

```text
57 passed, 1 warning
```

### CI Result

```text
GitHub Actions CI: green
```

### Notes

Day18 improves RAG observability without introducing a vector database or embedding dependency.

This keeps the project deterministic and CI-safe.

The debug endpoint helps inspect which chunks were retrieved and which query terms matched each chunk.

---

## Day19 - Smart Chat SSE Streaming

### Completed

- Added `src/app/agent/smart_streaming.py`
- Added `stream_smart_agent_events()`
- Added `/agent/smart-stream`
- Reused existing `invoke_smart_agent()`
- Supported `router_mode="deterministic"`
- Supported `router_mode="llm"` with `router_provider="mock"`
- Manually verified `router_provider="ollama"` locally
- Added SSE event sequence: `metadata -> route -> answer_chunk -> final -> done`
- Added `route_reason`, `router_mode`, `router_provider`, and `router_model` in SSE payloads
- Added `tests/test_smart_stream.py`
- Expanded pytest from 37 tests to 40 tests
- Verified local pytest
- Verified GitHub Actions CI

### New Endpoint

```text
POST /agent/smart-stream
```

### New Files

```text
src/app/agent/smart_streaming.py
tests/test_smart_stream.py
```

### Test Result

```text
57 passed, 1 warning
```

### CI Result

```text
GitHub Actions CI: green
```

### Notes

Day19 adds streaming capability to the Smart Chat unified entry point preview.

The current stream emits the full answer as one `answer_chunk`, leaving room for token-level streaming later.

---

## Day20 - Route Validation Metadata / Fallback Support

### Completed

- Added `src/app/agent/route_validation.py`
- Added `RouteValidationResult`
- Added `validate_route_decision()`
- Added invalid route fallback to `chat`
- Added `route_confidence`, `route_valid`, `fallback_used`, and `validation_reason`
- Updated `/agent/llm-router-chat`
- Updated `/agent/smart-chat`
- Updated `/agent/smart-stream`
- Added validation metadata to Smart Stream SSE payloads
- Added `tests/test_route_validation.py`
- Expanded pytest from 40 tests to 45 tests
- Verified local pytest
- Verified GitHub Actions CI

### New Files

```text
src/app/agent/route_validation.py
tests/test_route_validation.py
```

### Updated Endpoints

```text
POST /agent/llm-router-chat
POST /agent/smart-chat
POST /agent/smart-stream
```

### Test Result

```text
57 passed, 1 warning
```

### CI Result

```text
GitHub Actions CI: green
```

### Commit

```text
10e25aa add route validation metadata
```

---

## Day21 - RAG Chunk Pipeline / Vector DB Preparation

### Completed

- Added `src/app/rag/chunking.py`
- Added `split_text_into_chunks()`
- Added `load_markdown_documents()`
- Added `load_knowledge_chunks()`
- Added `debug_knowledge_chunks()`
- Added `/rag/chunks-debug`
- Added `RagChunksDebugRequest`
- Added `RagChunkInfo`
- Added `RagChunksDebugResponse`
- Supported `source_filter`
- Supported `max_chars`
- Returned `chunk_id`, `source`, `index`, `content`, `preview`, and `content_length`
- Preserved `trace_id`
- Added `tests/test_rag_chunks.py`
- Expanded pytest from 45 tests to 48 tests
- Verified local pytest
- Verified GitHub Actions CI

### New Endpoint

```text
POST /rag/chunks-debug
```

### New Files

```text
src/app/rag/chunking.py
tests/test_rag_chunks.py
```

### Test Result

```text
57 passed, 1 warning
```

### CI Result

```text
GitHub Actions CI: green
```

### Commit

```text
00a2cad add rag chunk debug endpoint
```

---

## Day22 - Deterministic RAG Vector Search Debug

### Completed

- Added `src/app/rag/vector_index.py`
- Added `build_deterministic_embedding()`
- Added `cosine_similarity()`
- Added `vector_search_knowledge()`
- Added `/rag/vector-search-debug`
- Reused Day21 `load_knowledge_chunks()`
- Added `RagVectorSearchDebugRequest`
- Added `RagVectorSearchDebugResult`
- Added `RagVectorSearchDebugResponse`
- Supported `top_k`
- Supported `source_filter`
- Supported `max_chars`
- Supported `embedding_dim`
- Returned `rank`, `chunk_id`, `source`, `index`, `score`, `content`, `preview`, `matched_terms`, and `content_length`
- Preserved `trace_id`
- Added `tests/test_rag_vector_search.py`
- Expanded pytest from 48 tests to 51 tests
- Verified local pytest
- Verified GitHub Actions CI

### New Endpoint

```text
POST /rag/vector-search-debug
```

### New Files

```text
src/app/rag/vector_index.py
tests/test_rag_vector_search.py
```

### Test Result

```text
57 passed, 1 warning
```

### CI Result

```text
GitHub Actions CI: green
```

### Commit

```text
1f1364d add deterministic rag vector search debug
```

### Notes

Day22 is a vector-search preview layer, not a production semantic embedding layer.

It keeps CI deterministic while preparing the API, schemas, and tests for future real embedding or vector DB integration.

---

## Day23 - Hybrid Retrieval Debug

### Completed

- Added `src/app/rag/hybrid.py`
- Added `hybrid_search_knowledge()`
- Added keyword scoring
- Added vector scoring reuse
- Added weighted `hybrid_score`
- Added `/rag/hybrid-search-debug`
- Reused Day21 `load_knowledge_chunks()`
- Reused Day22 `build_deterministic_embedding()`
- Reused Day22 `cosine_similarity()`
- Added `RagHybridSearchDebugRequest`
- Added `RagHybridSearchDebugResult`
- Added `RagHybridSearchDebugResponse`
- Supported `top_k`
- Supported `source_filter`
- Supported `max_chars`
- Supported `embedding_dim`
- Supported `keyword_weight`
- Supported `vector_weight`
- Returned `rank`, `chunk_id`, `source`, `index`, `hybrid_score`, `keyword_score`, `vector_score`, `content`, `preview`, `matched_terms`, and `content_length`
- Preserved `trace_id`
- Added `tests/test_rag_hybrid_search.py`
- Expanded pytest from 51 tests to 54 tests
- Verified local pytest
- Git push succeeded

### New Endpoint

```text
POST /rag/hybrid-search-debug
```

### New Files

```text
src/app/rag/hybrid.py
tests/test_rag_hybrid_search.py
```

### Test Result

```text
57 passed, 1 warning
```

### Commit

```text
b3a8f0c add rag hybrid search debug
```

### Notes

Day23 makes retrieval more realistic by combining keyword and vector retrieval signals.

This prepares the project for future reranking, RAG evaluation, and Agentic RAG.

---

## Day24 - Agentic RAG Debug Graph

### Completed

- Added `src/app/rag/agentic_graph.py`
- Added `AgenticRagState`
- Added `query_analyzer_node`
- Added `query_rewriter_node`
- Added `retrieve_node`
- Added `relevance_grade_node`
- Added `answer_node`
- Added `direct_answer_node`
- Added `build_agentic_rag_graph()`
- Added `invoke_agentic_rag()`
- Added `/rag/agentic-debug`
- Reused Day23 `hybrid_search_knowledge()`
- Supported retrieval path
- Supported direct non-retrieval path
- Returned `rewritten_query`
- Returned `retrieval_needed`
- Returned `relevance_score`
- Returned `citations`
- Returned `retrieval_results`
- Returned `final_answer`
- Returned `steps`
- Preserved `trace_id`
- Added `tests/test_rag_agentic_debug.py`
- Expanded pytest from 54 tests to 57 tests
- Verified local pytest
- Git push succeeded

### New Endpoint

```text
POST /rag/agentic-debug
```

### New Files

```text
src/app/rag/agentic_graph.py
tests/test_rag_agentic_debug.py
```

### Test Result

```text
57 passed, 1 warning
```

### Commit

```text
4ed753a add agentic rag debug graph
```

### Notes

Day24 upgrades RAG from retrieval endpoints to a debuggable Agentic RAG workflow.

The provided log does not show GitHub Actions CI status. Confirm CI separately from GitHub Actions.


---

## Current RAG Evaluation Strategy

Day25 added a RAG evaluation debug layer.

Current evaluation dataset:

```text
eval_cases/rag_agentic_eval.jsonl
```

Current evaluation module:

```text
src/app/evaluation/rag_eval.py
```

Current endpoint:

```text
POST /rag/eval-debug
```

Current functions:

```text
load_rag_eval_cases()
evaluate_rag_cases()
```

It reuses:

```text
invoke_agentic_rag()
```

Current metrics:

```text
pass_rate
retrieval_decision_accuracy
expected_terms_hit_rate
citation_hit_rate
average_relevance_score
```

Current local evaluation result:

```text
total_cases = 3
passed_cases = 3
pass_rate = 1.0
retrieval_decision_accuracy = 1.0
expected_terms_hit_rate = 1.0
citation_hit_rate = 1.0
average_relevance_score = 0.278223
```

---

## Day25 - RAG Evaluation Debug

### Completed

- Added `eval_cases/rag_agentic_eval.jsonl`
- Added `src/app/evaluation/__init__.py`
- Added `src/app/evaluation/rag_eval.py`
- Added `load_rag_eval_cases()`
- Added `evaluate_rag_cases()`
- Added `/rag/eval-debug`
- Reused Day24 `invoke_agentic_rag()`
- Added RAG evaluation schemas
- Evaluated retrieval decision accuracy
- Evaluated expected terms hit rate
- Evaluated citation hit rate
- Evaluated pass rate
- Returned per-case evaluation details
- Added `tests/test_rag_eval.py`
- Expanded pytest from 57 tests to 60 tests
- Verified local pytest
- Git push succeeded

### Test Result

```text
60 passed, 1 warning
```

### Commit

```text
958b791 add rag evaluation debug
```


---

## Current Observability Trace Store Strategy

Day26 added a SQLite-backed observability trace store.

Current files:

```text
src/app/observability/trace_store.py
src/app/schemas/observability.py
src/app/routes/routes_observability.py
tests/test_observability.py
```

Current endpoints:

```text
GET /observability/traces/{trace_id}
GET /observability/traces
```

Current trace database:

```text
data/observability.sqlite
```

Current functions:

```text
init_trace_store()
record_trace_event()
get_trace_events()
list_recent_trace_ids()
```

Current event types:

```text
rag_agentic_debug
rag_eval_debug
```

---

## Day26 - Observability Trace Store

### Completed

- Added `src/app/observability/__init__.py`
- Added `src/app/observability/trace_store.py`
- Added `src/app/schemas/observability.py`
- Added `src/app/routes/routes_observability.py`
- Registered Observability router in `main.py`
- Added `/observability/traces/{trace_id}`
- Added `/observability/traces`
- Added `init_trace_store()`
- Added `record_trace_event()`
- Added `get_trace_events()`
- Added `list_recent_trace_ids()`
- Added SQLite trace table `trace_events`
- Added `rag_agentic_debug` event writes from `/rag/agentic-debug`
- Added `rag_eval_debug` event writes from `/rag/eval-debug`
- Verified direct trace-store Python usage
- Verified Agentic RAG trace lookup
- Verified RAG Eval trace lookup
- Verified recent trace listing
- Added `tests/test_observability.py`
- Expanded pytest from 60 tests to 63 tests
- Verified local pytest
- Verified GitHub Actions CI
- Git push succeeded

### Test Result

```text
66 passed, 1 warning
```

### CI Result

```text
GitHub Actions CI: green
```

### Commit

```text
ce8fe35 add observability trace store
```

---

## Day27 - Agentic RAG Streaming

### Completed

- Added `src/app/rag/agentic_streaming.py`
- Added `stream_agentic_rag_events()`
- Added `/rag/agentic-stream`
- Reused Day24 `invoke_agentic_rag()`
- Reused Day26 `record_trace_event()`
- Added retrieval path SSE event sequence:
  - `metadata`
  - `decision`
  - `rewrite`
  - `retrieval`
  - `relevance`
  - `citation`
  - `answer_chunk`
  - `final`
  - `done`
- Added direct path SSE event sequence:
  - `metadata`
  - `decision`
  - `answer_chunk`
  - `final`
  - `done`
- Added `rag_agentic_stream` observability event
- Verified stream trace lookup through `/observability/traces/{trace_id}`
- Added `tests/test_rag_agentic_stream.py`
- Expanded pytest from 63 tests to 66 tests
- Verified local pytest
- Verified GitHub Actions CI
- Git push succeeded

### New Endpoint

```text
POST /rag/agentic-stream
```

### New Files

```text
src/app/rag/agentic_streaming.py
tests/test_rag_agentic_stream.py
```

### Test Result

```text
66 passed, 1 warning
```

### CI Result

```text
GitHub Actions CI: green
```

### Commit

```text
1976482 add agentic rag streaming
```

### Notes

Day27 adds real-time SSE output for Agentic RAG and stores stream execution summaries in the observability trace store.

---

## Known Issues / Notes

### SQLite runtime files

If `data/checkpoints.sqlite-shm` or `data/checkpoints.sqlite-wal` appears in Git status, run:

```bash
git rm --cached -r data || true
```

Make sure `.gitignore` includes:

```text
data/
*.sqlite
*.sqlite-shm
*.sqlite-wal
*.sqlite-journal
```

### Knowledge base files

Knowledge base files are source-controlled project files and should live under:

```text
knowledge/
```

Do not put source-controlled knowledge files under `data/`, because `data/` is runtime-only and ignored by Git.

Knowledge base files must be UTF-8 encoded. If a Markdown file was created by a Windows editor and pytest raises `UnicodeDecodeError`, convert it:

```bash
iconv -f gbk -t utf-8 knowledge/agent_basics.md -o /tmp/agent_basics.md
mv /tmp/agent_basics.md knowledge/agent_basics.md
```

### Current agent_node label

Some normal deterministic responses still contain:

```text
Day4 agent response
```

This is harmless but can be renamed later to a neutral label such as:

```text
Agent response
```

### Test warning

Local pytest currently shows:

```text
57 passed, 1 warning
```

The warning is:

```text
StarletteDeprecationWarning: Using httpx with starlette.testclient is deprecated; install httpx2 instead.
```

It does not block local tests or CI and can be handled later.

### JSON Unicode escaping

`python -m json.tool` may display Chinese text as Unicode escape sequences, for example:

```text
\u8ba1\u7b97\u7ed3\u679c\u662f 42\u3002
```

Use:

```bash
python -m json.tool --no-ensure-ascii
```

or:

```bash
python -c "import sys,json; print(json.dumps(json.load(sys.stdin), ensure_ascii=False, indent=4))"
```

### Commit typo

Day2 commit message was:

```text
add minimal langraph agent
```

It has a typo: `langraph` should be `langgraph`. This does not affect code and does not need rewriting Git history.

---

## Next Milestones

Recommended next route:

```text
Day28: answer verification, real embedding/vector DB preparation, or richer observability
Day29+: real embedding or vector database backed RAG
Later: vector DB based RAG
Later: GraphRAG + Neo4j + Multi-Agent Supervisor
```

---

## Current Completion Checklist

Completed:

- [x] Day1 project initialization
- [x] Day2 minimal LangGraph graph
- [x] Day3 minimal Tool Calling Agent
- [x] Day4 InMemorySaver short-term memory
- [x] Day5 SqliteSaver persistent memory
- [x] Day6 debug endpoint
- [x] Day7 pytest
- [x] Day7 README.md initial version
- [x] Day7 GitHub Actions CI
- [x] Day8 request logging middleware
- [x] Day8 x-trace-id response header
- [x] Day8 trace_id response body
- [x] Day8 latency logging
- [x] Day8 trace tests
- [x] Day8 GitHub Actions CI
- [x] Day9 Ollama LLM provider abstraction
- [x] Day9 mock provider
- [x] Day9 Ollama provider
- [x] Day9 LLM tests
- [x] Day9 GitHub Actions CI
- [x] Day10 real LLM tool calling
- [x] Day10 `/agent/llm-chat`
- [x] Day10 `/agent/llm-debug`
- [x] Day10 LLM-generated `add` tool call
- [x] Day10 LLM-generated `multiply` tool call
- [x] Day10 GitHub Actions CI
- [x] Day11 streaming response
- [x] Day11 `/agent/stream`
- [x] Day11 `/agent/llm-stream`
- [x] Day11 SSE tests
- [x] Day11 GitHub Actions CI
- [x] Day12 RAG search tool
- [x] Day12 `/rag/search`
- [x] Day12 `search_knowledge_base`
- [x] Day12 Agent RAG tool path
- [x] Day12 RAG tests
- [x] Day12 GitHub Actions CI
- [x] Day13 Router Agent
- [x] Day13 `/agent/router-chat`
- [x] Day13 `/agent/router-debug`
- [x] Day13 calculator route
- [x] Day13 RAG route
- [x] Day13 chat route
- [x] Day13 Router Agent tests
- [x] Day13 GitHub Actions CI
- [x] Day14 Router delegation
- [x] Day14 calculator route delegates to existing Agent
- [x] Day14 RAG route delegates to existing Agent
- [x] Day14 Router-triggered calculation can be recalled by `/agent/chat`
- [x] Day14 Router delegation tests
- [x] Day14 GitHub Actions CI
- [x] Day15 Router streaming endpoint
- [x] Day15 `/agent/router-stream`
- [x] Day15 Router stream calculator route
- [x] Day15 Router stream RAG route
- [x] Day15 Router stream chat route
- [x] Day15 Router stream tests
- [x] Day15 GitHub Actions CI
- [x] Day16 initial LLM Router Agent
- [x] Day16 `/agent/llm-router-chat`
- [x] Day16 mock LLM Router calculator route
- [x] Day16 mock LLM Router RAG route
- [x] Day16 mock LLM Router chat route
- [x] Day16 Ollama LLM Router manual verification
- [x] Day16 LLM Router tests
- [x] Day16 GitHub Actions CI
- [x] Day17 Smart Chat unified entry point preview
- [x] Day17 `/agent/smart-chat`
- [x] Day17 deterministic Smart Chat route
- [x] Day17 LLM mock Smart Chat RAG route
- [x] Day17 LLM mock Smart Chat chat route
- [x] Day17 Ollama Smart Chat manual verification
- [x] Day17 Smart Chat tests
- [x] Day17 GitHub Actions CI
- [x] Day18 RAG Search Debug endpoint
- [x] Day18 `/rag/search-debug`
- [x] Day18 retrieval explainability metadata
- [x] Day18 matched terms
- [x] Day18 RAG debug tests
- [x] Day18 GitHub Actions CI
- [x] Day19 Smart Chat SSE streaming endpoint
- [x] Day19 `/agent/smart-stream`
- [x] Day19 deterministic Smart Stream calculator route
- [x] Day19 LLM mock Smart Stream RAG route
- [x] Day19 LLM mock Smart Stream chat route
- [x] Day19 Ollama Smart Stream manual verification
- [x] Day19 Smart Stream tests
- [x] Day19 GitHub Actions CI
- [x] Day20 route validation metadata
- [x] Day20 `validate_route_decision()`
- [x] Day20 invalid route fallback to chat
- [x] Day20 `/agent/llm-router-chat` validation metadata
- [x] Day20 `/agent/smart-chat` validation metadata
- [x] Day20 `/agent/smart-stream` validation metadata
- [x] Day20 route validation tests
- [x] Day20 GitHub Actions CI
- [x] Day21 RAG chunk pipeline
- [x] Day21 `/rag/chunks-debug`
- [x] Day21 Markdown document loading
- [x] Day21 blank-line based chunk splitting
- [x] Day21 chunk metadata
- [x] Day21 source_filter support
- [x] Day21 max_chars support
- [x] Day21 RAG chunk tests
- [x] Day21 GitHub Actions CI
- [x] Day22 deterministic RAG vector-search debug
- [x] Day22 `/rag/vector-search-debug`
- [x] Day22 deterministic hashed embedding
- [x] Day22 cosine similarity ranking
- [x] Day22 vector-search metadata
- [x] Day22 source_filter support
- [x] Day22 max_chars support
- [x] Day22 embedding_dim support
- [x] Day22 RAG vector-search tests
- [x] Day22 GitHub Actions CI
- [x] Day23 Hybrid Retrieval Debug
- [x] Day23 `/rag/hybrid-search-debug`
- [x] Day23 keyword_score
- [x] Day23 vector_score
- [x] Day23 hybrid_score
- [x] Day23 keyword_weight support
- [x] Day23 vector_weight support
- [x] Day23 hybrid retrieval tests
- [x] Day23 Git push
- [x] Day24 Agentic RAG Debug Graph
- [x] Day24 `/rag/agentic-debug`
- [x] Day24 query_analyzer
- [x] Day24 query_rewriter
- [x] Day24 hybrid_retrieve
- [x] Day24 relevance_grade
- [x] Day24 answer_with_citations
- [x] Day24 direct_answer
- [x] Day24 retrieval path tests
- [x] Day24 direct path tests
- [x] Day24 Git push

Next:

- [x] Day25 RAG Evaluation Debug
- [x] Day25 `/rag/eval-debug`
- [x] Day25 JSONL eval cases
- [x] Day25 retrieval_decision_accuracy
- [x] Day25 expected_terms_hit_rate
- [x] Day25 citation_hit_rate
- [x] Day25 pass_rate
- [x] Day25 RAG eval tests
- [x] Day25 Git push

Next:

- [x] Day26 Observability Trace Store
- [x] Day26 `/observability/traces/{trace_id}`
- [x] Day26 `/observability/traces`
- [x] Day26 `record_trace_event()`
- [x] Day26 `get_trace_events()`
- [x] Day26 `list_recent_trace_ids()`
- [x] Day26 `rag_agentic_debug` trace event
- [x] Day26 `rag_eval_debug` trace event
- [x] Day26 observability tests
- [x] Day26 GitHub Actions CI
- [x] Day26 Git push

Next:

- [x] Day27 Agentic RAG Streaming
- [x] Day27 `/rag/agentic-stream`
- [x] Day27 `stream_agentic_rag_events()`
- [x] Day27 retrieval path SSE events
- [x] Day27 direct path SSE events
- [x] Day27 `rag_agentic_stream` trace event
- [x] Day27 observability lookup for stream trace
- [x] Day27 Agentic RAG stream tests
- [x] Day27 GitHub Actions CI
- [x] Day27 Git push

Next:

- [ ] Day28 answer verification, real embedding/vector DB preparation, or richer observability
