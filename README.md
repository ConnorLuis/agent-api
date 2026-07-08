# agent-api

`agent-api` is a FastAPI + LangGraph backend project for building an Agent service step by step.

This project is the second project in the AI internship preparation roadmap, following the completed `chat-api-v2` project. The current version implements a deterministic Tool Calling Agent, SQLite-based short-term memory, graph debug output, request tracing, LLM provider abstraction, a real Ollama-backed LLM Tool Calling Agent path, SSE streaming endpoints, a lightweight local RAG search tool, a RAG search-debug endpoint with explainability metadata, a deterministic Router Agent that delegates calculator and RAG routes to the existing Agent graph, a Router Agent SSE streaming endpoint, an initial LLM Router Agent endpoint with mock and Ollama router providers, a Smart Chat endpoint as a future unified Agent entry point preview, a Smart Chat SSE streaming endpoint, route validation metadata for Router and Smart Chat paths, and a RAG chunk pipeline debug endpoint for vector DB preparation, a deterministic RAG vector-search debug endpoint, a hybrid retrieval debug endpoint that combines keyword and vector signals, an Agentic RAG debug graph with query analysis, query rewriting, hybrid retrieval, relevance grading, citation-aware answers, an Agentic RAG SSE streaming endpoint, an Agentic RAG answer verification debug endpoint, a SQLite-backed vector store debug layer for real vector database preparation, an EmbeddingProvider abstraction layer with an embedding debug endpoint, a Chroma-backed persistent vector store debug endpoint, an Agentic RAG retrieval backend switch that supports both hybrid and Chroma backends, and a backend-aware RAG evaluation comparison layer for hybrid-vs-Chroma metrics, refined backend comparison metrics, backend-aware Agentic RAG SSE streaming alignment, a reranker-ready retrieval backend extension with `chroma_rerank`, pairwise backend metric deltas for multi-backend comparison, a multi-backend-aware comparison summary, local semantic embedding provider validation with a CI-safe fallback, and a backend evaluation report layer that converts raw backend metrics into engineering selection guidance, with observability trace payload alignment for that report, an extended RAG evaluation dataset for less tiny backend comparison signals, Day40 failure-analysis plus selection-policy evaluation for conservative backend decisions, and Day41 semantic embedding evaluation plus failure-case review for backend switch readiness, Day42 GraphRAG + Neo4j schema/health-debug foundation, Day43 deterministic Entity / Relation extraction with `/graph/extract-debug`, Day44 Neo4j graph ingestion with `/graph/ingest-debug`, Day45 Neo4j graph retrieval with `/graph/retrieval-debug`, Day46 GraphRAG + VectorRAG fusion with `/graph/fusion-debug`, Day47 Agentic RAG connection to GraphRAG through `retrieval_backend="graph_fusion"` on `/rag/agentic-debug`, Day48 GraphRAG evaluation support for `graph_fusion` across `/rag/eval-debug` and `/rag/backend-eval-debug`, Day49 GraphRAG-aware observability / answer verification hardening for `graph_fusion`, Day50 GraphRAG architecture documentation through `docs/GRAPHRAG.md`, Day51 GraphRAG interview material prepared locally through Chinese talk track and Q&A notes, and Day52 Multi-Agent state foundation through `/multi-agent/state-debug`.

## Current Status

```text
Day1-Day52 completed.
Current stage: Day52 completed.
Day52 completed: Multi-Agent state foundation with shared task / event / artifact / memory structures and /multi-agent/state-debug.
Local pytest baseline after Day52: 167 passed, 1 warning.
Git commit: c07bd45 add multi agent state debug.
Git push: success.
GitHub Actions CI: green.
Next milestone: Day53 Planner Agent.
```


## Day51 GraphRAG Interview Material

Day51 converted the completed GraphRAG implementation into interview-ready Chinese material.

Status-only repository decision:

```text
The Chinese talk track, Q&A, and Day51 summary were prepared locally / in the project conversation.
The files docs/DAY51.md and docs/interview/* were intentionally not committed in that update.
README.md and HANDOFF.md recorded that Day51 was complete and routed the project to Day52.
```

Important Day51 boundary:

```text
Day51 did not modify core GraphRAG logic.
It did not make graph_fusion the default backend.
It did not start Multi-Agent.
```

## Day52 Multi-Agent State Foundation

Day52 starts the Complex Multi-Agent Workflow stage by adding the shared state foundation.

New capability:

```text
POST /multi-agent/state-debug
```

Day52 added:

```text
src/app/multi_agent/__init__.py
src/app/multi_agent/state.py
src/app/schemas/multi_agent.py
src/app/routes/routes_multi_agent.py
tests/multi_agent/test_multi_agent_state.py
tests/multi_agent/test_multi_agent_state_debug.py
```

Day52 state model includes:

```text
MultiAgentRole:
  supervisor, planner, researcher, tool, critic, memory, reflection

MultiAgentTask:
  task_id, title, description, assigned_role, status, depends_on, result, metadata

MultiAgentEvent:
  event_id, event_type, role, message, metadata

MultiAgentArtifact:
  artifact_id, name, artifact_type, content, created_by, metadata

MultiAgentState:
  task, thread_id, trace_id, current_role, tasks, events, artifacts, memory, final_answer, status
```

Day52 debug response includes a summary with:

```text
task_count
event_count
artifact_count
status_counts
role_counts
current_role
status
```

Validation:

```text
pytest tests/multi_agent -q
7 passed, 1 warning

pytest tests/core tests/agent tests/rag tests/graph tests/observability tests/multi_agent -q
165 passed, 1 warning

pytest -q
167 passed, 1 warning

Git commit: c07bd45 add multi agent state debug
Git push: success
GitHub Actions CI: green
```

Important Day52 boundary:

```text
Day52 only adds Multi-Agent state foundation.
It does not implement Planner Agent yet.
It does not implement Research / Tool / Critic / Memory / Reflection agents.
It does not implement Supervisor graph.
It does not call LLM.
It does not connect Multi-Agent to Neo4j.
It does not make graph_fusion the default backend.
```

Next milestone:

```text
Day53: Planner Agent.
```


## Project Positioning

This project is intentionally positioned differently from `chat-api`.

```text
agent-api:
  Agent / RAG / GraphRAG / Multi-Agent workflow project.

chat-api:
  Production-grade LLM Chat Backend / LLM Gateway project.
```

The two projects should not duplicate each other. `chat-api` proves production LLM application backend engineering ability. `agent-api` proves complex Agentic RAG and Multi-Agent system ability.

`agent-api` should continue toward:

```text
FastAPI + LangGraph Agentic RAG / GraphRAG / Multi-Agent backend system.
```

`chat-api` should later be upgraded toward:

```text
Production-ready LLM Chat Gateway with multi-provider access, conversation
storage, SSE streaming, usage/cost statistics, API key auth, rate limiting,
prompt cache, provider fallback, observability, and deployment.
```

## Locked Development Roadmap

The VectorRAG stage has been expanded enough and should be considered closed for now.

```text
Day29-Day41:
  Completed SQLite Vector Store, EmbeddingProvider, Chroma, Agentic RAG backend
  switch, rerank, backend evaluation, semantic evaluation, evaluation_report,
  failure analysis, and semantic review.

Day42-Day51:
  GraphRAG + Neo4j

Day42:
  Completed GraphRAG + Neo4j environment and schema foundation.

Day43:
  Completed deterministic Entity / Relation extraction.

Day44:
  Completed Neo4j graph ingestion.

Day45:
  Completed Graph retrieval debug.

Day46:
  Completed GraphRAG + VectorRAG fusion.

Day47:
  Completed Agentic RAG connection to GraphRAG.

Day48:
  Completed GraphRAG evaluation.

Day49:
  Completed Observability / answer verification for GraphRAG.

Day50:
  Completed GraphRAG docs.

Day51:
  Completed GraphRAG interview material.

Day52-Day63:
  Complex Multi-Agent Workflow

Day52:
  Completed Multi-Agent state foundation.

Day53:
  Planner Agent.

Day64-Day66:
  Final review, README / HANDOFF refactor, and resume / interview material cleanup
```

Route guard:

```text
Day42 started GraphRAG + Neo4j environment and schema.
Day43 completed deterministic Entity / Relation extraction.
Day44 completed Neo4j graph ingestion.
Day45 completed Graph retrieval debug over the ingested Neo4j seed graph.
Day46 completed GraphRAG + VectorRAG fusion debug as a standalone boundary.
Day47 completed Agentic RAG connection to GraphRAG through an explicit graph_fusion backend.
Day48 completed GraphRAG evaluation for the explicit graph_fusion backend without making it the default.
Day49 completed observability / answer verification hardening for GraphRAG.
Day50 completed GraphRAG architecture documentation.
Day51 completed GraphRAG interview material. Day52 completed Multi-Agent state foundation. Day53 should start Planner Agent.
Do not continue VectorRAG production selection-policy polishing before GraphRAG.
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
* `/rag/embedding-debug` embedding provider debug endpoint
* `/rag/chroma-search-debug` Chroma persistent vector store debug endpoint
* `/rag/eval-debug` RAG evaluation debug endpoint
* `/rag/backend-eval-debug` RAG backend evaluation comparison endpoint
* `/rag/eval-debug` supports `retrieval_backend="graph_fusion"` for GraphRAG evaluation
* `/rag/backend-eval-debug` compares `hybrid`, `chroma`, `chroma_rerank`, and `graph_fusion`
* GraphRAG evaluation keeps `graph_dry_run=true` by default for CI safety
* GraphRAG evaluation case metadata includes `graph_vector_contribution`
* Graph/vector contribution metadata summarizes graph status, graph chunk count, vector result count, fusion result count, and graph/vector source counts
* Manual live Neo4j-backed GraphRAG evaluation verified with `graph_dry_run=false`
* GraphRAG-aware observability traces preserve `retrieval_metadata`, `graph_vector_contribution`, and `graph_fusion_verification` for `graph_fusion`
* `/rag/answer-verify-debug` supports `retrieval_backend="graph_fusion"`
* GraphRAG answer verification preserves both nested `verification` and flattened verification fields
* GraphRAG answer verification returns `graph_fusion_verification` with graph/vector evidence flags
* Manual live Neo4j-backed GraphRAG answer verification verified with graph + vector evidence
* `docs/GRAPHRAG.md` documents the full GraphRAG architecture, including schema, extraction, ingestion, retrieval, fusion, Agentic RAG integration, evaluation, observability, and answer verification.
* `/graph/schema-debug` GraphRAG schema debug endpoint
* `/graph/health-debug` Neo4j health debug endpoint
* `/graph/extract-debug` deterministic GraphRAG Entity / Relation extraction debug endpoint
* `/graph/ingest-debug` Neo4j graph ingestion debug endpoint
* `/graph/retrieval-debug` Neo4j graph retrieval debug endpoint
* `/graph/fusion-debug` GraphRAG + VectorRAG fusion debug endpoint
* `/rag/agentic-debug` supports `retrieval_backend="graph_fusion"` as an explicit GraphRAG-capable Agentic RAG backend
* Agentic RAG `graph_fusion` backend reuses Day46 `run_graph_vector_fusion_debug()` instead of duplicating graph/vector logic
* Agentic RAG graph fusion retrieval results preserve `fusion_score`, `graph_score`, `vector_score`, `retrieval_sources`, `matched_entities`, `mentions`, `graph_metadata`, and `vector_metadata`
* Manual live Neo4j-backed Agentic RAG graph fusion verified with graph + vector evidence merged by `chunk_id`
* Extended RAG evaluation dataset with 12 cases through `eval_cases/rag_agentic_eval_extended.jsonl`
* Extended backend failure analysis through `evaluation_report.failure_analysis`
* Conservative backend selection-policy evaluation through `evaluation_report.selection_policy_evaluation`
* Semantic extended backend evaluation script through `scripts/validate_semantic_extended_backend_eval.py`
* Semantic backend review analysis through `src/app/evaluation/semantic_review.py`
* Semantic backend review report generation through `scripts/review_semantic_backend_eval_report.py`
* Agent graph-flow knowledge clarification through `START -> agent -> tools -> agent -> END`
* GraphRAG + Neo4j schema foundation through `src/app/graph/schema.py`
* Neo4j client boundary through `src/app/graph/neo4j_client.py`
* `/graph/schema-debug` GraphRAG schema debug endpoint
* `/graph/health-debug` CI-safe Neo4j health debug endpoint
* Manual live Neo4j health validation through `/graph/health-debug?check_connection=true`
* Deterministic graph extraction through `src/app/graph/extraction.py`
* Graph extraction entities: Agent, RAG, LangGraph, Tool, and Memory over the current `agent_basics` knowledge chunks
* Graph extraction relationships: `HAS_CHUNK`, `NEXT_CHUNK`, `MENTIONS`, and optional `RELATED_TO`
* `/graph/extract-debug` returns documents, chunks, entities, relations, and extraction counts without writing to Neo4j
* Neo4j graph ingestion through `src/app/graph/ingestion.py`
* Graph ingestion supports dry-run planning and live execution through `/graph/ingest-debug`
* Graph ingestion upserts `Document`, `Chunk`, and `Entity` nodes
* Graph ingestion upserts `HAS_CHUNK`, `NEXT_CHUNK`, `MENTIONS`, and `RELATED_TO` relationships
* Manual live Neo4j ingestion verified with 1 Document, 3 Chunk, 5 Entity nodes and HAS_CHUNK / NEXT_CHUNK / MENTIONS / RELATED_TO relationships
* Neo4j graph retrieval through `src/app/graph/retrieval.py`
* Graph retrieval supports query entity matching against ingested `Entity` nodes
* Graph retrieval retrieves chunks through `MENTIONS` relationships
* Graph retrieval retrieves related entities through `RELATED_TO` relationships
* `/graph/retrieval-debug` returns query entity matches, retrieval plan, matched entities, chunks, related entities, and counts
* Manual live Neo4j retrieval verified for `RAG 和 LangGraph 有什么关系？` and `智能体如何使用工具和短期记忆？`
* GraphRAG + VectorRAG fusion through `src/app/graph/fusion.py`
* `/graph/fusion-debug` merges graph retrieval chunks and hybrid VectorRAG chunks by `chunk_id`
* Fusion result metadata includes `fusion_score`, `graph_score`, `vector_score`, `retrieval_sources`, `graph_metadata`, and `vector_metadata`
* Manual live graph + vector fusion verified for `RAG 和 LangGraph 有什么关系？` and `智能体如何使用工具和短期记忆？`
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
* EmbeddingProvider abstraction layer with `deterministic` provider and reserved `sentence_transformers` provider
* Embedding debug metadata: `provider`, `model`, `requested_embedding_dim`, `actual_embedding_dim`, `query_embedding_preview`, `query_embedding_norm`, and document embedding previews
* Embedding debug observability event: `rag_embedding_debug`
* Provider-aware vector store debug fields: `embedding_provider` and `embedding_model`
* Chroma persistent vector store debug layer with `build_chroma_index()`, `query_chroma_store()`, and `debug_chroma_search()`
* Chroma index statistics: `collection_name`, `persist_dir`, `loaded_chunks`, `upserted_count`, and `stored_count`
* Chroma search result metadata: `distance`, `score`, `chunk_id`, `source`, `index`, `preview`, and `content_length`
* Chroma search debug observability event: `rag_chroma_search_debug`
* Agentic RAG retrieval backend switch
* Backend-aware RAG evaluation comparison with `retrieval_backend="hybrid"` and `retrieval_backend="chroma"`
* Chroma collection naming with short readable tokens plus a stable hash suffix
* Backend-normalized retrieval results for Agentic RAG
* Agentic RAG backend metadata: `retrieval_backend` and `retrieval_metadata`
* Agentic RAG trace payload records retrieval backend and retrieval metadata
* `/rag/eval-debug` backend-aware evaluation with `retrieval_backend`
* `/rag/backend-eval-debug` hybrid-vs-Chroma backend comparison
* RAG backend comparison metrics: `pass_rate`, `retrieval_decision_accuracy`, `expected_terms_hit_rate`, `citation_hit_rate`, and `average_relevance_score`
* Backend comparison trace event: `rag_backend_eval_debug`
* Refined backend comparison metrics: `metric_deltas`, `case_comparisons`, and `comparison_summary`
* Backend comparison trace payload now records refined metrics and per-case backend comparisons
* `/rag/agentic-stream` supports `retrieval_backend="hybrid"` and `retrieval_backend="chroma"`
* Agentic RAG stream events include `retrieval_backend` and `retrieval_metadata`
* Agentic RAG stream trace payload includes backend metadata
* Deterministic reranker layer for CI-safe rerank experiments
* `retrieval_backend="chroma_rerank"` for Chroma retrieval followed by lightweight reranking
* Rerank metadata: `original_rank`, `original_score`, `rerank_score`, `rerank_keyword_score`, and `rerank_matched_terms`
* Reranker-ready Agentic RAG path step: `chroma_rerank_retrieve`
* Backend evaluation can compare `hybrid`, `chroma`, and `chroma_rerank`
* Pairwise backend metric deltas through `pairwise_metric_deltas`
* Multi-backend comparison pairs: `hybrid -> chroma`, `hybrid -> chroma_rerank`, and `chroma -> chroma_rerank`
* Backend comparison trace payload records `pairwise_metric_deltas`
* Backward-compatible `metric_deltas` remains first-vs-second
* Multi-backend-aware `comparison_summary.notes`
* `comparison_summary.evaluated_backends`
* `comparison_summary.metric_winners`
* `comparison_summary.metric_rankings`
* `comparison_summary.top_improvement_pairs`
* Trace payload records the refined multi-backend comparison summary
* Backend evaluation report builder through `build_backend_evaluation_report()`
* Backend evaluation report trace payload alignment through `rag_backend_eval_debug`
* Extended evaluation validates `evaluation_report.eval_case_count = 12` and removes the small/tiny eval-set caveat
* `/rag/backend-eval-debug` returns `evaluation_report`
* `rag_backend_eval_debug` trace payload records `evaluation_report`
* Evaluation report fields: `recommended_backend`, `recommendation_reason`, `default_backend_should_change`, `metric_highlights`, `risk_notes`, `failure_analysis`, `selection_policy_evaluation`, and `backend_rank_summary`
* Backend selection policy keeps `hybrid` as the default until semantic embedding evaluation and failed-case review validate switching
* Local semantic embedding validation for `sentence_transformers` with `/mnt/f/LLM/maidalun/bce-embedding-base_v1`
* Day38 semantic embedding validation script: `scripts/validate_semantic_embedding_provider.py`
* CI-safe semantic embedding provider test: `tests/test_rag_semantic_embedding_provider.py`
* `/rag/embedding-debug` verified with `provider="sentence_transformers"` and local BCE model path
* `/rag/chroma-search-debug`, `/rag/agentic-debug`, and `/rag/backend-eval-debug` verified with local semantic embeddings
* Provider argument boundary normalized across `get_embedding_provider()`, `SentenceTransformersEmbeddingProvider`, Chroma store, and SQLite vector store
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
* Server-Sent Events
* Backend-aware Agentic RAG streaming response
* Reranker-ready retrieval backend
* SSE event helper with `ensure_ascii=False` for readable Chinese output
* Environment-based LLM provider configuration
* Request-level provider override for `/llm/chat`
* Split pytest API tests
* GitHub Actions CI
* `/multi-agent/state-debug` Multi-Agent state debug endpoint
* Multi-Agent shared state foundation through `src/app/multi_agent/state.py`
* Multi-Agent role definitions for supervisor, planner, researcher, tool, critic, memory, and reflection
* Multi-Agent task / event / artifact structures for future workflow orchestration
* Multi-Agent state summary with task, event, artifact, status, and role counts
* CI-safe Multi-Agent state tests under `tests/multi_agent/`

Not implemented yet:

* OpenAI provider
* Replacing `/agent/chat` with the real LLM Agent as the default main route
* Making Smart Chat the default production entry point
* Document upload and parsing pipeline
* Full Multi-Agent workflow beyond Day52 state foundation

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
* ChromaDB persistent vector store debug layer
* Optional local `sentence-transformers` semantic embedding validation
* Neo4j Python Driver
* GraphRAG schema foundation
* Neo4j health-check debug boundary
* Deterministic Entity / Relation extraction for GraphRAG seed data
* Neo4j graph ingestion debug boundary
* Neo4j graph retrieval debug boundary
* GraphRAG + VectorRAG fusion debug boundary
* Agentic RAG GraphRAG backend path through `retrieval_backend="graph_fusion"`
* GraphRAG evaluation support for `retrieval_backend="graph_fusion"`
* GraphRAG observability and answer verification metadata for `retrieval_backend="graph_fusion"`
* GraphRAG architecture documentation through `docs/GRAPHRAG.md`
* Agentic RAG retrieval backend switch
* Multi-Agent state foundation
* Multi-Agent state debug endpoint
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
├── scripts/
│   ├── validate_semantic_embedding_provider.py
│   ├── validate_semantic_extended_backend_eval.py
│   └── review_semantic_backend_eval_report.py
├── .env.example
├── .gitignore
├── .github/
│   └── workflows/
│       └── ci.yml
├── eval_cases/
│   ├── rag_agentic_eval.jsonl
│   └── rag_agentic_eval_extended.jsonl
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
│   ├── DAY38.md
│   ├── DAY39.md
│   ├── DAY40.md
│   ├── DAY41.md
│   ├── DAY42.md
│   ├── DAY43.md
│   ├── DAY44.md
│   ├── DAY45.md
│   ├── DAY46.md
│   ├── DAY47.md
│   ├── DAY48.md
│   ├── DAY49.md
│   ├── DAY50.md
│   ├── DAY52.md
│   └── GRAPHRAG.md
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
│       │   ├── graph.py
│       │   ├── multi_agent.py
│       │   └── observability.py
│       ├── routes/
│       │   ├── routes_agent.py
│       │   ├── routes_llm.py
│       │   ├── routes_rag.py
│       │   ├── routes_graph.py
│       │   ├── routes_multi_agent.py
│       │   └── routes_observability.py
│       ├── evaluation/
│       │   ├── __init__.py
│       │   ├── rag_eval.py
│       │   ├── rag_report.py
│       │   └── semantic_review.py
│       ├── observability/
│       │   ├── __init__.py
│       │   └── trace_store.py
│       ├── graph/
│       │   ├── __init__.py
│       │   ├── schema.py
│       │   ├── neo4j_client.py
│       │   ├── extraction.py
│       │   ├── ingestion.py
│       │   ├── retrieval.py
│       │   └── fusion.py
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
│       │   ├── graph_fusion_metadata.py
│       │   └── retriever.py
│       ├── multi_agent/
│       │   ├── __init__.py
│       │   └── state.py
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
    ├── test_graph_schema.py
    ├── test_graph_debug.py
    ├── test_graph_extraction.py
    ├── test_graph_extract_debug.py
    ├── test_graph_ingestion.py
    ├── test_graph_ingest_debug.py
    ├── test_graph_retrieval.py
    ├── test_graph_retrieval_debug.py
    ├── test_graph_fusion.py
    ├── test_graph_fusion_debug.py
    ├── test_rag_agentic_graph_fusion_backend.py
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

Day25 added a RAG evaluation debug layer. Day33 upgraded it into a backend-aware evaluation layer. Day34 refined the backend comparison output. Day36 extended metric deltas from first-vs-second comparison to pairwise multi-backend comparison. Day37 made `comparison_summary` multi-backend-aware. Day39 added an engineering-facing `evaluation_report` layer for backend selection guidance and aligned that report with the `rag_backend_eval_debug` trace payload. Day40 first stage added an extended 12-case RAG evaluation dataset so backend comparison is no longer limited to the original tiny 3-case regression set. Day40 second stage added failure analysis and selection-policy evaluation so backend comparison can explain failed cases and conservative default-switch blockers. Day41 validated the extended eval set with local semantic embeddings, added semantic backend review analysis, and resolved the agent_graph_flow common failed case. Day48 added GraphRAG evaluation support for `retrieval_backend="graph_fusion"` and four-backend comparison across `hybrid`, `chroma`, `chroma_rerank`, and `graph_fusion`.

```text
eval_cases/rag_agentic_eval.jsonl
eval_cases/rag_agentic_eval_extended.jsonl
  ↓
load_rag_eval_cases()
  ↓
evaluate_rag_cases(retrieval_backend=...)
  ↓
invoke_agentic_rag(retrieval_backend=...)
  ↓
metrics + per-case backend-aware results
  ↓
compare_rag_retrieval_backends()
  ↓
metric_deltas + pairwise_metric_deltas + case_comparisons + comparison_summary
  ↓
build_backend_evaluation_report()
  ↓
evaluation_report
  ↓
/rag/backend-eval-debug
```

Current evaluation files:

```text
eval_cases/rag_agentic_eval.jsonl
eval_cases/rag_agentic_eval_extended.jsonl
src/app/evaluation/rag_eval.py
tests/test_rag_eval.py
tests/test_rag_backend_eval.py
tests/test_rag_agentic_stream_backend.py
tests/test_rag_reranker.py
tests/test_rag_backend_pairwise_eval.py
tests/test_rag_backend_comparison_summary.py
tests/test_rag_backend_report.py
tests/test_rag_eval_extended_dataset.py
tests/test_rag_backend_extended_analysis.py
tests/test_semantic_backend_review.py
```

Current endpoints:

```text
POST /rag/eval-debug
POST /rag/backend-eval-debug
```

Current evaluation functions:

```text
load_rag_eval_cases()
evaluate_rag_cases()
compare_rag_retrieval_backends()
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

Current backend comparison fields:

```text
metric_deltas
pairwise_metric_deltas
case_comparisons
comparison_summary
evaluation_report
evaluation_report.failure_analysis
evaluation_report.selection_policy_evaluation
```

Compatibility behavior:

```text
metric_deltas remains first-vs-second.
pairwise_metric_deltas compares every backend pair in request order.
comparison_summary is multi-backend-aware.
```

Day37 comparison summary fields:

```text
comparison_summary.total_backends
comparison_summary.evaluated_backends
comparison_summary.best_backend_by_pass_rate
comparison_summary.best_backend_by_average_relevance
comparison_summary.metric_winners
comparison_summary.metric_rankings
comparison_summary.top_improvement_pairs
comparison_summary.notes
```

Example backend request:

```text
["hybrid", "chroma", "chroma_rerank", "graph_fusion"]
```

Observed Day37 backend metrics:

```text
hybrid:
  pass_rate = 1.0
  expected_terms_hit_rate = 1.0
  average_relevance_score = 0.278223

chroma:
  pass_rate = 0.666667
  expected_terms_hit_rate = 0.666667
  average_relevance_score = 0.279233

chroma_rerank:
  pass_rate = 1.0
  expected_terms_hit_rate = 1.0
  average_relevance_score = 0.394302
```

Observed Day37 metric winners:

```text
pass_rate:
  value = 1.0
  winners = hybrid, chroma_rerank
  tie = true

average_relevance_score:
  value = 0.394302
  winners = chroma_rerank
  tie = false

retrieval_decision_accuracy:
  value = 1.0
  winners = hybrid, chroma, chroma_rerank
  tie = true

expected_terms_hit_rate:
  value = 1.0
  winners = hybrid, chroma_rerank
  tie = true

citation_hit_rate:
  value = 1.0
  winners = hybrid, chroma, chroma_rerank
  tie = true
```

Observed Day37 top improvement pairs:

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

Observed Day37 summary notes:

```text
Evaluated 3 backends: hybrid, chroma, chroma_rerank.
Pass rate is tied at 1.0 by hybrid, chroma_rerank.
Best average_relevance_score is chroma_rerank with value 0.394302.
Largest pass_rate improvement is chroma -> chroma_rerank with delta 0.333333.
Largest average_relevance_score improvement is hybrid -> chroma_rerank with delta 0.116079.
```

Important interpretation:

```text
comparison_summary.notes no longer describes only the first two backends.
The summary can now report ties, per-metric winners, metric rankings, and top improvement pairs across all evaluated backends.
```

Example backend comparison request:

```bash
curl -s -X POST http://localhost:8000/rag/backend-eval-debug \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day37-backend-summary-001" \
  -d '{"backends":["hybrid","chroma","chroma_rerank"],"source_filter":"agent_basics","max_chars":300,"embedding_dim":64,"keyword_weight":0.6,"vector_weight":0.4,"embedding_provider":"deterministic","rebuild_index":true}' \
  | python -m json.tool --no-ensure-ascii
```

Trace lookup:

```bash
curl -s http://localhost:8000/observability/traces/day37-backend-summary-001 \
  | python -m json.tool --no-ensure-ascii
```

The `rag_backend_eval_debug` trace event now includes the refined multi-backend `comparison_summary` and the Day39 `evaluation_report`.

## Current Extended RAG Evaluation Dataset

Day40 added an extended RAG evaluation dataset and then used it for backend failure analysis and conservative backend selection-policy refinement.

Current extended eval file:

```text
eval_cases/rag_agentic_eval_extended.jsonl
```

Current extended eval tests:

```text
tests/test_rag_eval_extended_dataset.py
tests/test_rag_backend_extended_analysis.py
```

Design:

```text
Default eval set:
  eval_cases/rag_agentic_eval.jsonl
  3 cases, fast CI regression signal.

Extended eval set:
  eval_cases/rag_agentic_eval_extended.jsonl
  12 cases, broader backend comparison signal.
```

The extended dataset covers:

```text
RAG definition
LangGraph definition
Agent definition
Agent components
Tools
Memory
Agent graph flow
RAG core flow
RAG retrieval reason
LangGraph workflow
Direct greeting
Direct casual chat
```

Observed Day40 extended deterministic backend comparison:

```text
hybrid:
  total_cases = 12
  passed_cases = 10
  pass_rate = 0.833333
  expected_terms_hit_rate = 0.833333
  citation_hit_rate = 1.0
  average_relevance_score = 0.407461

chroma:
  total_cases = 12
  passed_cases = 9
  pass_rate = 0.75
  expected_terms_hit_rate = 0.75
  citation_hit_rate = 1.0
  average_relevance_score = 0.412151

chroma_rerank:
  total_cases = 12
  passed_cases = 10
  pass_rate = 0.833333
  expected_terms_hit_rate = 0.833333
  citation_hit_rate = 1.0
  average_relevance_score = 0.529049
```

Observed Day40 phase 2 report result:

```text
evaluation_report.eval_case_count = 12
recommended_backend = chroma_rerank
default_backend = hybrid
default_backend_should_change = false
selection_policy = keep_default_hybrid_until_semantic_eval
```

Observed failure analysis:

```text
common_failed_cases:
  - agent_definition
  - agent_graph_flow

failure_count_by_backend:
  hybrid = 2
  chroma = 3
  chroma_rerank = 2

unique_failed_cases_by_backend:
  chroma = langgraph_definition
  hybrid = none
  chroma_rerank = none
```

Observed selection-policy evaluation:

```text
candidate_backend = chroma_rerank
default_backend = hybrid
pass_rate_winners = hybrid, chroma_rerank
best_relevance_backend = chroma_rerank
default_backend_should_change = false
```

Supporting reasons:

```text
chroma_rerank is in the top pass-rate group.
chroma_rerank has the best average relevance score.
The extended eval set has 12 cases, so it is no longer treated as a tiny regression-only eval set.
```

Blocking reasons:

```text
The run uses deterministic embeddings; semantic embedding validation is required before switching the default backend.
Common failed cases must be reviewed before changing the default backend: agent_definition, agent_graph_flow.
```

Important interpretation:

```text
The extended eval set removes the small/tiny eval-set caveat from the report.
The deterministic embedding caveat remains, because deterministic embeddings are CI-safe but do not represent real semantic embedding quality.
The common failed cases show that some failures are not backend-specific; they likely require reviewing eval case design, knowledge content, chunking, query rewriting, or answer construction.
chroma_rerank remains the strongest experiment candidate by average relevance score.
The default backend remains hybrid until semantic embedding evaluation and failure-case review justify a production switch.
```

Example extended backend comparison request:

```bash
curl -s -X POST http://localhost:8000/rag/backend-eval-debug \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day40-extended-analysis-manual-001" \
  -d '{"eval_file":"eval_cases/rag_agentic_eval_extended.jsonl","backends":["hybrid","chroma","chroma_rerank"],"source_filter":"agent_basics","max_chars":300,"embedding_dim":64,"keyword_weight":0.6,"vector_weight":0.4,"embedding_provider":"deterministic","rebuild_index":true}' \
  | python -m json.tool --no-ensure-ascii
```

Trace lookup:

```bash
curl -s http://localhost:8000/observability/traces/day40-extended-analysis-manual-001 \
  | python -m json.tool --no-ensure-ascii
```

Expected trace payload fields:

```text
payload.evaluation_report.failure_analysis
payload.evaluation_report.selection_policy_evaluation
payload.evaluation_report.default_backend_should_change = false
```

## Current Day41 Semantic Backend Evaluation and Failure-case Review

Day41 completed semantic embedding evaluation on the extended RAG eval dataset and converted the result into a switch-readiness review.

Current Day41 files:

```text
scripts/validate_semantic_extended_backend_eval.py
scripts/review_semantic_backend_eval_report.py
src/app/evaluation/semantic_review.py
tests/test_semantic_backend_review.py
knowledge/agent_basics.md
```

Generated local report artifacts are intentionally ignored by Git:

```text
reports/day41_semantic_extended_backend_eval.json
reports/day41_semantic_backend_review.md
```

Day41 used the local BCE sentence-transformers embedding model:

```text
embedding_provider = sentence_transformers
embedding_model = /mnt/f/LLM/maidalun/bce-embedding-base_v1
embedding_dim = 768
eval_file = eval_cases/rag_agentic_eval_extended.jsonl
backends = hybrid, chroma, chroma_rerank
```

Observed semantic extended backend comparison after the `agent_graph_flow` knowledge fix:

```text
hybrid:
  total_cases = 12
  passed_cases = 11
  pass_rate = 0.916667
  expected_terms_hit_rate = 0.916667
  citation_hit_rate = 1.0
  average_relevance_score = 0.35149

chroma:
  total_cases = 12
  passed_cases = 12
  pass_rate = 1.0
  expected_terms_hit_rate = 1.0
  citation_hit_rate = 1.0
  average_relevance_score = 0.517869

chroma_rerank:
  total_cases = 12
  passed_cases = 12
  pass_rate = 1.0
  expected_terms_hit_rate = 1.0
  citation_hit_rate = 1.0
  average_relevance_score = 0.607509
```

Observed Day41 report result:

```text
best_backend_by_pass_rate = chroma
best_backend_by_average_relevance = chroma_rerank
recommended_backend = chroma_rerank
default_backend = hybrid
default_backend_should_change = true
selection_policy = candidate_backend_ready_for_default_switch
eval_case_count = 12
```

Observed Day41 semantic review result:

```text
review_decision = candidate_ready_for_default_switch_review
semantic_candidate_validated = true
candidate_backend = chroma_rerank
default_backend = hybrid
common_failed_cases = []
blocking_reasons = []
```

Failure analysis after the knowledge fix:

```text
common_failed_cases = []
failure_count_by_backend:
  hybrid = 1
  chroma = 0
  chroma_rerank = 0

unique_failed_cases_by_backend:
  hybrid = agent_definition
  chroma = none
  chroma_rerank = none
```

Knowledge fix:

```text
knowledge/agent_basics.md now explicitly documents:
START -> agent -> tools -> agent -> END
```

Important interpretation:

```text
Day41 validates chroma_rerank as the strongest semantic backend candidate.
The prior agent_graph_flow common failed case was caused by missing explicit graph-flow knowledge rather than a backend-specific retrieval bug.
After adding the START -> agent -> tools -> agent -> END explanation, common_failed_cases becomes empty in the semantic review.
The report now says the candidate is ready for default-switch review, but Day41 does not directly switch the production default backend.
The default retrieval backend remains hybrid; production backend-switch policy hardening is deferred so Day42 can return to the GraphRAG + Neo4j roadmap.
```

Validation:

```text
pytest tests/test_rag_agentic_backend.py \
       tests/test_rag_chroma_store.py \
       tests/test_rag_vector_store.py \
       tests/test_rag_backend_comparison_summary.py \
       tests/test_rag_backend_extended_analysis.py -q
14 passed, 1 warning

pytest -q
108 passed, 1 warning

GitHub Actions CI: green
```


## Current GraphRAG / Neo4j Foundation, Extraction, Ingestion, and Retrieval

Day42 started the GraphRAG + Neo4j stage while keeping the existing Agentic RAG default retrieval backend unchanged. Day43 added deterministic Entity / Relation extraction over the existing Markdown knowledge chunks. Day44 added a Neo4j ingestion boundary that consumes the Day43 extraction output and writes the seed graph into Neo4j through controlled upsert queries. Day45 added a Neo4j graph retrieval boundary over that seed graph. Day46 added a standalone GraphRAG + VectorRAG fusion debug boundary. Day47 connected that fusion boundary to Agentic RAG through an explicit `graph_fusion` backend while keeping the default backend unchanged. Day48 added GraphRAG evaluation support so `graph_fusion` can be evaluated and compared against existing RAG backends without making it the default.

```text
/graph/schema-debug
  ↓
get_graph_schema()
  ↓
GraphRAG schema metadata
```

```text
/graph/health-debug
  ↓
skipped_neo4j_connection_check()
  ↓
CI-safe Neo4j settings response without requiring a live Neo4j service
```

```text
/graph/health-debug?check_connection=true
  ↓
check_neo4j_connection()
  ↓
Neo4j Python driver
  ↓
RETURN 1 AS ok
```

```text
/graph/extract-debug
  ↓
extract_graph_items()
  ↓
load_knowledge_chunks()
  ↓
deterministic entity matching + deterministic relation building
  ↓
Document / Chunk / Entity / Relation debug payload
```

```text
/graph/ingest-debug
  ↓
run_graph_ingestion_debug()
  ↓
extract_graph_items()
  ↓
build_graph_ingestion_plan()
  ├── dry_run=true  -> CI-safe ingestion plan only
  └── dry_run=false -> execute_graph_ingestion() -> Neo4j upserts
```

```text
/graph/retrieval-debug
  ↓
run_graph_retrieval_debug()
  ↓
extract_query_entity_matches()
  ↓
build_graph_retrieval_plan()
  ├── dry_run=true  -> CI-safe retrieval plan only
  └── dry_run=false -> execute_graph_retrieval() -> Neo4j graph retrieval
```

Current graph files:

```text
src/app/graph/__init__.py
src/app/graph/schema.py
src/app/graph/neo4j_client.py
src/app/graph/extraction.py
src/app/graph/ingestion.py
src/app/graph/retrieval.py
src/app/graph/fusion.py
src/app/routes/routes_graph.py
src/app/schemas/graph.py
tests/test_graph_schema.py
tests/test_graph_debug.py
tests/test_graph_extraction.py
tests/test_graph_extract_debug.py
tests/test_graph_ingestion.py
tests/test_graph_ingest_debug.py
tests/test_graph_retrieval.py
tests/test_graph_retrieval_debug.py
tests/test_graph_fusion.py
tests/test_graph_fusion_debug.py
```

Current schema version:

```text
day42_graph_schema_v1
```

Current node labels:

```text
Document
Chunk
Entity
```

Current relationship types:

```text
HAS_CHUNK
NEXT_CHUNK
MENTIONS
RELATED_TO
```

Current GraphRAG shape:

```text
(Document)-[:HAS_CHUNK]->(Chunk)
(Chunk)-[:NEXT_CHUNK]->(Chunk)
(Chunk)-[:MENTIONS]->(Entity)
(Entity)-[:RELATED_TO]->(Entity)
```

Current deterministic extraction behavior:

```text
Document:
  Built from knowledge source path.

Chunk:
  Reuses the existing RAG chunk pipeline from src/app/rag/chunking.py.

Entity:
  Extracted by deterministic alias matching.

Relation:
  HAS_CHUNK links documents to chunks.
  NEXT_CHUNK links adjacent chunks from the same source.
  MENTIONS links chunks to detected entities.
  RELATED_TO links co-occurring entities in the same chunk when include_related_entities=true.
```

Currently extracted entities over `knowledge/agent_basics.md` with `max_chars=300`:

```text
Agent
RAG
LangGraph
Tool
Memory
```

Current graph retrieval behavior:

```text
Query entity matching:
  Query text is matched against the deterministic EntityPattern alias table.

Matched Entity retrieval:
  MATCH (e:Entity)
  WHERE e.entity_id IN $entity_ids

Chunk retrieval:
  MATCH (chunk:Chunk)-[m:MENTIONS]->(e:Entity)
  WHERE e.entity_id IN $entity_ids

Related Entity retrieval:
  MATCH (e:Entity)-[r:RELATED_TO]-(related:Entity)
  WHERE e.entity_id IN $entity_ids
```

Day45 retrieval debug response fields:

```text
trace_id
query
chunk_limit
related_entity_limit
dry_run
query_entity_matches
plan
execution
execution.matched_entities
execution.chunks
execution.related_entities
execution.counts
```

Observed Day44 dry-run ingestion plan:

```text
documents = 1
chunks = 3
entities = 5
relations = 29

node_counts:
  Document = 1
  Chunk = 3
  Entity = 5

relationship_counts:
  HAS_CHUNK = 3
  NEXT_CHUNK = 2
  MENTIONS = 10
  RELATED_TO = 14

schema_statement_count = 6
total_node_upserts = 9
total_relationship_upserts = 29
execution.status = dry_run
```

Observed Day44 live Neo4j ingestion result:

```text
dry_run = false
execution.ok = true
execution.status = ingested
execution.schema.applied_statement_count = 6

node_upsert_attempts:
  Document = 1
  Chunk = 3
  Entity = 5

relationship_upsert_attempts:
  HAS_CHUNK = 3
  NEXT_CHUNK = 2
  MENTIONS = 10
  RELATED_TO = 14
```

Observed Neo4j Browser node counts after ingestion:

```text
Chunk = 3
Document = 1
Entity = 5
```

Observed Neo4j Browser relationship counts after ingestion:

```text
HAS_CHUNK = 3
MENTIONS = 10
NEXT_CHUNK = 2
RELATED_TO = 10
```

Important relationship-count note:

```text
The ingestion plan attempts 14 RELATED_TO upserts from extraction output.
The current Neo4j Cypher uses MERGE on (source Entity)-[:RELATED_TO]->(target Entity),
so repeated same entity-pair co-occurrences collapse into one stored relationship.
Therefore the live graph stores 10 unique RELATED_TO entity-pair edges.
This is acceptable for the current seed graph. Future evidence-level relationship
storage can preserve per-chunk evidence lists if needed.
```

Observed Day45 dry-run retrieval result:

```text
trace_id = day45-graph-retrieval-dry-run-001
query = RAG 和 LangGraph 有什么关系？
dry_run = true

query_entity_matches:
  Entity:concept:rag
  Entity:framework:langgraph

plan.cypher_query_keys:
  matched_entities
  mentioned_chunks
  related_entities

execution.status = dry_run
execution.counts:
  matched_entities = 0
  chunks = 0
  related_entities = 0
```

Observed Day45 live retrieval result for `RAG 和 LangGraph 有什么关系？`:

```text
trace_id = day45-graph-retrieval-live-001
dry_run = false
execution.ok = true
execution.status = retrieved

query_entity_matches:
  RAG
  LangGraph

execution.counts:
  matched_entities = 2
  chunks = 2
  related_entities = 8

retrieved chunks:
  knowledge/agent_basics.md::chunk-1
  knowledge/agent_basics.md::chunk-2
```

Observed Day45 Chinese alias retrieval result for `智能体如何使用工具和短期记忆？`:

```text
trace_id = day45-graph-retrieval-cn-alias-001
dry_run = false
execution.ok = true
execution.status = retrieved

query_entity_matches:
  Agent matched by 智能体
  Tool matched by 工具
  Memory matched by 短期记忆

execution.counts:
  matched_entities = 3
  chunks = 3
  related_entities = 10
```

Observed Neo4j Browser retrieval validation:

```text
MATCH (c:Chunk)-[:MENTIONS]->(e:Entity {normalized_name: "rag"})
RETURN c.chunk_id AS chunk_id, c.index AS chunk_index, c.preview AS preview
ORDER BY c.index;
```

Result:

```text
knowledge/agent_basics.md::chunk-1
knowledge/agent_basics.md::chunk-2
```

```text
MATCH (:Entity {normalized_name: "rag"})-[r:RELATED_TO]-(related:Entity)
RETURN related.name AS name,
       related.type AS type,
       r.relation_type AS relation_type,
       r.confidence AS confidence,
       r.source AS source
ORDER BY related.type, related.name;
```

Result includes:

```text
Agent
Memory
Tool
LangGraph
```

Day42 validation:

```text
pytest tests/test_graph_schema.py tests/test_graph_debug.py -q
7 passed, 1 warning

pytest tests/test_health.py tests/test_trace.py tests/test_graph_schema.py tests/test_graph_debug.py -q
12 passed, 1 warning

pytest -q
115 passed, 1 warning
```

Day43 validation:

```text
pytest tests/test_graph_extraction.py tests/test_graph_extract_debug.py -q
7 passed, 1 warning

pytest tests/test_graph_schema.py \
       tests/test_graph_debug.py \
       tests/test_graph_extraction.py \
       tests/test_graph_extract_debug.py -q
14 passed, 1 warning

pytest -q
122 passed, 1 warning

GitHub Actions CI: green
```

Day44 validation:

```text
pytest tests/test_graph_ingestion.py tests/test_graph_ingest_debug.py -q
7 passed, 1 warning

pytest tests/test_graph_schema.py \
       tests/test_graph_debug.py \
       tests/test_graph_extraction.py \
       tests/test_graph_extract_debug.py \
       tests/test_graph_ingestion.py \
       tests/test_graph_ingest_debug.py -q
21 passed, 1 warning

pytest -q
129 passed, 1 warning

GitHub Actions CI: green
```

Day45 validation:

```text
pytest tests/test_graph_retrieval.py tests/test_graph_retrieval_debug.py -q
10 passed, 1 warning

pytest tests/test_graph_schema.py \
       tests/test_graph_debug.py \
       tests/test_graph_extraction.py \
       tests/test_graph_extract_debug.py \
       tests/test_graph_ingestion.py \
       tests/test_graph_ingest_debug.py \
       tests/test_graph_retrieval.py \
       tests/test_graph_retrieval_debug.py -q
31 passed, 1 warning

pytest -q
139 passed, 1 warning

GitHub Actions CI: green
```

Important Day45 boundary:

```text
Day45 only retrieves graph context from Neo4j.
It does not fuse GraphRAG with VectorRAG.
It does not connect Agentic RAG to GraphRAG.
It does not generate final answers from graph retrieval results.
The default Agentic RAG retrieval backend remains unchanged.
```


## Current Day47 Agentic RAG GraphRAG Backend

Day47 connects Agentic RAG to GraphRAG through an explicit backend path while preserving the existing default backend.

```text
/rag/agentic-debug
  ↓
invoke_agentic_rag(retrieval_backend="graph_fusion")
  ↓
retrieve_agentic_context()
  ↓
run_graph_vector_fusion_debug()
  ├── graph_dry_run=true  -> CI-safe vector-only fusion with graph plan metadata
  └── graph_dry_run=false -> live Neo4j graph retrieval + vector retrieval fusion
  ↓
normalized Agentic RAG retrieval_results
  ↓
relevance_grade
  ↓
answer_with_citations
```

New / modified files:

```text
src/app/rag/retrieval_backend.py
src/app/rag/agentic_graph.py
src/app/schemas/rag.py
src/app/routes/routes_rag.py
tests/test_rag_agentic_graph_fusion_backend.py
```

Supported Agentic RAG retrieval backends now include:

```text
hybrid
chroma
chroma_rerank
graph_fusion
```

Default backend:

```text
hybrid
```

Day47 request example:

```bash
curl -s -X POST http://localhost:8000/rag/agentic-debug \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day47-agentic-rag-graph-fusion-live-001" \
  -d '{"query":"RAG 和 LangGraph 有什么关系？","top_k":2,"source_filter":"agent_basics","max_chars":300,"embedding_dim":64,"retrieval_backend":"graph_fusion","graph_dry_run":false}' \
  | python -m json.tool --no-ensure-ascii
```

Day47 normalized retrieval result fields:

```text
fusion_score
graph_score
vector_score
retrieval_sources
matched_entities
mentions
graph_metadata
vector_metadata
```

Observed live Neo4j-backed Agentic RAG result:

```text
retrieval_backend = graph_fusion
steps include graph_fusion_retrieve
graph_dry_run = false
graph_retrieval.status = retrieved
graph_retrieval.ok = true
graph_retrieval.chunk_count = 2
vector_retrieval.result_count = 2
fusion.source_counts.graph_and_vector = 2
retrieval_sources = graph + vector
graph_score = 1.0
```

Observed CI-safe dry-run result:

```text
graph_dry_run = true
graph_retrieval.status = dry_run
vector_retrieval.result_count = 2
fusion.source_counts.vector_only = 2
```

Validation:

```text
pytest tests/test_rag_agentic_graph_fusion_backend.py -q
3 passed, 1 warning

pytest tests/test_rag_agentic_debug.py \
       tests/test_rag_agentic_backend.py \
       tests/test_graph_fusion.py \
       tests/test_graph_fusion_debug.py \
       tests/test_rag_agentic_graph_fusion_backend.py -q
19 passed, 1 warning

pytest -q
151 passed, 1 warning

GitHub Actions CI: green
```

Important Day47 boundary:

```text
Day47 connects Agentic RAG to GraphRAG only through an explicit backend.
It does not make GraphRAG the default backend.
It does not replace hybrid, chroma, or chroma_rerank.
It does not change /agent/chat or Smart Chat default behavior.
Day48 evaluated graph_fusion against existing RAG backends. Day49 completed GraphRAG observability / answer verification hardening. Day50 completed GraphRAG architecture documentation. Day51 completed GraphRAG interview material. Day52 completed Multi-Agent state foundation. Day53 should start Planner Agent.
```


## Current Day48 GraphRAG Evaluation

Day48 evaluates the explicit GraphRAG backend introduced in Day47 while preserving the existing default retrieval backend.

Scope:

```text
Day48 intentionally adds only the GraphRAG evaluation layer:
  - /rag/eval-debug supports retrieval_backend="graph_fusion"
  - /rag/backend-eval-debug can compare hybrid, chroma, chroma_rerank, and graph_fusion
  - graph_fusion remains a non-default backend
  - graph_dry_run=true remains the CI-safe default
  - case-level evaluation metadata includes graph/vector contribution summaries
  - live Neo4j-backed evaluation can be verified locally with graph_dry_run=false

Day48 does not:
  - make graph_fusion the default backend
  - start Multi-Agent
  - change /agent/chat
  - change Smart Chat defaults
  - implement GraphRAG answer verification
```

New / modified files:

```text
src/app/schemas/rag.py
src/app/evaluation/rag_eval.py
src/app/routes/routes_rag.py
tests/test_rag_graph_fusion_eval.py
```

Evaluation pipeline:

```text
/rag/eval-debug
  ↓
evaluate_rag_cases(retrieval_backend="graph_fusion", graph_dry_run=...)
  ↓
invoke_agentic_rag(retrieval_backend="graph_fusion")
  ↓
run_graph_vector_fusion_debug()
  ↓
case metrics + retrieval_metadata + graph_vector_contribution
```

Four-backend comparison pipeline:

```text
/rag/backend-eval-debug
  ↓
compare_rag_retrieval_backends(
      backends=["hybrid", "chroma", "chroma_rerank", "graph_fusion"]
    )
  ↓
evaluate_rag_cases() for each backend
  ↓
comparison_summary + pairwise_metric_deltas + evaluation_report
```

New GraphRAG evaluation fields:

```text
graph_dry_run
fusion_graph_weight
fusion_vector_weight
graph_chunk_limit
related_entity_limit
graph_evaluation_metadata
cases[*].graph_vector_contribution
```

`graph_vector_contribution` summarizes:

```text
retrieval_backend
graph_dry_run
graph_status
graph_ok
graph_chunk_count
graph_related_entity_count
vector_result_count
fusion_result_count
graph_only_count
vector_only_count
graph_and_vector_count
query_entity_match_count
```

CI-safe dry-run validation:

```text
pytest tests/test_rag_graph_fusion_eval.py -q
4 passed, 1 warning

pytest tests/test_rag_eval.py \
       tests/test_rag_backend_eval.py \
       tests/test_rag_backend_pairwise_eval.py \
       tests/test_rag_backend_comparison_summary.py \
       tests/test_rag_backend_report.py \
       tests/test_rag_graph_fusion_eval.py \
       tests/test_rag_agentic_graph_fusion_backend.py -q
23 passed, 1 warning

pytest -q
155 passed, 1 warning
```

Observed dry-run GraphRAG evaluation:

```text
trace_id = day48-rag-eval-graph-fusion-dry-run-001
retrieval_backend = graph_fusion
graph_dry_run = true
graph_evaluation_metadata.graph_fusion_enabled = true

metrics:
  total_cases = 3
  passed_cases = 3
  pass_rate = 1.0
  retrieval_decision_accuracy = 1.0
  expected_terms_hit_rate = 1.0
  citation_hit_rate = 1.0
  average_relevance_score = 0.13841

retrieval cases:
  graph_retrieval.status = dry_run
  vector_retrieval.result_count = 2
  fusion.source_counts.vector_only = 2
  fusion.source_counts.graph_and_vector = 0
```

Observed dry-run four-backend comparison:

```text
trace_id = day48-backend-eval-four-backends-dry-run-001
backends = hybrid, chroma, chroma_rerank, graph_fusion
graph_dry_run = true
graph_evaluation_metadata.graph_fusion_included = true

best_backend_by_pass_rate = hybrid
best_backend_by_average_relevance = chroma_rerank

graph_fusion:
  passed_cases = 3 / 3
  pass_rate = 1.0
  average_relevance_score = 0.13841
```

Live Neo4j-backed evaluation validation:

```text
trace_id = day48-neo4j-health-before-eval-001
connection.ok = true
connection.status = connected

trace_id = day48-reingest-seed-graph-001
execution.ok = true
execution.status = ingested
Document = 1
Chunk = 3
Entity = 5
```

Observed live GraphRAG evaluation:

```text
trace_id = day48-rag-eval-graph-fusion-live-001
retrieval_backend = graph_fusion
graph_dry_run = false

metrics:
  total_cases = 3
  passed_cases = 3
  pass_rate = 1.0
  retrieval_decision_accuracy = 1.0
  expected_terms_hit_rate = 1.0
  citation_hit_rate = 1.0
  average_relevance_score = 0.471744

rag_definition:
  graph_retrieval.status = retrieved
  graph_retrieval.ok = true
  graph_chunk_count = 2
  vector_result_count = 2
  graph_and_vector_count = 2

langgraph_definition:
  graph_retrieval.status = retrieved
  graph_retrieval.ok = true
  graph_chunk_count = 1
  vector_result_count = 2
  graph_and_vector_count = 1
```

Observed live four-backend comparison:

```text
trace_id = day48-backend-eval-four-backends-live-001
backends = hybrid, chroma, chroma_rerank, graph_fusion
graph_dry_run = false

best_backend_by_pass_rate = hybrid
best_backend_by_average_relevance = graph_fusion

graph_fusion:
  passed_cases = 3 / 3
  pass_rate = 1.0
  average_relevance_score = 0.471744

chroma_rerank:
  passed_cases = 3 / 3
  pass_rate = 1.0
  average_relevance_score = 0.393338

hybrid:
  passed_cases = 3 / 3
  pass_rate = 1.0
  average_relevance_score = 0.276821

chroma:
  passed_cases = 2 / 3
  pass_rate = 0.666667
  average_relevance_score = 0.277211
```

Selection-policy interpretation:

```text
evaluation_report.recommended_backend = graph_fusion in the live tiny eval run.
evaluation_report.default_backend = hybrid.
evaluation_report.default_backend_should_change = false.

The default backend does not change because:
  - the eval set has only 3 cases
  - the run uses deterministic embeddings
  - GraphRAG default-switch policy needs larger and more representative evaluation
```

Safety validation:

```text
No evidence that graph_fusion was made the default backend.
No Multi-Agent files were added.
```

Important Day48 boundary:

```text
Day48 evaluates graph_fusion as an explicit backend.
It does not switch the default retrieval_backend from hybrid.
It does not start Multi-Agent.
It does not implement GraphRAG answer verification.
Day49 completed observability / answer verification hardening for GraphRAG.
Day50 completed GraphRAG architecture documentation.
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

Day27 added an Agentic RAG SSE streaming endpoint. Day34 aligned this streaming endpoint with the Day32 retrieval backend switch.

```text
/rag/agentic-stream
  ↓
stream_agentic_rag_events(retrieval_backend=...)
  ↓
invoke_agentic_rag(retrieval_backend=...)
  ├── hybrid -> hybrid_retrieve
  └── chroma -> chroma_retrieve
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
Day24/Day32: invoke_agentic_rag()
Day26: record_trace_event()
Day32: retrieval_backend switch
```

Retrieval path event sequence:

```text
metadata -> decision -> rewrite -> retrieval -> relevance -> citation -> answer_chunk -> final -> done
```

Direct path event sequence:

```text
metadata -> decision -> answer_chunk -> final -> done
```

Day34 stream backend fields:

```text
retrieval_backend
retrieval_metadata
```

These fields are included in:

```text
metadata event
retrieval event
final event
rag_agentic_stream trace payload
```

Hybrid stream behavior:

```text
retrieval_backend = hybrid
steps include hybrid_retrieve
```

Chroma stream behavior:

```text
retrieval_backend = chroma
steps include chroma_retrieve
retrieval_metadata.collection_name exists
retrieval_metadata.total_indexed_chunks = 3
```

Observed Chroma stream trace fields:

```text
event_type = rag_agentic_stream
payload.retrieval_backend = chroma
payload.retrieval_metadata.retrieval_backend = chroma
payload.steps = query_analyzer -> query_rewriter -> chroma_retrieve -> relevance_grade -> answer_with_citations
payload.retrieval_results_count = 2
```

Example Chroma stream request:

```bash
curl -N -X POST http://localhost:8000/rag/agentic-stream \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day34-agentic-stream-chroma-001" \
  -d '{"query":"请搜索知识库：RAG 是什么？","top_k":2,"source_filter":"agent_basics","max_chars":300,"embedding_dim":64,"retrieval_backend":"chroma","embedding_provider":"deterministic","rebuild_index":true}'
```

Expected Chroma stream events:

```text
event: metadata      # retrieval_backend = chroma
event: decision      # steps include chroma_retrieve
event: rewrite
event: retrieval     # retrieval_backend = chroma and Chroma retrieval metadata
event: relevance
event: citation
event: answer_chunk
event: final         # retrieval_backend = chroma and retrieval_metadata
event: done
```

This keeps JSON debug and SSE streaming behavior aligned across retrieval backends.

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

## Current EmbeddingProvider Architecture

Day30 added an EmbeddingProvider abstraction layer and an embedding debug endpoint.

```text
/rag/embedding-debug
  ↓
debug_embeddings()
  ↓
get_embedding_provider()
  ├── deterministic -> DeterministicEmbeddingProvider
  └── sentence_transformers -> SentenceTransformersEmbeddingProvider  # reserved
  ↓
query/document embeddings
  ↓
record_trace_event(event_type="rag_embedding_debug")
```

Current embedding provider file:

```text
src/app/rag/embedding_provider.py
```

Current embedding debug endpoint:

```text
POST /rag/embedding-debug
```

Current functions and classes:

```text
EmbeddingProvider
DeterministicEmbeddingProvider
SentenceTransformersEmbeddingProvider
get_embedding_provider()
debug_embeddings()
embedding_norm()
```

The default provider is:

```text
deterministic
```

The default deterministic model name is:

```text
deterministic-hash
```

The reserved local semantic embedding provider is:

```text
sentence_transformers
```

The reserved sentence-transformers model name is:

```text
/mnt/f/LLM/maidalun/bce-embedding-base_v1
```

Day30 also upgraded `/rag/vector-store-debug` to be provider-aware. Vector store indexing and querying now use `get_embedding_provider()` instead of directly calling deterministic embedding functions.

Provider-aware vector store fields:

```text
embedding_provider
embedding_model
```

The endpoint writes an observability event:

```text
event_type = rag_embedding_debug
```

Day30 intentionally keeps the deterministic provider as the default so local pytest and GitHub Actions remain stable. Real semantic embeddings and Chroma integration are deferred to Day31.

## Current Chroma Vector Store Debug Architecture

Day31 added a Chroma-backed persistent vector store debug layer.

```text
/rag/chroma-search-debug
  ↓
debug_chroma_search()
  ↓
build_chroma_index()
  ↓
load_knowledge_chunks()
  ↓
get_embedding_provider()
  ↓
provider.embed_text(chunk)
  ↓
chromadb.PersistentClient(path="data/chroma")
  ↓
collection.upsert(ids, documents, metadatas, embeddings)
  ↓
query_chroma_store()
  ↓
provider.embed_text(query)
  ↓
collection.query(query_embeddings=[...])
  ↓
ranked Chroma results
  ↓
record_trace_event(event_type="rag_chroma_search_debug")
```

Current Chroma store file:

```text
src/app/rag/chroma_store.py
```

Current Chroma debug endpoint:

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

The Chroma debug layer reuses:

```text
Day21: load_knowledge_chunks()
Day30: get_embedding_provider()
Day30: DeterministicEmbeddingProvider
Day26: record_trace_event()
```

Current persistent directory:

```text
data/chroma
```

Returned index statistics:

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

Returned search result metadata:

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

The endpoint writes an observability event:

```text
event_type = rag_chroma_search_debug
```

Important implementation note:

```text
Day31 uses Chroma as a real persistent vector database, but still uses deterministic embeddings by default so pytest and GitHub Actions remain stable.
The observed Chroma collection name is truncated to satisfy Chroma's collection name length constraint, so the full embedding_dim is reliably preserved in request metadata, index_stats, and collection metadata rather than relying only on the visible collection name.
```

## Current Agentic RAG Retrieval Backend Switch

Day32 added a retrieval backend abstraction for Agentic RAG. Day35 extended it with a reranker-ready Chroma path.

```text
/rag/agentic-debug
  ↓
invoke_agentic_rag(retrieval_backend=...)
  ↓
retrieve_agentic_context()
  ├── hybrid        -> hybrid_search_knowledge()
  ├── chroma        -> debug_chroma_search()
  └── chroma_rerank -> debug_chroma_search() -> rerank_retrieval_results()
  ↓
normalized retrieval results
  ↓
relevance_grade
  ↓
answer_with_citations
  ↓
record_trace_event(event_type="rag_agentic_debug")
```

Current backend switch files:

```text
src/app/rag/retrieval_backend.py
src/app/rag/reranker.py
```

Supported backends:

```text
hybrid
chroma
chroma_rerank
```

The default backend remains `hybrid` for compatibility and CI stability.

`chroma_rerank` keeps Chroma as the first-stage retriever, then applies a deterministic lightweight reranker over the retrieved results.

Current reranker fields:

```text
original_rank
original_score
rerank_score
rerank_keyword_score
rerank_matched_terms
```

Observed Day35 LangGraph rerank behavior:

```text
Before rerank:
  chunk-2 had original_rank = 1 and original_score = 0.392506
  chunk-1 had original_rank = 2 and original_score = 0.387532

After rerank:
  chunk-1 becomes rank 1
  rerank_score = 0.571272
  rerank_matched_terms = ["langgraph"]
  citation = knowledge/agent_basics.md::chunk-1
```

Agentic RAG retrieval path with `chroma_rerank`:

```text
query_analyzer -> query_rewriter -> chroma_rerank_retrieve -> relevance_grade -> answer_with_citations
```

Important compatibility detail:

```text
The deterministic reranker is CI-safe.
It does not introduce model downloads, GPU requirements, external services, or flaky semantic embedding dependencies.
It creates a reranker-ready interface that can later be replaced by a cross-encoder reranker, BGE reranker, or LLM-based reranker.
```

## Current Reranker-ready Retrieval Extension

Day35 added a deterministic reranker layer.

Current reranker file:

```text
src/app/rag/reranker.py
```

Current reranker functions:

```text
extract_rerank_terms()
calculate_keyword_rerank_score()
rerank_retrieval_results()
```

Current reranker scoring:

```text
rerank_score = 0.7 * original_score + 0.3 * keyword_score
```

Current backend comparison result on the tiny deterministic eval set:

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

Current best backend summary:

```text
best_backend_by_pass_rate = hybrid
best_backend_by_average_relevance = chroma_rerank
```

The `best_backend_by_pass_rate` is `hybrid` because `hybrid` and `chroma_rerank` both reach `pass_rate = 1.0`, and the current comparison function returns the first max backend.

Important Day35 interpretation:

```text
chroma_rerank fixes the Day33/Day34 LangGraph case miss by promoting the LangGraph chunk back to rank 1.
The goal is not to prove a production reranker is better; the goal is to create a CI-safe reranker-ready retrieval architecture.
```

Example Agentic RAG request:

```bash
curl -s -X POST http://localhost:8000/rag/agentic-debug \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day35-agentic-chroma-rerank-001" \
  -d '{"query":"请搜索知识库：LangGraph 是什么？","top_k":2,"source_filter":"agent_basics","max_chars":300,"embedding_dim":64,"retrieval_backend":"chroma_rerank","embedding_provider":"deterministic","rebuild_index":true}' \
  | python -m json.tool --no-ensure-ascii
```

Expected fields:

```text
retrieval_backend = chroma_rerank
steps include chroma_rerank_retrieve
citations include knowledge/agent_basics.md::chunk-1
retrieval_results[0].rerank_score exists
retrieval_results[0].rerank_matched_terms contains langgraph
```

Example backend comparison request:

```bash
curl -s -X POST http://localhost:8000/rag/backend-eval-debug \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day35-backend-eval-rerank-001" \
  -d '{"backends":["hybrid","chroma","chroma_rerank"],"source_filter":"agent_basics","max_chars":300,"embedding_dim":64,"keyword_weight":0.6,"vector_weight":0.4,"embedding_provider":"deterministic","rebuild_index":true}' \
  | python -m json.tool --no-ensure-ascii
```

Note:

```text
Day35 keeps the existing `metric_deltas` behavior from Day34.
`metric_deltas` compares backend_results[0] against backend_results[1].
When passing ["hybrid", "chroma", "chroma_rerank"], the deltas still compare hybrid vs chroma.
Day36 can refine this into multi-backend pairwise deltas.
```

## Current Pairwise Backend Comparison Refinement

Day36 refined backend comparison from a two-backend delta to a multi-backend pairwise delta.

Current file:

```text
src/app/evaluation/rag_eval.py
```

Current helper functions:

```text
_calculate_metric_delta()
_build_metric_deltas()
_build_pairwise_metric_deltas()
```

Current endpoint:

```text
POST /rag/backend-eval-debug
```

New response field:

```text
pairwise_metric_deltas
```

Backward-compatible response field:

```text
metric_deltas
```

Design:

```text
metric_deltas:
  backend_results[0] -> backend_results[1]

pairwise_metric_deltas:
  all ordered pairs where comparison appears after baseline in the requested backend list
```

For this request:

```text
["hybrid", "chroma", "chroma_rerank"]
```

the pairwise comparisons are:

```text
hybrid -> chroma
hybrid -> chroma_rerank
chroma -> chroma_rerank
```

Observed Day36 pairwise output count:

```text
pairwise_count = 3
```

Observed trace event:

```text
event_type = rag_backend_eval_debug
payload.pairwise_metric_deltas length = 3
payload.backend_metrics includes hybrid, chroma, and chroma_rerank
```

New Day36 test file:

```text
tests/test_rag_backend_pairwise_eval.py
```

## Current Multi-backend Comparison Summary Refinement

Day37 refined `comparison_summary` so it is multi-backend-aware.

Current file:

```text
src/app/evaluation/rag_eval.py
```

Current helper functions:

```text
_build_metric_rankings()
_build_metric_winners()
_build_top_improvement_pairs()
_build_multi_backend_summary_notes()
_build_comparison_summary()
```

Current endpoint:

```text
POST /rag/backend-eval-debug
```

The response still includes:

```text
metric_deltas
pairwise_metric_deltas
case_comparisons
comparison_summary
```

The refined `comparison_summary` now includes:

```text
evaluated_backends
metric_winners
metric_rankings
top_improvement_pairs
notes
```

Observed Day37 summary keys:

```text
best_backend_by_average_relevance
best_backend_by_pass_rate
evaluated_backends
metric_rankings
metric_winners
notes
top_improvement_pairs
total_backends
```

Observed key summary result:

```text
evaluated_backends = hybrid, chroma, chroma_rerank
best_backend_by_pass_rate = hybrid
best_backend_by_average_relevance = chroma_rerank
pass_rate is tied by hybrid and chroma_rerank
average_relevance_score winner is chroma_rerank
```

Observed summary notes:

```text
Evaluated 3 backends: hybrid, chroma, chroma_rerank.
Pass rate is tied at 1.0 by hybrid, chroma_rerank.
Best average_relevance_score is chroma_rerank with value 0.394302.
Largest pass_rate improvement is chroma -> chroma_rerank with delta 0.333333.
Largest average_relevance_score improvement is hybrid -> chroma_rerank with delta 0.116079.
```

New Day37 test file:

```text
tests/test_rag_backend_comparison_summary.py
```

## Current Semantic Embedding Local Validation Architecture

Day38 validated the reserved `sentence_transformers` embedding provider locally while preserving the deterministic embedding provider as the default CI-safe path.

```text
scripts/validate_semantic_embedding_provider.py
  ↓
get_embedding_provider(provider="sentence_transformers", embedding_model="/mnt/f/LLM/maidalun/bce-embedding-base_v1")
  ↓
SentenceTransformersEmbeddingProvider(model_name=local_model_path)
  ↓
provider.embed_text(...)
  ↓
/rag/embedding-debug
/rag/chroma-search-debug
/rag/agentic-debug
/rag/backend-eval-debug
```

Current local semantic model:

```text
/mnt/f/LLM/maidalun/bce-embedding-base_v1
```

Current local semantic embedding dimension:

```text
768
```

Day38 validated these paths:

```text
Python direct semantic provider validation
/rag/embedding-debug with provider="sentence_transformers"
/rag/chroma-search-debug with embedding_provider="sentence_transformers"
/rag/agentic-debug with retrieval_backend="chroma" and semantic embeddings
/rag/backend-eval-debug comparing hybrid, chroma, and chroma_rerank with semantic embeddings
/observability/traces/{trace_id} for rag_embedding_debug and rag_backend_eval_debug
```

Observed Day38 semantic backend comparison with the local BCE embedding model:

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

Observed Day38 summary:

```text
best_backend_by_pass_rate = hybrid
best_backend_by_average_relevance = chroma_rerank
pass_rate is tied by hybrid, chroma, and chroma_rerank
average_relevance_score winner is chroma_rerank
```

Important compatibility behavior:

```text
The deterministic provider remains the default for CI.
The sentence_transformers provider is validated locally through a script and a CI-safe skip test.
CI skips the semantic provider test when the local model path is unavailable.
No model download, GPU dependency, or Hugging Face network access is required in CI.
```

Day38 also fixed the embedding model parameter boundary:

```text
API/request level and store functions:
  embedding_model

get_embedding_provider():
  embedding_model

SentenceTransformersEmbeddingProvider.__init__():
  model_name
```

## Current Backend Evaluation Report Architecture

Day39 added a backend evaluation report layer on top of the existing backend comparison output and aligned that report with the observability trace payload. Day40 extended the report with failure analysis and selection-policy evaluation based on the 12-case extended eval set.

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
  ↓
response payload + rag_backend_eval_debug trace payload
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
evaluation_report.selection_policy_evaluation
evaluation_report.embedding_provider
evaluation_report.embedding_model
evaluation_report.eval_file
evaluation_report.eval_case_count
evaluation_report.metric_highlights
evaluation_report.risk_notes
evaluation_report.failure_analysis
evaluation_report.backend_rank_summary
evaluation_report.interpretation
```

The `rag_backend_eval_debug` trace payload records the same report-level decision fields:

```text
payload.evaluation_report.recommended_backend
payload.evaluation_report.default_backend_should_change
payload.evaluation_report.risk_notes
payload.evaluation_report.backend_rank_summary
payload.evaluation_report.failure_analysis
payload.evaluation_report.selection_policy_evaluation
```

Current conservative selection policy:

```text
policy_name = pass_rate_first_relevance_tiebreak_conservative

A candidate backend must:
  1. be in the top pass-rate group
  2. have strong relevance-score evidence
  3. be evaluated on a non-tiny eval set
  4. pass semantic embedding validation before production switching
  5. have common failed cases reviewed before production switching
```

Observed Day40 deterministic evaluation report:

```text
recommended_backend = chroma_rerank
default_backend = hybrid
default_backend_should_change = false
selection_policy = keep_default_hybrid_until_semantic_eval
embedding_provider = deterministic
eval_case_count = 12
```

Observed Day40 backend ranking:

```text
chroma_rerank:
  pass_rate = 0.833333
  average_relevance_score = 0.529049
  passed_cases = 10 / 12
  strength = recommended candidate on current evaluation

hybrid:
  pass_rate = 0.833333
  average_relevance_score = 0.407461
  passed_cases = 10 / 12
  strength = top pass-rate group

chroma:
  pass_rate = 0.75
  average_relevance_score = 0.412151
  passed_cases = 9 / 12
  strength = comparison backend
```

Observed Day40 failure analysis:

```text
common_failed_cases = agent_definition, agent_graph_flow
unique_failed_cases_by_backend.chroma = langgraph_definition
failure_count_by_backend.hybrid = 2
failure_count_by_backend.chroma = 3
failure_count_by_backend.chroma_rerank = 2
```

Observed Day40 trace alignment:

```text
trace_id = day40-extended-analysis-manual-001
event_type = rag_backend_eval_debug
payload.evaluation_report.failure_analysis exists
payload.evaluation_report.selection_policy_evaluation exists
payload.evaluation_report.default_backend_should_change = false
```

Important Day40 interpretation:

```text
chroma_rerank is recommended as an experiment candidate because it ties hybrid on pass_rate and wins average_relevance_score.
The default backend should remain hybrid because the current run uses deterministic embeddings and still has common failed cases across all evaluated backends.
The recommendation is visible both in the API response and in the observability trace payload.
```

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
  "total_chunks": 3,
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
"total_chunks": 3
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
"total_chunks": 3
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
total_indexed_chunks = 3
index_stats.loaded_chunks = 3
index_stats.inserted_count = 3
index_stats.stored_count = 3
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
payload.total_indexed_chunks = 3
payload.results_count = 2
payload.index_stats.inserted_count = 3
payload.index_stats.stored_count = 3
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
total_indexed_chunks = 3
index_stats.loaded_chunks = 3
index_stats.inserted_count = 3
index_stats.stored_count = 3
results_count = 2
trace_id = day29-vector-store-rag-001
```

### RAG Embedding Debug

`/rag/embedding-debug` exposes embedding provider behavior for a query and optional document list.

```bash
curl -s -X POST http://localhost:8000/rag/embedding-debug \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day30-embedding-debug-001" \
  -d '{"query":"LangGraph 是什么？","documents":["LangGraph 是一个适合构建 Agent 工作流的框架。","RAG 是 Retrieval-Augmented Generation。"],"provider":"deterministic","embedding_dim":64}' \
  | python -m json.tool --no-ensure-ascii
```

Expected response fields:

```text
provider = deterministic
model = deterministic-hash
requested_embedding_dim = 64
actual_embedding_dim = 64
query_embedding_norm = 1.0
documents_count = 2
documents[*].embedding_dim = 64
documents[*].embedding_norm = 1.0
trace_id = day30-embedding-debug-001
```

Trace lookup:

```bash
curl -s http://localhost:8000/observability/traces/day30-embedding-debug-001 \
  | python -m json.tool --no-ensure-ascii
```

Expected trace fields:

```text
event_type = rag_embedding_debug
payload.provider = deterministic
payload.model = deterministic-hash
payload.actual_embedding_dim = 64
payload.documents_count = 2
```

### Provider-aware RAG Vector Store Debug

Day30 upgrades `/rag/vector-store-debug` with embedding provider metadata.

```bash
curl -s -X POST http://localhost:8000/rag/vector-store-debug \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day30-vector-store-provider-001" \
  -d '{"query":"LangGraph 是什么？","top_k":2,"source_filter":"agent_basics","max_chars":300,"embedding_dim":64,"embedding_provider":"deterministic","rebuild_index":true}' \
  | python -m json.tool --no-ensure-ascii
```

Expected response fields:

```text
embedding_provider = deterministic
embedding_model = deterministic-hash
index_key includes embedding_provider and embedding_model
total_indexed_chunks = 3
index_stats.embedding_provider = deterministic
index_stats.embedding_model = deterministic-hash
index_stats.loaded_chunks = 3
index_stats.inserted_count = 3
index_stats.stored_count = 3
```

### RAG Chroma Search Debug

`/rag/chroma-search-debug` builds a Chroma persistent vector index and queries it with provider-generated query embeddings.

```bash
curl -s -X POST http://localhost:8000/rag/chroma-search-debug \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day31-chroma-langgraph-001" \
  -d '{"query":"LangGraph 是什么？","top_k":2,"source_filter":"agent_basics","max_chars":300,"embedding_dim":64,"embedding_provider":"deterministic","rebuild_index":true}' \
  | python -m json.tool --no-ensure-ascii
```

Expected response fields:

```text
query = LangGraph 是什么？
top_k = 2
source_filter = agent_basics
embedding_provider = deterministic
embedding_model = deterministic-hash
persist_dir = data/chroma
total_indexed_chunks = 3
index_stats.loaded_chunks = 3
index_stats.upserted_count = 3
index_stats.stored_count = 3
results_count = 2
trace_id = day31-chroma-langgraph-001
```

Trace lookup:

```bash
curl -s http://localhost:8000/observability/traces/day31-chroma-langgraph-001 \
  | python -m json.tool --no-ensure-ascii
```

Expected trace fields:

```text
event_type = rag_chroma_search_debug
payload.total_indexed_chunks = 3
payload.results_count = 2
payload.index_stats.stored_count = 3
payload.embedding_provider = deterministic
payload.embedding_model = deterministic-hash
```

RAG query:

```bash
curl -s -X POST http://localhost:8000/rag/chroma-search-debug \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day31-chroma-rag-001" \
  -d '{"query":"RAG 是什么？","top_k":2,"source_filter":"agent_basics","max_chars":300,"embedding_dim":64,"embedding_provider":"deterministic","rebuild_index":true}' \
  | python -m json.tool --no-ensure-ascii
```

Expected response fields:

```text
total_indexed_chunks = 3
index_stats.loaded_chunks = 3
index_stats.upserted_count = 3
index_stats.stored_count = 3
results_count = 2
distance >= 0
score > 0
trace_id = day31-chroma-rag-001
```

### Agentic RAG Backend Switch

Day32 lets `/rag/agentic-debug` use either the existing hybrid backend or the Chroma backend.

Hybrid backend:

```bash
curl -s -X POST http://localhost:8000/rag/agentic-debug \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day32-agentic-hybrid-001" \
  -d '{"query":"请搜索知识库：LangGraph 是什么？","top_k":2,"source_filter":"agent_basics","max_chars":300,"embedding_dim":64,"keyword_weight":0.6,"vector_weight":0.4,"retrieval_backend":"hybrid"}' \
  | python -m json.tool --no-ensure-ascii
```

Expected hybrid fields:

```text
retrieval_backend = hybrid
steps = query_analyzer -> query_rewriter -> hybrid_retrieve -> relevance_grade -> answer_with_citations
retrieval_metadata.retrieval_backend = hybrid
retrieval_metadata.total_chunks = 3
citations include knowledge/agent_basics.md::chunk-1
```

Chroma backend:

```bash
curl -s -X POST http://localhost:8000/rag/agentic-debug \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day32-agentic-chroma-001" \
  -d '{"query":"请搜索知识库：RAG 是什么？","top_k":2,"source_filter":"agent_basics","max_chars":300,"embedding_dim":64,"retrieval_backend":"chroma","embedding_provider":"deterministic","rebuild_index":true}' \
  | python -m json.tool --no-ensure-ascii
```

Expected Chroma fields:

```text
retrieval_backend = chroma
steps = query_analyzer -> query_rewriter -> chroma_retrieve -> relevance_grade -> answer_with_citations
retrieval_metadata.retrieval_backend = chroma
retrieval_metadata.total_indexed_chunks = 3
retrieval_metadata.collection_name exists
citations include knowledge/agent_basics.md::chunk-2
```

Trace lookup:

```bash
curl -s http://localhost:8000/observability/traces/day32-agentic-chroma-001 \
  | python -m json.tool --no-ensure-ascii
```

If the same trace id was reused during debugging, multiple events may appear. The latest event should contain the corrected citations and the non-duplicated step list.

### RAG Backend Evaluation Debug

Day33 adds backend-aware RAG evaluation.

Hybrid `/rag/eval-debug`:

```bash
curl -s -X POST http://localhost:8000/rag/eval-debug \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day33-eval-hybrid-001" \
  -d '{"source_filter":"agent_basics","max_chars":300,"embedding_dim":64,"keyword_weight":0.6,"vector_weight":0.4,"retrieval_backend":"hybrid"}' \
  | python -m json.tool --no-ensure-ascii
```

Expected hybrid metrics:

```text
pass_rate = 1.0
retrieval_decision_accuracy = 1.0
expected_terms_hit_rate = 1.0
citation_hit_rate = 1.0
average_relevance_score = 0.278223
```

Chroma `/rag/eval-debug`:

```bash
curl -s -X POST http://localhost:8000/rag/eval-debug \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day33-eval-chroma-001" \
  -d '{"source_filter":"agent_basics","max_chars":300,"embedding_dim":64,"retrieval_backend":"chroma","embedding_provider":"deterministic","rebuild_index":true}' \
  | python -m json.tool --no-ensure-ascii
```

Expected Chroma metrics:

```text
pass_rate = 0.666667
retrieval_decision_accuracy = 1.0
expected_terms_hit_rate = 0.666667
citation_hit_rate = 1.0
average_relevance_score = 0.279233
```

Backend comparison:

```bash
curl -s -X POST http://localhost:8000/rag/backend-eval-debug \
  -H "Content-Type: application/json" \
  -H "x-trace-id: day33-backend-eval-001" \
  -d '{"backends":["hybrid","chroma"],"source_filter":"agent_basics","max_chars":300,"embedding_dim":64,"keyword_weight":0.6,"vector_weight":0.4,"embedding_provider":"deterministic","rebuild_index":true}' \
  | python -m json.tool --no-ensure-ascii
```

Expected comparison fields:

```text
backends = ["hybrid", "chroma"]
best_backend_by_pass_rate = hybrid
best_backend_by_average_relevance = chroma
results[0].retrieval_backend = hybrid
results[1].retrieval_backend = chroma
trace_id = day33-backend-eval-001
```

## Tests

Run tests:

```bash
pytest -q
```

Current result:

```text
97 passed, 1 warning
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
* Chroma collection name short hash and dimension behavior
* `retrieve_agentic_context()` hybrid backend behavior
* `retrieve_agentic_context()` Chroma backend behavior
* `invoke_agentic_rag()` with `retrieval_backend="chroma"`
* `/rag/agentic-debug` Chroma backend response and trace event

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
├── test_rag_embedding_provider.py
├── test_rag_chroma_store.py
├── test_rag_agentic_backend.py
├── test_rag_backend_eval.py
├── test_router_agent.py
├── test_router_delegation.py
├── test_router_stream.py
├── test_llm_router.py
├── test_smart_chat.py
├── test_smart_stream.py
├── test_route_validation.py
└── test_rag_chunks.py
```

Ollama provider, real LLM tool calling, `/agent/llm-stream`, `/agent/llm-router-chat` with `router_provider="ollama"`, `/agent/smart-chat` with `router_provider="ollama"`, and `/agent/smart-stream` with `router_provider="ollama"` are manually tested locally and are not covered by CI, because CI should not depend on a local Ollama service. The deterministic `/agent/stream`, `/rag/search`, `/rag/search-debug`, `/rag/chunks-debug`, `/rag/vector-search-debug`, `/rag/hybrid-search-debug`, `/rag/agentic-debug`, deterministic RAG tool path, Router Agent path, Router delegation memory path, Router stream path, `/agent/llm-router-chat` mock path, `/agent/smart-chat` deterministic/mock paths, `/agent/smart-stream` deterministic/mock paths, route validation paths, chunk pipeline paths, deterministic vector-search paths, hybrid retrieval paths, and Agentic RAG debug paths are covered by local pytest. Day38 semantic embedding validation is covered by a local test that skips in CI when the local BCE model path is unavailable. CI status should be confirmed from GitHub Actions.

## Current Day49 GraphRAG Observability and Answer Verification

Day49 adds GraphRAG-aware observability and answer verification hardening for the explicit `retrieval_backend="graph_fusion"` path.

Current Day49 files:

```text
src/app/rag/graph_fusion_metadata.py
src/app/rag/answer_verifier.py
src/app/rag/agentic_graph.py
src/app/evaluation/rag_eval.py
src/app/routes/routes_rag.py
src/app/schemas/rag.py
tests/test_rag_graph_fusion_observability.py
tests/test_rag_answer_verify_graph_fusion.py
```

New metadata helper:

```text
build_graph_vector_contribution()
build_graph_fusion_trace_payload()
```

Current GraphRAG-aware trace payloads preserve:

```text
retrieval_backend
retrieval_metadata
graph_vector_contribution
graph_fusion_verification
verification
```

`/rag/answer-verify-debug` now supports:

```text
retrieval_backend="graph_fusion"
graph_dry_run=true   # CI-safe default
graph_dry_run=false  # manual live Neo4j-backed validation
```

Dry-run answer verification preserves vector-only fused evidence:

```text
graph_status = dry_run
vector_result_count = 2
fusion_result_count = 2
vector_only_count = 2
graph_and_vector_count = 0
verification_pass = true
```

Live Neo4j-backed answer verification preserves graph + vector evidence:

```text
graph_status = retrieved
graph_ok = true
graph_chunk_count = 2
vector_result_count = 2
fusion_result_count = 2
graph_and_vector_count = 2
verification_pass = true
confidence = high
```

Day49 keeps the production default unchanged:

```text
Default retrieval_backend = hybrid
Explicit GraphRAG path = graph_fusion
```


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
Day52 local pytest passed: 167 passed, 1 warning.
Day52 Git commit: c07bd45 add multi agent state debug.
Day52 Git push succeeded.
GitHub Actions CI: green.
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

* Day53: Planner Agent
* Day54-Day63: Continue Complex Multi-Agent Workflow
* Day64-Day66: Final review, README / HANDOFF refactor, and resume / interview material cleanup

Deferred:

* Production retrieval backend selection-policy implementation and config hardening
* Document upload and parsing pipeline
* MCP integration layer, if needed after GraphRAG / Multi-Agent
