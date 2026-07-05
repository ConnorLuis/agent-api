# HANDOFF.md

## Project

agent-api

## Current Status

Project 2 has officially started and is now the main development line.

`chat-api-v2` has been completed. Future review of that project will happen in the separate conversation named **Chat-API项目复习**.

Current `agent-api` status:

```text
Day1-Day39 first stage completed.
Day39 first stage completed: Backend evaluation report layer.
Local pytest: 100 passed, 1 warning.
Git push: success.
GitHub Actions CI: not shown in provided Day39 log; confirm from GitHub Actions.
Next: Day39 second stage evaluation report polishing or production retrieval backend selection.
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
- Agentic RAG Answer Verification endpoint
- Deterministic answer support, citation, grounding-term, and risk-flag checks
- SQLite Vector Store Debug endpoint
- SQLite-backed deterministic chunk embedding persistence for real vector DB preparation
- EmbeddingProvider abstraction layer
- DeterministicEmbeddingProvider as CI-safe fallback
- Reserved SentenceTransformersEmbeddingProvider for local semantic embeddings
- RAG Embedding Debug endpoint
- Provider-aware SQLite vector store debug endpoint
- Chroma persistent vector store debug endpoint
- ChromaDB PersistentClient based index and query path
- Chroma search observability event
- Agentic RAG retrieval backend switch
- Chroma-backed Agentic RAG debug path
- Chroma collection naming with short stable hash suffix
- Backend-normalized retrieval results for Agentic RAG
- Backend-aware RAG evaluation debug endpoint
- RAG backend evaluation comparison endpoint
- Hybrid-vs-Chroma backend metrics comparison
- Backend evaluation observability event
- Refined backend comparison metrics: `metric_deltas`, `case_comparisons`, and `comparison_summary`
- Backend comparison trace payload with refined metrics
- Backend-aware Agentic RAG streaming endpoint
- Chroma-backed Agentic RAG SSE stream path
- Agentic RAG stream trace backend metadata
- Deterministic reranker layer for CI-safe rerank experiments
- `retrieval_backend="chroma_rerank"`
- Chroma retrieval followed by lightweight keyword-aware reranking
- Reranker metadata fields for Agentic RAG retrieval results
- Backend evaluation comparison across `hybrid`, `chroma`, and `chroma_rerank`
- Pairwise backend metric deltas with `pairwise_metric_deltas`
- Backward-compatible first-vs-second `metric_deltas`
- Backend comparison trace payload records `pairwise_metric_deltas`
- Multi-backend comparison support for `hybrid`, `chroma`, and `chroma_rerank`
- Multi-backend-aware `comparison_summary.notes`
- `comparison_summary.evaluated_backends`
- `comparison_summary.metric_winners`
- `comparison_summary.metric_rankings`
- `comparison_summary.top_improvement_pairs`
- Trace payload records refined multi-backend `comparison_summary`
- Local semantic embedding provider validation with `sentence_transformers`
- Local BCE embedding model path: `/mnt/f/LLM/maidalun/bce-embedding-base_v1`
- CI-safe semantic provider test that skips when the local model path is unavailable
- Day38 validation script for semantic provider, Chroma, Agentic RAG, and backend comparison
- Backend evaluation report builder for retrieval backend selection guidance
- `/rag/backend-eval-debug` response-level `evaluation_report`
- pytest
- GitHub Actions CI

Not yet implemented:

- OpenAI provider
- Replacing `/agent/chat` with the real LLM Agent as the default route
- Making Smart Chat the default production entry point
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
├── scripts/
│   └── validate_semantic_embedding_provider.py
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
│   ├── DAY27.md
│   ├── DAY28.md
│   ├── DAY29.md
│   ├── DAY30.md
│   ├── DAY31.md
│   ├── DAY32.md
│   ├── DAY33.md
│   ├── DAY34.md
│   ├── DAY35.md
│   ├── DAY36.md
│   ├── DAY37.md
│   └── DAY38.md
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
│       │   ├── rag_eval.py
│       │   └── rag_report.py
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
│       │   ├── answer_verifier.py
│       │   ├── embedding_provider.py
│       │   ├── chroma_store.py
│       │   ├── retrieval_backend.py
│       │   ├── reranker.py
│       │   ├── vector_store.py
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
    ├── test_rag_answer_verify.py
    ├── test_rag_vector_store.py
    ├── test_rag_embedding_provider.py
    ├── test_rag_chroma_store.py
    ├── test_rag_agentic_backend.py
    ├── test_rag_backend_eval.py
├── test_rag_agentic_stream_backend.py
├── test_rag_reranker.py
├── test_rag_backend_pairwise_eval.py
├── test_rag_backend_comparison_summary.py
├── test_rag_semantic_embedding_provider.py
├── test_rag_backend_report.py
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
POST /rag/answer-verify-debug
POST /rag/vector-store-debug
POST /rag/embedding-debug
POST /rag/chroma-search-debug
POST /rag/eval-debug
POST /rag/backend-eval-debug
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

## Current Agentic RAG Answer Verification Strategy

Day28 added a deterministic answer verification layer.

Current verification file:

```text
src/app/rag/answer_verifier.py
```

Current endpoint:

```text
POST /rag/answer-verify-debug
```

Current function:

```text
verify_agentic_rag_answer()
```

It reuses:

```text
invoke_agentic_rag()
record_trace_event()
```

Verification metadata:

```text
verification_mode
answer_supported
verification_pass
confidence
answer_has_citation
citation_coverage_pass
cited_in_answer
unsupported_citations
grounding_terms
matched_grounding_terms
risk_flags
```

Retrieval verification checks:

```text
citations exist
citations come from retrieval_results
answer contains a citation/source marker
answer contains matched grounding terms
relevance_score is positive
risk_flags is empty
```

Direct verification checks:

```text
citations is empty
retrieval_results is empty
relevance_score is 0.0
risk_flags is empty
```

Observability event:

```text
rag_answer_verify_debug
```

Important:

```text
Day28 adds a post-answer support check to Agentic RAG.
It helps detect unsupported citations, missing citations, low relevance, and missing grounding terms.
```

New Day28 test file:

```text
tests/test_rag_answer_verify.py
```

---

## Current SQLite Vector Store Debug Strategy

Day29 added a SQLite-backed vector store debug layer.

Current file:

```text
src/app/rag/vector_store.py
```

Current endpoint:

```text
POST /rag/vector-store-debug
```

Current functions:

```text
init_vector_store()
build_vector_store_index()
query_vector_store()
debug_vector_store_search()
```

It reuses:

```text
load_knowledge_chunks()
build_deterministic_embedding()
cosine_similarity()
record_trace_event()
```

Current SQLite database:

```text
data/rag_vector_store.sqlite
```

Current SQLite table:

```text
rag_chunk_vectors
```

Current request fields:

```text
query
top_k
source_filter
max_chars
embedding_dim
rebuild_index
```

Returned metadata:

```text
query
top_k
source_filter
max_chars
embedding_dim
index_key
total_indexed_chunks
rebuild_index
index_stats
results
trace_id
```

Index statistics:

```text
index_key
source_filter
max_chars
embedding_dim
rebuild_index
loaded_chunks
inserted_count
stored_count
db_path
```

Observability event:

```text
rag_vector_store_debug
```

Important:

```text
Day29 is not the final real vector database integration.
It introduces a vector-store-shaped persistence and query layer using SQLite and deterministic embeddings.
This keeps tests stable while preparing the codebase for Chroma, FAISS, Milvus, or Qdrant.
```

New Day29 test file:

```text
tests/test_rag_vector_store.py
```

---

## Current EmbeddingProvider Strategy

Day30 added an EmbeddingProvider abstraction layer.

Current file:

```text
src/app/rag/embedding_provider.py
```

Current endpoint:

```text
POST /rag/embedding-debug
```

Current classes and functions:

```text
EmbeddingProvider
DeterministicEmbeddingProvider
SentenceTransformersEmbeddingProvider
get_embedding_provider()
debug_embeddings()
embedding_norm()
```

Current default provider:

```text
deterministic
```

Current default deterministic model:

```text
deterministic-hash
```

Reserved semantic embedding provider:

```text
sentence_transformers
```

Reserved semantic embedding model:

```text
/mnt/f/LLM/maidalun/bce-embedding-base_v1
```

Day30 also upgraded the SQLite vector store debug layer so `build_vector_store_index()` and `query_vector_store()` use `get_embedding_provider()` instead of directly depending on deterministic embedding functions.

Provider-aware vector store request/response fields:

```text
embedding_provider
embedding_model
```

Embedding debug response metadata:

```text
provider
model
requested_embedding_dim
actual_embedding_dim
query_embedding_preview
query_embedding_norm
documents_count
documents
trace_id
```

Observability event:

```text
rag_embedding_debug
```

Important:

```text
Day30 does not yet make Chroma the production retriever.
It creates the provider abstraction needed before connecting Chroma or other vector databases.
The deterministic provider remains the default CI-safe fallback.
```

New Day30 test file:

```text
tests/test_rag_embedding_provider.py
```

---

## Current Chroma Vector Store Strategy

Day31 added a Chroma-backed persistent vector store debug layer.

Current file:

```text
src/app/rag/chroma_store.py
```

Current endpoint:

```text
POST /rag/chroma-search-debug
```

Current functions:

```text
build_chroma_collection_name()
build_chroma_index()
query_chroma_store()
debug_chroma_search()
reset_chroma_persist_dir()
```

It reuses:

```text
load_knowledge_chunks()
get_embedding_provider()
record_trace_event()
```

Current Chroma persistent directory:

```text
data/chroma
```

Current request fields:

```text
query
top_k
source_filter
max_chars
embedding_dim
embedding_provider
embedding_model
rebuild_index
```

Returned metadata:

```text
query
top_k
source_filter
max_chars
embedding_dim
embedding_provider
embedding_model
collection_name
persist_dir
total_indexed_chunks
rebuild_index
index_stats
results
trace_id
```

Index statistics:

```text
collection_name
persist_dir
source_filter
max_chars
embedding_dim
embedding_provider
embedding_model
rebuild_index
loaded_chunks
upserted_count
stored_count
```

Result metadata:

```text
rank
chunk_id
source
index
distance
score
content
preview
content_length
```

Observability event:

```text
rag_chroma_search_debug
```

Important:

```text
Day31 uses Chroma as a real persistent vector store, but still uses deterministic embeddings by default for CI stability.
The current Chroma path is a debug endpoint and does not yet replace Agentic RAG's retrieval backend.
The observed collection name may be truncated by the collection-name length guard; use request metadata and index_stats as the source of truth for embedding_dim/provider/model.
```

New Day31 test file:

```text
tests/test_rag_chroma_store.py
```

---

## Current Agentic RAG Retrieval Backend Strategy

Day32 added a retrieval backend switch for Agentic RAG.

Current files:

```text
src/app/rag/retrieval_backend.py
src/app/rag/agentic_graph.py
```

Current endpoint:

```text
POST /rag/agentic-debug
```

Current backend switch function:

```text
retrieve_agentic_context()
```

Supported backends:

```text
hybrid
chroma
```

Default backend:

```text
hybrid
```

Hybrid path:

```text
retrieve_agentic_context() -> hybrid_search_knowledge() -> normalized hybrid retrieval results
```

Chroma path:

```text
retrieve_agentic_context() -> debug_chroma_search() -> normalized Chroma retrieval results
```

Agentic RAG retrieval path with hybrid:

```text
query_analyzer -> query_rewriter -> hybrid_retrieve -> relevance_grade -> answer_with_citations
```

Agentic RAG retrieval path with Chroma:

```text
query_analyzer -> query_rewriter -> chroma_retrieve -> relevance_grade -> answer_with_citations
```

Returned Agentic RAG metadata now includes:

```text
retrieval_backend
retrieval_metadata
```

Trace payload now includes:

```text
retrieval_backend
retrieval_metadata
```

Important compatibility notes:

```text
The default backend remains hybrid, so previous Day24-Day31 tests and behavior remain stable.
Chroma results are normalized to include hybrid_score, keyword_score, and vector_score.
For Chroma results, keyword_score is 0.0 and vector_score/hybrid_score use the normalized Chroma score.
```

Day32 also fixed the Day31 Chroma collection naming issue.

New collection name shape:

```text
agent_api_rag_<source>_<provider>_d<dim>_<hash8>
```

Observed examples:

```text
agent_api_rag_agent_basics_deterministi_d64_5aeff12d
agent_api_rag_agent_basics_deterministi_d128_72a03a28
```

New Day32 test file:

```text
tests/test_rag_agentic_backend.py
```

---

## Current RAG Backend Evaluation Strategy

Day33 upgraded the RAG evaluation layer into a backend-aware evaluation and comparison layer.

Current files:

```text
src/app/evaluation/rag_eval.py
tests/test_rag_backend_eval.py
```

Current endpoints:

```text
POST /rag/eval-debug
POST /rag/backend-eval-debug
```

Current functions:

```text
evaluate_rag_cases()
compare_rag_retrieval_backends()
```

`/rag/eval-debug` now supports:

```text
retrieval_backend
embedding_provider
embedding_model
rebuild_index
```

Supported evaluation backends:

```text
hybrid
chroma
```

Default backend remains:

```text
hybrid
```

`/rag/backend-eval-debug` compares multiple backends on the same JSONL eval set and returns:

```text
best_backend_by_pass_rate
best_backend_by_average_relevance
results[*].metrics
results[*].cases
```

Current observed metrics:

```text
hybrid:
  total_cases = 3
  passed_cases = 3
  pass_rate = 1.0
  retrieval_decision_accuracy = 1.0
  expected_terms_hit_rate = 1.0
  citation_hit_rate = 1.0
  average_relevance_score = 0.278223

chroma:
  total_cases = 3
  passed_cases = 2
  pass_rate = 0.666667
  retrieval_decision_accuracy = 1.0
  expected_terms_hit_rate = 0.666667
  citation_hit_rate = 1.0
  average_relevance_score = 0.279233
```

Current backend comparison result:

```text
best_backend_by_pass_rate = hybrid
best_backend_by_average_relevance = chroma
```

Current trace event:

```text
rag_backend_eval_debug
```

Important interpretation:

```text
Hybrid wins pass_rate on the current tiny deterministic eval set.
Chroma slightly wins average_relevance_score, but deterministic hash embeddings cause the LangGraph query to retrieve the RAG chunk first, so Chroma misses the expected LangGraph terms in one case.
This is acceptable for Day33 because the goal is backend comparison infrastructure, not proving Chroma is better on this toy dataset.
```

New Day33 test file:

```text
tests/test_rag_backend_eval.py
```

---

## Current Day34 Backend Metrics and Stream Alignment Strategy

Day34 refined the backend comparison layer and aligned Agentic RAG streaming with the retrieval backend switch.

Current files:

```text
src/app/evaluation/rag_eval.py
src/app/rag/agentic_streaming.py
src/app/routes/routes_rag.py
src/app/schemas/rag.py
tests/test_rag_backend_eval.py
tests/test_rag_agentic_stream_backend.py
```

Current endpoints:

```text
POST /rag/backend-eval-debug
POST /rag/agentic-stream
```

Backend comparison now returns:

```text
metric_deltas
case_comparisons
comparison_summary
```

Observed Day34 metric deltas:

```text
baseline_backend = hybrid
comparison_backend = chroma
pass_rate_delta = -0.333333
retrieval_decision_accuracy_delta = 0.0
expected_terms_hit_rate_delta = -0.333333
citation_hit_rate_delta = 0.0
average_relevance_score_delta = 0.00101
```

Observed comparison summary:

```text
best_backend_by_pass_rate = hybrid
best_backend_by_average_relevance = chroma
notes:
  - hybrid has a higher pass_rate than chroma.
  - chroma has a higher average_relevance_score than hybrid.
```

Observed case comparisons:

```text
rag_definition: winner_by_pass = tie, winner_by_relevance = hybrid
langgraph_definition: winner_by_pass = hybrid, winner_by_relevance = chroma
direct_chat: winner_by_pass = tie, winner_by_relevance = hybrid
```

Agentic RAG stream now supports:

```text
retrieval_backend = hybrid
retrieval_backend = chroma
```

Chroma stream expected step path:

```text
query_analyzer -> query_rewriter -> chroma_retrieve -> relevance_grade -> answer_with_citations
```

Stream payload backend fields:

```text
retrieval_backend
retrieval_metadata
```

These are present in:

```text
metadata event
retrieval event
final event
rag_agentic_stream trace payload
```

New Day34 test file:

```text
tests/test_rag_agentic_stream_backend.py
```

---

## Current Day35 Reranker-ready Retrieval Strategy

Day35 added a deterministic reranker-ready retrieval backend.

Current files:

```text
src/app/rag/reranker.py
src/app/rag/retrieval_backend.py
src/app/rag/agentic_graph.py
src/app/schemas/rag.py
tests/test_rag_reranker.py
```

Current new backend:

```text
retrieval_backend = chroma_rerank
```

Supported Agentic RAG retrieval backends now include:

```text
hybrid
chroma
chroma_rerank
```

Default backend remains:

```text
hybrid
```

Chroma rerank path:

```text
retrieve_agentic_context()
  ↓
debug_chroma_search()
  ↓
_normalize_chroma_results()
  ↓
rerank_retrieval_results()
  ↓
Agentic RAG
```

Current reranker functions:

```text
extract_rerank_terms()
calculate_keyword_rerank_score()
rerank_retrieval_results()
```

Current deterministic scoring:

```text
rerank_score = 0.7 * original_score + 0.3 * keyword_score
```

Returned rerank metadata:

```text
original_rank
original_score
rerank_score
rerank_keyword_score
rerank_matched_terms
```

Agentic RAG step path with Chroma rerank:

```text
query_analyzer -> query_rewriter -> chroma_rerank_retrieve -> relevance_grade -> answer_with_citations
```

Observed LangGraph case behavior:

```text
chroma:
  citation = knowledge/agent_basics.md::chunk-2
  expected_terms_pass = false

chroma_rerank:
  citation = knowledge/agent_basics.md::chunk-1
  expected_terms_pass = true
  rerank_matched_terms = ["langgraph"]
```

Observed backend metrics:

```text
hybrid:
  pass_rate = 1.0
  average_relevance_score = 0.278223

chroma:
  pass_rate = 0.666667
  average_relevance_score = 0.279233

chroma_rerank:
  pass_rate = 1.0
  average_relevance_score = 0.394302
```

Important note:

```text
Day35 keeps the reranker deterministic and CI-safe.
It is a placeholder architecture for future cross-encoder, BGE reranker, or LLM reranker integration.
Day36 can refine multi-backend metric deltas or add a local semantic embedding validation path.
```

New Day35 test file:

```text
tests/test_rag_reranker.py
```

---

## Current Day36 Pairwise Backend Comparison Strategy

Day36 refined backend evaluation metric deltas.

Current files:

```text
src/app/evaluation/rag_eval.py
src/app/routes/routes_rag.py
src/app/schemas/rag.py
tests/test_rag_backend_pairwise_eval.py
```

Current endpoint:

```text
POST /rag/backend-eval-debug
```

Current comparison fields:

```text
metric_deltas
pairwise_metric_deltas
case_comparisons
comparison_summary
```

Backward compatibility:

```text
metric_deltas remains backend_results[0] vs backend_results[1].
```

New Day36 behavior:

```text
pairwise_metric_deltas compares all backend pairs in request order.
```

For:

```text
["hybrid", "chroma", "chroma_rerank"]
```

Day36 returns:

```text
hybrid -> chroma
hybrid -> chroma_rerank
chroma -> chroma_rerank
```

Observed pairwise metric deltas:

```text
hybrid -> chroma:
  pass_rate_delta = -0.333333
  expected_terms_hit_rate_delta = -0.333333
  average_relevance_score_delta = 0.00101

hybrid -> chroma_rerank:
  pass_rate_delta = 0.0
  expected_terms_hit_rate_delta = 0.0
  average_relevance_score_delta = 0.116079

chroma -> chroma_rerank:
  pass_rate_delta = 0.333333
  expected_terms_hit_rate_delta = 0.333333
  average_relevance_score_delta = 0.115069
```

Observed best backend fields:

```text
best_backend_by_pass_rate = hybrid
best_backend_by_average_relevance = chroma_rerank
```

Trace event:

```text
rag_backend_eval_debug
```

Trace payload now includes:

```text
pairwise_metric_deltas
```

Known compatibility note:

```text
comparison_summary.notes still follows the earlier first-vs-second summary wording.
This is acceptable for Day36 because Day36 specifically targets pairwise metric deltas.
Day37 can optionally make summary notes fully multi-backend-aware.
```

New Day36 test file:

```text
tests/test_rag_backend_pairwise_eval.py
```

---

## Current Day37 Multi-backend Comparison Summary Strategy

Day37 refined backend comparison summary generation.

Current files:

```text
src/app/evaluation/rag_eval.py
tests/test_rag_backend_comparison_summary.py
```

Current endpoint:

```text
POST /rag/backend-eval-debug
```

Current comparison fields:

```text
metric_deltas
pairwise_metric_deltas
case_comparisons
comparison_summary
```

New Day37 `comparison_summary` fields:

```text
evaluated_backends
metric_winners
metric_rankings
top_improvement_pairs
notes
```

Helper functions:

```text
_build_metric_rankings()
_build_metric_winners()
_build_top_improvement_pairs()
_build_multi_backend_summary_notes()
_build_comparison_summary()
```

Observed evaluated backends:

```text
hybrid
chroma
chroma_rerank
```

Observed metric winners:

```text
pass_rate:
  winners = hybrid, chroma_rerank
  tie = true
  value = 1.0

average_relevance_score:
  winners = chroma_rerank
  tie = false
  value = 0.394302
```

Observed top improvement pairs:

```text
pass_rate:
  chroma -> chroma_rerank, delta = 0.333333

expected_terms_hit_rate:
  chroma -> chroma_rerank, delta = 0.333333

average_relevance_score:
  hybrid -> chroma_rerank, delta = 0.116079
  chroma -> chroma_rerank, delta = 0.115069
  hybrid -> chroma, delta = 0.00101
```

Observed notes:

```text
Evaluated 3 backends: hybrid, chroma, chroma_rerank.
Pass rate is tied at 1.0 by hybrid, chroma_rerank.
Best average_relevance_score is chroma_rerank with value 0.394302.
Largest pass_rate improvement is chroma -> chroma_rerank with delta 0.333333.
Largest average_relevance_score improvement is hybrid -> chroma_rerank with delta 0.116079.
```

Trace event:

```text
rag_backend_eval_debug
```

Trace payload includes the refined multi-backend `comparison_summary`.

New Day37 test file:

```text
tests/test_rag_backend_comparison_summary.py
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
72 passed, 1 warning
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
72 passed, 1 warning
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

## Day28 - Agentic RAG Answer Verification

### Completed

- Added `src/app/rag/answer_verifier.py`
- Added `verify_agentic_rag_answer()`
- Added `/rag/answer-verify-debug`
- Reused Day24 `invoke_agentic_rag()`
- Reused Day26 `record_trace_event()`
- Added retrieval path verification
- Added direct path verification
- Returned `verification_mode`
- Returned `answer_supported`
- Returned `verification_pass`
- Returned `confidence`
- Returned `answer_has_citation`
- Returned `citation_coverage_pass`
- Returned `cited_in_answer`
- Returned `unsupported_citations`
- Returned `grounding_terms`
- Returned `matched_grounding_terms`
- Returned `risk_flags`
- Added `rag_answer_verify_debug` observability event
- Verified verification trace lookup through `/observability/traces/{trace_id}`
- Added `tests/test_rag_answer_verify.py`
- Expanded pytest from 66 tests to 69 tests
- Verified local pytest
- Verified GitHub Actions CI
- Git push succeeded

### New Endpoint

```text
POST /rag/answer-verify-debug
```

### New Files

```text
src/app/rag/answer_verifier.py
tests/test_rag_answer_verify.py
```

### Test Result

```text
72 passed, 1 warning
```

### CI Result

```text
GitHub Actions CI: green
```

### Commit

```text
25b07cd add agentic rag answer verification
```

### Notes

Day28 adds deterministic post-answer verification for Agentic RAG.

---

## Day29 - SQLite Vector Store Debug

### Completed

- Added `src/app/rag/vector_store.py`
- Added `init_vector_store()`
- Added `build_vector_store_index()`
- Added `query_vector_store()`
- Added `debug_vector_store_search()`
- Added `/rag/vector-store-debug`
- Reused Day21 `load_knowledge_chunks()`
- Reused Day22 `build_deterministic_embedding()`
- Reused Day22 `cosine_similarity()`
- Reused Day26 `record_trace_event()`
- Persisted chunk embeddings into SQLite
- Added SQLite table `rag_chunk_vectors`
- Returned `index_stats`
- Returned ranked vector-store results
- Supported `source_filter`
- Supported `max_chars`
- Supported `embedding_dim`
- Supported `top_k`
- Supported `rebuild_index`
- Added `rag_vector_store_debug` observability event
- Fixed JSON serialization issue by converting `db_path` to string and adding `default=str` in trace serialization
- Fixed schema mismatch from `inserted_chunks` to `inserted_count`
- Verified vector store Python direct calls
- Verified `/rag/vector-store-debug`
- Verified `/observability/traces/{trace_id}` for vector store traces
- Added `tests/test_rag_vector_store.py`
- Expanded pytest from 69 tests to 72 tests
- Verified local pytest
- Git push succeeded

### New Endpoint

```text
POST /rag/vector-store-debug
```

### New Files

```text
src/app/rag/vector_store.py
tests/test_rag_vector_store.py
```

### Modified Files

```text
src/app/observability/trace_store.py
src/app/routes/routes_rag.py
src/app/schemas/rag.py
```

### Test Result

```text
72 passed, 1 warning
```

### CI Result

```text
Not shown in the provided Day29 log. Confirm from GitHub Actions.
```

### Commit

```text
24bd5c0 add sqlite vector store debug
```

### Notes

Day29 prepares the project for real vector database integration. It still uses deterministic embeddings for stable tests, but the storage/query shape is closer to a real vector store.

---

## Day30 - EmbeddingProvider Abstraction

### Completed

- Added `src/app/rag/embedding_provider.py`
- Added `EmbeddingProvider` protocol
- Added `DeterministicEmbeddingProvider`
- Reserved `SentenceTransformersEmbeddingProvider`
- Added `get_embedding_provider()`
- Added `debug_embeddings()`
- Added `embedding_norm()`
- Added `/rag/embedding-debug`
- Added `rag_embedding_debug` observability event
- Upgraded `src/app/rag/vector_store.py` to use `EmbeddingProvider`
- Upgraded `/rag/vector-store-debug` with `embedding_provider`
- Upgraded `/rag/vector-store-debug` with `embedding_model`
- Updated vector store `index_key` to include provider and model
- Preserved deterministic provider as the default CI-safe fallback
- Verified direct Python embedding provider usage
- Verified `/rag/embedding-debug`
- Verified `/observability/traces/{trace_id}` for embedding debug traces
- Verified provider-aware `/rag/vector-store-debug`
- Added `tests/test_rag_embedding_provider.py`
- Expanded pytest from 72 tests to 75 tests
- Verified local pytest
- Verified GitHub Actions CI
- Git push succeeded

### New Endpoint

```text
POST /rag/embedding-debug
```

### Updated Endpoint

```text
POST /rag/vector-store-debug
```

### New Files

```text
src/app/rag/embedding_provider.py
tests/test_rag_embedding_provider.py
```

### Modified Files

```text
src/app/rag/vector_store.py
src/app/routes/routes_rag.py
src/app/schemas/rag.py
```

### Test Result

```text
75 passed, 1 warning
```

### CI Result

```text
GitHub Actions CI: green
```

### Notes

Day30 prepares the project for real vector database integration by decoupling embedding generation from vector store indexing/querying.

The project still defaults to deterministic embeddings for CI stability. Day31 can now add Chroma or another persistent vector database without changing the upper RAG endpoint contract.

---

## Day31 - Chroma Persistent Vector Store Debug

### Completed

- Added `chromadb` to `requirements.txt`
- Added `src/app/rag/chroma_store.py`
- Added `build_chroma_collection_name()`
- Added `build_chroma_index()`
- Added `query_chroma_store()`
- Added `debug_chroma_search()`
- Added `reset_chroma_persist_dir()`
- Added `/rag/chroma-search-debug`
- Reused Day21 `load_knowledge_chunks()`
- Reused Day30 `EmbeddingProvider`
- Used `chromadb.PersistentClient`
- Used Chroma persistent path `data/chroma`
- Added Chroma collection metadata for source/provider/model/dim
- Supported `top_k`, `source_filter`, `max_chars`, `embedding_dim`, `embedding_provider`, `embedding_model`, and `rebuild_index`
- Returned Chroma `index_stats`
- Returned ranked Chroma search results with `distance` and normalized `score`
- Added `rag_chroma_search_debug` observability event
- Verified Python direct Chroma index/search calls
- Verified `/rag/chroma-search-debug`
- Verified `/observability/traces/{trace_id}` for Chroma search traces
- Added `tests/test_rag_chroma_store.py`
- Expanded pytest from 75 tests to 78 tests
- Verified local pytest
- Verified GitHub Actions CI
- Git push succeeded

### New Endpoint

```text
POST /rag/chroma-search-debug
```

### New Files

```text
src/app/rag/chroma_store.py
tests/test_rag_chroma_store.py
```

### Modified Files

```text
requirements.txt
src/app/routes/routes_rag.py
src/app/schemas/rag.py
```

### Test Result

```text
78 passed, 1 warning
```

### CI Result

```text
GitHub Actions CI: green
```

### Commit

```text
747fed9 add chroma vector store debug
```

### Notes

Day31 connects a real persistent vector database path through Chroma while preserving deterministic embeddings as the default provider.

The current endpoint is intentionally debug-oriented. It proves index build, persistence, query, metadata, trace, and tests before wiring Chroma into the production Agentic RAG backend.

The observed collection name is truncated to satisfy Chroma's collection name length limit, so metadata and index_stats should be treated as the reliable source for `embedding_dim`, `embedding_provider`, and `embedding_model`.

---

## Day32 - Agentic RAG Retrieval Backend Switch

### Completed

- Optimized Chroma collection naming from long truncated names to short readable names with stable hash suffix
- Added `src/app/rag/retrieval_backend.py`
- Added `DEFAULT_RETRIEVAL_BACKEND`
- Added `SUPPORTED_RETRIEVAL_BACKENDS`
- Added `normalize_retrieval_backend()`
- Added `retrieve_agentic_context()`
- Added hybrid backend support through `hybrid_search_knowledge()`
- Added Chroma backend support through `debug_chroma_search()`
- Normalized hybrid retrieval results for Agentic RAG
- Normalized Chroma retrieval results for Agentic RAG
- Added Chroma compatibility fields: `hybrid_score`, `keyword_score`, and `vector_score`
- Updated `src/app/rag/agentic_graph.py`
- Added `retrieval_backend` to Agentic RAG state and response
- Added `retrieval_metadata` to Agentic RAG state and response
- Added `embedding_provider`, `embedding_model`, and `rebuild_index` to Agentic RAG state
- Updated retrieval node to use `retrieve_agentic_context()`
- Preserved default hybrid path and historical steps
- Added Chroma path step `chroma_retrieve`
- Fixed relevance grading to support both hybrid score and Chroma score
- Fixed answer node to return citations for retrieval results
- Fixed LangGraph `steps` duplication by returning only the current node step when using `operator.add`
- Updated `/rag/agentic-debug` request schema
- Updated `/rag/agentic-debug` response schema
- Updated `/rag/agentic-debug` route to pass backend parameters
- Updated `rag_agentic_debug` trace payload with backend metadata
- Verified collection names preserve `d64` and `d128`
- Verified hybrid backend direct Python call
- Verified Chroma backend direct Python call
- Verified `/rag/agentic-debug` hybrid backend
- Verified `/rag/agentic-debug` Chroma backend
- Verified `/observability/traces/{trace_id}` contains latest correct Chroma backend trace event
- Added `tests/test_rag_agentic_backend.py`
- Expanded pytest from 78 tests to 82 tests
- Verified local pytest
- Git push succeeded

### New Files

```text
src/app/rag/retrieval_backend.py
tests/test_rag_agentic_backend.py
```

### Modified Files

```text
src/app/rag/agentic_graph.py
src/app/rag/chroma_store.py
src/app/routes/routes_rag.py
src/app/schemas/rag.py
```

### Test Result

```text
82 passed, 1 warning
```

### CI Result

```text
Not shown in the provided Day32 log. Confirm from GitHub Actions.
```

### Commit

```text
ebc575e add agentic rag retrieval backend switch
```

### Notes

Day32 makes Chroma usable inside Agentic RAG without replacing the default hybrid backend.

The default `retrieval_backend` remains `hybrid` for compatibility and CI stability. Chroma can be selected explicitly by passing `retrieval_backend="chroma"`.

The trace lookup for `day32-agentic-chroma-001` contains multiple events because the same trace id was reused during debugging. Earlier events show the pre-fix state. The latest event is the source of truth and shows correct citations and the correct non-duplicated step list.

---

## Day33 - Chroma-backed RAG Evaluation and Backend Comparison

### Completed

- Extended `evaluate_rag_cases()` with backend-aware evaluation parameters
- Added `retrieval_backend` support to `/rag/eval-debug`
- Added `embedding_provider`, `embedding_model`, and `rebuild_index` support to `/rag/eval-debug`
- Preserved default hybrid backend behavior for compatibility
- Added Chroma backend evaluation path
- Added `compare_rag_retrieval_backends()`
- Added `/rag/backend-eval-debug`
- Added backend comparison response fields
- Added `best_backend_by_pass_rate`
- Added `best_backend_by_average_relevance`
- Added backend metrics list in trace payload
- Added `rag_backend_eval_debug` observability event
- Preserved Day25 case schema fields:
  - `matched_expected_terms`
  - `expected_citation_keywords`
  - `final_answer_preview`
  - `passed`
- Added backend-aware case fields:
  - `retrieval_backend`
  - `retrieval_metadata`
  - `steps`
- Verified direct Python hybrid evaluation
- Verified direct Python Chroma evaluation
- Verified direct Python backend comparison
- Verified `/rag/eval-debug` hybrid backend
- Verified `/rag/eval-debug` Chroma backend
- Verified `/rag/backend-eval-debug`
- Verified `/observability/traces/{trace_id}` for backend comparison traces
- Added `tests/test_rag_backend_eval.py`
- Expanded pytest from 82 tests to 86 tests
- Verified local pytest
- Verified GitHub Actions CI
- Git push succeeded

### New Endpoint

```text
POST /rag/backend-eval-debug
```

### Updated Endpoint

```text
POST /rag/eval-debug
```

### New File

```text
tests/test_rag_backend_eval.py
```

### Modified Files

```text
src/app/evaluation/rag_eval.py
src/app/routes/routes_rag.py
src/app/schemas/rag.py
```

### Test Result

```text
97 passed, 1 warning
```

### CI Result

```text
GitHub Actions CI: green
```

### Commit

```text
9ecc589 add rag backend evaluation comparison
```

### Notes

Day33 validates that the same evaluation cases can compare hybrid and Chroma retrieval backends through a common metrics contract.

Observed result: hybrid has better pass_rate on the current small eval set, while Chroma has a slightly higher average relevance score. This is expected because the current Chroma path still uses deterministic hash embeddings, not a semantic embedding model.

---

## Day34 - Backend Metrics Refinement and Stream Backend Alignment

### Completed

- Refined backend comparison output from `/rag/backend-eval-debug`
- Added `metric_deltas`
- Added `case_comparisons`
- Added `comparison_summary`
- Added helper logic for per-metric deltas
- Added helper logic for per-case backend comparisons
- Added helper logic for comparison summary notes
- Updated `RagBackendEvalDebugResponse`
- Updated `rag_backend_eval_debug` trace payload with refined metrics
- Aligned `/rag/agentic-stream` with `retrieval_backend`
- Added `retrieval_backend`, `embedding_provider`, `embedding_model`, and `rebuild_index` support to stream payload builder
- Passed backend parameters from route layer into `stream_agentic_rag_events()`
- Fixed the route-layer `trace_id` argument for `stream_agentic_rag_events()`
- Added `retrieval_backend` and `retrieval_metadata` to stream metadata event
- Added `retrieval_backend` and `retrieval_metadata` to stream retrieval event
- Added `retrieval_backend` and `retrieval_metadata` to stream final event
- Added `retrieval_backend` and `retrieval_metadata` to `rag_agentic_stream` trace payload
- Verified Chroma-backed Agentic RAG stream through curl
- Verified Chroma-backed stream trace lookup
- Added refined backend eval tests
- Added stream backend test file
- Expanded pytest from 86 tests to 89 tests
- Verified local pytest
- Verified GitHub Actions CI
- Git push succeeded

### New File

```text
tests/test_rag_agentic_stream_backend.py
```

### Modified Files

```text
src/app/evaluation/rag_eval.py
src/app/rag/agentic_streaming.py
src/app/routes/routes_rag.py
src/app/schemas/rag.py
tests/test_rag_backend_eval.py
```

### Test Result

```text
97 passed, 1 warning
```

### CI Result

```text
GitHub Actions CI: green
```

### Commit

```text
732742a refine rag backend metrics and stream backend support
```

### Notes

Day34 makes backend comparison more explainable and keeps JSON debug and SSE streaming behavior aligned.

Current backend comparison conclusion on the tiny deterministic eval set:

```text
best_backend_by_pass_rate = hybrid
best_backend_by_average_relevance = chroma
```

The result is expected because deterministic hash embeddings make Chroma retrieve the RAG chunk before the LangGraph chunk for the LangGraph case. The Day34 goal is comparison observability and stream alignment, not proving Chroma quality superiority.

---

## Day35 - Reranker-ready Retrieval Backend Extension

### Completed

- Added deterministic reranker layer
- Added `src/app/rag/reranker.py`
- Added `extract_rerank_terms()`
- Added `calculate_keyword_rerank_score()`
- Added `rerank_retrieval_results()`
- Added `retrieval_backend="chroma_rerank"`
- Added backend aliases for Chroma rerank
- Updated `retrieve_agentic_context()` to support Chroma retrieval followed by reranking
- Preserved default backend as `hybrid`
- Added Chroma rerank metadata: `base_backend`, `rerank_enabled`, and Chroma index metadata
- Updated Agentic RAG step name to `chroma_rerank_retrieve`
- Updated Agentic RAG answer prefix for Chroma rerank
- Extended `RagAgenticDebugResult` with reranker-compatible optional fields
- Verified standalone reranker promotes keyword-matching result
- Verified `retrieve_agentic_context(retrieval_backend="chroma_rerank")`
- Verified `invoke_agentic_rag(retrieval_backend="chroma_rerank")`
- Verified `/rag/agentic-debug` with Chroma rerank backend
- Verified `/rag/backend-eval-debug` can compare `hybrid`, `chroma`, and `chroma_rerank`
- Verified `chroma_rerank` fixes the LangGraph expected-terms miss from plain Chroma
- Added `tests/test_rag_reranker.py`
- Expanded pytest from 89 tests to 93 tests
- Verified local pytest
- Verified GitHub Actions CI
- Git push succeeded

### New Files

```text
src/app/rag/reranker.py
tests/test_rag_reranker.py
```

### Modified Files

```text
src/app/rag/agentic_graph.py
src/app/rag/retrieval_backend.py
src/app/schemas/rag.py
```

### Test Result

```text
97 passed, 1 warning
```

### CI Result

```text
GitHub Actions CI: green
```

### Commit

```text
19a8462 add reranker ready retrieval backend
```

### Notes

Day35 adds reranker-ready retrieval without introducing a heavy model dependency.

The deterministic reranker is intentionally simple and CI-safe. It fixes the current LangGraph case by promoting the chunk that matches the rewritten query term `langgraph`.

The current backend comparison result:

```text
best_backend_by_pass_rate = hybrid
best_backend_by_average_relevance = chroma_rerank
```

`hybrid` remains the best backend by pass rate only because `hybrid` and `chroma_rerank` tie at `pass_rate = 1.0`, and the current max selection returns the first maximum backend.

---

## Day36 - Pairwise Backend Comparison Refinement

### Completed

- Added common metric delta helper `_calculate_metric_delta()`
- Kept old `_build_metric_deltas()` behavior for backward compatibility
- Added `_build_pairwise_metric_deltas()`
- Added `pairwise_metric_deltas` to backend comparison result
- Added `pairwise_metric_deltas` to `RagBackendEvalDebugResponse`
- Added `pairwise_metric_deltas` to `rag_backend_eval_debug` trace payload
- Verified Python direct `compare_rag_retrieval_backends()` call
- Verified `/rag/backend-eval-debug` API response
- Verified `/observability/traces/{trace_id}` trace payload
- Added `tests/test_rag_backend_pairwise_eval.py`
- Verified Day36 focused tests
- Verified backend-related tests
- Verified full pytest
- Verified GitHub Actions CI
- Git push succeeded

### New File

```text
tests/test_rag_backend_pairwise_eval.py
```

### Modified Files

```text
src/app/evaluation/rag_eval.py
src/app/routes/routes_rag.py
src/app/schemas/rag.py
```

### Test Result

```text
97 passed, 1 warning
```

### CI Result

```text
GitHub Actions CI: green
```

### Commit

```text
ad05e3f add pairwise rag backend metric deltas
```

### Observed Pairwise Deltas

```text
hybrid -> chroma:
  pass_rate_delta = -0.333333
  expected_terms_hit_rate_delta = -0.333333
  average_relevance_score_delta = 0.00101

hybrid -> chroma_rerank:
  pass_rate_delta = 0.0
  expected_terms_hit_rate_delta = 0.0
  average_relevance_score_delta = 0.116079

chroma -> chroma_rerank:
  pass_rate_delta = 0.333333
  expected_terms_hit_rate_delta = 0.333333
  average_relevance_score_delta = 0.115069
```

### Notes

Day36 makes the backend evaluation endpoint suitable for more than two retrieval strategies.

The old `metric_deltas` field remains first-vs-second so Day34/Day35 clients and tests remain compatible. The new `pairwise_metric_deltas` field should be used for multi-backend comparison.

---

## Day37 - Multi-backend Comparison Summary Refinement

### Completed

- Refined `comparison_summary` from first-vs-second notes to multi-backend-aware summary
- Added metric ranking helper
- Added metric winner helper
- Added top improvement pair helper
- Added multi-backend summary notes helper
- Updated `_build_comparison_summary()`
- Added `comparison_summary.evaluated_backends`
- Added `comparison_summary.metric_winners`
- Added `comparison_summary.metric_rankings`
- Added `comparison_summary.top_improvement_pairs`
- Updated `comparison_summary.notes` to describe all evaluated backends
- Preserved existing response field names
- Verified Python direct `compare_rag_retrieval_backends()` call
- Verified `/rag/backend-eval-debug` API response
- Verified `/observability/traces/{trace_id}` trace payload
- Added `tests/test_rag_backend_comparison_summary.py`
- Verified Day37 focused tests
- Verified backend evaluation related tests
- Verified full pytest
- Verified GitHub Actions CI
- Git push succeeded

### New File

```text
tests/test_rag_backend_comparison_summary.py
```

### Modified File

```text
src/app/evaluation/rag_eval.py
```

### Test Result

```text
97 passed, 1 warning
```

### CI Result

```text
GitHub Actions CI: green
```

### Commit

```text
d1e0878 refine rag backend comparison summary
```

### Observed Summary

```text
evaluated_backends = hybrid, chroma, chroma_rerank
best_backend_by_pass_rate = hybrid
best_backend_by_average_relevance = chroma_rerank
pass_rate tie = hybrid, chroma_rerank
average_relevance_score winner = chroma_rerank
```

### Notes

Day37 closes the known Day36 limitation. The backend comparison summary is now aligned with pairwise backend comparison and can directly explain multi-backend evaluation results.

---

## Current Day38 Semantic Embedding Provider Local Validation Strategy

Day38 validated the previously reserved `sentence_transformers` provider locally without making CI depend on model downloads, GPU, or Hugging Face network access.

Current local semantic embedding configuration:

```text
provider = sentence_transformers
model = /mnt/f/LLM/maidalun/bce-embedding-base_v1
embedding_dim = 768
```

Current validation script:

```text
scripts/validate_semantic_embedding_provider.py
```

Current CI-safe test:

```text
tests/test_rag_semantic_embedding_provider.py
```

Validated paths:

```text
get_embedding_provider(provider="sentence_transformers", embedding_model=local_model_path)
/rag/embedding-debug
/rag/chroma-search-debug
/rag/agentic-debug with retrieval_backend="chroma"
/rag/backend-eval-debug with hybrid, chroma, and chroma_rerank
/observability/traces/day38-local-embedding-debug-001
/observability/traces/day38-local-backend-eval-001
```

Observed local semantic backend metrics:

```text
hybrid:
  pass_rate = 1.0
  average_relevance_score = 0.235843

chroma:
  pass_rate = 1.0
  average_relevance_score = 0.415862

chroma_rerank:
  pass_rate = 1.0
  average_relevance_score = 0.491103
```

Parameter boundary fixed in Day38:

```text
API and store-layer request fields:
  embedding_model

get_embedding_provider():
  embedding_model

SentenceTransformersEmbeddingProvider.__init__():
  model_name
```

Important compatibility note:

```text
The deterministic provider remains the default.
The local semantic provider is manually validated and covered by a skip-safe test.
CI should skip the semantic provider test when `/mnt/f/LLM/maidalun/bce-embedding-base_v1` is unavailable.
```

## Current Day39 Backend Evaluation Report Strategy

Day39 added a backend evaluation report layer on top of the existing backend comparison output.

```text
/rag/backend-eval-debug
  ↓
compare_rag_retrieval_backends()
  ↓
metric_deltas + pairwise_metric_deltas + case_comparisons + comparison_summary
  ↓
build_backend_evaluation_report()
  ↓
evaluation_report
```

Current report file:

```text
src/app/evaluation/rag_report.py
```

Current report builder:

```text
build_backend_evaluation_report(comparison: dict) -> dict
```

The report builder is intentionally pure:

```text
No FastAPI dependency
No Chroma dependency
No embedding model loading
No evaluation re-run
```

The backend evaluation response now includes:

```text
evaluation_report.recommended_backend
evaluation_report.recommendation_reason
evaluation_report.default_backend
evaluation_report.default_backend_should_change
evaluation_report.selection_policy
evaluation_report.embedding_provider
evaluation_report.embedding_model
evaluation_report.eval_file
evaluation_report.eval_case_count
evaluation_report.metric_highlights
evaluation_report.risk_notes
evaluation_report.backend_rank_summary
evaluation_report.interpretation
```

Observed Day39 deterministic evaluation report:

```text
recommended_backend = chroma_rerank
default_backend = hybrid
default_backend_should_change = false
selection_policy = keep_default_hybrid_until_larger_eval_set
embedding_provider = deterministic
eval_case_count = 3
```

Observed Day39 backend ranking:

```text
chroma_rerank:
  pass_rate = 1.0
  average_relevance_score = 0.394302
  strength = recommended candidate on current evaluation

hybrid:
  pass_rate = 1.0
  average_relevance_score = 0.278223
  strength = top pass-rate group

chroma:
  pass_rate = 0.666667
  average_relevance_score = 0.279233
  strength = comparison backend
```

Important Day39 interpretation:

```text
chroma_rerank is recommended as an experiment candidate on the current tiny deterministic eval set.
The default backend should remain hybrid until a larger and more representative eval set validates a production switch.
Deterministic embeddings are CI-safe but do not represent real semantic embedding quality.
```

## Day38 - Semantic Embedding Provider Local Validation

### Completed

- Added local validation script for the reserved `sentence_transformers` provider
- Updated validation to use the local BCE embedding model path instead of remote Hugging Face model name
- Validated local model loading from `/mnt/f/LLM/maidalun/bce-embedding-base_v1`
- Validated `actual_embedding_dim = 768`
- Validated `/rag/embedding-debug` with `provider="sentence_transformers"`
- Validated `/rag/chroma-search-debug` with semantic embeddings
- Validated `/rag/agentic-debug` with `retrieval_backend="chroma"` and semantic embeddings
- Validated `/rag/backend-eval-debug` with `hybrid`, `chroma`, and `chroma_rerank`
- Verified trace events for `rag_embedding_debug` and `rag_backend_eval_debug`
- Added CI-safe semantic provider test that skips when `sentence-transformers` or the local model path is unavailable
- Fixed provider argument naming across Chroma and SQLite vector store paths
- Preserved deterministic embeddings as the default CI-safe provider
- Verified local focused tests
- Verified local full pytest
- Verified GitHub Actions CI
- Git push succeeded

### New File

```text
tests/test_rag_semantic_embedding_provider.py
```

### New Script

```text
scripts/validate_semantic_embedding_provider.py
```

### Modified Files

```text
src/app/rag/embedding_provider.py
src/app/rag/chroma_store.py
src/app/rag/vector_store.py
```

### Test Result

```text
RAG focused tests: 28 passed, 1 warning
Full local pytest: 98 passed, 1 warning
```

### CI Result

```text
GitHub Actions CI: green
```

### Notes

Day38 proves that the project can switch from deterministic hash embeddings to a real local semantic embedding provider for Chroma-backed RAG paths while keeping CI deterministic and dependency-safe.

## Day39 - Backend Evaluation Report

### Completed

- Added backend evaluation report builder
- Added `src/app/evaluation/rag_report.py`
- Added pure function `build_backend_evaluation_report(comparison: dict) -> dict`
- Integrated `evaluation_report` into `compare_rag_retrieval_backends()`
- Added `evaluation_report` to `RagBackendEvalDebugResponse`
- Preserved existing backend comparison fields:
  - `metric_deltas`
  - `pairwise_metric_deltas`
  - `case_comparisons`
  - `comparison_summary`
  - `results`
- Added report-level recommendation fields:
  - `recommended_backend`
  - `recommendation_reason`
  - `default_backend`
  - `default_backend_should_change`
  - `selection_policy`
- Added report-level evidence fields:
  - `metric_highlights`
  - `risk_notes`
  - `backend_rank_summary`
  - `interpretation`
- Added deterministic embedding risk note
- Added small/tiny eval set caveat
- Added default-backend safety policy that keeps `hybrid` as the default until a larger eval set validates switching
- Added `tests/test_rag_backend_report.py`
- Verified focused backend report tests
- Verified backend evaluation related tests
- Verified RAG related tests
- Verified full local pytest
- Verified `/rag/backend-eval-debug` returns `evaluation_report`
- Git push succeeded

### New File

```text
src/app/evaluation/rag_report.py
tests/test_rag_backend_report.py
```

### Modified Files

```text
src/app/evaluation/rag_eval.py
src/app/schemas/rag.py
```

### Test Result

```text
Backend report focused tests: 2 passed, 1 warning
Backend eval related tests: 12 passed, 1 warning
RAG related tests: 30 passed, 1 warning
Full local pytest: 100 passed, 1 warning
```

### API Verification

```text
POST /rag/backend-eval-debug
```

Observed `evaluation_report`:

```text
recommended_backend = chroma_rerank
recommendation_reason = chroma_rerank is the current experiment candidate, but the default backend should remain hybrid until larger and more representative evaluation data is available.
default_backend = hybrid
default_backend_should_change = false
selection_policy = keep_default_hybrid_until_larger_eval_set
embedding_provider = deterministic
eval_case_count = 3
```

Observed report risk notes:

```text
The current eval set is small/tiny, so the report should be treated as a regression and debugging signal rather than a production-level benchmark.
The current run uses deterministic embeddings, which are CI-safe but do not represent real semantic embedding quality.
chroma_rerank is recommended as an experiment candidate, but the default backend should remain hybrid until a larger eval set validates the change.
```

### Commit

```text
1312c5f add rag backend evaluation report
```

### CI Result

```text
Not shown in the provided Day39 log. Confirm from GitHub Actions.
```

### Notes

Day39 first stage is complete locally. The project now converts raw backend comparison metrics into an engineering-facing retrieval backend selection report. This keeps the existing debug/eval output available while adding a safer decision layer that distinguishes experiment candidates from production default backend changes.

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
100 passed, 1 warning
```

CI may show `97 passed, 1 skipped, 1 warning` because the Day38 local semantic embedding test skips when the local BCE model path is unavailable.

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
Day39: Evaluation report polishing or production retrieval backend selection
Day40: Documentation cleanup and optional semantic retrieval evaluation expansion
Later: Document upload and parsing pipeline
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

- [x] Day28 Agentic RAG Answer Verification
- [x] Day28 `/rag/answer-verify-debug`
- [x] Day28 `verify_agentic_rag_answer()`
- [x] Day28 retrieval path verification
- [x] Day28 direct path verification
- [x] Day28 `verification_pass`
- [x] Day28 `confidence`
- [x] Day28 citation coverage checks
- [x] Day28 grounding terms checks
- [x] Day28 `risk_flags`
- [x] Day28 `rag_answer_verify_debug` trace event
- [x] Day28 answer verification tests
- [x] Day28 GitHub Actions CI
- [x] Day28 Git push

Next:

- [x] Day29 SQLite Vector Store Debug
- [x] Day29 `/rag/vector-store-debug`
- [x] Day29 `build_vector_store_index()`
- [x] Day29 `query_vector_store()`
- [x] Day29 `debug_vector_store_search()`
- [x] Day29 SQLite chunk embedding persistence
- [x] Day29 `index_stats`
- [x] Day29 `rag_vector_store_debug` trace event
- [x] Day29 vector store tests
- [x] Day29 local pytest
- [x] Day29 Git push

Next:

- [x] Day30 EmbeddingProvider abstraction
- [x] Day30 `/rag/embedding-debug`
- [x] Day30 `EmbeddingProvider`
- [x] Day30 `DeterministicEmbeddingProvider`
- [x] Day30 reserved `SentenceTransformersEmbeddingProvider`
- [x] Day30 `get_embedding_provider()`
- [x] Day30 `debug_embeddings()`
- [x] Day30 provider-aware `/rag/vector-store-debug`
- [x] Day30 `rag_embedding_debug` trace event
- [x] Day30 embedding provider tests
- [x] Day30 local pytest
- [x] Day30 GitHub Actions CI
- [x] Day30 Git push

Next:

- [x] Day31 Chroma persistent vector store debug
- [x] Day31 `chromadb` dependency
- [x] Day31 `/rag/chroma-search-debug`
- [x] Day31 `build_chroma_index()`
- [x] Day31 `query_chroma_store()`
- [x] Day31 `debug_chroma_search()`
- [x] Day31 Chroma PersistentClient path
- [x] Day31 Chroma index stats
- [x] Day31 `rag_chroma_search_debug` trace event
- [x] Day31 Chroma tests
- [x] Day31 local pytest
- [x] Day31 GitHub Actions CI
- [x] Day31 Git push

Next:

- [x] Day32 Agentic RAG retrieval backend switch
- [x] Day32 Chroma collection short hash naming
- [x] Day32 `src/app/rag/retrieval_backend.py`
- [x] Day32 `retrieve_agentic_context()`
- [x] Day32 `retrieval_backend="hybrid"`
- [x] Day32 `retrieval_backend="chroma"`
- [x] Day32 `/rag/agentic-debug` Chroma backend
- [x] Day32 `retrieval_backend` response field
- [x] Day32 `retrieval_metadata` response field
- [x] Day32 trace backend metadata
- [x] Day32 Agentic RAG backend tests
- [x] Day32 local pytest
- [x] Day32 Git push

Next:

- [x] Day33 Chroma-backed RAG evaluation and backend comparison
- [x] Day33 `/rag/eval-debug` backend-aware evaluation
- [x] Day33 `/rag/backend-eval-debug`
- [x] Day33 `compare_rag_retrieval_backends()`
- [x] Day33 hybrid evaluation metrics
- [x] Day33 Chroma evaluation metrics
- [x] Day33 backend comparison trace event
- [x] Day33 backend eval tests
- [x] Day33 local pytest
- [x] Day33 GitHub Actions CI
- [x] Day33 Git push

Next:

- [x] Day34 Backend metrics refinement and stream/backend alignment
- [x] Day34 `metric_deltas`
- [x] Day34 `case_comparisons`
- [x] Day34 `comparison_summary`
- [x] Day34 refined `rag_backend_eval_debug` trace payload
- [x] Day34 `/rag/agentic-stream` supports `retrieval_backend="hybrid"`
- [x] Day34 `/rag/agentic-stream` supports `retrieval_backend="chroma"`
- [x] Day34 stream `metadata` event includes backend metadata
- [x] Day34 stream `retrieval` event includes backend metadata
- [x] Day34 stream `final` event includes backend metadata
- [x] Day34 `rag_agentic_stream` trace includes backend metadata
- [x] Day34 stream backend tests
- [x] Day34 local pytest
- [x] Day34 GitHub Actions CI
- [x] Day34 Git push

Next:

- [x] Day35 Reranker-ready retrieval backend extension
- [x] Day35 `src/app/rag/reranker.py`
- [x] Day35 `retrieval_backend="chroma_rerank"`
- [x] Day35 `chroma_rerank_retrieve` Agentic RAG step
- [x] Day35 reranker metadata fields
- [x] Day35 `/rag/agentic-debug` Chroma rerank path
- [x] Day35 `/rag/backend-eval-debug` comparison with `chroma_rerank`
- [x] Day35 `tests/test_rag_reranker.py`
- [x] Day35 local pytest
- [x] Day35 GitHub Actions CI
- [x] Day35 Git push

Next:

- [x] Day36 Pairwise backend comparison refinement
- [x] Day36 `_calculate_metric_delta()`
- [x] Day36 `_build_pairwise_metric_deltas()`
- [x] Day36 `pairwise_metric_deltas` response field
- [x] Day36 `pairwise_metric_deltas` trace payload
- [x] Day36 `tests/test_rag_backend_pairwise_eval.py`
- [x] Day36 local pytest
- [x] Day36 GitHub Actions CI
- [x] Day36 Git push

Next:

- [x] Day37 Multi-backend comparison summary refinement
- [x] Day37 `comparison_summary.evaluated_backends`
- [x] Day37 `comparison_summary.metric_winners`
- [x] Day37 `comparison_summary.metric_rankings`
- [x] Day37 `comparison_summary.top_improvement_pairs`
- [x] Day37 multi-backend-aware `comparison_summary.notes`
- [x] Day37 `tests/test_rag_backend_comparison_summary.py`
- [x] Day37 local pytest
- [x] Day37 GitHub Actions CI
- [x] Day37 Git push

Next:

- [x] Day38 Semantic embedding provider local validation
- [x] Day38 local semantic BCE model validation
- [x] Day38 `/rag/embedding-debug` semantic provider validation
- [x] Day38 `/rag/chroma-search-debug` semantic provider validation
- [x] Day38 `/rag/agentic-debug` Chroma semantic validation
- [x] Day38 `/rag/backend-eval-debug` semantic backend comparison
- [x] Day38 semantic provider CI-safe skip test
- [x] Day38 local pytest
- [x] Day38 GitHub Actions CI
- [x] Day38 Git push

Next:

- [x] Day39 Backend evaluation report layer
- [x] Day39 `src/app/evaluation/rag_report.py`
- [x] Day39 `build_backend_evaluation_report()`
- [x] Day39 `/rag/backend-eval-debug` returns `evaluation_report`
- [x] Day39 `evaluation_report.recommended_backend`
- [x] Day39 `evaluation_report.metric_highlights`
- [x] Day39 `evaluation_report.risk_notes`
- [x] Day39 `evaluation_report.backend_rank_summary`
- [x] Day39 `tests/test_rag_backend_report.py`
- [x] Day39 focused backend report tests
- [x] Day39 backend evaluation related tests
- [x] Day39 RAG related tests
- [x] Day39 full local pytest
- [x] Day39 Git push
- [ ] Day39 GitHub Actions CI confirmation

Next:

- [ ] Day39 second stage evaluation report polishing or production retrieval backend selection
