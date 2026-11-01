# FDE Agentic AI Labs

**Building, testing, and understanding agentic AI systems through hands-on engineering labs.**

This repository documents my journey toward becoming a Forward Deployed Engineer (FDE), with a focus on AI agents, tool orchestration, memory, validation, and reliable software engineering.

Rather than treating AI agents as black boxes, I am building their core components incrementally to understand how they work, how they fail, and how to make them more reliable.

## Objectives

- Understand the architecture and execution flow of tool-based AI agents.
- Implement tool selection, registration, authorization, and execution.
- Explore dynamic tool argument passing and validation.
- Build session-scoped and user-scoped long-term memory.
- Add persistent storage and test memory isolation.
- Validate inputs and outputs and handle failures predictably.
- Progress toward observable and production-ready AI systems.

## Current Labs

| Lab | Focus | Status |
|---|---|---|
| Agent Labs 1–3 | Agent foundations and execution flow | Implemented |
| Agent Lab 4 | Tool execution, argument passing, validation, permissions, retries, execution limits, and agent loop | Implemented; tests available |
| Memory Lab 1 | Session-based conversation history | Implemented; tests available |
| Memory Lab 2 | In-process, user-scoped long-term memory | Implemented; tests available |
| Memory Lab 3 | SQLite-backed persistent, user-scoped memory | Implemented; tests available |
| Agent + SQLite integration | Inject persistent memory into the agent and verify cross-session retrieval and user isolation | Implemented on the integration branch; 47 local tests passed |

## Repository Structure

```text
fde-agentic-ai-labs/
├── README.md
├── .gitignore
├── requirements.txt
├── docs/
│   └── learning-roadmap.md
├── fde_agent_lab1.py
├── fde_agent_lab2.py
├── fde_agent_lab3.py
├── fde_agent_lab4.py
├── fde_memory_lab1.py
├── fde_memory_lab2.py
├── fde_memory_lab3.py
├── test_fde_agent_lab4.py
├── test_fde_memory_lab1.py
├── test_fde_memory_lab2.py
└── test_fde_memory_lab3.py
```

## Getting Started

### Prerequisites

- Python 3.10 or later
- Git

The current test suite uses Python's built-in `unittest` framework. No third-party testing package is required.

### Setup

Clone the repository:

```bash
git clone https://github.com/sayush-dev-backend/fde-agentic-ai-labs.git
cd fde-agentic-ai-labs
```

Create and activate a virtual environment (recommended):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Run the Tests

Run the complete test suite from the repository root:

```bash
python3 -m unittest discover -v
```

To run a specific test module:

```bash
python3 -m unittest -v test_fde_agent_lab4.py
```

## Memory Architecture

The project currently contains three complementary memory layers:

- **Session memory:** `SessionManager` stores structured conversation messages within a session.
- **In-process long-term memory:** `LongTermMemory` stores user-scoped key/value preferences in application memory. Data does not survive process restarts.
- **Persistent long-term memory:** `LongTermMemorySQLite` stores JSON-compatible user-scoped values in SQLite, allowing data to survive new memory instances and application restarts when they use the same database file.

The agent accepts either long-term memory implementation through dependency injection. The caller supplies a trusted `user_id`; the agent does not infer identity from user text.

## Engineering Principles

- **Understandability:** Know what each component does and why it exists.
- **Correctness:** Validate behavior instead of relying on assumptions.
- **Reliability:** Test invalid inputs, unexpected outputs, and failure scenarios.
- **Security:** Treat tool execution and external inputs as trust boundaries.
- **Incremental development:** Build a working foundation before introducing complexity.
- **Production thinking:** Consider observability, maintainability, and operational risks.

## Roadmap

- [x] Implement initial agent labs.
- [x] Implement session-based memory.
- [x] Implement in-process user-scoped long-term memory.
- [x] Implement SQLite-backed persistent memory.
- [x] Integrate persistent memory with the agent and test cross-session retrieval and user isolation.
- [x] Add automated tests for agent and memory components using `unittest`.
- [ ] Document each lab's architecture and learning objectives in greater depth.
- [ ] Expand security, concurrency, and failure-mode testing.
- [ ] Add structured logging, tracing, and operational metrics.
- [ ] Build an end-to-end agentic workflow around a real FDE problem.
- [ ] Develop deployment and production-readiness practices.

## Philosophy

> An AI system is not finished when it produces an answer. It is finished when its behavior is understood, its failures are handled, and its reliability can be tested.

This repository is a work in progress. Each lab represents a step toward building AI systems that solve real problems reliably.
