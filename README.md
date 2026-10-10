# Agent-DB

A production-grade **Agent DB** project built on the architecture of:

> **Agent Data Gateway + Context Engine + Memory + Workflow + Knowledge + Tool Registry + State Store**

Agent-DB is not an ordinary database. It is a unified data backend that lets LLM Agents move from "stateless Q&A machines" to "persistent intelligent agents with memory, knowledge, planning, and recovery capabilities."

---

## Table of Contents

- [Why Agent-DB Exists](#why-agent-db-exists)
- [Overall Architecture](#overall-architecture)
- [Core: Agent Data Gateway](#core-agent-data-gateway)
- [How Agent-DB Serves an Agent](#how-agent-db-serves-an-agent)
- [Why the Gateway Is Essential](#why-the-gateway-is-essential)
- [Five Core Modules](#five-core-modules)
- [Multi-Agent Support](#multi-agent-support)
- [Context Construction](#context-construction)
- [Code-Level Calling](#code-level-calling)
- [How Workflow Is Called by an Agent](#how-workflow-is-called-by-an-agent)
- [Why This Architecture Is Industrial-Grade](#why-this-architecture-is-industrial-grade)
- [Industrial-Grade vs. Ordinary RAG](#industrial-grade-vs-ordinary-rag)
- [One-Sentence Summary](#one-sentence-summary)
- [Key Recommendation](#key-recommendation)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Core APIs](#core-apis)
- [Testing](#testing)
- [GitHub Upload Checklist](#github-upload-checklist)

---

## Why Agent-DB Exists

An LLM Agent by default is **stateless**:

- No memory of previous conversations.
- No knowledge of private documents.
- No ability to follow a predefined execution plan.
- No way to track task progress across multiple turns.

Agent-DB solves this by providing a **persistent, shared, context-aware data layer** that agents can query through a single gateway.

---

## Overall Architecture

This is a production-grade architecture close to real-world AI infrastructure.

```
                        ┌────────────────────┐
                        │        USER        │
                        └─────────┬──────────┘
                                  │
                                  ▼
                        ┌────────────────────┐
                        │    API Gateway     │
                        └─────────┬──────────┘
                                  │
                                  ▼
                     ┌─────────────────────────┐
                     │   Agent Runtime Layer    │
                     │  (OpenClaw / Multi-Agent)│
                     └─────────┬───────────────┘
                               │
            ┌──────────────────┼──────────────────┐
            ▼                  ▼                  ▼
   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
   │   Planner    │   │   Executor   │   │ Tool Router  │
   └──────┬───────┘   └──────┬───────┘   └──────┬───────┘
          │                  │                  │
          └──────────┬───────┴──────────┬──────┘
                     ▼                  ▼
              ┌────────────────────────────────┐
              │       Agent Data Gateway       │  ⭐ Core
              └────────────────────────────────┘
                     │         │         │
     ┌───────────────┼─────────┼─────────┼───────────────┐
     ▼               ▼         ▼         ▼               ▼
┌──────────┐   ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│ Workflow │   │  Memory  │ │Knowledge │ │  Tools   │ │  State   │
│   DB     │   │  System  │ │   RAG    │ │ Registry │ │  Store   │
└────┬─────┘   └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘
     ▼              ▼            ▼            ▼            ▼
Postgres        Vector DB     Vector DB     Postgres     Postgres
                 + Cache       + Graph      + API        + Redis
                                DB
```

### User flow

```
User
  ↓
API Gateway
  ↓
Agent Runtime (OpenClaw / Multi-Agent)
  ↓
Planner / Executor / Tool Router
  ↓
Agent Data Gateway
  ↓
Workflow DB | Memory System | Knowledge RAG | Tool Registry | State Store
```

---

## Core: Agent Data Gateway

The **Agent Data Gateway** is the most critical layer.

Agent-DB is **not** called directly by agents. Instead, agents go through the Gateway.

The Gateway's responsibilities:

1. **Unified entry point** — one interface for all data access.
2. **Unified query model** — consistent query and retrieval semantics.
3. **Unified permissions** — enforce access control at the data layer.
4. **Unified context construction** — build the structured context an LLM needs.

> **Agent → Tool → Gateway → DB**

An LLM cannot directly operate a database. It must call tools, and those tools call the Gateway.

---

## How Agent-DB Serves an Agent

### Example flow

**User:** "Help me analyze this company."

```
User query
  ↓
Agent (LLM reasoning)
  ↓
Planner:
  - Needs knowledge
  - Needs graph relationships
  - Needs workflow
  ↓
Tool Router:
  - search_knowledge
  - query_graph
  - run_workflow
  ↓
Agent Data Gateway
  ↓
Gateway scheduling:
  → Vector DB
  → Graph DB
  → Postgres
  ↓
Structured context returned
  ↓
LLM generates answer
```

This is the core calling pattern. The agent never touches raw data; it receives a ranked, merged context object.

---

## Why the Gateway Is Essential

The fundamental reason is:

> **Database ≠ Information an Agent Can Use**

What an agent needs is **context**, not raw data.

- Raw data is scattered across tables, vector stores, and graph stores.
- Raw data is not ranked or summarized.
- Raw data is not formatted for an LLM prompt.

The Gateway transforms raw data into **structured, ranked, prompt-ready context**.

---

## Five Core Modules

Based on production experience, an Agent DB must contain five modules.

### 1. Memory System (most important)

A production agent system must have **multi-layer memory**:

- **Working memory** — short-term context for the current turn.
- **Episodic memory** — past interactions and events.
- **Semantic memory** — long-term facts and concepts.
- **State** — current task execution status.

Multi-layer memory is essential for any production-grade agent.

### 2. Workflow DB

Stores:

- Task graphs
- Execution plans
- Decision trees

Purpose:

> Let the agent **execute a process** instead of guessing.

### 3. Knowledge (RAG)

Stores:

- Documents
- Embeddings
- Chunks

Provides vector-based retrieval augmented generation.

### 4. Tool Registry

Stores:

- API schemas
- Function schemas
- Permission rules

Purpose: the agent picks tools by schema, and the Gateway enforces permissions.

### 5. State Store

Tracks:

- Current task status
- Session progress
- Execution progress

Backed by Postgres + Redis for persistence and fast access.

---

## Multi-Agent Support

Multiple agents can share the same Agent-DB:

- Research Agent
- Coding Agent
- Finance Agent
- Support Agent

Shared access pattern:

```
Agent A → Gateway → Memory
Agent B → Gateway → Knowledge
Agent C → Gateway → Workflow
```

All agents share:

- Unified knowledge
- Unified memory
- Unified workflow
- Unified state

This enables **knowledge sharing, state synchronization, and task collaboration**.

---

## Context Construction

The most important capability of Agent-DB is **context engineering**.

```
query
  ↓
retrieve memory
  ↓
retrieve knowledge
  ↓
retrieve graph
  ↓
merge
  ↓
rank
  ↓
inject into prompt
```

The Gateway builds the context so the LLM can reason effectively.

---

## Code-Level Calling

### Agent side

```python
context = agent_gateway.build_context(query)
response = llm.generate(context)
```

### Gateway side

```python
class AgentGateway:
    def build_context(self, query):
        memory = self.memory.search(query)
        knowledge = self.knowledge.search(query)
        graph = self.graph.expand(query)
        return merge(memory, knowledge, graph)
```

---

## How Workflow Is Called by an Agent

```python
workflow = gateway.get_workflow("analysis")
result = workflow_engine.execute(workflow)
```

The workflow is stored in the Workflow DB, loaded by name, and executed by the agent runtime.

---

## Why This Architecture Is Industrial-Grade

It solves three core problems.

### 1. LLM is stateless

An LLM by default has no memory. Agent-DB provides **long-term memory** so the agent can work continuously.

> Without memory, an agent cannot sustain a long-running task.

### 2. Multiple data types

Different data needs different storage:

- Vector data → Vector DB
- Graph data → Graph DB
- Structured data → SQL DB
- Logs → Log store

A single database cannot satisfy all requirements. Agent-DB provides a unified Gateway over heterogeneous storage.

### 3. Multi-agent collaboration

Agent-DB enables:

- Knowledge sharing
- State synchronization
- Task collaboration

---

## Industrial-Grade vs. Ordinary RAG

### Ordinary RAG

```
query → Vector DB → LLM
```

### Agent-DB

```
query
  ↓
planner
  ↓
workflow
  ↓
memory + graph + knowledge
  ↓
tool execution
  ↓
LLM
```

Agent-DB adds planning, memory, workflow, tool execution, and state on top of RAG.

---

## One-Sentence Summary

> **Agent-DB = Memory + Workflow + Tools + Context Engine**

---

## Key Recommendation

If you are building on top of OpenClaw or any multi-agent framework:

> **Do not build a "database."**
>
> **Build an Agent Data Gateway + Context Engine.**

That is the correct abstraction for agent systems.

---

## Technology Stack

| Layer | Technology |
|-------|------------|
| API Framework | FastAPI |
| ORM / Migrations | SQLAlchemy 2.0 + Alembic |
| Database | PostgreSQL + pgvector |
| Cache / State | Redis |
| Testing | pytest + pytest-asyncio |
| Containerization | Docker + Docker Compose |

---

## Project Structure

```
agent-db/
├── alembic/                 # Database migrations
│   └── versions/
├── src/
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Configuration management
│   ├── api/                 # API route layer
│   ├── core/                # Gateway + Context Engine + shared models
│   ├── services/            # Business logic layer
│   ├── db/                  # Database connection and base
│   └── models/              # SQLAlchemy ORM models
├── tests/                   # Test cases
├── docker-compose.yml       # PostgreSQL + Redis + API services
├── Dockerfile               # Production API image
├── alembic.ini              # Alembic configuration
├── requirements.txt         # Python dependencies
├── .env.example             # Example environment variables
├── .gitignore               # Git exclusions
├── .dockerignore            # Docker build exclusions
└── README.md                # This file
```

---

## Quick Start

### 1. Prepare the environment

```bash
# Create a virtual environment (Python 3.10+)
python -m venv venv

# Linux / macOS
source venv/bin/activate

# Windows
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Edit .env if your PostgreSQL / Redis URLs differ
```

### 3. Start infrastructure

```bash
docker compose up -d postgres redis
```

### 4. Run database migrations

```bash
alembic upgrade head
```

This creates all tables: `memories`, `workflows`, `knowledge`, `tools`, `states`, `customers`, `email_logs`.

### 5. Start the service

```bash
uvicorn src.main:app --reload
```

Visit `http://localhost:8000/docs` for the interactive OpenAPI documentation.

### 6. Start the full stack (optional)

```bash
docker compose up -d
```

This builds the API image and starts PostgreSQL, Redis, and the API together.

---

## Core APIs

### Agent Gateway

- `POST /gateway/context` — Build context from memory + knowledge + graph
- `GET /gateway/workflow/{name}` — Load a workflow definition by name

### Module CRUD Routers

- `/memory/*` — Memory System (working / episodic / semantic / state)
- `/workflows/*` — Workflow DB
- `/knowledge/*` — Knowledge RAG
- `/tools/*` — Tool Registry
- `/state/*` — State Store
- `/customers/*` — Customer profiles
- `/emails/*` — Email logs and threads

### Health Check

```bash
GET /health
```

---

## Testing

```bash
pytest tests/ -v
```

The test suite includes:

- CRUD tests for each module
- Gateway context-building tests
- End-to-end agent capability tests

> PostgreSQL and Redis must be running before running tests.
