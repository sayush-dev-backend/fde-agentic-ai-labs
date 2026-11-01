from typing import Any
from fde_memory_interfaces import MemoryStore


class BrokenMemory:
    def remember(self, user_id: str, key: str, value: Any) -> None:
        ...

    def recall(self, user_id: str, key: str) -> Any | None:
        ...

    def forget(self, user_id: str, key: str) -> bool:
         return True

def use_memory(memory: MemoryStore) -> None:
    pass


memory = BrokenMemory()
use_memory(memory)