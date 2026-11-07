
import math
import re
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any
from rank_bm25 import BM25Okapi


class ContextBuilder:

    def build_context(
        self,
        current_input: str,
        conversation_history: list[dict[str, Any]],
        retrieved_memories: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Build an LLM-ready context from conversation history
        and the current user input.
        """

        context = deepcopy(conversation_history)

        context.append({
            "role": "user",
            "content": current_input,
        })

        return context

    def calculate_relevance(
        self,
        query: str,
        message: dict[str, Any],
    ) -> float:
        """
        Calculate baseline keyword-based relevance.

        Returns a score between 0.0 and 1.0.
        """

        query_words = set(
            re.findall(r"\b\w+\b", query.lower())
        )

        message_words = set(
            re.findall(
                r"\b\w+\b",
                str(message.get("content", "")).lower(),
            )
        )

        if not query_words:
            return 0.0

        matching_words = query_words.intersection(message_words)

        return len(matching_words) / len(query_words)

    def select_relevant_messages(
        self,
        query: str,
        conversation_history: list[dict[str, Any]],
        threshold: float = 0.3,
    ) -> list[dict[str, Any]]:
        return deepcopy([
            message
            for message in conversation_history
            if self.calculate_relevance(query, message) >= threshold
        ])
    def tokenize(self, text: str) -> list[str]:
        """
        Tokenize the input text into a list of words.
        """
        return re.findall(r"\b\w+\b", str(text).lower())

    def rank_messages(
            self,
            query: str,
            conversation_history: list[dict[str, Any]],
        ) -> list[dict[str, Any]]:
            """Return a copied history ranked from most to least relevant."""
            query_tokens = self.tokenize(query)
            if not query_tokens or not conversation_history:
                return []

            messages = deepcopy(conversation_history)
            documents = [
                self.tokenize(str(message.get("content", "")))
                for message in messages
            ]
            if not any(documents):
                return []

            scores = self.normalize_scores(
                list(BM25Okapi(documents).get_scores(query_tokens))
            )
            ranked = sorted(
                zip(messages, scores),
                key=lambda pair: (
                    self.calculate_relevance(query, pair[0]),
                    pair[1],
                ),
                reverse=True,
            )
            return [message for message, _score in ranked]

    def select_top_messages(
        self,
        query: str,
        conversation_history: list[dict[str, Any]],
        top_k: int,
    ) -> list[dict[str, Any]]:
        """Return at most ``top_k`` messages ranked by relevance."""
        if top_k <= 0:
            return []
        return self.rank_messages(query, conversation_history)[:top_k]

    def rank_messages_hybrid(
        self,
        query: str,
        conversation_history: list[dict[str, Any]],
        current_time: datetime,
        relevance_weight: float = 0.7,
        recency_weight: float = 0.3,
    ) -> list[dict[str, Any]]:
        """Rank messages using normalized BM25 relevance and recency."""
        if (
            not math.isfinite(relevance_weight)
            or not math.isfinite(recency_weight)
            or relevance_weight < 0
            or recency_weight < 0
            or relevance_weight + recency_weight <= 0
        ):
            raise ValueError("Ranking weights must be non-negative and non-zero")

        query_tokens = self.tokenize(query)
        if not query_tokens or not conversation_history:
            return []

        messages = deepcopy(conversation_history)
        documents = [
            self.tokenize(str(message.get("content", "")))
            for message in messages
        ]
        if not any(documents):
            return []

        bm25_scores = self.normalize_scores(
            list(BM25Okapi(documents).get_scores(query_tokens))
        )
        keyword_scores = [
            self.calculate_relevance(query, message)
            for message in messages
        ]
        relevance_scores = [
            (bm25_score + keyword_score) / 2
            for bm25_score, keyword_score in zip(
                bm25_scores,
                keyword_scores,
            )
        ]
        combined_scores = [
            relevance_weight * relevance_score
            + recency_weight * self.calculate_recency(message, current_time)
            for message, relevance_score in zip(messages, relevance_scores)
        ]
        ranked = sorted(
            zip(messages, combined_scores),
            key=lambda pair: pair[1],
            reverse=True,
        )
        return [message for message, _score in ranked]

    def normalize_scores(
        self,
        scores: list[float],
    ) -> list[float]:
        if not scores:
            return []

        minimum = min(scores)
        maximum = max(scores)
        score_range = maximum - minimum

        if score_range == 0:
            return [1.0] * len(scores)

        return [
            (score - minimum) / score_range
            for score in scores
        ]
    
    def calculate_recency(
            self,
            message: dict[str, Any],
            current_time: datetime,
        ) -> float:
            """Return exponential recency decay with a 60-minute half-life."""
            timestamp = message.get("timestamp")
            if not isinstance(timestamp, str):
                return 0.0

            try:
                message_time = datetime.fromisoformat(timestamp)
            except ValueError:
                return 0.0

            if message_time.tzinfo is None:
                message_time = message_time.replace(tzinfo=timezone.utc)
            else:
                message_time = message_time.astimezone(timezone.utc)

            if current_time.tzinfo is None:
                normalized_current_time = current_time.replace(
                    tzinfo=timezone.utc
                )
            else:
                normalized_current_time = current_time.astimezone(timezone.utc)

            age_minutes = max(
                0.0,
                (normalized_current_time - message_time).total_seconds() / 60,
            )
            return math.exp(-math.log(2) * age_minutes / 60)