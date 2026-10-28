# FDE Agentic AI Labs

**Building, testing, and understanding agentic AI systems through hands-on engineering labs.**

This repository documents my journey toward becoming a Forward Deployed Engineer (FDE), with a focus on AI agents, tool orchestration, memory, validation, and reliable software engineering.

Rather than treating AI agents as black boxes, I am building their core components incrementally to understand how they work, how they fail, and how to make them more reliable.

## Objectives

- Understand the architecture of tool-based AI agents.
- Implement tool selection and execution workflows.
- Explore dynamic tool argument passing.
- Build memory components for agentic systems.
- Validate inputs and outputs.
- Write automated tests for correctness and failure handling.
- Progress toward secure, observable, and production-ready AI systems.

## Current Labs

| Lab | Focus | Status |
|---|---|---|
| Agent Lab 1 | Initial agent implementation | Implemented; documentation pending |
| Agent Lab 2 | Agent architecture and behavior | Implemented; documentation pending |
| Agent Lab 3 | Further agent implementation | Implemented; documentation pending |
| Agent Lab 4 | Tool execution, argument passing, and validation | Implemented; automated tests available |
| Memory Lab 1 | Initial agent memory implementation | Implemented; automated tests available |

*The precise learning objectives for each lab will be documented as the implementations are reviewed.*

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
├── test_fde_agent_lab4.py
└── test_fde_memory_lab1.py
```

## Getting Started

### Prerequisites

- Python 3.10 or later
- Git
- `pytest` for running the automated test suite

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

Install the testing dependency:

```bash
python -m pip install pytest
```

### Run the Tests

```bash
python -m pytest -v
```

## Engineering Principles

My approach to building agentic systems emphasizes:

- **Understandability:** Know what each component does and why it exists.
- **Correctness:** Validate behavior instead of relying on assumptions.
- **Reliability:** Test invalid inputs, unexpected outputs, and failure scenarios.
- **Security:** Treat tool execution and external inputs as trust boundaries.
- **Incremental development:** Build a working foundation before introducing complexity.
- **Production thinking:** Consider observability, maintainability, and operational risks.

## Roadmap

- [x] Implement initial agent labs.
- [x] Implement an initial memory lab.
- [x] Add automated tests for selected labs.
- [ ] Document each lab's architecture and learning objectives.
- [ ] Expand test coverage across the agent and memory components.
- [ ] Implement safer tool execution and argument validation.
- [ ] Explore persistent memory and retrieval.
- [ ] Add structured logging and observability.
- [ ] Build an end-to-end agentic workflow.
- [ ] Develop deployment and production-readiness practices.

## Philosophy

> An AI system is not finished when it produces an answer. It is finished when its behavior is understood, its failures are handled, and its reliability can be tested.

This repository is a work in progress. Each lab represents a step toward building AI systems that solve real problems reliably.