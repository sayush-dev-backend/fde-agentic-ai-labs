import unittest

from labs.lab_03_context_management.fde_token_budget import (
    TokenBudgetManager,
    count_tokens,
)


class TestTokenBudget(unittest.TestCase):

    def test_empty_string_returns_zero_tokens(self):
        self.assertEqual(count_tokens(""), 0)

    def test_normal_text_returns_positive_token_count(self):
        self.assertGreater(count_tokens("This is a normal sentence."), 0)

    def test_long_text_has_more_tokens_than_short_text(self):
        short_text = "Hello."
        long_text = " ".join(["Hello, this is a longer piece of text."] * 20)
        self.assertGreater(count_tokens(long_text), count_tokens(short_text))

    def test_non_string_input_raises_type_error(self):
        for value in (42, None):
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    count_tokens(value)

    def test_unsupported_model_raises_value_error(self):
        with self.assertRaises(ValueError):
            count_tokens("Some text", model="unsupported-model")

    def test_punctuation_is_counted_successfully(self):
        self.assertGreater(count_tokens("!!! ... ??? , ; :"), 0)

    def test_available_budget_is_context_minus_reserved_output(self):
        manager = TokenBudgetManager(
            context_window=16000,
            reserved_output_tokens=4000,
        )
        self.assertEqual(manager.get_available_budget(), 12000)

    def test_valid_configuration_calculates_available_budget(self):
        manager = TokenBudgetManager(
            context_window=8000,
            reserved_output_tokens=2000,
        )
        self.assertEqual(manager.context_window, 8000)
        self.assertEqual(manager.reserved_output_tokens, 2000)
        self.assertEqual(manager.get_available_budget(), 6000)

    def test_zero_context_window_raises_value_error(self):
        with self.assertRaises(ValueError):
            TokenBudgetManager(0, 1)

    def test_negative_context_window_raises_value_error(self):
        with self.assertRaises(ValueError):
            TokenBudgetManager(-1, 1)

    def test_zero_output_reservation_raises_value_error(self):
        with self.assertRaises(ValueError):
            TokenBudgetManager(10, 0)

    def test_negative_output_reservation_raises_value_error(self):
        with self.assertRaises(ValueError):
            TokenBudgetManager(10, -1)

    def test_output_exceeds_context_window_raises_value_error(self):
        with self.assertRaises(ValueError):
            TokenBudgetManager(100, 101)

    def test_float_input_raises_type_error(self):
        for value in (1.5, 2.0):
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    TokenBudgetManager(value, 1)
                with self.assertRaises(TypeError):
                    TokenBudgetManager(1, value)

    def test_boolean_input_raises_type_error(self):
        for value in (True, False):
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    TokenBudgetManager(value, 1)
                with self.assertRaises(TypeError):
                    TokenBudgetManager(1, value)

    def test_token_budgets_must_be_positive_integers(self):
        for value in (0, -1):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    TokenBudgetManager(value, 1)
                with self.assertRaises(ValueError):
                    TokenBudgetManager(1, value)

        for value in (1.5, "10", True):
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    TokenBudgetManager(value, 1)
                with self.assertRaises(TypeError):
                    TokenBudgetManager(1, value)

    def test_reserved_output_tokens_cannot_exceed_context_window(self):
        with self.assertRaises(ValueError):
            TokenBudgetManager(
                context_window=100,
                reserved_output_tokens=101,
            )

    def test_allocate_budget_accepts_valid_allocation_dict(self):
        manager = TokenBudgetManager(1000, 200)
        allocations = {"system": 200, "tools": 300, "memory": 150}
        self.assertEqual(manager.allocate_budget(allocations), allocations)

    def test_allocate_budget_rejects_empty_dictionary(self):
        manager = TokenBudgetManager(1000, 200)
        with self.assertRaises(ValueError):
            manager.allocate_budget({})

    def test_allocate_budget_rejects_non_string_component_names(self):
        manager = TokenBudgetManager(1000, 200)
        with self.assertRaises(TypeError):
            manager.allocate_budget({123: 100})

    def test_allocate_budget_rejects_empty_component_name(self):
        manager = TokenBudgetManager(1000, 200)
        with self.assertRaises(ValueError):
            manager.allocate_budget({"": 100})

    def test_allocate_budget_rejects_non_positive_or_boolean_allocation_values(self):
        manager = TokenBudgetManager(1000, 200)

        with self.assertRaises(ValueError):
            manager.allocate_budget({"system": 0})
        with self.assertRaises(ValueError):
            manager.allocate_budget({"system": -1})
        with self.assertRaises(TypeError):
            manager.allocate_budget({"system": True})
        with self.assertRaises(TypeError):
            manager.allocate_budget({"system": 1.5})

    def test_allocate_budget_rejects_total_allocation_over_budget(self):
        manager = TokenBudgetManager(1000, 200)
        with self.assertRaises(ValueError):
            manager.allocate_budget({"system": 400, "tools": 400, "memory": 400})

    def test_allocate_budget_valid_allocations_return_dictionary(self):
        manager = TokenBudgetManager(1000, 200)
        allocations = {"system": 200, "tools": 300, "memory": 150}
        result = manager.allocate_budget(allocations)
        self.assertEqual(result, allocations)
        self.assertEqual(allocations, {"system": 200, "tools": 300, "memory": 150})

    def test_allocate_budget_rejects_empty_dictionary(self):
        manager = TokenBudgetManager(1000, 200)
        with self.assertRaises(ValueError):
            manager.allocate_budget({})

    def test_allocate_budget_rejects_non_dictionary_input(self):
        manager = TokenBudgetManager(1000, 200)
        with self.assertRaises(TypeError):
            manager.allocate_budget(["system", 200])

    def test_allocate_budget_rejects_empty_component_name(self):
        manager = TokenBudgetManager(1000, 200)
        with self.assertRaises(ValueError):
            manager.allocate_budget({"": 100})

    def test_allocate_budget_rejects_whitespace_only_component_name(self):
        manager = TokenBudgetManager(1000, 200)
        with self.assertRaises(ValueError):
            manager.allocate_budget({"   ": 100})

    def test_allocate_budget_rejects_non_string_component_names(self):
        manager = TokenBudgetManager(1000, 200)
        with self.assertRaises(TypeError):
            manager.allocate_budget({123: 100})

    def test_allocate_budget_rejects_zero_allocation(self):
        manager = TokenBudgetManager(1000, 200)
        with self.assertRaises(ValueError):
            manager.allocate_budget({"system": 0})

    def test_allocate_budget_rejects_negative_allocation(self):
        manager = TokenBudgetManager(1000, 200)
        with self.assertRaises(ValueError):
            manager.allocate_budget({"system": -1})

    def test_allocate_budget_rejects_boolean_allocation(self):
        manager = TokenBudgetManager(1000, 200)
        with self.assertRaises(TypeError):
            manager.allocate_budget({"system": True})

    def test_allocate_budget_rejects_float_allocation(self):
        manager = TokenBudgetManager(1000, 200)
        with self.assertRaises(TypeError):
            manager.allocate_budget({"system": 1.5})

    def test_allocate_budget_rejects_total_allocation_over_budget(self):
        manager = TokenBudgetManager(1000, 200)
        with self.assertRaises(ValueError):
            manager.allocate_budget({"system": 400, "tools": 400, "memory": 400})

    def test_allocate_budget_allows_allocation_exactly_equal_to_budget(self):
        manager = TokenBudgetManager(1000, 200)
        allocations = {"system": 300, "tools": 500}
        result = manager.allocate_budget(allocations)
        self.assertEqual(result, allocations)

    def test_allocate_budget_does_not_mutate_original_dictionary(self):
        manager = TokenBudgetManager(1000, 200)
        allocations = {"system": 200, "tools": 300}
        original = allocations.copy()
        result = manager.allocate_budget(allocations)
        self.assertEqual(result, allocations)
        self.assertEqual(allocations, original)

    def test_context_truncator_removes_oldest_complete_turns_first(self):
        class FakeTokenCounter:
            def count_tokens(self, text):
                return len(str(text).split())

        truncator = __import__("labs.lab_03_context_management.fde_token_budget", fromlist=["ContextTruncator"]).ContextTruncator(FakeTokenCounter())
        history = [
            {"role": "user", "content": "alpha beta"},
            {"role": "assistant", "content": "gamma"},
            {"role": "user", "content": "delta epsilon"},
            {"role": "assistant", "content": "zeta"},
            {"role": "user", "content": "eta theta"},
            {"role": "assistant", "content": "iota"},
        ]

        result = truncator.truncate_history(history, 5)

        self.assertEqual(result, [
            {"role": "user", "content": "eta theta"},
            {"role": "assistant", "content": "iota"},
        ])
        self.assertEqual(len(history), 6)

    def test_context_truncator_returns_new_list_without_mutating_original(self):
        class FakeTokenCounter:
            def count_tokens(self, text):
                return len(str(text).split())

        truncator = __import__("labs.lab_03_context_management.fde_token_budget", fromlist=["ContextTruncator"]).ContextTruncator(FakeTokenCounter())
        history = [
            {"role": "user", "content": "one two"},
            {"role": "assistant", "content": "three"},
            {"role": "user", "content": "four five"},
            {"role": "assistant", "content": "six"},
        ]
        original = [message.copy() for message in history]

        result = truncator.truncate_history(history, 6)

        self.assertIsNot(result, history)
        self.assertEqual(history, original)
        self.assertEqual(result, [
            {"role": "user", "content": "one two"},
            {"role": "assistant", "content": "three"},
            {"role": "user", "content": "four five"},
            {"role": "assistant", "content": "six"},
        ])

    def test_context_truncator_raises_when_newest_turn_exceeds_budget(self):
        class FakeTokenCounter:
            def count_tokens(self, text):
                return len(str(text).split())

        truncator = __import__("labs.lab_03_context_management.fde_token_budget", fromlist=["ContextTruncator"]).ContextTruncator(FakeTokenCounter())
        history = [
            {"role": "user", "content": "one two"},
            {"role": "assistant", "content": "three"},
            {"role": "user", "content": "four five six"},
            {"role": "assistant", "content": "seven eight nine"},
        ]

        with self.assertRaisesRegex(ValueError, "newest.*budget|budget"):
            truncator.truncate_history(history, 4)

    def test_context_truncator_validates_history_and_budget(self):
        class FakeTokenCounter:
            def count_tokens(self, text):
                return len(str(text).split())

        truncator = __import__("labs.lab_03_context_management.fde_token_budget", fromlist=["ContextTruncator"]).ContextTruncator(FakeTokenCounter())

        with self.assertRaises(TypeError):
            truncator.truncate_history("not-a-list", 10)
        with self.assertRaises(TypeError):
            truncator.truncate_history([{"role": "user", "content": 123}], 10)
        with self.assertRaises(TypeError):
            truncator.truncate_history([{"role": "user", "content": "hi"}], 1.5)
        with self.assertRaises(ValueError):
            truncator.truncate_history([{"role": "user", "content": "hi"}], 0)

    def test_context_truncator_removes_oldest_complete_turns_when_over_budget(self):
        class FakeTokenCounter:
            def count_tokens(self, text):
                return len(str(text).split())

        truncator = __import__("labs.lab_03_context_management.fde_token_budget", fromlist=["ContextTruncator"]).ContextTruncator(FakeTokenCounter())
        history = [
            {"role": "user", "content": "one two"},
            {"role": "assistant", "content": "three"},
            {"role": "user", "content": "four five"},
            {"role": "assistant", "content": "six"},
            {"role": "user", "content": "seven eight"},
            {"role": "assistant", "content": "nine"},
        ]

        result = truncator.truncate_history(history, 7)

        self.assertEqual(result, [
            {"role": "user", "content": "four five"},
            {"role": "assistant", "content": "six"},
            {"role": "user", "content": "seven eight"},
            {"role": "assistant", "content": "nine"},
        ])

    def test_context_truncator_preserves_newest_complete_turns(self):
        class FakeTokenCounter:
            def count_tokens(self, text):
                return len(str(text).split())

        truncator = __import__("labs.lab_03_context_management.fde_token_budget", fromlist=["ContextTruncator"]).ContextTruncator(FakeTokenCounter())
        history = [
            {"role": "user", "content": "one"},
            {"role": "assistant", "content": "two"},
            {"role": "user", "content": "three four"},
            {"role": "assistant", "content": "five"},
            {"role": "user", "content": "six seven"},
            {"role": "assistant", "content": "eight"},
        ]

        result = truncator.truncate_history(history, 6)

        self.assertEqual(result, [
            {"role": "user", "content": "three four"},
            {"role": "assistant", "content": "five"},
            {"role": "user", "content": "six seven"},
            {"role": "assistant", "content": "eight"},
        ])

    def test_context_truncator_preserves_chronological_ordering(self):
        class FakeTokenCounter:
            def count_tokens(self, text):
                return len(str(text).split())

        truncator = __import__("labs.lab_03_context_management.fde_token_budget", fromlist=["ContextTruncator"]).ContextTruncator(FakeTokenCounter())
        history = [
            {"role": "user", "content": "first"},
            {"role": "assistant", "content": "second"},
            {"role": "user", "content": "third"},
            {"role": "assistant", "content": "fourth"},
        ]

        result = truncator.truncate_history(history, 8)

        self.assertEqual(result, history)

    def test_context_truncator_returns_all_messages_when_within_budget(self):
        class FakeTokenCounter:
            def count_tokens(self, text):
                return len(str(text).split())

        truncator = __import__("labs.lab_03_context_management.fde_token_budget", fromlist=["ContextTruncator"]).ContextTruncator(FakeTokenCounter())
        history = [
            {"role": "user", "content": "hello"},
            {"role": "assistant", "content": "hi"},
            {"role": "user", "content": "next"},
            {"role": "assistant", "content": "okay"},
        ]

        result = truncator.truncate_history(history, 20)

        self.assertEqual(result, history)

    def test_context_truncator_handles_empty_history(self):
        class FakeTokenCounter:
            def count_tokens(self, text):
                return len(str(text).split())

        truncator = __import__("labs.lab_03_context_management.fde_token_budget", fromlist=["ContextTruncator"]).ContextTruncator(FakeTokenCounter())
        self.assertEqual(truncator.truncate_history([], 10), [])

    def test_context_truncator_groups_consecutive_user_messages_correctly(self):
        class FakeTokenCounter:
            def count_tokens(self, text):
                return len(str(text).split())

        truncator = __import__("labs.lab_03_context_management.fde_token_budget", fromlist=["ContextTruncator"]).ContextTruncator(FakeTokenCounter())
        history = [
            {"role": "user", "content": "first"},
            {"role": "user", "content": "second"},
            {"role": "assistant", "content": "reply"},
            {"role": "user", "content": "third"},
            {"role": "assistant", "content": "done"},
        ]

        result = truncator.truncate_history(history, 12)

        self.assertEqual(result, history)

    def test_context_truncator_preserves_tool_messages_within_their_initiating_turn(self):
        class FakeTokenCounter:
            def count_tokens(self, text):
                return len(str(text).split())

        truncator = __import__("labs.lab_03_context_management.fde_token_budget", fromlist=["ContextTruncator"]).ContextTruncator(FakeTokenCounter())
        history = [
            {"role": "user", "content": "request"},
            {"role": "tool", "content": "tool output"},
            {"role": "assistant", "content": "answer"},
            {"role": "user", "content": "next request"},
            {"role": "assistant", "content": "response"},
        ]

        result = truncator.truncate_history(history, 14)

        self.assertEqual(result, history)

    def test_context_truncator_rejects_invalid_token_budgets(self):
        class FakeTokenCounter:
            def count_tokens(self, text):
                return len(str(text).split())

        truncator = __import__("labs.lab_03_context_management.fde_token_budget", fromlist=["ContextTruncator"]).ContextTruncator(FakeTokenCounter())
        history = [{"role": "user", "content": "hello"}]

        with self.assertRaises(TypeError):
            truncator.truncate_history(history, 1.5)
        with self.assertRaises(TypeError):
            truncator.truncate_history(history, True)
        with self.assertRaises(ValueError):
            truncator.truncate_history(history, 0)
        with self.assertRaises(ValueError):
            truncator.truncate_history(history, -1)
