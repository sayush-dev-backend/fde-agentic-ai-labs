"""
FDE Incident Investigator — Lab 1
Python 3.10+; no third-party dependencies required.

This lab focuses on the agent execution boundary:
tool registry -> argument validation -> authorization -> execution
-> result validation.
"""

from dataclasses import dataclass
from typing import Any, Callable
import math  # 🆕 CHANGE: Used to reject NaN and infinity in metrics.


# ---------- 1. A tool implementation ----------

def get_payment_metrics(
    service: str,
    window_minutes: int,
) -> dict[str, Any]:
    """Return mocked monitoring metrics for an approved service."""

    # A real implementation would call an authenticated monitoring API.
    return {
        "service": service,
        "window_minutes": window_minutes,
        "p95_latency_ms": 1420,
        "error_rate_percent": 8.4,
        "baseline_p95_latency_ms": 180,
        "source": "mock-monitoring-data",
    }


# ---------- 2. Describe the tool and its contract ----------

@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    implementation: Callable[..., Any]
    allowed_roles: frozenset[str]
    allowed_services: frozenset[str]


# ---------- 3. Validate tool arguments ----------

def validate_metrics_args(args: dict[str, Any]) -> None:
    """Reject unknown/missing fields and values with the wrong type."""

    expected = {"service", "window_minutes"}

    if set(args) != expected:
        raise ValueError(
            f"Expected exactly {sorted(expected)}; got {sorted(args)}"
        )

    service = args["service"]
    window = args["window_minutes"]

    if not isinstance(service, str) or not service.strip():
        raise ValueError("'service' must be a non-empty string")

    # bool is a subclass of int in Python, so reject it explicitly.
    if isinstance(window, bool) or not isinstance(window, int):
        raise ValueError("'window_minutes' must be an integer")

    if not 1 <= window <= 30:
        raise ValueError("'window_minutes' must be between 1 and 30")


# ---------- 4. Validate tool results ----------

def validate_metrics_result(result: dict[str, Any]) -> None:
    """
    Validate the structure and values returned by the monitoring tool.

    🆕 CHANGE:
    This function is now called by execute_tool() after execution.
    """

    # Validate the result structure.
    if not isinstance(result, dict):
        raise ValueError("Metrics result must be a dictionary")

    required_fields = {
        "service",
        "p95_latency_ms",
        "error_rate_percent",
        "source",
    }

    if not required_fields.issubset(result):
        raise ValueError("Metrics result is missing required fields")

    # Validate service.
    service = result["service"]

    if not isinstance(service, str) or not service.strip():
        raise ValueError("Service must be a non-empty string")

    # Validate latency.
    latency = result["p95_latency_ms"]

    # 🆕 CHANGE: Reject booleans, invalid types, NaN and infinity.
    if (
        isinstance(latency, bool)
        or not isinstance(latency, (int, float))
        or not math.isfinite(latency)
    ):
        raise ValueError("Invalid latency value")

    if latency < 0:
        raise ValueError("Latency cannot be negative")

    # Validate error rate.
    error_rate = result["error_rate_percent"]

    # 🆕 CHANGE: Reject booleans, invalid types, NaN and infinity.
    if (
        isinstance(error_rate, bool)
        or not isinstance(error_rate, (int, float))
        or not math.isfinite(error_rate)
    ):
        raise ValueError("Invalid error rate")

    if error_rate < 0 or error_rate > 100:
        raise ValueError("Error rate must be between 0 and 100")

    # Validate source.
    source = result["source"]

    if not isinstance(source, str) or not source.strip():
        raise ValueError("Source must be a non-empty string")


# ---------- 5. Authorize tool calls ----------

def authorize_metrics_call(
    *,
    role: str,
    service: str,
    tool: ToolSpec,
) -> None:
    """Enforce policy using trusted application identity/context."""

    if role not in tool.allowed_roles:
        raise PermissionError(
            f"Role {role!r} cannot use {tool.name!r}"
        )

    if service not in tool.allowed_services:
        raise PermissionError(
            f"Role {role!r} is not allowed to inspect service {service!r}"
        )


# ---------- 6. Register tools ----------

TOOLS: dict[str, ToolSpec] = {
    "get_payment_metrics": ToolSpec(
        name="get_payment_metrics",
        description=(
            "Retrieve p95 latency and error rate for an approved service "
            "over a recent time window."
        ),
        implementation=get_payment_metrics,
        allowed_roles=frozenset({
            "on_call_engineer",
            "platform_admin",
            "incident_responder",
        }),
        allowed_services=frozenset({
            "payment-api",
            "checkout-api",
        }),
    )
}


# ---------- 7. Secure tool execution boundary ----------

def execute_tool(
    *,
    tool_name: str,
    arguments: dict[str, Any],
    principal_role: str,
) -> dict[str, Any]:
    """
    Validate, authorize, execute, and validate a tool request.

    In production, principal_role must come from trusted,
    server-side authentication—not from the LLM or user text.
    """

    # 1. Resolve the requested tool.
    tool = TOOLS.get(tool_name)

    if tool is None:
        raise LookupError(f"Unknown tool: {tool_name!r}")

    # 2. Validate the argument container.
    if not isinstance(arguments, dict):
        raise TypeError("Tool arguments must be a dictionary")

    # 3. Validate the caller's role.
    if principal_role not in tool.allowed_roles:
        raise PermissionError(
            f"Role '{principal_role}' is not authorized "
            f"to use tool '{tool_name}'"
        )

    # 4. Validate argument names, types, and permitted values.
    validate_metrics_args(arguments)

    # 5. Enforce service-level authorization.
    authorize_metrics_call(
        role=principal_role,
        service=arguments["service"],
        tool=tool,
    )

    # 6. Execute only after all authorization checks succeed.
    result = tool.implementation(**arguments)

    # 🆕 CHANGE: Validate the result before returning it.
    # Previously, the function returned the tool output directly,
    # allowing invalid monitoring data to pass through.
    validate_metrics_result(result)

    # 7. Return only validated results.
    return result


# ---------- 8. Run a few experiments ----------

def demo() -> None:
    print("\nCASE 1 — permitted request")

    result = execute_tool(
        tool_name="get_payment_metrics",
        arguments={
            "service": "payment-api",
            "window_minutes": 10,
        },
        principal_role="on_call_engineer",
    )

    print(result)

    print("\nCASE 2 — unknown tool")

    try:
        execute_tool(
            tool_name="delete_database_records",
            arguments={
                "service": "payment-api",
                "window_minutes": 10,
            },
            principal_role="on_call_engineer",
        )
    except Exception as exc:
        print(f"Blocked: {type(exc).__name__}: {exc}")

    print("\nCASE 3 — invalid arguments")

    try:
        execute_tool(
            tool_name="get_payment_metrics",
            arguments={
                "service": "payment-api",
                "window_minutes": "all",
            },
            principal_role="on_call_engineer",
        )
    except Exception as exc:
        print(f"Blocked: {type(exc).__name__}: {exc}")

    print("\nCASE 4 — unauthorized service")

    try:
        execute_tool(
            tool_name="get_payment_metrics",
            arguments={
                "service": "payroll-db",
                "window_minutes": 10,
            },
            principal_role="on_call_engineer",
        )
    except Exception as exc:
        print(f"Blocked: {type(exc).__name__}: {exc}")


if __name__ == "__main__":
    demo()