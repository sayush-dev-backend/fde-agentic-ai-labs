# FDE Agentic AI Labs

**Building, testing, and understanding agentic AI systems through hands-on engineering labs.**

This repository documents my journey toward becoming a Forward Deployed Engineer (FDE), focusing on AI agents, tool orchestration, memory, validation, and reliable software engineering.

## Objectives

- Understand agent execution flow and tool orchestration.
- Implement tool registration, authorization, execution, and validation.
- Build session-scoped and user-scoped long-term memory.
- Add persistent storage and test memory isolation.
- Progress toward observable and production-ready AI systems.

## Current Labs

| Lab | Focus | Status |
|---|---|---|
| Agent Labs 1–3 | Agent foundations and execution flow | Implemented |
| Agent Lab 4 | Tool execution, argument passing, validation, permissions, retries, and execution limits | Implemented; tests available |
| Memory Lab 1 | Session-based conversation history | Implemented; tests available |
| Memory Lab 2 | In-process, user-scoped long-term memory | Implemented; tests available |
| Memory Lab 3 | SQLite-backed persistent, user-scoped memory | Implemented; tests available |
| Agent + SQLite integration | Cross-session retrieval and user isolation using persistent memory | Implemented on integration branch; 47 local tests passed |

## Repository Structure

```text
fde-agentic-ai-labs/
├── README.md
├── .gitignore
├── requirements.txt
├── docs/learning-roadmap.md
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

The current test suite uses Python's built-in `unittest`; no third-party testing package is required.

### Setup

```bash
git clone https://github.com/sayush-dev-backend/fde-agentic-ai-labs.git
cd fde-agentic-ai-labs
python3 -m venv .venv
source .venv/bin/activate
```

### Run the Tests

Run from the repository root:

```bash
python3 -m unittest discover -v
```

Run one test module:

```bash
python3 -m unittest -v test_fde_agent_lab4.py
```

## Memory Architecture

- **Session memory:** `SessionManager` stores structured conversation messages within a session.
- **In-process long-term memory:** `LongTermMemory` stores user-scoped key/value preferences in application memory; data does not survive process restarts.
- **Persistent long-term memory:** `LongTermMemorySQLite` stores JSON-compatible user-scoped values in SQLite, allowing data to survive new memory instances when they use the same database file.

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
- [x] Add automated tests using `unittest`.
- [ ] Document each lab's architecture and learning objectives in greater depth.
- [ ] Expand security, concurrency, and failure-mode testing.
- [ ] Add structured logging, tracing, and operational metrics.
- [ ] Build an end-to-end agentic workflow around a real FDE problem.
- [ ] Develop deployment and production-readiness practices.

## Philosophy

> An AI system is not finished when it produces an answer. It is finished when its behavior is understood, its failures are handled, and its reliability can be tested.

This repository is a work in progress. Each lab represents a step toward building AI systems that solve real problems reliably.
