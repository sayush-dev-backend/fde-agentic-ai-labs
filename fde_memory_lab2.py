"""Simple in-process, user-scoped long-term memory for the FDE agent.

This lab intentionally uses dictionaries so the storage semantics are easy to
inspect. Data is not durable across process restarts; persistence is a later lab.
"""

from typing import Any


class LongTermMemory:
    """Store selected reusable facts, isolated by trusted application user ID."""

    def __init__(self) -> None:
        self.memories: dict[str, dict[str, Any]] = {}

    def remember(self, user_id: str, key: str, value: Any) -> None:
        if not isinstance(user_id, str) or not user_id.strip():
            raise ValueError("user_id must be a non-empty string")
        if not isinstance(key, str) or not key.strip():
            raise ValueError("key must be a non-empty string")

        self.memories.setdefault(user_id, {})[key] = value

    def recall(self, user_id: str, key: str) -> Any | None:
        if not isinstance(user_id, str) or not user_id.strip():
            raise ValueError("user_id must be a non-empty string")
        if not isinstance(key, str) or not key.strip():
            raise ValueError("key must be a non-empty string")

        return self.memories.get(user_id, {}).get(key)

    def forget(self, user_id: str, key: str) -> None:
        if not isinstance(user_id, str) or not user_id.strip():
            raise ValueError("user_id must be a non-empty string")
        if not isinstance(key, str) or not key.strip():
            raise ValueError("key must be a non-empty string")

        user_memories = self.memories.get(user_id)
        if user_memories is not None:
            user_memories.pop(key, None)
            if not user_memories:
                self.memories.pop(user_id, None)
