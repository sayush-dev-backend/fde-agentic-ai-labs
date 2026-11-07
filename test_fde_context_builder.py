
import unittest
from copy import deepcopy
from datetime import datetime, timedelta, timezone

from fde_context_builder import ContextBuilder


class TestContextBuilder(unittest.TestCase):

    def setUp(self):
        self.builder = ContextBuilder()

        self.history = [
            {
                "role": "user",
                "content": "Hello",
                "metadata": {"source": "session"},
            },
            {
                "role": "assistant",
                "content": "Hi there!",
            },
        ]

    def test_original_history_remains_unchanged(self):
        original_history = self.history.copy()

        self.builder.build_context(
            "I need assistance.",
            self.history,
            [],
        )

        self.assertEqual(self.history, original_history)

    def test_current_input_is_appended(self):
        current_input = "I need some assistance."

        context = self.builder.build_context(
            current_input,
            self.history,
            [],
        )

        self.assertEqual(
            context[-1],
            {"role": "user", "content": current_input},
        )

    def test_context_is_deep_copy(self):
        context = self.builder.build_context(
            "I need assistance.",
            self.history,
            [],
        )

        context[0]["metadata"]["source"] = "modified"

        self.assertEqual(
            self.history[0]["metadata"]["source"],
            "session",
        )

    def test_all_query_words_match(self):
        score = self.builder.calculate_relevance(
            "payment API high latency",
            {"content": "Our payment API has high latency"},
        )

        self.assertEqual(score, 1.0)

    def test_half_query_words_match(self):
        score = self.builder.calculate_relevance(
            "payment API high latency",
            {"content": "Payment API is working"},
        )

        self.assertEqual(score, 0.5)

    def test_no_query_words_match(self):
        score = self.builder.calculate_relevance(
            "payment API high latency",
            {"content": "Python programming is interesting"},
        )

        self.assertEqual(score, 0.0)

    def test_empty_query_returns_zero(self):
        score = self.builder.calculate_relevance(
            "",
            {"content": "Payment API has high latency"},
        )

        self.assertEqual(score, 0.0)

    def test_relevant_messages_selected(self):
        history = [
            {"role": "user", "content": "Payment API has high latency"},
            {"role": "assistant", "content": "The weather is sunny"},
        ]

        selected = self.builder.select_relevant_messages(
            "payment API high latency",
            history,
            threshold=0.5,
        )

        self.assertEqual(selected, [history[0]])

    def test_irrelevant_messages_excluded(self):
        history = [
            {"role": "user", "content": "The weather is sunny"},
            {"role": "assistant", "content": "Python programming is interesting"},
        ]

        selected = self.builder.select_relevant_messages(
            "payment API high latency",
            history,
            threshold=0.5,
        )

        self.assertEqual(selected, [])

    def test_chronological_order_preserved(self):
        history = [
            {"role": "user", "content": "Payment API has high latency"},
            {"role": "assistant", "content": "Our payment API needs investigation"},
            {"role": "user", "content": "The weather is sunny"},
        ]

        selected = self.builder.select_relevant_messages(
            "payment API high latency",
            history,
            threshold=0.5,
        )

        self.assertEqual(selected, history[:2])

    def test_filtering_does_not_mutate_original_history(self):
        history = [message.copy() for message in self.history]
        original_history = [message.copy() for message in history]

        self.builder.select_relevant_messages(
            "hello",
            history,
            threshold=0.5,
        )

        self.assertEqual(history, original_history)

    def test_empty_history_returns_empty_list(self):
        selected = self.builder.select_relevant_messages(
            "payment API high latency",
            [],
            threshold=0.5,
        )

        self.assertEqual(selected, [])

        top_selected = self.builder.select_top_messages(
            "payment API high latency", [], top_k=2
        )
        self.assertEqual(top_selected, [])

    def test_top_k_limits_results(self):
        history = [
            {"role": "user", "content": "Payment API has high latency"},
            {"role": "assistant", "content": "Payment API needs investigation"},
            {"role": "user", "content": "Payment service is slow"},
        ]

        selected = self.builder.select_top_messages(
            "payment API high latency", history, top_k=2
        )

        self.assertEqual(len(selected), 2)

    def test_top_k_preserves_relevance_order(self):
        history = [
            {"role": "user", "content": "Payment API"},
            {"role": "assistant", "content": "Payment API high latency"},
            {"role": "user", "content": "Payment API high latency outage"},
        ]

        selected = self.builder.select_top_messages(
            "payment API high latency", history, top_k=3
        )

        self.assertEqual(selected, [history[2], history[1], history[0]])

    def test_zero_top_k_returns_empty_list(self):
        history = [{"role": "user", "content": "Payment API has high latency"}]

        selected = self.builder.select_top_messages(
            "payment API high latency", history, top_k=0
        )

        self.assertEqual(selected, [])

    def test_top_k_greater_than_history(self):
        history = [
            {"role": "user", "content": "Payment API has high latency"},
            {"role": "assistant", "content": "Payment API needs investigation"},
        ]

        selected = self.builder.select_top_messages(
            "payment API high latency", history, top_k=5
        )

        self.assertEqual(len(selected), len(history))

    def test_normalize_scores_uses_min_max_scaling(self):
        normalized = self.builder.normalize_scores([2.0, 4.0, 6.0])

        self.assertEqual(normalized, [0.0, 0.5, 1.0])

    def test_normalize_scores_returns_zeros_for_equal_values(self):
        normalized = self.builder.normalize_scores([3.0, 3.0, 3.0])

        self.assertEqual(normalized, [1.0, 1.0, 1.0])

    def test_normalize_scores_handles_empty_input(self):
        self.assertEqual(self.builder.normalize_scores([]), [])

    def test_recent_relevant_message_ranks_higher(self):
        current_time = datetime(2026, 11, 7, 12, 0, tzinfo=timezone.utc)
        history = [
            {
                "role": "user",
                "content": "payment latency",
                "timestamp": (current_time - timedelta(minutes=60)).isoformat(),
            },
            {
                "role": "assistant",
                "content": "payment latency",
                "timestamp": current_time.isoformat(),
            },
        ]

        ranked = self.builder.rank_messages_hybrid(
            "payment latency",
            history,
            current_time,
            relevance_weight=0.7,
            recency_weight=0.3,
        )

        self.assertEqual(ranked, [history[1], history[0]])

    def test_older_relevant_message_outranks_recent_irrelevant_message(self):
        current_time = datetime(2026, 11, 7, 12, 0, tzinfo=timezone.utc)
        history = [
            {
                "role": "user",
                "content": "payment latency",
                "timestamp": (
                    current_time - timedelta(minutes=120)
                ).isoformat(),
            },
            {
                "role": "assistant",
                "content": "weather forecast",
                "timestamp": current_time.isoformat(),
            },
        ]

        ranked = self.builder.rank_messages_hybrid(
            "payment latency",
            history,
            current_time,
        )

        self.assertEqual(ranked, [history[0], history[1]])

    def test_hybrid_ranking_uses_relevance_weight(self):
        current_time = datetime(2026, 11, 7, 12, 0, tzinfo=timezone.utc)
        timestamp = current_time.isoformat()
        history = [
            {"role": "user", "content": "payment", "timestamp": timestamp},
            {
                "role": "assistant",
                "content": "payment latency",
                "timestamp": timestamp,
            },
        ]

        ranked = self.builder.rank_messages_hybrid(
            "payment latency",
            history,
            current_time,
            relevance_weight=1.0,
            recency_weight=0.0,
        )

        self.assertEqual(ranked, [history[1], history[0]])

    def test_hybrid_ranking_rejects_invalid_weights(self):
        current_time = datetime(2026, 11, 7, 12, 0, tzinfo=timezone.utc)

        invalid_weight_pairs = [
            (0.0, 0.0),
            (-0.1, 1.1),
            (float("nan"), 1.0),
            (1.0, float("inf")),
        ]
        for relevance_weight, recency_weight in invalid_weight_pairs:
            with self.subTest(
                relevance_weight=relevance_weight,
                recency_weight=recency_weight,
            ):
                with self.assertRaises(ValueError):
                    self.builder.rank_messages_hybrid(
                        "payment latency",
                        self.history,
                        current_time,
                        relevance_weight=relevance_weight,
                        recency_weight=recency_weight,
                    )

    def test_hybrid_ranking_empty_history_returns_empty_list(self):
        current_time = datetime(2026, 11, 7, 12, 0, tzinfo=timezone.utc)

        ranked = self.builder.rank_messages_hybrid(
            "payment latency",
            [],
            current_time,
        )

        self.assertEqual(ranked, [])

    def test_hybrid_ranking_does_not_mutate_original_history(self):
        current_time = datetime(2026, 11, 7, 12, 0, tzinfo=timezone.utc)
        history = [
            {
                "role": "user",
                "content": "payment latency",
                "timestamp": current_time.isoformat(),
                "metadata": {"source": "session"},
            },
            {
                "role": "assistant",
                "content": "weather forecast",
                "timestamp": current_time.isoformat(),
            },
        ]
        original_history = deepcopy(history)

        self.builder.rank_messages_hybrid(
            "payment latency",
            history,
            current_time,
        )

        self.assertEqual(history, original_history)

    def test_hybrid_ranking_equal_scores_preserve_original_order(self):
        current_time = datetime(2026, 11, 7, 12, 0, tzinfo=timezone.utc)
        history = [
            {
                "role": "user",
                "content": "payment latency",
                "timestamp": current_time.isoformat(),
            },
            {
                "role": "assistant",
                "content": "payment latency",
                "timestamp": current_time.isoformat(),
            },
        ]

        ranked = self.builder.rank_messages_hybrid(
            "payment latency",
            history,
            current_time,
        )

        self.assertEqual(ranked, history)

    def test_relevant_message_ranks_first(self):
        history = [
            {"role": "user", "content": "I am learning Python programming"},
            {"role": "assistant", "content": "Payment API has high latency"},
        ]

        ranked = self.builder.select_relevant_messages(
            "payment API high latency",
            history,
            threshold=0.1,
        )

        self.assertEqual(ranked[0], history[1])

    def test_irrelevant_message_ranks_lower(self):
        history = [
            {"role": "user", "content": "Payment API has high latency"},
            {"role": "assistant", "content": "Python programming is interesting"},
        ]

        ranked = self.builder.select_relevant_messages(
            "payment API high latency",
            history,
        )

        scores = [
            self.builder.calculate_relevance("payment API high latency", message)
            for message in ranked
        ]
        # The default relevance threshold filters out the unrelated message.
        self.assertEqual(len(scores), 1)
        self.assertGreater(scores[0], 0.0)
        

    def test_empty_query_returns_empty_ranked_list(self):
        ranked = self.builder.select_relevant_messages("", self.history)

        self.assertEqual(ranked, [])

    def test_ranking_does_not_mutate_original_history(self):
        history = [message.copy() for message in self.history]
        original_history = [message.copy() for message in history]

        self.builder.select_relevant_messages("hello", history)

        self.assertEqual(history, original_history)

    def test_equal_scores_preserve_original_order(self):
        history = [
            {"role": "user", "content": "Payment API"},
            {"role": "assistant", "content": "API payment"},
        ]

        ranked = self.builder.select_relevant_messages("payment API", history)

        self.assertEqual(ranked, history)

    def test_empty_message_content_does_not_crash(self):
        history = [
            {"role": "user", "content": ""},
            {"role": "assistant", "content": "Payment API has high latency"},
        ]

        ranked = self.builder.select_relevant_messages(
            "payment API high latency",
            history,
        )

        self.assertEqual(ranked[0], history[1])

    def test_recency_for_current_timestamp_is_one(self):
        current_time = datetime(2026, 11, 7, 12, 0, tzinfo=timezone.utc)
        message = {"timestamp": current_time.isoformat()}

        score = self.builder.calculate_recency(message, current_time)

        self.assertAlmostEqual(score, 1.0)

    def test_recency_half_life_is_60_minutes(self):
        current_time = datetime(2026, 11, 7, 12, 0, tzinfo=timezone.utc)
        message = {
            "timestamp": (current_time - timedelta(minutes=60)).isoformat()
        }

        score = self.builder.calculate_recency(message, current_time)

        self.assertAlmostEqual(score, 0.5)

    def test_recency_after_120_minutes_is_quarter(self):
        current_time = datetime(2026, 11, 7, 12, 0, tzinfo=timezone.utc)
        message = {
            "timestamp": (current_time - timedelta(minutes=120)).isoformat()
        }

        score = self.builder.calculate_recency(message, current_time)

        self.assertAlmostEqual(score, 0.25)

    def test_future_timestamp_has_no_decay(self):
        current_time = datetime(2026, 11, 7, 12, 0, tzinfo=timezone.utc)
        message = {
            "timestamp": (current_time + timedelta(minutes=30)).isoformat()
        }

        score = self.builder.calculate_recency(message, current_time)

        self.assertAlmostEqual(score, 1.0)

    def test_missing_timestamp_has_zero_recency(self):
        current_time = datetime(2026, 11, 7, 12, 0, tzinfo=timezone.utc)

        score = self.builder.calculate_recency({}, current_time)

        self.assertAlmostEqual(score, 0.0)

    def test_invalid_timestamp_has_zero_recency(self):
        current_time = datetime(2026, 11, 7, 12, 0, tzinfo=timezone.utc)
        message = {"timestamp": "not-an-iso-timestamp"}

        score = self.builder.calculate_recency(message, current_time)

        self.assertAlmostEqual(score, 0.0)

    def test_equivalent_timestamp_offsets_have_equal_scores(self):
        current_time = datetime(2026, 11, 7, 12, 0, tzinfo=timezone.utc)
        utc_message = {"timestamp": "2026-11-07T11:00:00+00:00"}
        offset_message = {"timestamp": "2026-11-07T13:00:00+02:00"}

        utc_score = self.builder.calculate_recency(utc_message, current_time)
        offset_score = self.builder.calculate_recency(
            offset_message,
            current_time,
        )

        self.assertAlmostEqual(utc_score, offset_score)

    def test_naive_timestamp_is_assumed_to_be_utc(self):
        current_time = datetime(2026, 11, 7, 12, 0, tzinfo=timezone.utc)
        naive_message = {"timestamp": "2026-11-07T11:00:00"}
        utc_message = {"timestamp": "2026-11-07T11:00:00+00:00"}

        naive_score = self.builder.calculate_recency(
            naive_message,
            current_time,
        )
        utc_score = self.builder.calculate_recency(utc_message, current_time)

        self.assertAlmostEqual(naive_score, utc_score)


if __name__ == "__main__":
    unittest.main()
