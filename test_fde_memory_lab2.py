import unittest

from fde_memory_lab2 import LongTermMemory


class TestLongTermMemory(unittest.TestCase):
    def setUp(self):
        self.memory = LongTermMemory()

    def test_remember_and_recall(self):
        self.memory.remember("user-1", "preferred_language", "Python")
        self.assertEqual(
            self.memory.recall("user-1", "preferred_language"),
            "Python",
        )

    def test_forget(self):
        self.memory.remember("user-1", "preferred_language", "Python")
        self.memory.forget("user-1", "preferred_language")
        self.assertIsNone(
            self.memory.recall("user-1", "preferred_language")
        )

    def test_forgetting_missing_key_is_safe(self):
        self.memory.forget("user-1", "missing")
        self.assertIsNone(self.memory.recall("user-1", "missing"))

    def test_recall_missing_user_or_key_returns_none(self):
        self.assertIsNone(self.memory.recall("unknown-user", "key"))
        self.memory.remember("user-1", "known", "value")
        self.assertIsNone(self.memory.recall("user-1", "missing"))

    def test_remember_overwrites_existing_value(self):
        self.memory.remember("user-1", "preferred_language", "Python")
        self.memory.remember("user-1", "preferred_language", "Rust")
        self.assertEqual(
            self.memory.recall("user-1", "preferred_language"),
            "Rust",
        )

    def test_memory_isolation_between_instances(self):
        first = LongTermMemory()
        second = LongTermMemory()
        first.remember("user-1", "key", "value")
        self.assertEqual(first.recall("user-1", "key"), "value")
        self.assertIsNone(second.recall("user-1", "key"))

    def test_users_are_isolated(self):
        self.memory.remember("user-1", "preferred_language", "Python")
        self.memory.remember("user-2", "preferred_language", "Java")
        self.assertEqual(
            self.memory.recall("user-1", "preferred_language"),
            "Python",
        )
        self.assertEqual(
            self.memory.recall("user-2", "preferred_language"),
            "Java",
        )

    def test_empty_user_id_and_key_are_rejected(self):
        with self.assertRaises(ValueError):
            self.memory.remember("", "key", "value")
        with self.assertRaises(ValueError):
            self.memory.remember("user-1", " ", "value")


if __name__ == "__main__":
    unittest.main()
