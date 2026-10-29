from typing import Any


class LongTermMemory:

    def remember(self,user_id : str,  key: str, value: Any) -> None:
        """
        Store a memory by key.
        """
        if user_id not in self.memories:
            self.memories[user_id] = {}
        self.memories[user_id][key] = value

    def recall(self, user_id: str, key: str) -> Any | None:
        """
        Retrieve a memory by key.
        """
        return self.memories.get(user_id, {}).get(key)

    def forget(self, user_id: str, key: str) -> None:
       """
       Delete a memory by key.
       """
       if user_id in self.memories and key in self.memories[user_id]:
            del self.memories[user_id][key]



    def __init__(self) -> None:
        self.memories: dict[str, Any] = {}
