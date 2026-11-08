# FDE Learning Roadmap

## Learning approach

Follow the book's overall progression while organizing each topic around the FDE Agentic AI Labs project, practical engineering problems, tests, and production readiness.

The goal is not to add technologies for the sake of appearances. Each concept should be understood, implemented when appropriate, tested, and revisited as the agent becomes more complex.

## Project layout and setup

The repository uses a `src` layout for the `fde_agent` package while keeping the learning labs in the top-level `labs` package:

```text
src/fde_agent/                         Core package namespace
labs/lab_01_agent_fundamentals/        Agent execution and tool fundamentals
labs/lab_02_memory/                    Session and long-term memory
labs/lab_03_context_management/        Context construction and retrieval
tests/unit/                            Focused component tests
tests/integration/                     Cross-component agent tests
examples/                              Runnable learning examples
```

Create an environment and install the project from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

The editable install reads dependencies from `pyproject.toml` and ensures imports such as `labs.lab_02_memory.fde_memory_lab1` work regardless of the current test runner.

## Phase 1: Agent Fundamentals

**Goal:** Understand how an agent decides what action to take and how that action gets executed.

Topics:
- Agent execution flow
- Action selection
- Tool registration
- Tool lookup and execution
- Passing arguments to functions
- Handling tool results

**Progress:** Initial agent labs implemented. Lab 3 includes a simulated model decision and an agent execution loop.

## Phase 2: Tool Orchestration and Validation

**Goal:** Make tool execution predictable and validate the data flowing through the system.

Topics:
- Dynamic tool selection
- Keyword argument passing
- Input and action validation
- Tool result handling
- Error handling
- Execution-step limits
- Automated testing

**Progress:** Agent Lab 4 builds on the earlier agent flow and executes tools through the Lab 1 security boundary. It validates model actions and tool arguments, handles expected tool failures, and enforces a maximum number of execution steps.

## Phase 3: Agent Memory

**Goal:** Understand how an agent retains and retrieves useful information, and how storage can be separated from agent logic.

Topics:
- Session memory and conversation history
- User-scoped long-term memory
- Remember, recall, and forget operations
- In-process storage
- Persistent SQLite storage
- JSON serialization
- Memory validation and testing
- Dependency Injection
- Structural typing with Protocols

**Progress:**
- Session management is implemented in Memory Lab 1.
- Memory Lab 2 provides user-scoped in-process long-term memory.
- Memory Lab 3 provides SQLite-backed persistent memory for JSON-compatible values.
- Agent Lab 4 integrates long-term memory for a focused preferred-programming-language example.
- `MemoryStore` defines a Protocol shared by the in-process and SQLite implementations.
- The agent accepts the memory abstraction as a dependency, allowing the concrete storage implementation to be supplied externally.
- The `forget()` operation returns a Boolean indicating whether a key existed and was deleted.

**Important distinction:** The current memory integration is a narrow deterministic example. It does not yet implement general conversational memory extraction, relevance-based retrieval, summarization, or context-window management.

## Phase 4: Reliable Agent Architecture

**Goal:** Move from individual learning exercises toward a coherent agent framework.

Planned topics:
- Context construction and context-window management
- Selecting relevant conversation history and retrieved memory
- Tool schemas and structured inputs/outputs
- Typed data contracts and validation
- Structured errors
- Execution limits and loop prevention
- Retry policies and failure recovery
- Tool permissions and security boundaries
- Prompt-injection defenses
- Observability

Some foundations, such as execution limits, basic tool permissions, and input validation, already appear in earlier labs. This phase will deepen and integrate them rather than repeat them without purpose.

## Phase 5: Production Engineering

**Goal:** Build systems that can be deployed, monitored, and maintained.

Planned topics:
- Structured logging and tracing
- Metrics and operational visibility
- API integration
- Configuration management
- Database and storage lifecycle considerations
- Docker
- CI/CD
- Deployment
- Failure recovery

## Phase 6: End-to-End FDE Project

**Goal:** Demonstrate the ability to take a real problem from discovery through implementation and deployment.

Planned deliverables:
- Problem definition and requirements
- Architecture document and design trade-offs
- Working agentic system
- Tool integrations and memory
- Automated tests
- Security and failure handling
- Deployment instructions
- Observability
- Demonstration and technical write-up

## Engineering quality checks

The project uses Python's built-in `unittest` framework for automated tests and Mypy for static type checking. The supported Python version is 3.11 or later.

Run the test suite:

```bash
python -m unittest discover -v
```

Run static type checking (with Mypy installed in the active environment):

```bash
python -m mypy .
```

## Development principle

Every major capability should have:
1. A clear engineering problem it solves.
2. An understandable implementation.
3. Tests for expected and failure behavior.
4. Documentation of its design and limitations.
5. An explanation of relevant engineering trade-offs.
