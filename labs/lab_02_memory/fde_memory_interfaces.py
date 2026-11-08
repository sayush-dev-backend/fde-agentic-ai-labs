from typing import Any, Protocol


class MemoryStore(Protocol):
    """A protocol for a memory store that can remember, recall, and forget values."""

    def remember(self, user_id: str, key: str, value: Any) -> None:
        """Store a value associated with a user ID and key."""
        ...

    def recall(self, user_id: str, key: str) -> Any | None:
        """Retrieve a value associated with a user ID and key."""
        ...

    def forget(self, user_id: str, key: str) -> bool:
        """Forget a value associated with a user ID and key. Returns True if the key existed and was removed, False otherwise."""
        ...