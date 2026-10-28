
"""
FDE Incident Investigator — Lab 4

Integrates:
- Lab 1: Secure tool execution
- Lab 3: Simulated LLM and agent loop

Python 3.10+
No third-party dependencies required.
"""

import time
from typing import Any, Callable

from fde_agent_lab1 import execute_tool


MAX_STEPS = 3


# ---------- 1. Simulated LLM ----------

def simulated_llm(
    messages: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Simulate an LLM deciding whether to call a tool
    or return a final answer.
    """

    # Find tool results in the conversation history.
    tool_messages = [
        message
        for message in messages
        if message["role"] == "tool"
    ]

    # If no tool result exists, request payment metrics.
    if not tool_messages:
        return {
            "type": "tool_call",
            "tool": "get_payment_metrics",
            "arguments": {
                "service": "payment-api",
                "window_minutes": 15,
            },
        }

    # Read the latest tool result.
    tool_result = tool_messages[-1]["content"]

    # Handle unsuccessful tool execution.
    if not tool_result["ok"]:
        return {
            "type": "final",
            "content": (
                "I couldn't retrieve the payment metrics. "
                "The tool request was rejected."
            ),
            "trust_level": "untrusted",
        }

    # Generate a final answer from successful results.
    metrics = tool_result["data"]

    return {
        "type": "final",
        "content": (
            f"Service: {metrics['service']}. "
            f"P95 latency: {metrics['p95_latency_ms']} ms. "
            f"Error rate: {metrics['error_rate_percent']}%. "
            "The service is experiencing elevated latency."
        ),
    }

def call_with_retry(
    operation: Callable[[], Any],
    *,
    max_attempts: int = 3,
    base_delay: float = 1.0,
) -> Any:
    for attempt in range(max_attempts):
        try:
            return operation()

        except ConnectionError:
            # Stop if no attempts remain.
            if attempt == max_attempts - 1:
                raise

            # Exponential backoff.
            delay = base_delay * (2 ** attempt)
            time.sleep(delay)

    raise RuntimeError("Retry loop exited unexpectedly")
# ---------- 2. Agent execution loop ----------

def run_agent(
    user_input: str,
    *,
    principal_role: str,
) -> str:
    """
    Run the agent using a trusted application-supplied role.

    The role must come from trusted application context,
    not from the LLM or user-provided text.
    """

    messages: list[dict[str, Any]] = [
        {
            "role": "user",
            "content": user_input,
        }
    ]

    for step in range(MAX_STEPS):

        # Ask the simulated LLM for its next action.
        action = simulated_llm(messages)

        if not isinstance(action, dict):
            raise ValueError("LLM action must be a dictionary")

        action_type = action.get("type")

        # Handle a final answer.
        if action_type == "final":
            content = action.get("content")

            if not isinstance(content, str):
                raise ValueError("Final answer must be a string")

            return content

        # Reject unsupported actions.
        if action_type != "tool_call":
            raise ValueError("Unsupported action type")

        # Extract the requested tool and arguments.
        tool_name = action.get("tool")
        arguments = action.get("arguments")

        if not isinstance(tool_name, str):
            raise ValueError("Tool name must be a string")

        # Execute through Lab 1's security boundary.
        try:
            result = execute_tool(
                tool_name=tool_name,
                arguments=arguments,
                principal_role=principal_role,
            )

            tool_result = {
                "ok": True,
                "data": result,
            }

        except PermissionError:
            tool_result = {
                "ok": False,
                "error": "permission_denied",
            }

        except LookupError:
            tool_result = {
                "ok": False,
                "error": "unknown_tool",
            }

        except (TypeError, ValueError):
            tool_result = {
                "ok": False,
                "error": "invalid_tool_request",
            }

        # Append the result so the LLM can use it next.
        messages.append({
            "role": "tool",
            "content": tool_result,
            "trust_level": "untrusted",
        })

    return (
    "I couldn't complete the request because "
    f"the execution limit of {MAX_STEPS} steps was reached."
)


# ---------- 3. Run experiments ----------

def demo() -> None:

    print("\nCASE 1 — Authorized caller")

    answer = run_agent(
        "Why is payment-api slow?",
        principal_role="on_call_engineer",
    )

    print(answer)

    print("\nCASE 2 — Unauthorized caller")

    answer = run_agent(
        "Why is payment-api slow?",
        principal_role="customer",
    )

    print(answer)


if __name__ == "__main__":
    demo()
