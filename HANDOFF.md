# HANDOFF.md

## Project

agent-api

## Current Status

Project 2 has officially started and is now the main development line.

`chat-api-v2` has been completed. Future review of that project will happen in the separate conversation named **Chat-API项目复习**.

Current `agent-api` status:

```text
Day1-Day8 completed.
Day8 completed: request logging middleware with x-trace-id and latency.
Local pytest: 12 passed, 1 warning.
GitHub Actions CI: green.
Next: Day9 Ollama LLM provider abstraction.
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
LLM integration
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

## Tech Stack

Current:

- FastAPI
- Uvicorn
- Pydantic
- LangGraph
- LangChain Core
- LangGraph prebuilt `ToolNode`
- LangGraph prebuilt `tools_condition`
- SQLite checkpoint saver
- Request logging middleware
- `ContextVar` based request trace context
- pytest
- GitHub Actions CI

Not yet implemented:

- Real LLM integration
- Ollama provider
- OpenAI provider
- Real LLM tool calling
- Streaming response
- RAG tool
- Router Agent
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
│   └── DAY08.md
├── data/
│   └── checkpoints.sqlite          # runtime only, ignored by Git
├── src/
│   └── app/
│       ├── main.py
│       ├── core/
│       │   ├── logging.py
│       │   ├── middleware.py
│       │   └── request_context.py
│       ├── schemas/
│       │   └── agent.py
│       ├── routes/
│       │   └── routes_agent.py
│       └── agent/
│           ├── graph.py
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
    └── test_trace.py
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

### Agent Chat

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

### Agent Debug

```text
POST /agent/debug
```

Request:

```json
{
  "message": "请计算 8 乘 9",
  "thread_id": "debug-demo-001"
}
```

Expected node path:

```text
agent -> tools -> agent
```

Response includes:

```text
thread_id
steps
final_answer
messages_count
trace_id
```

---

## Current Graph

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

For tool calls, the message flow is:

```text
HumanMessage
  ↓
AIMessage(tool_calls)
  ↓
ToolMessage
  ↓
AIMessage(final answer)
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

Agent response body:

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
request_completed method=POST path=/agent/chat status_code=200 latency_ms=12.34 trace_id=chat-trace-001
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

### Verified

```bash
curl -X POST http://localhost:8000/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"你好，这是Agent项目Day2 LangGraph测试","thread_id":"test-thread-001"}'
```

Expected:

```json
{
  "answer": "LangGraph agent response: 你好，这是Agent项目Day2 LangGraph测试",
  "thread_id": "test-thread-001"
}
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

### Verified

```bash
curl -X POST http://localhost:8000/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"请计算 3 加 5","thread_id":"test-thread-001"}'
```

Expected:

```json
{
  "answer": "工具 `add` 执行结果：8",
  "thread_id": "test-thread-001"
}
```

```bash
curl -X POST http://localhost:8000/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"请计算 6 乘 7","thread_id":"test-thread-001"}'
```

Expected:

```json
{
  "answer": "工具 `multiply` 执行结果：42",
  "thread_id": "test-thread-001"
}
```

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

### Verified

First request:

```bash
curl -X POST http://localhost:8000/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"请计算 3 加 5","thread_id":"memory-test-001"}'
```

Second request:

```bash
curl -X POST http://localhost:8000/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"我刚才计算了什么？","thread_id":"memory-test-001"}'
```

Expected:

```json
{
  "answer": "我记得上一轮工具 `add` 的执行结果是：8",
  "thread_id": "memory-test-001"
}
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

### Current Memory Strategy

```text
Persistent short-term memory = SqliteSaver + thread_id + checkpoints.sqlite
```

### Verified

```bash
sqlite3 data/checkpoints.sqlite ".tables"
```

Expected:

```text
checkpoints  writes
```

Cross-process local test:

```bash
python - <<'PY'
from src.app.agent.graph import invoke_agent

result = invoke_agent(
    message="请计算 10 乘 6",
    thread_id="local-sqlite-memory-001",
)

print(result["messages"][-1].content)
PY
```

Then:

```bash
python - <<'PY'
from src.app.agent.graph import invoke_agent

result = invoke_agent(
    message="我刚才计算了什么？",
    thread_id="local-sqlite-memory-001",
)

print(result["messages"][-1].content)
print("\nMESSAGES COUNT:", len(result["messages"]))
PY
```

Expected:

```text
我记得上一轮工具 `multiply` 的执行结果是：60
MESSAGES COUNT: 6
```

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

### Debug Endpoint

```text
POST /agent/debug
```

### Verified

```bash
curl -X POST http://localhost:8000/agent/debug \
  -H "Content-Type: application/json" \
  -d '{"message":"请计算 8 乘 9","thread_id":"debug-tool-001"}'
```

Expected:

```text
agent -> tools -> agent
```

Expected final answer:

```text
工具 `multiply` 执行结果：72
```

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

### Test Organization

Current test structure:

```text
tests/
├── conftest.py
├── test_health.py
├── test_agent_chat.py
├── test_agent_memory.py
└── test_agent_debug.py
```

Later, after adding real LLM, RAG, and GraphRAG, expand to:

```text
tests/
├── api/
├── unit/
├── integration/
└── conftest.py
```

### Deterministic Tests

Current tests cover:

- `/health`
- `/agent/chat` normal response
- `add` tool
- `multiply` tool
- same-thread memory
- different-thread memory isolation
- `/agent/debug` normal path
- `/agent/debug` tool path

### Local pytest Result

```text
8 passed, 1 warning
```

The warning is from `fastapi.testclient` / Starlette deprecation and currently does not affect tests.

### CI Result

```text
GitHub Actions CI: green
```

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

### Known CI Fix

Do not blindly run:

```bash
pip freeze > requirements.txt
```

inside the conda environment.

Reason:

```text
It may write conda build artifact paths such as /home/conda/feedstock_root/...
Those paths do not exist on GitHub Actions runners and will break CI.
```

Use a minimal hand-maintained `requirements.txt` instead.

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

### Current Observability

```text
method
path
status_code
latency_ms
trace_id
```

### Verified

Auto-generated trace id:

```bash
curl -i http://localhost:8000/health
```

Result includes:

```text
x-trace-id: trace-183ab0ea9895
```

Client-provided trace id:

```bash
curl -i http://localhost:8000/health \
  -H "x-trace-id: manual-trace-001"
```

Result:

```text
x-trace-id: manual-trace-001
```

Agent chat:

```bash
curl -i -X POST http://localhost:8000/agent/chat \
  -H "Content-Type: application/json" \
  -H "x-trace-id: chat-trace-001" \
  -d '{"message":"请计算 3 加 5","thread_id":"day8-chat-001"}'
```

Expected response body:

```json
{
  "answer": "工具 `add` 执行结果：8",
  "thread_id": "day8-chat-001",
  "trace_id": "chat-trace-001"
}
```

Agent debug:

```bash
curl -i -X POST http://localhost:8000/agent/debug \
  -H "Content-Type: application/json" \
  -H "x-trace-id: debug-trace-001" \
  -d '{"message":"请计算 8 乘 9","thread_id":"day8-debug-001"}'
```

Expected:

```text
x-trace-id: debug-trace-001
final_answer: 工具 `multiply` 执行结果：72
trace_id: debug-trace-001
```

### Test Result

```text
12 passed, 1 warning
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

### Current agent_node label

Some normal responses still contain:

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
12 passed, 1 warning
```

The warning is:

```text
StarletteDeprecationWarning: Using httpx with starlette.testclient is deprecated; install httpx2 instead.
```

It does not block local tests or CI and can be handled later.

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
Day9: Ollama LLM provider abstraction
Day10: real LLM tool calling
Day11: /agent/stream
Day12: RAG tool
Day13+: Router Agent
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

Next:

- [ ] Day9 Ollama LLM provider abstraction
