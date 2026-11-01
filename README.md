# FDE Agentic AI Labs

**Building, testing, and understanding agentic AI systems through hands-on engineering labs.**

This repository documents my journey toward becoming a Forward Deployed Engineer (FDE). The focus is on understanding how tool-based agents work and how to engineer them to be reliable, secure, testable, and maintainable.

Rather than treating agents as black boxes, I build their components incrementally, test their behavior, and document the engineering decisions behind them.

## Objectives

- Understand the execution flow of tool-based agents.
- Implement tool registration, selection, argument passing, and execution.
- Validate tool requests and results and handle failures safely.
- Build session and long-term memory with user-scoped access.
- Compare in-process and persistent storage implementations.
- Use Protocols and dependency injection to decouple agent logic from storage.
- Apply automated testing and static type checking.
- Progress toward secure, observable, production-oriented agent systems.

## Current Progress

| Area | What has been implemented |
|---|---|
| Agent fundamentals | Initial agent execution flow and simulated model decisions |
| Tool execution | Tool lookup and execution, argument passing, and execution through a security boundary |
| Validation and control | Action validation, tool argument checks, error handling, and an execution-step limit |
| Session memory | Session creation and structured conversation history |
| In-process long-term memory | User-scoped remember, recall, and forget operations |
| Persistent memory | SQLite-backed storage with JSON serialization and persistence across instances |
| Agent-memory integration | Long-term memory integrated into the agent for a narrow preferred-language example |
| Storage abstraction | A `MemoryStore` Protocol shared by the in-process and SQLite implementations |
| Quality checks | `unittest` coverage and Mypy static type checking |

These are incremental learning implementations. They are not yet a complete production agent framework.

## Memory Architecture

The memory work currently has three main pieces:

- **Session memory** — maintains conversation history for a session.
- **In-process long-term memory** — stores user-scoped values in Python dictionaries. It is simple to inspect, but data does not survive process restarts.
- **SQLite long-term memory** — persists JSON-compatible values in a database and can be accessed by a new storage instance.

The agent depends on the `MemoryStore` Protocol rather than a specific storage class. This allows a compatible implementation to be supplied by the application at the composition point (dependency injection), keeping storage selection separate from agent orchestration.

The current agent-memory demonstration saves and recalls a user's explicitly stated preferred programming language. This is a focused learning example, not a general-purpose memory extraction or retrieval system.

## Repository Structure

The repository is organized around individual learning labs, their tests, and supporting documentation. Key modules include:

```text
fde-agentic-ai-labs/
├── README.md
├── docs/
│   └── learning-roadmap.md
├── fde_agent_lab1.py
├── fde_agent_lab2.py
├── fde_agent_lab3.py
├── fde_agent_lab4.py
├── fde_memory_interfaces.py
├── fde_memory_lab1.py
├── fde_memory_lab2.py
├── fde_memory_lab3.py
├── test_fde_agent_lab4.py
├── test_fde_memory_lab2.py
├── test_fde_memory_lab3.py
└── test_protocol_experiment.py
```

## Getting Started

### Prerequisites

- Python 3.10 or later
- Git

### Setup

Clone the repository:

```bash
git clone https://github.com/sayush-dev-backend/fde-agentic-ai-labs.git
cd fde-agentic-ai-labs
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Run the tests

The project uses Python's built-in `unittest` framework:

```bash
python -m unittest discover -v
```

### Run static type checking

Mypy is used as a development-time static type checker. Install it in the active virtual environment if it is not already installed:

```bash
python -m pip install mypy
python -m mypy .
```

## Engineering Principles

- **Understandability:** Know what each component does and why it exists.
- **Correctness:** Validate behavior rather than relying on assumptions.
- **Testability:** Test expected behavior, invalid inputs, and failure scenarios.
- **Separation of concerns:** Keep agent orchestration separate from storage implementation.
- **Security:** Treat tool execution, user identity, and external inputs as trust boundaries.
- **Incremental development:** Build a working foundation before introducing complexity.
- **Production thinking:** Consider observability, maintainability, and operational risks.

## Roadmap

See [docs/learning-roadmap.md](docs/learning-roadmap.md) for completed work and the next learning stages.

## Philosophy

> An AI system is not finished when it produces an answer. It is finished when its behavior is understood, its failures are handled, and its reliability can be tested.

This repository is a work in progress. Each lab is a step toward building AI systems that solve real problems reliably.
