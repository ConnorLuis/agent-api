# HANDOFF.md

## Project

agent-api

## Current Status

Project 2 has officially started and is now the main development line.

`chat-api-v2` has been completed. Future review of that project will happen in the separate conversation named **Chat-API项目复习**.

Current `agent-api` status:

```text
Day1-Day13 completed.
Day13 completed: deterministic Router Agent.
Local pytest: 23 passed, 1 warning.
GitHub Actions CI: green.
Next: Day14 connect Router Agent with existing Agent capabilities.
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
- Local Markdown knowledge base
- Deterministic Router Agent
- pytest
- GitHub Actions CI

Not yet implemented:

- OpenAI provider
- Replacing `/agent/chat` with the real LLM Agent as the default route
- LLM-based Router Agent
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
│   └── DAY13.md
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
│       │   └── rag.py
│       ├── routes/
│       │   ├── routes_agent.py
│       │   ├── routes_llm.py
│       │   └── routes_rag.py
│       ├── rag/
│       │   ├── __init__.py
│       │   └── retriever.py
│       ├── llm/
│       │   ├── base.py
│       │   ├── factory.py
│       │   ├── mock.py
│       │   └── ollama.py
│       └── agent/
│           ├── graph.py
│           ├── router_graph.py
│           ├── streaming.py
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
    └── test_router_agent.py
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
```

### Router Agent

```text
POST /agent/router-chat
POST /agent/router-debug
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
It prepares the project for Day14+ integration with existing Agent capabilities.
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
23 passed, 1 warning
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
23 passed, 1 warning
```

### CI Result

```text
GitHub Actions CI: green
```

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
23 passed, 1 warning
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
Day14: Connect Router Agent with existing Agent capabilities
Day15+: LLM-based routing or richer RAG integration
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

Next:

- [ ] Day14 connect Router Agent with existing Agent capabilities
