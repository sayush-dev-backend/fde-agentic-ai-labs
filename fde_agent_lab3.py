from typing import Any


def get_payment_metrics() -> dict[str, Any]:
    print("Executing get_payment_metrics()")

    return {
        "service": "payment-api",
        "p95_latency_ms": 850,
        "error_rate_percent": 4.2,
    }


def get_recent_deployments() -> dict[str, Any]:
    print("Executing get_recent_deployments()")

    return {
        "service": "payment-api",
        "latest_deployment": "v2.4.1",
        "minutes_ago": 12,
        "status": "completed",
    }


TOOLS = {
    "get_payment_metrics": get_payment_metrics,
    "get_recent_deployments": get_recent_deployments,
}

# Simulated LLM
def simulated_llm(messages: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Return a predefined decision based on the conversation.
    This simulates an LLM without making an API request.
    """

    # Find out whether the tool has already returned a result.
    tool_result_received = any(
        message["role"] == "tool"
        for message in messages
    )

    if not tool_result_received:
        return {
            "type": "tool_call",
            "tool": "get_payment_metrics",
        }

    # After receiving the tool result, provide a final answer.
    metrics = next(
        message["content"]
        for message in messages
        if message["role"] == "tool"
    )

    return {
        "type": "final",
        "content": (
            f"Service: {metrics['service']}. "
            f"P95 latency: {metrics['p95_latency_ms']} ms. "
            f"Error rate: {metrics['error_rate_percent']}%. "
            "The service is experiencing elevated latency."
        ),
    }


def run_agent(user_input: str) -> str:
    messages: list[dict[str, Any]] = [
        {
            "role": "user",
            "content": user_input,
        }
    ]
    user_input = messages[0]["content"]

    for step in range(MAX_STEPS):
        action = simulated_llm(messages)

        if action["type"] == "final":
            return action["content"]

        if action["type"] != "tool_call":
            raise ValueError("Unsupported action type")

        if action["tool"] != "get_payment_metrics":
            raise ValueError("Unknown tool requested")

        result = get_payment_metrics()

        messages.append({
            "role": "tool",
            "content": result,
        })

    raise RuntimeError("Agent exhausted its execution budget")


if __name__ == "__main__":
    answer = run_agent("Why is payment-api slow?")
    print("\nAgent answer:")
    print(answer)
