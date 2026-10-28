from typing import Any

MAX_STEPS = 3


def run_agent(
    actions: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Execute a sequence of simulated agent actions.

    Process at most MAX_STEPS actions.
    Stop on a final answer, invalid action, or exhausted budget.
    """
    results = []

    for step, action in enumerate(actions, start=1):

        if not isinstance(action, dict):
            results.append({
                "status": "error",
                "message": "Action must be a dictionary",
            })
            break

        action_type = action.get("type")

        if action_type not in ("tool_call", "final"):
            results.append({
                "status": "error",
                "message": f"Unknown action type: {action_type!r}",
            })
            break

        if action_type == "final":
            if "content" not in action:
                results.append({
                    "status": "error",
                    "message": "Final action is missing 'content'",
                })
            else:
                results.append({
                    "status": "completed",
                    "answer": action["content"],
                })
            break

        # From here, action_type must be "tool_call".
        tool_name = action.get("tool")

        if not isinstance(tool_name, str) or not tool_name.strip():
            results.append({
                "status": "error",
                "message": "Tool call is missing a valid 'tool' field",
            })
            break

        results.append({
            "status": "tool_requested",
            "tool": tool_name,
        })

        if step == MAX_STEPS:
            results.append({
                "status": "error",
                "message": "Agent exhausted its execution budget",
            })
            break

    return results

actions = [
    {"type": "tool_call", "tool": "get_payment_metrics"},
    {"type": "tool_call", "tool": "get_payment_metrics"},
    {"type": "tool_call", "tool": "get_payment_metrics"},
    {"type": "final", "content": "Latency is high."},
]

print(run_agent(actions))