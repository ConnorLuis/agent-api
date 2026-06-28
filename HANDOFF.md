# HANDOFF.md

## Project

agent-api

## Current Status

Project 2 has officially started and is now the main development line.

`chat-api-v2` has been completed. Future review of that project will happen in the separate conversation named **Chat-API项目复习**.

Current `agent-api` status:

```text
Day1-Day6 completed.
Day7 in progress: pytest + README.md initial version + GitHub Actions CI.
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

Recommended current structure:

```text
agent-api/
├── README.md
├── HANDOFF.md
├── requirements.txt
├── .gitignore
├── .github/
│   └── workflows/
│       └── ci.yml
├── data/
│   └── checkpoints.sqlite          # runtime only, ignored by Git
├── src/
│   └── app/
│       ├── main.py
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
    └── test_agent_debug.py
```

If tests have not yet been split, a single `tests/test_agent_api.py` is acceptable temporarily. The recommended Day7 direction is to split tests by feature.

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
  "thread_id": "demo-thread-001"
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

These files are runtime data and should be ignored by Git.

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

### Status

In progress.

### Goals

- Fix SQLite runtime files being tracked by Git
- Update `.gitignore`
- Add pytest tests
- Add README.md initial version
- Add GitHub Actions CI
- Run `pytest -q` locally
- Push and verify GitHub Actions CI

### Test Organization Recommendation

Current stage recommendation:

```text
tests/
├── conftest.py
├── test_health.py
├── test_agent_chat.py
├── test_agent_memory.py
└── test_agent_debug.py
```

A single `tests/test_agent_api.py` is acceptable temporarily, but it should be split once tests grow beyond the initial 8 deterministic cases.

Later, after adding real LLM, RAG, and GraphRAG, expand to:

```text
tests/
├── api/
├── unit/
├── integration/
└── conftest.py
```

### Suggested Deterministic Tests

- `/health`
- `/agent/chat` normal response
- `add` tool
- `multiply` tool
- same-thread memory
- different-thread memory isolation
- `/agent/debug` normal path
- `/agent/debug` tool path

### CI

Recommended workflow:

```text
GitHub Actions
  ↓
checkout
  ↓
setup-python 3.10
  ↓
pip install -r requirements.txt
  ↓
pytest -q
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
Day7: pytest + README.md initial version + CI
Day8: request logging middleware with x-trace-id and latency
Day9: Ollama LLM provider
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

In progress:

- [ ] Day7 pytest
- [ ] Day7 README.md initial version
- [ ] Day7 GitHub Actions CI
