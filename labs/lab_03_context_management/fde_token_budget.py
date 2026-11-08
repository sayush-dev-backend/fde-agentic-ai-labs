from copy import deepcopy

import tiktoken


class TokenCounter:

    def __init__(self, model: str):
        try:
            self.encoding = tiktoken.encoding_for_model(model)
        except KeyError as exc:
            raise ValueError(f"Unsupported model: {model!r}") from exc

    def count_tokens(self, text: str) -> int:
        if not isinstance(text, str):
            raise TypeError("text must be a string")
        if not text:
            return 0
        return len(self.encoding.encode(text))


def count_tokens(text: str, model: str = "gpt-4o") -> int:
    """Count tokens in text using the selected model's tokenizer."""
    return TokenCounter(model).count_tokens(text)



class TokenBudgetManager:

    def __init__(
        self,
        context_window: int,
        reserved_output_tokens: int,
    ):
        for name, value in (
            ("context_window", context_window),
            ("reserved_output_tokens", reserved_output_tokens),
        ):
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"{name} must be an integer")
            if value <= 0:
                raise ValueError(f"{name} must be positive")

        if reserved_output_tokens > context_window:
            raise ValueError(
                "reserved_output_tokens cannot exceed context_window"
            )

        self.context_window = context_window
        self.reserved_output_tokens = reserved_output_tokens

    def get_available_budget(self) -> int:
        return self.context_window - self.reserved_output_tokens

    def allocate_budget(
        self,
        allocations: dict[str, int],
    ) -> dict[str, int]:
        if not isinstance(allocations, dict):
            raise TypeError("allocations must be a dictionary")
        if not allocations:
            raise ValueError("allocations cannot be empty")

        available_budget = self.get_available_budget()
        validated_allocations: dict[str, int] = {}
        total_allocated = 0

        for component_name, allocation in allocations.items():
            if not isinstance(component_name, str):
                raise TypeError("component names must be non-empty strings")
            if not component_name.strip():
                raise ValueError("component names must be non-empty strings")
            if isinstance(allocation, bool) or not isinstance(allocation, int):
                raise TypeError("allocation values must be positive integers")
            if allocation <= 0:
                raise ValueError("allocation values must be positive integers")

            total_allocated += allocation
            validated_allocations[component_name] = allocation

        if total_allocated > available_budget:
            raise ValueError(
                "sum of allocations cannot exceed the available input budget"
            )

        return validated_allocations

class ContextTruncator:

    def __init__(self, token_counter: TokenCounter):
        if token_counter is None or not hasattr(token_counter, "count_tokens"):
            raise TypeError("token_counter must provide a count_tokens method")
        self.token_counter = token_counter

    def _group_turns(self, conversation_history: list[dict]) -> list[list[dict]]:
        turns: list[list[dict]] = []
        current_turn: list[dict] = []

        for message in conversation_history:
            role = message.get("role")

            if role == "user" and current_turn and current_turn[-1].get("role") != "user":
                turns.append(current_turn)
                current_turn = []

            current_turn.append(message)

        if current_turn:
            turns.append(current_turn)

        return turns

    def truncate_history(
        self,
        conversation_history: list[dict],
        token_budget: int,
    ) -> list[dict]:
        if not isinstance(conversation_history, list):
            raise TypeError("conversation_history must be a list of message dictionaries")
        if isinstance(token_budget, bool) or not isinstance(token_budget, int):
            raise TypeError("token_budget must be a positive integer")
        if token_budget <= 0:
            raise ValueError("token_budget must be a positive integer")

        if not conversation_history:
            return []

        for message in conversation_history:
            if not isinstance(message, dict):
                raise TypeError("conversation_history entries must be dictionaries")
            if "content" not in message:
                raise ValueError("each message must include a 'content' field")
            if not isinstance(message["content"], str):
                raise TypeError("message content must be a string")

        turns = self._group_turns(conversation_history)
        turn_token_counts = []
        for turn in turns:
            total_tokens = 0
            for message in turn:
                total_tokens += self.token_counter.count_tokens(message["content"])
            turn_token_counts.append(total_tokens)

        newest_turn_index = len(turns) - 1
        newest_turn_tokens = turn_token_counts[newest_turn_index]
        if newest_turn_tokens > token_budget:
            raise ValueError(
                "Newest conversation turn exceeds the available token budget. "
                f"Turn size: {newest_turn_tokens} > {token_budget}."
            )

        total_tokens = sum(turn_token_counts)
        while total_tokens > token_budget:
            removed_tokens = turn_token_counts.pop(0)
            turns.pop(0)
            total_tokens -= removed_tokens

        return [
            deepcopy(message)
            for turn in turns
            for message in turn
        ]