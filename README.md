# agent-api

`agent-api` is a FastAPI + LangGraph backend project for building an Agent service step by step.

This project is the second project in the AI internship preparation roadmap, following the completed `chat-api-v2` project. The current version implements a deterministic Tool Calling Agent, SQLite-based short-term memory, graph debug output, request tracing, LLM provider abstraction, a real Ollama-backed LLM Tool Calling Agent path, SSE streaming endpoints, a lightweight local RAG search tool, a RAG search-debug endpoint with explainability metadata, a deterministic Router Agent that delegates calculator and RAG routes to the existing Agent graph, a Router Agent SSE streaming endpoint, an initial LLM Router Agent endpoint with mock and Ollama router providers, a Smart Chat endpoint as a future unified Agent entry point preview, a Smart Chat SSE streaming endpoint, route validation metadata for Router and Smart Chat paths, and a RAG chunk pipeline debug endpoint for vector DB preparation, a deterministic RAG vector-search debug endpoint, a hybrid retrieval debug endpoint that combines keyword and vector signals, an Agentic RAG debug graph with query analysis, query rewriting, hybrid retrieval, relevance grading, citation-aware answers, an Agentic RAG SSE streaming endpoint, an Agentic RAG answer verification debug endpoint, and a SQLite-backed vector store debug layer for real vector database preparation.

## Current Status

```text
Day1-Day29 completed.
Current stage: SQLite Vector Store Debug completed.
Local pytest: 72 passed, 1 warning.
Git push: success.
GitHub Actions CI: not shown in the provided Day29 log; confirm from GitHub Actions.
Next milestone: Day30 real embedding provider and real vector database integration.
```

## Features

Current features:

* FastAPI backend service
* `/health` health check endpoint
* `/agent/chat` deterministic Agent chat endpoint
* `/agent/debug` deterministic graph execution debug endpoint
* `/llm/chat` LLM chat test endpoint
* `/agent/llm-chat` real LLM Tool Calling Agent endpoint
* `/agent/llm-debug` real LLM Tool Calling Agent debug endpoint
* `/agent/stream` deterministic Agent SSE streaming endpoint
* `/agent/llm-stream` real LLM Tool Calling Agent SSE streaming endpoint
* `/rag/search` lightweight local RAG search endpoint
* `/rag/search-debug` RAG search explainability endpoint
* `/rag/chunks-debug` RAG chunk pipeline debug endpoint
* `/rag/vector-search-debug`, `/rag/hybrid-search-debug` deterministic RAG vector-search debug endpoint
* `/rag/hybrid-search-debug` hybrid retrieval debug endpoint
* `/rag/agentic-debug` Agentic RAG debug graph endpoint
* `/rag/agentic-stream` Agentic RAG SSE streaming endpoint
* `/rag/answer-verify-debug` Agentic RAG answer verification debug endpoint
* `/rag/vector-store-debug` SQLite-backed vector store debug endpoint
* `/rag/eval-debug` RAG evaluation debug endpoint
* `/observability/traces/{trace_id}` trace event lookup endpoint
* `/observability/traces` recent trace list endpoint
* `/agent/router-chat` deterministic Router Agent chat endpoint
* `/agent/router-debug` deterministic Router Agent debug endpoint
* `/agent/router-stream` deterministic Router Agent SSE streaming endpoint
* `/agent/llm-router-chat` initial LLM Router Agent chat endpoint
* `/agent/smart-chat` Smart Chat unified entry point preview
* `/agent/smart-stream` Smart Chat SSE streaming endpoint
* LangGraph `StateGraph`
* Deterministic Tool Calling Agent loop
* Real LLM Tool Calling Agent loop
* Built-in tools:
  * `add`
  * `multiply`
  * `search_knowledge_base`
* Lightweight keyword-based retriever
* RAG debug metadata: `normalized_query`, `rank`, `source`, `score`, `preview`, `matched_terms`, and `content_length`
* RAG chunk metadata: `chunk_id`, `source`, `index`, `content`, `preview`, and `content_length`
* Markdown document loading and blank-line based chunk splitting
* Deterministic hashed embedding for CI-safe vector-search preview
* Cosine similarity based chunk ranking
* Vector search debug metadata: `rank`, `chunk_id`, `source`, `score`, `matched_terms`, `preview`, and `content_length`
* Hybrid retrieval scoring with `hybrid_score`, `keyword_score`, and `vector_score`
* Hybrid retrieval weights: `keyword_weight` and `vector_weight`
* Agentic RAG workflow with `query_analyzer`, `query_rewriter`, `hybrid_retrieve`, `relevance_grade`, and `answer_with_citations`
* Agentic RAG debug metadata: `rewritten_query`, `retrieval_needed`, `relevance_score`, `citations`, `retrieval_results`, `final_answer`, and `steps`
* Agentic RAG stream events: `metadata`, `decision`, `rewrite`, `retrieval`, `relevance`, `citation`, `answer_chunk`, `final`, and `done`
* Agentic RAG streaming observability event: `rag_agentic_stream`
* Agentic RAG answer verification metadata: `verification_mode`, `answer_supported`, `verification_pass`, `confidence`, `answer_has_citation`, `citation_coverage_pass`, `cited_in_answer`, `unsupported_citations`, `grounding_terms`, `matched_grounding_terms`, and `risk_flags`
* Agentic RAG answer verification observability event: `rag_answer_verify_debug`
* SQLite-backed vector store debug layer with `build_vector_store_index()`, `query_vector_store()`, and `debug_vector_store_search()`
* Vector store index statistics: `index_key`, `loaded_chunks`, `inserted_count`, `stored_count`, and `db_path`
* Vector store debug observability event: `rag_vector_store_debug`
* Local Markdown knowledge base under `knowledge/`
* UTF-8 encoded knowledge base files for CI compatibility
* Deterministic Router Agent route classification
* Router branches: `calculator`, `rag`, and `chat`
* Router `calculator` and `rag` routes delegated to existing deterministic Agent graph
* Router delegation shares `thread_id` with Agent memory
* Router SSE stream events: `metadata`, `route`, `answer_chunk`, `final`, `done`
* LLM Router provider switch: `mock` for CI and `ollama` for local manual verification
* LLM Router response metadata: `route_reason`, `router_provider`, and `router_model`
* Smart Chat router mode switch: `deterministic` or `llm`
* Smart Chat unified response metadata: `route`, `route_reason`, `router_mode`, `router_provider`, and `router_model`
* Smart Stream SSE events: `metadata`, `route`, `answer_chunk`, `final`, `done`
* Smart Stream SSE payload metadata: `route_reason`, `router_mode`, `router_provider`, and `router_model`
* Route validation metadata: `route_confidence`, `route_valid`, `fallback_used`, and `validation_reason`
* Invalid route fallback support through `validate_route_decision()`
* SQLite checkpoint-based short-term memory
* `thread_id` based conversation state
* Request logging middleware
* `x-trace-id` request tracing
* Automatic trace id generation when client does not provide one
* Trace id reuse when client provides `x-trace-id`
* `trace_id` included in Agent, LLM, RAG, and streaming responses
* Latency logging with `latency_ms`
* LLM provider abstraction
* Mock LLM provider for deterministic tests and CI
* Ollama LLM provider based on `langchain-ollama`
* Ollama tool binding via `bind_tools()`
* Server-Sent Events streaming response
* SSE event helper with `ensure_ascii=False` for readable Chinese output
* Environment-based LLM provider configuration
* Request-level provider override for `/llm/chat`
* Split pytest API tests
* GitHub Actions CI

Not implemented yet:

* OpenAI provider
* Replacing `/agent/chat` with the real LLM Agent as the default main route
* Making Smart Chat the default production entry point
* Vector database based RAG
* Embedding-based retrieval
* Document upload and parsing pipeline
* GraphRAG
* Multi-Agent workflow

## Tech Stack

* Python 3.10
* FastAPI
* Uvicorn
* Pydantic
* Pydantic Settings
* LangGraph
* LangChain Core
* LangChain Ollama
* LangGraph prebuilt `ToolNode`
* LangGraph prebuilt `tools_condition`
* SQLite checkpoint saver
* Local Markdown knowledge base
* Lightweight keyword retriever
* Deterministic Router Agent
* Initial LLM Router Agent
* Smart Chat unified entry point preview
* Route validation metadata layer
* RAG chunk pipeline for vector DB preparation
* Deterministic RAG vector-search debug layer
* Hybrid retrieval debug layer
* Agentic RAG debug graph
* RAG evaluation debug layer
* Observability trace store
* Agentic RAG streaming layer
* Agentic RAG answer verification layer
* SQLite-backed vector store debug layer
* pytest
* GitHub Actions
* Server-Sent Events

## Project Structure

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
│   ├── DAY27.md
│   ├── DAY28.md
│   └── DAY29.md
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
│       │   ├── answer_verifier.py
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
    ├── test_router_agent.py
    ├── test_router_delegation.py
    ├── test_router_stream.py
    ├── test_llm_router.py
    └── test_smart_chat.py
```

## Current Agent Graphs

### Deterministic Agent Graph

`/agent/chat`, `/agent/debug`, and `/agent/stream` use the deterministic graph.

```text
START
  ↓
agent
  ↓
tools_condition
  ├── END
  └── tools
        ↓
      agent
```

For a deterministic tool call, the message flow is:

```text
HumanMessage
  ↓
AIMessage(tool_calls generated by rule-based node)
  ↓
ToolMessage
  ↓
AIMessage(final answer)
```

The deterministic graph currently supports:

```text
add
multiply
search_knowledge_base
```

RAG-related questions such as `请搜索知识库：RAG 是什么？` are routed to the `search_knowledge_base` tool by deterministic keyword rules.

### Real LLM Tool Calling Agent Graph

`/agent/llm-chat`, `/agent/llm-debug`, and `/agent/llm-stream` use the real LLM Tool Calling Agent graph.

```text
START
  ↓
llm_agent_node
  ↓
tools_condition
  ├── END
  └── tools
        ↓
      llm_agent_node
```

For a real LLM tool call, the message flow is:

```text
HumanMessage
  ↓
AIMessage(tool_calls generated by Ollama model)
  ↓
ToolMessage
  ↓
AIMessage(final answer generated by Ollama model)
```

## Current LLM Provider Architecture

Day9 added an independent LLM provider abstraction. Day10 uses the Ollama provider in the LLM Agent graph and binds the existing tools to the model.

```text
FastAPI
  ↓
/agent/llm-chat or /agent/llm-debug
  ↓
llm_agent_graph
  ↓
llm_agent_node
  ↓
get_chat_provider(provider="ollama")
  ↓
OllamaChatProvider.bind_tools(tools)
  ↓
ToolNode(tools)
```

Current providers:

```text
mock
ollama
```

Provider configuration:

```env
LLM_PROVIDER=mock
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b
OLLAMA_TEMPERATURE=0
```

When WSL accesses Ollama running on the Windows host, `OLLAMA_BASE_URL` can be set to the Windows host IP exposed through WSL networking.

## Current Streaming Architecture

Day11 added SSE streaming endpoints while keeping deterministic and real LLM paths separate.

```text
/agent/stream
  ↓
stream_agent_events()
  ↓
invoke_agent()
  ↓
metadata -> answer_chunk -> final -> done
```

```text
/agent/llm-stream
  ↓
stream_llm_agent_events()
  ↓
llm_agent_graph.stream(..., stream_mode="updates")
  ↓
metadata -> step(agent) -> step(tools) -> step(agent) -> final -> done
```

SSE payloads are serialized with:

```text
ensure_ascii=False
```

This keeps Chinese output readable in terminal responses instead of showing Unicode escape sequences.

## Current RAG Architecture

Day12 added a lightweight deterministic RAG search path.

```text
knowledge/agent_basics.md
  ↓
search_knowledge()
  ↓
/rag/search
```

The same retriever is also exposed to the deterministic Agent as a tool:

```text
/agent/chat or /agent/debug
  ↓
agent_node
  ↓
AIMessage(tool_calls=[search_knowledge_base])
  ↓
ToolNode(tools)
  ↓
search_knowledge_base()
  ↓
search_knowledge()
  ↓
AIMessage(final answer)
```

Day12 intentionally uses a simple keyword retriever instead of embeddings or a vector database. This keeps pytest and GitHub Actions deterministic and avoids external services.

Important Day12 notes:

```text
Knowledge files are stored under knowledge/.
Knowledge files must be UTF-8 encoded.
Runtime files remain under data/ and are ignored by Git.
The initial vector DB / embedding pipeline is intentionally deferred.
```

## Current Router Agent Architecture

Day13 added a deterministic Router Agent while keeping the existing deterministic Agent and real LLM Agent paths separate.

```text
/agent/router-chat or /agent/router-debug
  ↓
router_agent_graph
  ↓
router
  ├── calculator
  ├── rag
  └── chat
```

The Router Agent classifies each user message into one route:

```text
calculator  # arithmetic requests such as 请计算 3 加 5
rag         # knowledge-base / RAG / LangGraph search requests
chat        # ordinary chat requests
```

Current Router Agent endpoints:

```text
POST /agent/router-chat
POST /agent/router-debug
```

`/agent/router-chat` returns the selected `route` and final answer.

`/agent/router-debug` exposes node-level routing steps such as:

```text
router -> rag
```

Day13 introduced deterministic rule-based routing. Day14 keeps that routing layer but delegates `calculator` and `rag` execution to the existing deterministic Agent graph through `invoke_agent()`. This reuses the existing tools, graph behavior, and SQLite short-term memory instead of duplicating logic inside the router.

## Current Router Delegation Architecture

Day14 connects the Router Agent to existing Agent capabilities.

```text
/agent/router-chat
  ↓
router_agent_graph
  ↓
router
  ├── calculator -> invoke_agent() -> add / multiply tool
  ├── rag        -> invoke_agent() -> search_knowledge_base tool
  └── chat       -> Router chat response
```

The important Day14 behavior is that delegated routes reuse the same `thread_id` when calling `invoke_agent()`.

This means a Router call can write to the existing Agent short-term memory, and a later `/agent/chat` request with the same `thread_id` can recall that interaction.

Example:

```text
/agent/router-chat: 请计算 4 乘 9
  ↓
calculator route
  ↓
invoke_agent(thread_id=same_thread_id)
  ↓
ToolMessage(name=multiply, content=36)
  ↓
/agent/chat: 我刚才计算了什么？
  ↓
我记得上一轮工具 `multiply` 的执行结果是：36
```

## Current Router Streaming Architecture

Day15 added a Router Agent SSE streaming endpoint.

```text
/agent/router-stream
  ↓
stream_router_agent_events()
  ↓
invoke_router_agent()
  ↓
metadata -> route -> answer_chunk -> final -> done
```

The Router stream supports all three deterministic Router routes:

```text
calculator
rag
chat
```

Current event sequence:

```text
event: metadata      # thread_id and trace_id
event: route         # selected route
event: answer_chunk  # current implementation emits the full answer as one chunk
event: final         # final answer payload
event: done          # stream completion marker
```

Day15 intentionally keeps `answer_chunk` as one complete chunk because the deterministic Router does not generate token-level output. This design keeps the SSE contract stable and prepares the endpoint for future token-level LLM streaming.

## Current LLM Router Architecture

Day16 added an initial LLM Router Agent endpoint while keeping the deterministic Router Agent unchanged.

```text
/agent/llm-router-chat
  ↓
invoke_llm_router_agent()
  ↓
classify_route_with_llm()
  ├── mock   -> CI-safe deterministic router decision
  └── ollama -> local manual LLM router decision
  ↓
calculator -> invoke_agent() -> add / multiply tool
rag        -> invoke_agent() -> search_knowledge_base tool
chat       -> Router chat response
```

The LLM Router returns route decision metadata:

```text
route
route_reason
router_provider
router_model
```

Current router providers:

```text
mock
ollama
```

Important Day16 behavior:

```text
router_provider="mock"   -> always uses mock-router and is covered by CI
router_provider="ollama" -> uses local Ollama and is manually verified
```

This keeps CI independent from a local Ollama service while still allowing local experiments with real LLM-based routing.

## Current Smart Chat Architecture

Day17 added `/agent/smart-chat` as a future unified Agent entry point preview.

```text
/agent/smart-chat
  ↓
invoke_smart_agent()
  ↓
router_mode
  ├── deterministic -> invoke_router_agent()
  └── llm           -> invoke_llm_router_agent()
```

The endpoint supports two router modes:

```text
deterministic
llm
```

In deterministic mode, Smart Chat reuses the deterministic Router Agent:

```text
router_mode="deterministic"
  ↓
invoke_router_agent()
  ↓
router_provider = deterministic
router_model = rule-based-router
```

In LLM mode, Smart Chat reuses the Day16 LLM Router Agent:

```text
router_mode="llm"
  ↓
invoke_llm_router_agent()
  ↓
router_provider = mock | ollama
router_model = mock-router | qwen2.5:7b
```

Smart Chat returns a unified response shape:

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

This endpoint does not replace `/agent/chat` yet. It is a compatibility-safe preview of a future main Agent entry point.

## Current RAG Debug Architecture

Day18 added a RAG search-debug endpoint for retrieval explainability.

```text
/rag/search-debug
  ↓
explain_search_knowledge()
  ↓
search_knowledge()
  ↓
ranked results + debug metadata
```

The debug endpoint does not replace `/rag/search`. It adds retrieval-level observability.

Returned debug fields include:

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

This helps diagnose whether a RAG failure comes from retrieval not finding the right context or from answer generation not using the retrieved context.

Day18 intentionally still uses the existing keyword retriever instead of adding embeddings or a vector database. This keeps the feature deterministic and CI-safe.

## Current Smart Stream Architecture

Day19 added `/agent/smart-stream` as the SSE streaming version of Smart Chat.

```text
/agent/smart-stream
  ↓
stream_smart_agent_events()
  ↓
invoke_smart_agent()
  ↓
metadata -> route -> answer_chunk -> final -> done
```

The endpoint supports the same routing strategy as `/agent/smart-chat`:

```text
router_mode="deterministic" -> deterministic Router Agent
router_mode="llm"           -> LLM Router Agent
```

CI-safe modes:

```text
router_mode="deterministic"
router_mode="llm", router_provider="mock"
```

Local manual mode:

```text
router_mode="llm", router_provider="ollama"
```

Smart Stream returns route and router metadata through SSE payloads:

```text
route
route_reason
router_mode
router_provider
router_model
thread_id
trace_id
```

Current `answer_chunk` is still a single full-answer chunk because the deterministic and mock router paths are not token-level generators.

## Current Route Validation Architecture

Day20 added a route validation layer for Router and Smart Chat paths.

```text
route decision
  ↓
validate_route_decision()
  ↓
validated route + validation metadata
  ↓
selected route execution
```

Current validation file:

```text
src/app/agent/route_validation.py
```

Returned validation metadata:

```text
route_confidence
route_valid
fallback_used
validation_reason
```

Current confidence strategy:

```text
deterministic -> 1.0
mock          -> 1.0
ollama        -> 0.85
unknown       -> 0.5
invalid route -> 0.0 and fallback to chat
```

Day20 applies this metadata to:

```text
POST /agent/llm-router-chat
POST /agent/smart-chat
POST /agent/smart-stream
```

## Current RAG Chunk Pipeline Architecture

Day21 added a deterministic RAG chunk pipeline as preparation for future vector database based RAG.

```text
knowledge/*.md
  ↓
load_markdown_documents()
  ↓
split_text_into_chunks()
  ↓
load_knowledge_chunks()
  ↓
/rag/chunks-debug
```

Current chunking file:

```text
src/app/rag/chunking.py
```

Current chunk debug endpoint:

```text
POST /rag/chunks-debug
```

Returned chunk metadata:

```text
chunk_id
source
index
content
preview
content_length
trace_id
```

Supported request fields:

```text
source_filter
max_chars
```

Day21 intentionally does not add embeddings or a vector database yet. It prepares the document loading and chunk metadata layer that a vector store will later persist and retrieve.

## Current Deterministic Vector Search Architecture

Day22 added a CI-safe deterministic vector-search debug layer.

```text
query
  ↓
build_deterministic_embedding()
  ↓
load_knowledge_chunks()
  ↓
chunk deterministic embeddings
  ↓
cosine_similarity()
  ↓
ranked vector-search results
  ↓
/rag/vector-search-debug
```

Current vector search file:

```text
src/app/rag/vector_index.py
```

Current vector-search debug endpoint:

```text
POST /rag/vector-search-debug
```

The implementation uses deterministic hashed embeddings instead of a real embedding model.

This is intentional:

```text
No external embedding service.
No vector database dependency.
Stable pytest and GitHub Actions CI.
Same API shape can later be backed by real embeddings and a vector store.
```

Supported request fields:

```text
query
top_k
source_filter
max_chars
embedding_dim
```

Returned metadata:

```text
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

## Current Hybrid Retrieval Architecture

Day23 added a hybrid retrieval debug layer.

```text
query
  ↓
load_knowledge_chunks()
  ↓
keyword scoring
  +
deterministic vector scoring
  ↓
weighted hybrid_score
  ↓
ranked hybrid retrieval results
  ↓
/rag/hybrid-search-debug
```

Current hybrid retrieval file:

```text
src/app/rag/hybrid.py
```

Current hybrid retrieval debug endpoint:

```text
POST /rag/hybrid-search-debug
```

Hybrid retrieval reuses:

```text
Day21: load_knowledge_chunks()
Day22: build_deterministic_embedding()
Day22: cosine_similarity()
```

Supported request fields:

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

The purpose of Day23 is to make retrieval ranking more realistic than pure keyword retrieval or pure vector retrieval. It exposes the score composition so retrieval behavior can be debugged and tuned.

## Current Agentic RAG Architecture

Day24 added an Agentic RAG debug graph.

```text
query
  ↓
query_analyzer
  ↓
retrieval_needed?
  ├── false -> direct_answer
  └── true
       ↓
     query_rewriter
       ↓
     hybrid_retrieve
       ↓
     relevance_grade
       ↓
     answer_with_citations
       ↓
     /rag/agentic-debug
```

Current Agentic RAG file:

```text
src/app/rag/agentic_graph.py
```

Current Agentic RAG endpoint:

```text
POST /rag/agentic-debug
```

Agentic RAG reuses:

```text
Day23: hybrid_search_knowledge()
```

The graph returns a full debug trace:

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

The retrieval path steps are:

```text
query_analyzer -> query_rewriter -> hybrid_retrieve -> relevance_grade -> answer_with_citations
```

The direct path steps are:

```text
query_analyzer -> direct_answer
```

This turns RAG from a single retrieval call into a controllable workflow that can decide whether to retrieve, rewrite the query, retrieve with hybrid search, grade relevance, and answer with citations.


## Current RAG Evaluation Architecture

Day25 added a RAG evaluation debug layer.

```text
eval_cases/rag_agentic_eval.jsonl
  ↓
load_rag_eval_cases()
  ↓
evaluate_rag_cases()
  ↓
invoke_agentic_rag()
  ↓
metrics + per-case results
  ↓
/rag/eval-debug
```

Current evaluation files:

```text
eval_cases/rag_agentic_eval.jsonl
src/app/evaluation/rag_eval.py
tests/test_rag_eval.py
```

Current endpoint:

```text
POST /rag/eval-debug
```

Current metrics:

```text
total_cases
passed_cases
pass_rate
retrieval_decision_accuracy
expected_terms_hit_rate
citation_hit_rate
average_relevance_score
```

Current local result:

```text
total_cases = 3
passed_cases = 3
pass_rate = 1.0
retrieval_decision_accuracy = 1.0
expected_terms_hit_rate = 1.0
citation_hit_rate = 1.0
average_relevance_score = 0.278223
```

### RAG Eval Debug

```bash
curl -s -X POST http://localhost:8000/rag/eval-debug \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day25-rag-eval-debug-001" \
  -d '{"source_filter":"agent_basics","max_chars":300,"embedding_dim":64,"keyword_weight":0.6,"vector_weight":0.4}' \
  | python -m json.tool --no-ensure-ascii
```


## Current Observability Trace Store Architecture

Day26 added an observability trace store.

```text
/rag/agentic-debug
  ↓
record_trace_event(event_type="rag_agentic_debug")
  ↓
data/observability.sqlite
  ↓
GET /observability/traces/{trace_id}
```

```text
/rag/eval-debug
  ↓
record_trace_event(event_type="rag_eval_debug")
  ↓
data/observability.sqlite
  ↓
GET /observability/traces/{trace_id}
```

Current observability files:

```text
src/app/observability/trace_store.py
src/app/schemas/observability.py
src/app/routes/routes_observability.py
tests/test_observability.py
```

Current observability endpoints:

```text
GET /observability/traces/{trace_id}
GET /observability/traces?limit=10
```

Each trace event contains:

```text
event_id
trace_id
event_type
payload
created_at_ms
```

Agentic RAG trace payload includes query, rewritten query, retrieval decision, relevance score, citations, steps, and retrieval result count. RAG Eval trace payload includes eval file, source filter, metrics, and case count.

## Current Agentic RAG Streaming Architecture

Day27 added an Agentic RAG SSE streaming endpoint.

```text
/rag/agentic-stream
  ↓
stream_agentic_rag_events()
  ↓
invoke_agentic_rag()
  ↓
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

Current streaming file:

```text
src/app/rag/agentic_streaming.py
```

Current streaming endpoint:

```text
POST /rag/agentic-stream
```

The streaming path reuses:

```text
Day24: invoke_agentic_rag()
Day26: record_trace_event()
```

Retrieval path event sequence:

```text
metadata -> decision -> rewrite -> retrieval -> relevance -> citation -> answer_chunk -> final -> done
```

Direct path event sequence:

```text
metadata -> decision -> answer_chunk -> final -> done
```

The stream writes an observability event:

```text
event_type = rag_agentic_stream
```

Stored stream trace payload includes:

```text
query
rewritten_query
retrieval_needed
relevance_score
citations
steps
retrieval_results_count
```

This turns Agentic RAG from a single JSON debug response into a real-time event stream suitable for frontend step-by-step display.

## Current Agentic RAG Answer Verification Architecture

Day28 added a deterministic answer verification layer for Agentic RAG.

```text
/rag/answer-verify-debug
  ↓
verify_agentic_rag_answer()
  ↓
invoke_agentic_rag()
  ↓
verification checks
  ↓
record_trace_event(event_type="rag_answer_verify_debug")
  ↓
verification result + trace_id
```

Current answer verification file:

```text
src/app/rag/answer_verifier.py
```

Current answer verification endpoint:

```text
POST /rag/answer-verify-debug
```

The verification path reuses:

```text
Day24: invoke_agentic_rag()
Day26: record_trace_event()
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

Retrieval-path verification checks:

```text
citations exist
citations come from retrieval_results
answer includes a citation/source marker
answer contains grounding terms from retrieved chunks
relevance_score is positive
risk_flags is empty
```

Direct-path verification checks:

```text
citations is empty
retrieval_results is empty
relevance_score is 0.0
risk_flags is empty
```

The endpoint writes an observability event:

```text
event_type = rag_answer_verify_debug
```

This makes the Agentic RAG answer post-checkable and helps identify unsupported or weakly grounded answers.

## Current SQLite Vector Store Debug Architecture

Day29 added a SQLite-backed vector store debug layer as preparation for real vector database integration.

```text
/rag/vector-store-debug
  ↓
debug_vector_store_search()
  ↓
build_vector_store_index()
  ↓
load_knowledge_chunks()
  ↓
build_deterministic_embedding()
  ↓
SQLite: data/rag_vector_store.sqlite
  ↓
query_vector_store()
  ↓
cosine_similarity()
  ↓
ranked vector-store results
  ↓
record_trace_event(event_type="rag_vector_store_debug")
```

Current vector store file:

```text
src/app/rag/vector_store.py
```

Current vector store debug endpoint:

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

The vector store debug layer reuses:

```text
Day21: load_knowledge_chunks()
Day22: build_deterministic_embedding()
Day22: cosine_similarity()
Day26: record_trace_event()
```

Current SQLite database:

```text
data/rag_vector_store.sqlite
```

Current SQLite table:

```text
rag_chunk_vectors
```

Stored fields include:

```text
index_key
chunk_id
source
chunk_index
content
preview
content_length
embedding_dim
embedding_json
created_at_ms
```

Returned index statistics:

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

The endpoint writes an observability event:

```text
event_type = rag_vector_store_debug
```

Day29 still uses deterministic hashed embeddings to keep local tests and CI stable. The purpose is to introduce a vector-store-shaped persistence and query abstraction that can later be replaced by Chroma, FAISS, Milvus, or Qdrant.

## Request Tracing

Every request has a trace id.

Rules:

```text
If the client provides x-trace-id:
  reuse the client-provided trace id.

If the client does not provide x-trace-id:
  generate trace-xxxxxxxxxxxx.
```

The trace id is returned in the response header:

```text
x-trace-id: trace-xxxxxxxxxxxx
```

For Agent, LLM, and RAG endpoints, the trace id is also returned in the response body:

```json
{
  "trace_id": "chat-trace-001"
}
```

Current request log includes:

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

## Quick Start

Create and activate the conda environment:

```bash
conda create -n agentapi python=3.10 -y
conda activate agentapi
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the server:

```bash
python -m uvicorn src.app.main:app --reload --port 8000
```

Health check:

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{"status":"ok"}
```

Health check with manual trace id:

```bash
curl -i http://localhost:8000/health \
  -H "x-trace-id: manual-trace-001"
```

Expected response header:

```text
x-trace-id: manual-trace-001
```

## API Usage

### Agent Chat - Deterministic Route

```bash
curl -i -X POST http://localhost:8000/agent/chat \
  -H "Content-Type: application/json" \
  -H "x-trace-id: chat-trace-001" \
  -d '{"message":"请计算 3 加 5","thread_id":"demo-thread-001"}'
```

Expected response:

```json
{
  "answer": "工具 `add` 执行结果：8",
  "thread_id": "demo-thread-001",
  "trace_id": "chat-trace-001"
}
```

### Short-Term Memory

Use the same `thread_id` to continue the same conversation thread.

First request:

```bash
curl -X POST http://localhost:8000/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"请计算 4 乘 9","thread_id":"memory-demo-001"}'
```

Second request:

```bash
curl -X POST http://localhost:8000/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"我刚才计算了什么？","thread_id":"memory-demo-001"}'
```

Expected response:

```json
{
  "answer": "我记得上一轮工具 `multiply` 的执行结果是：36",
  "thread_id": "memory-demo-001"
}
```

### Agent Debug Endpoint - Deterministic Route

```bash
curl -i -X POST http://localhost:8000/agent/debug \
  -H "Content-Type: application/json" \
  -H "x-trace-id: debug-trace-001" \
  -d '{"message":"请计算 8 乘 9","thread_id":"debug-demo-001"}'
```

Expected node path:

```text
agent -> tools -> agent
```

Expected response body includes:

```json
{
  "thread_id": "debug-demo-001",
  "final_answer": "工具 `multiply` 执行结果：72",
  "messages_count": 4,
  "trace_id": "debug-trace-001"
}
```

### LLM Chat - Mock Provider

```bash
curl -i -X POST http://localhost:8000/llm/chat \
  -H "Content-Type: application/json" \
  -H "x-trace-id: llm-mock-trace-001" \
  -d '{"message":"你好，这是 Day9 mock LLM 测试","provider":"mock"}'
```

Expected response:

```json
{
  "answer": "Mock LLM response: 你好，这是 Day9 mock LLM 测试",
  "provider": "mock",
  "model": "mock-echo",
  "trace_id": "llm-mock-trace-001"
}
```

### LLM Chat - Ollama Provider

```bash
curl -s -X POST http://localhost:8000/llm/chat \
  -H "Content-Type: application/json" \
  -H "x-trace-id: llm-ollama-trace-001" \
  -d '{"message":"请用一句话解释什么是 Agent。","provider":"ollama"}'
```

Example response:

```json
{
  "answer": "Agent是一种软件程序，它可以自动执行任务或在特定条件下采取行动，通常用于自动化管理和监控系统等场景。",
  "provider": "ollama",
  "model": "qwen2.5:7b",
  "trace_id": "llm-ollama-trace-001"
}
```

### Real LLM Tool Calling Agent

Addition:

```bash
curl -s -X POST http://localhost:8000/agent/llm-chat \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day10-llm-add-001" \
  -d '{"message":"请计算 13 加 29，必须使用工具。","thread_id":"day10-llm-add-001"}'
```

Example response:

```json
{
  "answer": "计算结果是 42。",
  "thread_id": "day10-llm-add-001",
  "provider": "ollama",
  "model": "qwen2.5:7b",
  "trace_id": "day10-llm-add-001"
}
```

Multiplication:

```bash
curl -s -X POST http://localhost:8000/agent/llm-chat \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day10-llm-mul-001" \
  -d '{"message":"请计算 8 乘 9，必须使用工具。","thread_id":"day10-llm-mul-001"}'
```

Example response:

```json
{
  "answer": "计算结果是 72。",
  "thread_id": "day10-llm-mul-001",
  "provider": "ollama",
  "model": "qwen2.5:7b",
  "trace_id": "day10-llm-mul-001"
}
```

### Real LLM Tool Calling Debug

Use `/agent/llm-debug` to verify whether the LLM really generated tool calls.

```bash
curl -s -X POST http://localhost:8000/agent/llm-debug \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day10-debug-add-001" \
  -d '{"message":"请计算 13 加 29，必须使用 add 工具。","thread_id":"day10-debug-add-001"}' \
  | python -m json.tool --no-ensure-ascii
```

Expected node path:

```text
agent -> tools -> agent
```

Expected tool call:

```json
{
  "name": "add",
  "args": {
    "a": 13,
    "b": 29
  }
}
```

Multiplication debug:

```bash
curl -s -X POST http://localhost:8000/agent/llm-debug \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day10-debug-mul-001" \
  -d '{"message":"请计算 8 乘 9，必须使用 multiply 工具。","thread_id":"day10-debug-mul-001"}' \
  | python -m json.tool --no-ensure-ascii
```

Expected tool call:

```json
{
  "name": "multiply",
  "args": {
    "a": 8,
    "b": 9
  }
}
```

### Agent Stream - Deterministic Route

`/agent/stream` streams deterministic Agent output as Server-Sent Events.

```bash
curl -N -X POST http://localhost:8000/agent/stream \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day11-stream-add-001" \
  -d '{"message":"请计算 3 加 5","thread_id":"day11-stream-add-001"}'
```

Expected event sequence:

```text
event: metadata
event: answer_chunk
event: final
event: done
```

Example final event:

```text
event: final
data: {"answer": "工具 `add` 执行结果：8", "thread_id": "day11-stream-add-001", "trace_id": "day11-stream-add-001"}
```

### Agent Stream - Real LLM Tool Calling Route

`/agent/llm-stream` streams real LLM Tool Calling Agent graph updates as SSE events.

```bash
curl -N -X POST http://localhost:8000/agent/llm-stream \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day11-llm-stream-add-001" \
  -d '{"message":"请计算 13 加 29，必须使用 add 工具。","thread_id":"day11-llm-stream-add-001"}'
```

Expected event sequence:

```text
event: metadata
event: step      # node=agent, LLM-generated tool_calls
event: step      # node=tools, ToolMessage result
event: step      # node=agent, final AIMessage
event: final
event: done
```

Expected tool-call path:

```text
agent -> tools -> agent
```

Example final answer:

```text
计算结果是 42。
```

### RAG Search

`/rag/search` uses the lightweight local keyword retriever.

```bash
curl -s -X POST http://localhost:8000/rag/search \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day12-rag-search-001" \
  -d '{"query":"RAG 是什么？","k":2}' \
  | python -m json.tool --no-ensure-ascii
```

Expected response includes:

```json
{
  "query": "RAG 是什么？",
  "results": [
    {
      "source": "knowledge/agent_basics.md",
      "content": "...RAG 是 Retrieval-Augmented Generation...",
      "score": 1
    }
  ],
  "trace_id": "day12-rag-search-001"
}
```

### Agent Chat with RAG Tool

`/agent/chat` can trigger the deterministic `search_knowledge_base` tool.

```bash
curl -s -X POST http://localhost:8000/agent/chat \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day12-agent-rag-001" \
  -d '{"message":"请搜索知识库：RAG 是什么？","thread_id":"day12-agent-rag-001"}' \
  | python -m json.tool --no-ensure-ascii
```

Expected answer starts with:

```text
根据知识库检索结果：
```

### Agent Debug with RAG Tool

`/agent/debug` can show the deterministic RAG tool-call path.

```bash
curl -s -X POST http://localhost:8000/agent/debug \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day12-debug-rag-001" \
  -d '{"message":"请搜索知识库：LangGraph 是什么？","thread_id":"day12-debug-rag-001"}' \
  | python -m json.tool --no-ensure-ascii
```

Expected node path:

```text
agent -> tools -> agent
```

Expected tool call:

```json
{
  "name": "search_knowledge_base",
  "args": {
    "query": "请搜索知识库：LangGraph 是什么？",
    "k": 3
  }
}
```

### Router Agent Chat

`/agent/router-chat` selects one of three routes: `calculator`, `rag`, or `chat`.

Calculator route:

```bash
curl -s -X POST http://localhost:8000/agent/router-chat \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day13-router-calc-001" \
  -d '{"message":"请计算 3 加 5","thread_id":"day13-router-calc-001"}' \
  | python -m json.tool --no-ensure-ascii
```

Expected response:

```json
{
  "answer": "工具 `add` 执行结果：8",
  "route": "calculator",
  "thread_id": "day13-router-calc-001",
  "trace_id": "day13-router-calc-001"
}
```

RAG route:

```bash
curl -s -X POST http://localhost:8000/agent/router-chat \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day13-router-rag-001" \
  -d '{"message":"请搜索知识库：RAG 是什么？","thread_id":"day13-router-rag-001"}' \
  | python -m json.tool --no-ensure-ascii
```

Expected response includes:

```json
{
  "route": "rag",
  "answer": "根据知识库检索结果：..."
}
```

Chat route:

```bash
curl -s -X POST http://localhost:8000/agent/router-chat \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day13-router-chat-001" \
  -d '{"message":"你好，介绍一下你自己","thread_id":"day13-router-chat-001"}' \
  | python -m json.tool --no-ensure-ascii
```

Expected response:

```json
{
  "answer": "Router chat response: 你好，介绍一下你自己",
  "route": "chat",
  "thread_id": "day13-router-chat-001",
  "trace_id": "day13-router-chat-001"
}
```

### Router Agent Debug

`/agent/router-debug` shows the selected route and node-level router execution path.

```bash
curl -s -X POST http://localhost:8000/agent/router-debug \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day13-router-debug-rag-001" \
  -d '{"message":"请搜索知识库：LangGraph 是什么？","thread_id":"day13-router-debug-rag-001"}' \
  | python -m json.tool --no-ensure-ascii
```

Expected node path:

```text
router -> rag
```

Expected response includes:

```json
{
  "route": "rag",
  "final_answer": "根据知识库检索结果：..."
}
```

### Router Delegation Memory Check

Day14 verifies that Router delegated routes use the existing Agent graph and memory.

First call the Router Agent calculator route:

```bash
curl -s -X POST http://localhost:8000/agent/router-chat \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day14-router-memory-001" \
  -d '{"message":"请计算 4 乘 9","thread_id":"day14-router-memory-001"}' \
  | python -m json.tool --no-ensure-ascii
```

Expected response:

```json
{
  "answer": "工具 `multiply` 执行结果：36",
  "route": "calculator",
  "thread_id": "day14-router-memory-001",
  "trace_id": "day14-router-memory-001"
}
```

Then ask the existing deterministic Agent route with the same `thread_id`:

```bash
curl -s -X POST http://localhost:8000/agent/chat \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day14-router-memory-002" \
  -d '{"message":"我刚才计算了什么？","thread_id":"day14-router-memory-001"}' \
  | python -m json.tool --no-ensure-ascii
```

Expected response:

```json
{
  "answer": "我记得上一轮工具 `multiply` 的执行结果是：36",
  "thread_id": "day14-router-memory-001",
  "trace_id": "day14-router-memory-002"
}
```

### Router Agent Stream

`/agent/router-stream` streams Router Agent output as Server-Sent Events.

Calculator route:

```bash
curl -N -X POST http://localhost:8000/agent/router-stream \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day15-router-stream-calc-001" \
  -d '{"message":"请计算 3 加 5","thread_id":"day15-router-stream-calc-001"}'
```

Expected event sequence:

```text
event: metadata
event: route
event: answer_chunk
event: final
event: done
```

Expected route and answer:

```text
"route": "calculator"
"answer": "工具 `add` 执行结果：8"
```

RAG route:

```bash
curl -N -X POST http://localhost:8000/agent/router-stream \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day15-router-stream-rag-001" \
  -d '{"message":"请搜索知识库：RAG 是什么？","thread_id":"day15-router-stream-rag-001"}'
```

Expected route and answer content:

```text
"route": "rag"
"根据知识库检索结果"
"knowledge/agent_basics.md"
```

Chat route:

```bash
curl -N -X POST http://localhost:8000/agent/router-stream \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day15-router-stream-chat-001" \
  -d '{"message":"你好，介绍一下你自己","thread_id":"day15-router-stream-chat-001"}'
```

Expected route and answer:

```text
"route": "chat"
"Router chat response: 你好，介绍一下你自己"
```

### LLM Router Agent Chat

`/agent/llm-router-chat` selects a route through a router provider and then executes the selected route.

The CI-safe provider is `mock`; the local manual provider is `ollama`.

Mock calculator route:

```bash
curl -s -X POST http://localhost:8000/agent/llm-router-chat \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day16-llm-router-calc-001" \
  -d '{"message":"请计算 3 加 5","thread_id":"day16-llm-router-calc-001","router_provider":"mock"}' \
  | python -m json.tool --no-ensure-ascii
```

Expected response:

```json
{
  "answer": "工具 `add` 执行结果：8",
  "route": "calculator",
  "route_reason": "Mock LLM router selected calculator because the message contains arithmetic intent.",
  "router_provider": "mock",
  "router_model": "mock-router",
  "thread_id": "day16-llm-router-calc-001",
  "trace_id": "day16-llm-router-calc-001"
}
```

Mock RAG route:

```bash
curl -s -X POST http://localhost:8000/agent/llm-router-chat \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day16-llm-router-rag-001" \
  -d '{"message":"请搜索知识库：RAG 是什么？","thread_id":"day16-llm-router-rag-001","router_provider":"mock"}' \
  | python -m json.tool --no-ensure-ascii
```

Expected response includes:

```text
"route": "rag"
"router_provider": "mock"
"router_model": "mock-router"
"根据知识库检索结果"
```

Mock chat route:

```bash
curl -s -X POST http://localhost:8000/agent/llm-router-chat \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day16-llm-router-chat-001" \
  -d '{"message":"你好，介绍一下你自己","thread_id":"day16-llm-router-chat-001","router_provider":"mock"}' \
  | python -m json.tool --no-ensure-ascii
```

Expected response includes:

```text
"route": "chat"
"answer": "Router chat response: 你好，介绍一下你自己"
```

Ollama router can be manually verified locally:

```bash
curl -s -X POST http://localhost:8000/agent/llm-router-chat \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day16-llm-router-ollama-001" \
  -d '{"message":"请计算 9 乘 9","thread_id":"day16-llm-router-ollama-001","router_provider":"ollama"}' \
  | python -m json.tool --no-ensure-ascii
```

Expected local response includes:

```text
"router_provider": "ollama"
"router_model": "qwen2.5:7b"
"route": "calculator"
"answer": "工具 `multiply` 执行结果：81"
```

### Smart Chat

`/agent/smart-chat` is the future unified Agent entry point preview.

It can use the deterministic Router or the LLM Router through `router_mode`.

Deterministic calculator route:

```bash
curl -s -X POST http://localhost:8000/agent/smart-chat \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day17-smart-deterministic-calc-001" \
  -d '{"message":"请计算 3 加 5","thread_id":"day17-smart-deterministic-calc-001","router_mode":"deterministic"}' \
  | python -m json.tool --no-ensure-ascii
```

Expected response:

```json
{
  "answer": "工具 `add` 执行结果：8",
  "route": "calculator",
  "route_reason": "Deterministic router selected calculator by rule-based classification.",
  "router_mode": "deterministic",
  "router_provider": "deterministic",
  "router_model": "rule-based-router",
  "thread_id": "day17-smart-deterministic-calc-001",
  "trace_id": "day17-smart-deterministic-calc-001"
}
```

LLM mock RAG route:

```bash
curl -s -X POST http://localhost:8000/agent/smart-chat \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day17-smart-llm-rag-001" \
  -d '{"message":"请搜索知识库：RAG 是什么？","thread_id":"day17-smart-llm-rag-001","router_mode":"llm","router_provider":"mock"}' \
  | python -m json.tool --no-ensure-ascii
```

Expected response includes:

```text
"route": "rag"
"router_mode": "llm"
"router_provider": "mock"
"router_model": "mock-router"
"根据知识库检索结果"
```

LLM mock chat route:

```bash
curl -s -X POST http://localhost:8000/agent/smart-chat \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day17-smart-llm-chat-001" \
  -d '{"message":"你好，介绍一下你自己","thread_id":"day17-smart-llm-chat-001","router_mode":"llm","router_provider":"mock"}' \
  | python -m json.tool --no-ensure-ascii
```

Expected response includes:

```text
"route": "chat"
"answer": "Router chat response: 你好，介绍一下你自己"
```

Ollama Smart Chat can be manually verified locally:

```bash
curl -s -X POST http://localhost:8000/agent/smart-chat \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day17-smart-ollama-calc-001" \
  -d '{"message":"请计算 9 乘 9","thread_id":"day17-smart-ollama-calc-001","router_mode":"llm","router_provider":"ollama"}' \
  | python -m json.tool --no-ensure-ascii
```

Expected local response includes:

```text
"router_mode": "llm"
"router_provider": "ollama"
"router_model": "qwen2.5:7b"
"route": "calculator"
"answer": "工具 `multiply` 执行结果：81"
```

### RAG Search Debug

`/rag/search-debug` exposes retrieval explainability metadata for the lightweight local RAG retriever.

```bash
curl -s -X POST http://localhost:8000/rag/search-debug \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day18-rag-search-debug-001" \
  -d '{"query":"RAG 是什么？","k":2}' \
  | python -m json.tool --no-ensure-ascii
```

Expected response structure:

```json
{
  "query": "RAG 是什么？",
  "normalized_query": "rag 是什么？",
  "k": 2,
  "results": [
    {
      "rank": 1,
      "source": "knowledge/agent_basics.md",
      "score": 1,
      "content": "...",
      "preview": "...",
      "matched_terms": ["rag"],
      "content_length": 234
    }
  ],
  "trace_id": "day18-rag-search-debug-001"
}
```

LangGraph debug example:

```bash
curl -s -X POST http://localhost:8000/rag/search-debug \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day18-rag-search-debug-langgraph-001" \
  -d '{"query":"LangGraph 是什么？","k":2}' \
  | python -m json.tool --no-ensure-ascii
```

Expected response includes:

```text
"source": "knowledge/agent_basics.md"
"matched_terms": ["langgraph"]
"trace_id": "day18-rag-search-debug-langgraph-001"
```

### Smart Stream

`/agent/smart-stream` is the SSE streaming version of the Smart Chat unified entry point preview.

Deterministic calculator route:

```bash
curl -N -X POST http://localhost:8000/agent/smart-stream \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day19-smart-stream-deterministic-calc-001" \
  -d '{"message":"请计算 3 加 5","thread_id":"day19-smart-stream-deterministic-calc-001","router_mode":"deterministic"}'
```

Expected event sequence:

```text
event: metadata
event: route
event: answer_chunk
event: final
event: done
```

Expected content:

```text
"route": "calculator"
"router_mode": "deterministic"
"router_provider": "deterministic"
"router_model": "rule-based-router"
"answer": "工具 `add` 执行结果：8"
```

LLM mock RAG route:

```bash
curl -N -X POST http://localhost:8000/agent/smart-stream \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day19-smart-stream-llm-rag-001" \
  -d '{"message":"请搜索知识库：RAG 是什么？","thread_id":"day19-smart-stream-llm-rag-001","router_mode":"llm","router_provider":"mock"}'
```

Expected content:

```text
"route": "rag"
"router_mode": "llm"
"router_provider": "mock"
"router_model": "mock-router"
"根据知识库检索结果"
"knowledge/agent_basics.md"
```

LLM mock chat route:

```bash
curl -N -X POST http://localhost:8000/agent/smart-stream \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day19-smart-stream-llm-chat-001" \
  -d '{"message":"你好，介绍一下你自己","thread_id":"day19-smart-stream-llm-chat-001","router_mode":"llm","router_provider":"mock"}'
```

Expected content:

```text
"route": "chat"
"router_mode": "llm"
"router_provider": "mock"
"Router chat response: 你好，介绍一下你自己"
```

Ollama Smart Stream can be manually verified locally with `router_provider="ollama"`.

### Route Validation Metadata

Day20 adds route validation metadata to Router and Smart Chat responses.

LLM Router validation example:

```bash
curl -s -X POST http://localhost:8000/agent/llm-router-chat \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day20-llm-router-validation-001" \
  -d '{"message":"请计算 3 加 5","thread_id":"day20-llm-router-validation-001","router_provider":"mock"}' \
  | python -m json.tool --no-ensure-ascii
```

Expected response includes:

```json
{
  "route_confidence": 1.0,
  "route_valid": true,
  "fallback_used": false,
  "validation_reason": "Route is valid."
}
```

Smart Stream validation payload should include the same metadata in `route` and `final` SSE events.

### RAG Chunks Debug

`/rag/chunks-debug` exposes the current Markdown document loading and chunk splitting result.

```bash
curl -s -X POST http://localhost:8000/rag/chunks-debug \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day21-rag-chunks-debug-001" \
  -d '{"source_filter":"agent_basics","max_chars":300}' \
  | python -m json.tool --no-ensure-ascii
```

Expected response structure:

```json
{
  "source_filter": "agent_basics",
  "max_chars": 300,
  "total_chunks": 2,
  "chunks": [
    {
      "chunk_id": "knowledge/agent_basics.md::chunk-1",
      "source": "knowledge/agent_basics.md",
      "index": 1,
      "content": "...",
      "preview": "...",
      "content_length": 291
    }
  ],
  "trace_id": "day21-rag-chunks-debug-001"
}
```

### RAG Vector Search Debug

`/rag/vector-search-debug`, `/rag/hybrid-search-debug` previews vector-search behavior with deterministic hashed embeddings.

```bash
curl -s -X POST http://localhost:8000/rag/vector-search-debug \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day22-rag-vector-search-debug-001" \
  -d '{"query":"RAG 是什么？","top_k":2,"source_filter":"agent_basics","max_chars":300,"embedding_dim":64}' \
  | python -m json.tool --no-ensure-ascii
```

Expected response includes:

```text
"query": "RAG 是什么？"
"top_k": 2
"source_filter": "agent_basics"
"embedding_dim": 64
"total_chunks": 2
"chunk_id": "knowledge/agent_basics.md::chunk-2"
"score": 0.376889
"matched_terms": ["rag", "是"]
"trace_id": "day22-rag-vector-search-debug-001"
```

LangGraph example:

```bash
curl -s -X POST http://localhost:8000/rag/vector-search-debug \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day22-rag-vector-search-debug-langgraph-001" \
  -d '{"query":"LangGraph 是什么？","top_k":2,"source_filter":"agent_basics","max_chars":300,"embedding_dim":64}' \
  | python -m json.tool --no-ensure-ascii
```

Expected response includes:

```text
"source": "knowledge/agent_basics.md"
"matched_terms": ["langgraph", "是"]
"trace_id": "day22-rag-vector-search-debug-langgraph-001"
```

### RAG Hybrid Search Debug

`/rag/hybrid-search-debug` combines keyword and deterministic vector signals.

```bash
curl -s -X POST http://localhost:8000/rag/hybrid-search-debug \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day23-rag-hybrid-search-debug-001" \
  -d '{"query":"RAG 是什么？","top_k":2,"source_filter":"agent_basics","max_chars":300,"embedding_dim":64,"keyword_weight":0.6,"vector_weight":0.4}' \
  | python -m json.tool --no-ensure-ascii
```

Expected response includes:

```text
"query": "RAG 是什么？"
"top_k": 2
"source_filter": "agent_basics"
"keyword_weight": 0.6
"vector_weight": 0.4
"total_chunks": 2
"chunk_id": "knowledge/agent_basics.md::chunk-2"
"hybrid_score": 0.450756
"keyword_score": 0.5
"vector_score": 0.376889
"matched_terms": ["rag"]
"trace_id": "day23-rag-hybrid-search-debug-001"
```

### RAG Agentic Debug

`/rag/agentic-debug` exposes the full Agentic RAG decision chain.

Retrieval path:

```bash
curl -s -X POST http://localhost:8000/rag/agentic-debug \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day24-rag-agentic-debug-001" \
  -d '{"query":"请搜索知识库：LangGraph 是什么？","top_k":2,"source_filter":"agent_basics","max_chars":300,"embedding_dim":64,"keyword_weight":0.6,"vector_weight":0.4}' \
  | python -m json.tool --no-ensure-ascii
```

Expected response includes:

```text
"rewritten_query": "LangGraph 是什么？"
"retrieval_needed": true
"relevance_score": 0.383914
"citations": ["knowledge/agent_basics.md::chunk-1", "knowledge/agent_basics.md::chunk-2"]
"steps": ["query_analyzer", "query_rewriter", "hybrid_retrieve", "relevance_grade", "answer_with_citations"]
"trace_id": "day24-rag-agentic-debug-001"
```

Direct path:

```bash
curl -s -X POST http://localhost:8000/rag/agentic-debug \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day24-rag-agentic-debug-direct-001" \
  -d '{"query":"你好，介绍一下你自己","top_k":2,"source_filter":"agent_basics"}' \
  | python -m json.tool --no-ensure-ascii
```

Expected response includes:

```text
"retrieval_needed": false
"citations": []
"retrieval_results": []
"steps": ["query_analyzer", "direct_answer"]
"trace_id": "day24-rag-agentic-debug-direct-001"
```


### Observability Trace Lookup

```bash
curl -s http://localhost:8000/observability/traces/day26-observability-agentic-001 \
  | python -m json.tool --no-ensure-ascii
```

Expected Agentic RAG trace fields:

```text
event_type = rag_agentic_debug
payload.rewritten_query = LangGraph 是什么？
payload.retrieval_needed = true
payload.relevance_score = 0.383914
payload.retrieval_results_count = 2
```

```bash
curl -s http://localhost:8000/observability/traces/day26-observability-eval-001 \
  | python -m json.tool --no-ensure-ascii
```

Expected RAG Eval trace fields:

```text
event_type = rag_eval_debug
payload.case_count = 3
payload.metrics.total_cases = 3
payload.metrics.pass_rate = 1.0
```

```bash
curl -s "http://localhost:8000/observability/traces?limit=10" \
  | python -m json.tool --no-ensure-ascii
```

### RAG Agentic Stream

`/rag/agentic-stream` exposes the Agentic RAG decision chain as SSE events.

Retrieval path:

```bash
curl -N -X POST http://localhost:8000/rag/agentic-stream \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day27-rag-agentic-stream-001" \
  -d '{"query":"请搜索知识库：LangGraph 是什么？","top_k":2,"source_filter":"agent_basics","max_chars":300,"embedding_dim":64,"keyword_weight":0.6,"vector_weight":0.4}'
```

Expected event sequence:

```text
event: metadata
event: decision
event: rewrite
event: retrieval
event: relevance
event: citation
event: answer_chunk
event: final
event: done
```

Expected retrieval path fields:

```text
retrieval_needed = true
rewritten_query = LangGraph 是什么？
relevance_score = 0.383914
citations include knowledge/agent_basics.md::chunk-1
steps include query_analyzer -> query_rewriter -> hybrid_retrieve -> relevance_grade -> answer_with_citations
```

Direct path:

```bash
curl -N -X POST http://localhost:8000/rag/agentic-stream \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day27-rag-agentic-stream-direct-001" \
  -d '{"query":"你好，介绍一下你自己","top_k":2,"source_filter":"agent_basics"}'
```

Expected direct path event sequence:

```text
event: metadata
event: decision
event: answer_chunk
event: final
event: done
```

Expected direct path fields:

```text
retrieval_needed = false
steps = ["query_analyzer", "direct_answer"]
citations = []
retrieval_results = []
```

Stream trace lookup:

```bash
curl -s http://localhost:8000/observability/traces/day27-rag-agentic-stream-001 \
  | python -m json.tool --no-ensure-ascii
```

Expected trace fields:

```text
event_type = rag_agentic_stream
payload.retrieval_needed = true
payload.rewritten_query = LangGraph 是什么？
payload.retrieval_results_count = 2
```

### RAG Answer Verification Debug

`/rag/answer-verify-debug` verifies whether an Agentic RAG answer is supported by retrieval results and citations.

Retrieval path:

```bash
curl -s -X POST http://localhost:8000/rag/answer-verify-debug \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day28-answer-verify-langgraph-001" \
  -d '{"query":"请搜索知识库：LangGraph 是什么？","top_k":2,"source_filter":"agent_basics","max_chars":300,"embedding_dim":64,"keyword_weight":0.6,"vector_weight":0.4}' \
  | python -m json.tool --no-ensure-ascii
```

Expected retrieval-path verification fields:

```text
retrieval_needed = true
relevance_score = 0.383914
verification_mode = retrieval
answer_supported = true
verification_pass = true
confidence = high
answer_has_citation = true
citation_coverage_pass = true
matched_grounding_terms = ["langgraph"]
risk_flags = []
trace_id = day28-answer-verify-langgraph-001
```

Trace lookup:

```bash
curl -s http://localhost:8000/observability/traces/day28-answer-verify-langgraph-001 \
  | python -m json.tool --no-ensure-ascii
```

Expected trace fields:

```text
event_type = rag_answer_verify_debug
payload.verification.verification_pass = true
payload.verification.confidence = high
payload.verification.matched_grounding_terms = ["langgraph"]
```

Direct path:

```bash
curl -s -X POST http://localhost:8000/rag/answer-verify-debug \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day28-answer-verify-direct-001" \
  -d '{"query":"你好，介绍一下你自己","top_k":2,"source_filter":"agent_basics"}' \
  | python -m json.tool --no-ensure-ascii
```

Expected direct-path verification fields:

```text
retrieval_needed = false
citations = []
retrieval_results = []
verification_mode = direct
answer_supported = true
verification_pass = true
confidence = high
risk_flags = []
trace_id = day28-answer-verify-direct-001
```

### RAG Vector Store Debug

`/rag/vector-store-debug` builds a SQLite-backed vector-store-like index and queries persisted chunk embeddings.

LangGraph query:

```bash
curl -s -X POST http://localhost:8000/rag/vector-store-debug \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day29-vector-store-langgraph-001" \
  -d '{"query":"LangGraph 是什么？","top_k":2,"source_filter":"agent_basics","max_chars":300,"embedding_dim":64,"rebuild_index":true}' \
  | python -m json.tool --no-ensure-ascii
```

Expected response fields:

```text
query = LangGraph 是什么？
top_k = 2
source_filter = agent_basics
embedding_dim = 64
rebuild_index = true
total_indexed_chunks = 2
index_stats.loaded_chunks = 2
index_stats.inserted_count = 2
index_stats.stored_count = 2
index_stats.db_path = data/rag_vector_store.sqlite
results_count = 2
trace_id = day29-vector-store-langgraph-001
```

Trace lookup:

```bash
curl -s http://localhost:8000/observability/traces/day29-vector-store-langgraph-001 \
  | python -m json.tool --no-ensure-ascii
```

Expected trace fields:

```text
event_type = rag_vector_store_debug
payload.total_indexed_chunks = 2
payload.results_count = 2
payload.index_stats.inserted_count = 2
payload.index_stats.stored_count = 2
```

RAG query:

```bash
curl -s -X POST http://localhost:8000/rag/vector-store-debug \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day29-vector-store-rag-001" \
  -d '{"query":"RAG 是什么？","top_k":2,"source_filter":"agent_basics","max_chars":300,"embedding_dim":64,"rebuild_index":true}' \
  | python -m json.tool --no-ensure-ascii
```

Expected response fields:

```text
total_indexed_chunks = 2
index_stats.loaded_chunks = 2
index_stats.inserted_count = 2
index_stats.stored_count = 2
results_count = 2
trace_id = day29-vector-store-rag-001
```

## Tests

Run tests:

```bash
pytest -q
```

Current result:

```text
72 passed, 1 warning
```

Current test coverage includes:

* `/health`
* `/health` generated `x-trace-id`
* `/health` client-provided `x-trace-id`
* `/agent/chat` normal response
* `/agent/chat` trace id in header and body
* `add` tool
* `multiply` tool
* `search_knowledge_base` tool through `/agent/chat`
* same-thread short-term memory
* different-thread memory isolation
* `/agent/debug` normal path
* `/agent/debug` tool-call path
* `/agent/debug` RAG tool-call path
* `/agent/debug` trace id in header and body
* `/llm/chat` mock provider
* `/llm/chat` mock provider with trace id
* `/agent/stream` deterministic add tool SSE response
* `/agent/stream` deterministic multiply tool SSE response
* `/rag/search` lightweight local RAG endpoint
* `/rag/search-debug` explainable RAG search endpoint
* `/agent/router-chat` calculator route
* `/agent/router-chat` RAG route
* `/agent/router-chat` chat route
* `/agent/router-debug` RAG route path
* Router calculator route delegates to existing Agent memory
* Router RAG route delegates to existing Agent memory
* `/agent/router-stream` calculator route SSE response
* `/agent/router-stream` RAG route SSE response
* `/agent/router-stream` chat route SSE response
* `/agent/llm-router-chat` mock calculator route
* `/agent/llm-router-chat` mock RAG route
* `/agent/llm-router-chat` mock chat route
* `/agent/smart-chat` deterministic calculator route
* `/agent/smart-chat` LLM mock RAG route
* `/agent/smart-chat` LLM mock chat route
* `/agent/smart-stream` deterministic calculator route SSE response
* `/agent/smart-stream` LLM mock RAG route SSE response
* `/agent/smart-stream` LLM mock chat route SSE response
* `validate_route_decision()` valid route behavior
* `validate_route_decision()` invalid route fallback behavior
* `/agent/llm-router-chat` route validation metadata
* `/agent/smart-chat` route validation metadata
* `/agent/smart-stream` route validation metadata
* `/rag/search-debug` explainable RAG result fields
* `/rag/search-debug` `k` limit behavior
* `/rag/search-debug` matched terms for LangGraph query
* `split_text_into_chunks()` blank-line based chunk splitting
* `debug_knowledge_chunks()` loads `knowledge/agent_basics.md`
* `/rag/chunks-debug` returns chunk metadata and trace id
* `build_deterministic_embedding()` stable embedding behavior
* `vector_search_knowledge()` ranked chunk results
* `/rag/vector-search-debug`, `/rag/hybrid-search-debug` vector-search metadata and trace id
* `hybrid_search_knowledge()` ranked hybrid retrieval results
* `hybrid_search_knowledge()` zero-weight normalization
* `/rag/hybrid-search-debug` hybrid retrieval metadata and trace id
* `invoke_agentic_rag()` retrieval path with citations
* `invoke_agentic_rag()` direct path without retrieval
* `/rag/agentic-debug` Agentic RAG metadata and trace id

Current test organization:

```text
tests/
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
├── test_router_agent.py
├── test_router_delegation.py
├── test_router_stream.py
├── test_llm_router.py
├── test_smart_chat.py
├── test_smart_stream.py
├── test_route_validation.py
└── test_rag_chunks.py
```

Ollama provider, real LLM tool calling, `/agent/llm-stream`, `/agent/llm-router-chat` with `router_provider="ollama"`, `/agent/smart-chat` with `router_provider="ollama"`, and `/agent/smart-stream` with `router_provider="ollama"` are manually tested locally and are not covered by CI, because CI should not depend on a local Ollama service. The deterministic `/agent/stream`, `/rag/search`, `/rag/search-debug`, `/rag/chunks-debug`, `/rag/vector-search-debug`, `/rag/hybrid-search-debug`, `/rag/agentic-debug`, deterministic RAG tool path, Router Agent path, Router delegation memory path, Router stream path, `/agent/llm-router-chat` mock path, `/agent/smart-chat` deterministic/mock paths, `/agent/smart-stream` deterministic/mock paths, route validation paths, chunk pipeline paths, deterministic vector-search paths, hybrid retrieval paths, and Agentic RAG debug paths are covered by local pytest. CI status should be confirmed from GitHub Actions.

## CI

GitHub Actions CI is enabled.

Workflow:

```text
checkout
  ↓
setup-python 3.10
  ↓
pip install -r requirements.txt
  ↓
pytest -q
```

Current CI status:

```text
Day28: green
Day29: not shown in the provided log; confirm from GitHub Actions
```

## Runtime Data

SQLite checkpoint files are generated under:

```text
data/
```

These files are runtime data and are ignored by Git.

Ignored runtime patterns include:

```text
data/
*.sqlite
*.sqlite-shm
*.sqlite-wal
*.sqlite-journal
```

Knowledge base files are stored separately under:

```text
knowledge/
```

These files are source-controlled project files, not runtime data.

## Development Notes

`requirements.txt` is manually maintained as a minimal dependency file. Do not blindly overwrite it with `pip freeze > requirements.txt` from a conda environment, because conda build artifact paths may break GitHub Actions CI.

Current local pytest warning:

```text
StarletteDeprecationWarning: Using httpx with starlette.testclient is deprecated; install httpx2 instead.
```

This warning does not block local tests or CI and can be handled later.

When formatting JSON output that contains Chinese text, prefer:

```bash
python -m json.tool --no-ensure-ascii
```

or:

```bash
python -c "import sys,json; print(json.dumps(json.load(sys.stdin), ensure_ascii=False, indent=4))"
```

Without this, `python -m json.tool` may display Chinese as Unicode escape sequences such as `\u8ba1\u7b97\u7ed3\u679c\u662f 42\u3002`.

For knowledge base files, use UTF-8 encoding. If a Markdown file was created or edited through Windows tools and pytest raises a `UnicodeDecodeError`, convert it:

```bash
iconv -f gbk -t utf-8 knowledge/agent_basics.md -o /tmp/agent_basics.md
mv /tmp/agent_basics.md knowledge/agent_basics.md
```

## Roadmap

Next milestones:

* Day30: Add real embedding provider and real vector database integration
* Day31-Day35: Chroma or another vector database backed RAG engineering integration
* Later: Add vector database based RAG
* Later: Add GraphRAG and Neo4j integration
* Later: Add Multi-Agent Supervisor workflow
