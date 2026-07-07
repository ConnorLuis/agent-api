# GraphRAG Architecture

This document describes the GraphRAG implementation in `agent-api`.

The current GraphRAG stack was implemented from Day42 to Day50:

```text
Day42: GraphRAG + Neo4j environment and schema
Day43: Deterministic Entity / Relation extraction
Day44: Neo4j graph ingestion
Day45: Neo4j graph retrieval
Day46: GraphRAG + VectorRAG fusion
Day47: Agentic RAG connection through retrieval_backend="graph_fusion"
Day48: GraphRAG evaluation
Day49: GraphRAG observability and answer verification metadata
Day50: GraphRAG architecture documentation
```

The implementation is intentionally incremental. Each stage has a debug boundary so the system can be tested, observed, and manually validated without making GraphRAG the default retrieval backend too early.

---

## 1. Design Goals

GraphRAG in this project has four main goals:

```text
1. Represent documents, chunks, entities, and relationships in Neo4j.
2. Retrieve evidence through graph structure instead of relying only on vector similarity.
3. Fuse graph retrieval and VectorRAG retrieval into one Agentic RAG backend.
4. Preserve evaluation, observability, and verification metadata for debugging and interview explanation.
```

The explicit GraphRAG-capable backend name is:

```text
retrieval_backend = graph_fusion
```

The default Agentic RAG backend remains:

```text
retrieval_backend = hybrid
```

GraphRAG is available as an explicit opt-in backend, but it is not the default production path yet.

---

## 2. High-level Architecture

```text
Markdown knowledge base
  ↓
RAG chunk pipeline
  ↓
Entity / Relation extraction
  ↓
Neo4j ingestion
  ↓
Graph retrieval
  ↓
GraphRAG + VectorRAG fusion
  ↓
Agentic RAG backend: graph_fusion
  ↓
Evaluation / observability / answer verification
```

Main implementation modules:

```text
src/app/graph/schema.py
src/app/graph/neo4j_client.py
src/app/graph/extraction.py
src/app/graph/ingestion.py
src/app/graph/retrieval.py
src/app/graph/fusion.py
src/app/rag/retrieval_backend.py
src/app/rag/agentic_graph.py
src/app/rag/graph_fusion_metadata.py
src/app/rag/answer_verifier.py
src/app/evaluation/rag_eval.py
src/app/routes/routes_graph.py
src/app/routes/routes_rag.py
src/app/schemas/graph.py
src/app/schemas/rag.py
```

---

## 3. Graph Schema

Current schema version:

```text
day42_graph_schema_v1
```

Node labels:

```text
Document
Chunk
Entity
```

Relationship types:

```text
HAS_CHUNK
NEXT_CHUNK
MENTIONS
RELATED_TO
```

Graph shape:

```text
(Document)-[:HAS_CHUNK]->(Chunk)
(Chunk)-[:NEXT_CHUNK]->(Chunk)
(Chunk)-[:MENTIONS]->(Entity)
(Entity)-[:RELATED_TO]->(Entity)
```

### 3.1 Document

A `Document` represents one source document from the local knowledge base.

Important fields:

```text
document_id
source
title
```

Current source example:

```text
knowledge/agent_basics.md
```

### 3.2 Chunk

A `Chunk` represents a split text segment from a document.

Important fields:

```text
chunk_id
source
index
content
preview
content_length
```

Example chunk id:

```text
knowledge/agent_basics.md::chunk-1
```

### 3.3 Entity

An `Entity` represents a deterministic concept or framework extracted from chunks.

Important fields:

```text
entity_id
name
normalized_name
type
aliases
```

Current seed entities over `agent_basics`:

```text
Agent
RAG
LangGraph
Tool
Memory
```

Current entity ids:

```text
Entity:concept:agent
Entity:concept:rag
Entity:framework:langgraph
Entity:concept:tool
Entity:concept:memory
```

---

## 4. Neo4j Configuration

Neo4j settings:

```text
NEO4J_ENABLED
NEO4J_URI
NEO4J_USERNAME
NEO4J_PASSWORD
NEO4J_DATABASE
```

Default values:

```text
NEO4J_ENABLED=false
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password
NEO4J_DATABASE=neo4j
```

The default behavior is CI-safe. Endpoints do not require a live Neo4j server unless a live check or live graph execution is explicitly requested.

Manual health check:

```bash
curl -s "http://localhost:8000/graph/health-debug?check_connection=true" \
  -H "x-trace-id: graphrag-health-manual-001" \
  | python -m json.tool --no-ensure-ascii
```

Expected live connection status:

```text
connection.ok = true
connection.status = connected
```

---

## 5. Endpoint Flow

### 5.1 Schema Debug

```text
GET /graph/schema-debug
```

Purpose:

```text
Return the current GraphRAG schema metadata.
```

This endpoint is fully CI-safe.

### 5.2 Health Debug

```text
GET /graph/health-debug
GET /graph/health-debug?check_connection=true
```

Default behavior:

```text
check_connection=false
```

This does not connect to Neo4j.

Manual live behavior:

```text
check_connection=true
```

This attempts a real Neo4j connection.

### 5.3 Extraction Debug

```text
POST /graph/extract-debug
```

Request example:

```json
{
  "source_filter": "agent_basics",
  "max_chars": 300,
  "include_related_entities": true
}
```

Pipeline:

```text
/graph/extract-debug
  ↓
extract_graph_items()
  ↓
load_knowledge_chunks()
  ↓
extract_entities_from_chunks()
  ↓
extract_relations_from_chunks()
  ↓
documents / chunks / entities / relations
```

Extraction is deterministic and does not write to Neo4j.

Current relation construction:

```text
HAS_CHUNK:
  Document -> Chunk

NEXT_CHUNK:
  Chunk -> next Chunk in same document

MENTIONS:
  Chunk -> Entity

RELATED_TO:
  Entity -> Entity when two entities co-occur in the same chunk
```

Observed seed extraction over `agent_basics`:

```text
documents = 1
chunks = 3
entities = 5
relations = 29
```

Relation counts with `include_related_entities=true`:

```text
HAS_CHUNK = 3
NEXT_CHUNK = 2
MENTIONS = 10
RELATED_TO = 14
```

### 5.4 Ingestion Debug

```text
POST /graph/ingest-debug
```

Dry-run request:

```json
{
  "source_filter": "agent_basics",
  "max_chars": 300,
  "include_related_entities": true,
  "dry_run": true,
  "apply_schema": true
}
```

Live request:

```json
{
  "source_filter": "agent_basics",
  "max_chars": 300,
  "include_related_entities": true,
  "dry_run": false,
  "apply_schema": true
}
```

Pipeline:

```text
/graph/ingest-debug
  ↓
run_graph_ingestion_debug()
  ↓
extract_graph_items()
  ↓
build_graph_ingestion_plan()
  ├── dry_run=true  -> return plan only
  └── dry_run=false -> execute_graph_ingestion()
```

Schema statements:

```text
CREATE CONSTRAINT document_source_unique IF NOT EXISTS
CREATE CONSTRAINT chunk_id_unique IF NOT EXISTS
CREATE CONSTRAINT entity_identity_unique IF NOT EXISTS
CREATE INDEX chunk_source_index IF NOT EXISTS
CREATE INDEX entity_name_index IF NOT EXISTS
CREATE INDEX entity_type_index IF NOT EXISTS
```

Live seed graph after ingestion:

```text
Document = 1
Chunk = 3
Entity = 5

HAS_CHUNK = 3
NEXT_CHUNK = 2
MENTIONS = 10
RELATED_TO = 10
```

Important note:

```text
Extraction produces 14 RELATED_TO records.
Neo4j stores 10 RELATED_TO relationships because the current MERGE key is the entity pair.
Repeated co-occurrences of the same entity pair collapse into one relationship.
```

This is acceptable for the current seed graph. If future work needs evidence-level relationships, add evidence metadata or a separate evidence relationship model.

### 5.5 Retrieval Debug

```text
POST /graph/retrieval-debug
```

Dry-run request:

```json
{
  "query": "RAG 和 LangGraph 有什么关系？",
  "source_filter": "agent_basics",
  "chunk_limit": 5,
  "related_entity_limit": 10,
  "dry_run": true
}
```

Live request:

```json
{
  "query": "RAG 和 LangGraph 有什么关系？",
  "source_filter": "agent_basics",
  "chunk_limit": 5,
  "related_entity_limit": 10,
  "dry_run": false
}
```

Pipeline:

```text
/graph/retrieval-debug
  ↓
run_graph_retrieval_debug()
  ↓
extract_query_entity_matches()
  ↓
build_graph_retrieval_plan()
  ├── dry_run=true  -> return plan only
  └── dry_run=false -> execute_graph_retrieval()
```

Query entity matching:

```text
User query
  ↓
EntityPattern aliases
  ↓
query_entity_matches
  ↓
matched_entity_ids
```

Cypher groups:

```text
matched_entities:
  MATCH (e:Entity)
  WHERE e.entity_id IN $entity_ids

mentioned_chunks:
  MATCH (chunk:Chunk)-[m:MENTIONS]->(e:Entity)
  WHERE e.entity_id IN $entity_ids
  OPTIONAL MATCH (doc:Document)-[:HAS_CHUNK]->(chunk)

related_entities:
  MATCH (e:Entity)-[r:RELATED_TO]-(related:Entity)
  WHERE e.entity_id IN $entity_ids
```

Observed live retrieval:

```text
query = RAG 和 LangGraph 有什么关系？
matched_entities = 2
chunks = 2
related_entities = 8
```

Chinese alias retrieval is supported:

```text
query = 智能体如何使用工具和短期记忆？

matched aliases:
  智能体 -> Agent
  工具 -> Tool
  短期记忆 -> Memory
```

### 5.6 Fusion Debug

```text
POST /graph/fusion-debug
```

Request:

```json
{
  "query": "RAG 和 LangGraph 有什么关系？",
  "top_k": 3,
  "source_filter": "agent_basics",
  "max_chars": 300,
  "embedding_dim": 64,
  "hybrid_keyword_weight": 0.6,
  "hybrid_vector_weight": 0.4,
  "fusion_graph_weight": 0.5,
  "fusion_vector_weight": 0.5,
  "graph_chunk_limit": 5,
  "related_entity_limit": 10,
  "graph_dry_run": true
}
```

Pipeline:

```text
/graph/fusion-debug
  ↓
run_graph_vector_fusion_debug()
  ↓
graph side:
  run_graph_retrieval_debug()
  ↓
vector side:
  hybrid_search_knowledge()
  ↓
fuse_graph_and_vector_results()
  ↓
chunk_id union + weighted score
```

Fusion formula:

```text
fusion_score = fusion_graph_weight * graph_score + fusion_vector_weight * vector_score
```

Default weights:

```text
fusion_graph_weight = 0.5
fusion_vector_weight = 0.5
```

Fusion result metadata:

```text
rank
chunk_id
source
index
content
preview
content_length
fusion_score
graph_score
vector_score
retrieval_sources
matched_entities
mentions
graph_metadata
vector_metadata
```

Retrieval source categories:

```text
graph
vector
graph + vector
```

Dry-run behavior:

```text
graph_dry_run=true
graph_retrieval.status = dry_run
graph_only = 0
graph_and_vector = 0
vector_only >= 1
```

Live behavior:

```text
graph_dry_run=false
graph_retrieval.status = retrieved
graph_and_vector >= 1 when graph and vector retrieve overlapping chunks
```

---

## 6. Agentic RAG Integration

GraphRAG is integrated into Agentic RAG through an explicit retrieval backend:

```text
retrieval_backend = graph_fusion
```

Endpoint:

```text
POST /rag/agentic-debug
```

Request:

```json
{
  "query": "RAG 和 LangGraph 有什么关系？",
  "top_k": 2,
  "source_filter": "agent_basics",
  "max_chars": 300,
  "embedding_dim": 64,
  "retrieval_backend": "graph_fusion",
  "graph_dry_run": true
}
```

Agentic RAG graph_fusion path:

```text
query_analyzer
  ↓
query_rewriter
  ↓
graph_fusion_retrieve
  ↓
relevance_grade
  ↓
answer_with_citations
```

Implementation flow:

```text
/rag/agentic-debug
  ↓
invoke_agentic_rag(retrieval_backend="graph_fusion")
  ↓
retrieve_agentic_context()
  ↓
run_graph_vector_fusion_debug()
  ↓
_normalize_graph_fusion_results()
  ↓
Agentic RAG retrieval_results
```

The default Agentic RAG path still uses:

```text
retrieval_backend = hybrid
```

Default path:

```text
query_analyzer
  ↓
query_rewriter
  ↓
hybrid_retrieve
  ↓
relevance_grade
  ↓
answer_with_citations
```

---

## 7. Evaluation

GraphRAG evaluation was added in Day48.

Endpoints:

```text
POST /rag/eval-debug
POST /rag/backend-eval-debug
```

Single-backend evaluation with graph_fusion:

```json
{
  "eval_file": "eval_cases/rag_agentic_eval.jsonl",
  "source_filter": "agent_basics",
  "max_chars": 300,
  "embedding_dim": 64,
  "keyword_weight": 0.6,
  "vector_weight": 0.4,
  "retrieval_backend": "graph_fusion",
  "embedding_provider": "deterministic",
  "rebuild_index": true,
  "graph_dry_run": true
}
```

Four-backend comparison:

```json
{
  "eval_file": "eval_cases/rag_agentic_eval.jsonl",
  "backends": [
    "hybrid",
    "chroma",
    "chroma_rerank",
    "graph_fusion"
  ],
  "source_filter": "agent_basics",
  "max_chars": 300,
  "embedding_dim": 64,
  "keyword_weight": 0.6,
  "vector_weight": 0.4,
  "embedding_provider": "deterministic",
  "rebuild_index": true,
  "graph_dry_run": true
}
```

GraphRAG evaluation metadata:

```text
graph_evaluation_metadata
cases[*].graph_vector_contribution
```

`graph_vector_contribution` fields:

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

Dry-run evaluation is CI-safe:

```text
graph_dry_run = true
graph_retrieval.status = dry_run
vector_result_count >= 1
fusion_result_count >= 1
```

Live evaluation validates the real Neo4j path:

```text
graph_dry_run = false
graph_retrieval.status = retrieved
graph_ok = true
graph_and_vector_count >= 1
```

Default backend switch policy:

```text
evaluation_report.default_backend = hybrid
evaluation_report.default_backend_should_change = false
```

GraphRAG can be recommended by evaluation, but it is not automatically made the default backend.

---

## 8. Observability

GraphRAG observability was hardened in Day49.

Important trace event types:

```text
rag_agentic_debug
rag_eval_debug
rag_backend_eval_debug
rag_answer_verify_debug
```

GraphRAG-aware trace payload fields:

```text
retrieval_backend
retrieval_metadata
graph_vector_contribution
graph_evaluation_metadata
graph_fusion_verification
```

For `retrieval_backend="graph_fusion"`, `retrieval_metadata` includes:

```text
retrieval_backend
graph_dry_run
fusion_graph_weight
fusion_vector_weight
graph_chunk_limit
related_entity_limit
query_entity_matches
graph_retrieval
vector_retrieval
fusion
```

Trace lookup:

```bash
curl -s http://localhost:8000/observability/traces/<trace_id> \
  | python -m json.tool --no-ensure-ascii
```

Expected GraphRAG trace behavior:

```text
/rag/agentic-debug:
  payload.retrieval_backend = graph_fusion
  payload.retrieval_metadata.graph_dry_run = true / false
  payload.graph_vector_contribution exists

/rag/eval-debug:
  payload.graph_evaluation_metadata.graph_fusion_enabled = true
  payload.cases[*].graph_vector_contribution exists

/rag/backend-eval-debug:
  payload.graph_evaluation_metadata.graph_fusion_included = true
  graph_fusion result cases preserve graph_vector_contribution

/rag/answer-verify-debug:
  payload.graph_vector_contribution exists
  payload.graph_fusion_verification exists
```

---

## 9. Answer Verification

GraphRAG answer verification was extended in Day49.

Endpoint:

```text
POST /rag/answer-verify-debug
```

Request:

```json
{
  "query": "请搜索知识库：RAG 是什么？",
  "top_k": 2,
  "source_filter": "agent_basics",
  "max_chars": 300,
  "embedding_dim": 64,
  "keyword_weight": 0.6,
  "vector_weight": 0.4,
  "retrieval_backend": "graph_fusion",
  "embedding_provider": "deterministic",
  "rebuild_index": true,
  "graph_dry_run": true
}
```

Verification response includes the original Day28 verification fields:

```text
verification
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

GraphRAG-specific verification fields:

```text
retrieval_backend
retrieval_metadata
graph_vector_contribution
graph_fusion_verification
```

`graph_fusion_verification` fields:

```text
retrieval_backend
graph_metadata_present
graph_or_vector_evidence_present
graph_and_vector_evidence_present
graph_dry_run
graph_status
graph_ok
query_entity_match_count
graph_chunk_count
vector_result_count
fusion_result_count
```

Dry-run GraphRAG verification behavior:

```text
graph_dry_run = true
graph_status = dry_run
graph_or_vector_evidence_present = true
graph_and_vector_evidence_present = false
verification_pass = true
```

Live GraphRAG verification behavior:

```text
graph_dry_run = false
graph_status = retrieved
graph_ok = true
graph_and_vector_evidence_present = true when graph and vector overlap
verification_pass = true
```

Day49 does not make verification fail simply because graph retrieval is dry-run. Dry-run mode is a CI-safe contract test, not a real graph-quality test.

---

## 10. CI Safety

The GraphRAG implementation is designed to avoid live Neo4j dependency in CI.

CI-safe defaults:

```text
/graph/health-debug:
  check_connection = false

/graph/ingest-debug:
  dry_run = true

/graph/retrieval-debug:
  dry_run = true

/graph/fusion-debug:
  graph_dry_run = true

/rag/agentic-debug with graph_fusion:
  graph_dry_run = true

/rag/eval-debug with graph_fusion:
  graph_dry_run = true

/rag/backend-eval-debug with graph_fusion:
  graph_dry_run = true

/rag/answer-verify-debug with graph_fusion:
  graph_dry_run = true
```

Live Neo4j validation is manual and local:

```text
graph_dry_run = false
check_connection = true
dry_run = false
```

---

## 11. Manual Validation Commands

Start the server:

```bash
python -m uvicorn src.app.main:app --reload --port 8000
```

Health check:

```bash
curl -s "http://localhost:8000/graph/health-debug?check_connection=true" \
  -H "x-trace-id: graphrag-health-live-001" \
  | python -m json.tool --no-ensure-ascii
```

Ingest seed graph:

```bash
curl -s -X POST http://localhost:8000/graph/ingest-debug \
  -H "Content-Type: application/json" \
  -H "x-trace-id: graphrag-ingest-live-001" \
  -d '{"source_filter":"agent_basics","max_chars":300,"include_related_entities":true,"dry_run":false,"apply_schema":true}' \
  | python -m json.tool --no-ensure-ascii
```

Graph retrieval:

```bash
curl -s -X POST http://localhost:8000/graph/retrieval-debug \
  -H "Content-Type: application/json" \
  -H "x-trace-id: graphrag-retrieval-live-001" \
  -d '{"query":"RAG 和 LangGraph 有什么关系？","source_filter":"agent_basics","chunk_limit":5,"related_entity_limit":10,"dry_run":false}' \
  | python -m json.tool --no-ensure-ascii
```

Fusion:

```bash
curl -s -X POST http://localhost:8000/graph/fusion-debug \
  -H "Content-Type: application/json" \
  -H "x-trace-id: graphrag-fusion-live-001" \
  -d '{"query":"RAG 和 LangGraph 有什么关系？","top_k":3,"source_filter":"agent_basics","max_chars":300,"embedding_dim":64,"hybrid_keyword_weight":0.6,"hybrid_vector_weight":0.4,"fusion_graph_weight":0.5,"fusion_vector_weight":0.5,"graph_chunk_limit":5,"related_entity_limit":10,"graph_dry_run":false}' \
  | python -m json.tool --no-ensure-ascii
```

Agentic RAG graph_fusion:

```bash
curl -s -X POST http://localhost:8000/rag/agentic-debug \
  -H "Content-Type: application/json" \
  -H "x-trace-id: graphrag-agentic-live-001" \
  -d '{"query":"RAG 和 LangGraph 有什么关系？","top_k":2,"source_filter":"agent_basics","max_chars":300,"embedding_dim":64,"retrieval_backend":"graph_fusion","graph_dry_run":false}' \
  | python -m json.tool --no-ensure-ascii
```

GraphRAG evaluation:

```bash
curl -s -X POST http://localhost:8000/rag/eval-debug \
  -H "Content-Type: application/json" \
  -H "x-trace-id: graphrag-eval-live-001" \
  -d '{"eval_file":"eval_cases/rag_agentic_eval.jsonl","source_filter":"agent_basics","max_chars":300,"embedding_dim":64,"keyword_weight":0.6,"vector_weight":0.4,"retrieval_backend":"graph_fusion","embedding_provider":"deterministic","rebuild_index":true,"graph_dry_run":false}' \
  | python -m json.tool --no-ensure-ascii
```

GraphRAG answer verification:

```bash
curl -s -X POST http://localhost:8000/rag/answer-verify-debug \
  -H "Content-Type: application/json" \
  -H "x-trace-id: graphrag-answer-verify-live-001" \
  -d '{"query":"请搜索知识库：RAG 是什么？","top_k":2,"source_filter":"agent_basics","max_chars":300,"embedding_dim":64,"keyword_weight":0.6,"vector_weight":0.4,"retrieval_backend":"graph_fusion","embedding_provider":"deterministic","rebuild_index":true,"graph_dry_run":false}' \
  | python -m json.tool --no-ensure-ascii
```

Trace lookup:

```bash
curl -s http://localhost:8000/observability/traces/graphrag-answer-verify-live-001 \
  | python -m json.tool --no-ensure-ascii
```

---

## 12. Safety Boundaries

GraphRAG is still explicit opt-in:

```text
retrieval_backend = graph_fusion
```

The project must not silently switch the default retrieval backend.

Current default:

```text
retrieval_backend = hybrid
```

Safety check:

```bash
grep -R --exclude-dir=__pycache__ \
  "retrieval_backend.*graph_fusion\|default.*graph_fusion\|graph_fusion.*default" \
  -n src/app tests/ || true
```

Allowed:

```text
explicit graph_fusion request fields
graph_fusion backend branch
graph_fusion tests
graph_fusion metadata helpers
```

Not allowed:

```text
DEFAULT_RETRIEVAL_BACKEND = "graph_fusion"
retrieval_backend: str = "graph_fusion"
```

Multi-Agent must not start before Day52:

```bash
find src/app -maxdepth 3 -type f | grep -i "multi\|supervisor\|planner\|critic" || true
```

---

## 13. Current Limitations

Current limitations:

```text
1. The seed graph is small and currently based on knowledge/agent_basics.md.
2. Entity extraction is deterministic alias matching, not LLM-based extraction.
3. RELATED_TO edges collapse repeated co-occurrences by entity pair.
4. graph_fusion is not the default retrieval backend.
5. CI uses graph_dry_run=true, so CI validates contracts but not live Neo4j retrieval quality.
6. Live Neo4j validation is manual.
7. The final answer template may still say "根据混合检索结果" even when retrieval_backend="graph_fusion".
```

These are intentional tradeoffs for a staged engineering project.

---

## 14. Interview Explanation

A concise explanation:

```text
This project implements GraphRAG as an explicit Agentic RAG backend. The system
first chunks Markdown knowledge, extracts deterministic entities and relations,
ingests Document / Chunk / Entity nodes into Neo4j, retrieves chunks and related
entities through graph traversal, then fuses graph evidence with hybrid vector
retrieval by chunk_id. The fused results are normalized into the existing
Agentic RAG pipeline through retrieval_backend="graph_fusion". Evaluation,
trace payloads, and answer verification all preserve graph/vector contribution
metadata, while graph_fusion remains non-default and CI-safe through dry-run
graph retrieval.
```

Key engineering points:

```text
1. GraphRAG is integrated through a backend switch, not a separate application path.
2. Graph retrieval and vector retrieval stay independently observable.
3. Fusion is deterministic and explainable through graph_score, vector_score, and fusion_score.
4. Evaluation compares graph_fusion against hybrid, chroma, and chroma_rerank.
5. Observability traces preserve graph/vector contribution metadata.
6. Answer verification checks both original citation support and GraphRAG evidence metadata.
7. CI stays stable because live Neo4j access is always opt-in.
```
