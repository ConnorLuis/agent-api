# agent-api

`agent-api` is a FastAPI + LangGraph backend project for building an Agent service step by step.

This project is the second project in the AI internship preparation roadmap, following the completed `chat-api-v2` project. The current version implements a deterministic Tool Calling Agent with SQLite-based short-term memory, graph debug output, pytest coverage, and GitHub Actions CI.

## Current Status

```text
Day1-Day7 completed.
Current stage: engineering foundation completed before real LLM integration.
Next milestone: Day8 request logging middleware with x-trace-id and latency.
```

## Features

Current features:

* FastAPI backend service
* `/health` health check endpoint
* `/agent/chat` chat endpoint
* LangGraph `StateGraph`
* Tool Calling Agent loop
* Built-in deterministic tools:
  * `add`
  * `multiply`
* SQLite checkpoint-based short-term memory
* `thread_id` based conversation state
* `/agent/debug` endpoint for inspecting graph execution steps
* Split pytest API tests
* GitHub Actions CI

Not implemented yet:

* Real LLM integration
* Ollama provider
* OpenAI provider
* Real LLM tool calling
* Streaming response
* RAG tool
* Router Agent
* GraphRAG
* Multi-Agent workflow

## Tech Stack

* Python 3.10
* FastAPI
* Uvicorn
* Pydantic
* LangGraph
* LangChain Core
* LangGraph prebuilt `ToolNode`
* LangGraph prebuilt `tools_condition`
* SQLite checkpoint saver
* pytest
* GitHub Actions

## Project Structure

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
│   └── DAY07.md
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

For a tool call, the message flow is:

```text
HumanMessage
  ↓
AIMessage(tool_calls)
  ↓
ToolMessage
  ↓
AIMessage(final answer)
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

## API Usage

### Chat

```bash
curl -X POST http://localhost:8000/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"请计算 3 加 5","thread_id":"demo-thread-001"}'
```

Expected response:

```json
{
  "answer": "工具 `add` 执行结果：8",
  "thread_id": "demo-thread-001"
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

### Debug Endpoint

The debug endpoint shows graph execution steps.

```bash
curl -X POST http://localhost:8000/agent/debug \
  -H "Content-Type: application/json" \
  -d '{"message":"请计算 8 乘 9","thread_id":"debug-demo-001"}'
```

Expected node path:

```text
agent -> tools -> agent
```

The response includes:

* `thread_id`
* `steps`
* `final_answer`
* `messages_count`

## Tests

Run tests:

```bash
pytest -q
```

Current result:

```text
8 passed, 1 warning
```

Current test coverage includes:

* `/health`
* `/agent/chat` normal response
* `add` tool
* `multiply` tool
* same-thread short-term memory
* different-thread memory isolation
* `/agent/debug` normal path
* `/agent/debug` tool-call path

Current test organization:

```text
tests/
├── conftest.py
├── test_health.py
├── test_agent_chat.py
├── test_agent_memory.py
└── test_agent_debug.py
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
green
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

## Development Notes

`requirements.txt` is manually maintained as a minimal dependency file. Do not blindly overwrite it with `pip freeze > requirements.txt` from a conda environment, because conda build artifact paths may break GitHub Actions CI.

## Roadmap

Next milestones:

* Day8: Add request logging middleware with `x-trace-id`
* Day8: Add latency logging
* Day8: Connect trace id with Agent debug output
* Day9: Add Ollama LLM provider
* Day10: Replace deterministic tool-call mock with real LLM tool calling
* Day11: Add `/agent/stream`
* Day12: Add RAG search tool
* Day13+: Add Router Agent
* Later: Add GraphRAG and Neo4j integration
* Later: Add Multi-Agent Supervisor workflow
