import tempfile
import unittest
from pathlib import Path

from fde_memory_lab3 import LongTermMemorySQLite


class TestLongTermMemorySQLite(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_dir.name) / "memory.db"
        self.memory = LongTermMemorySQLite(self.database_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_remember_and_recall(self):
        self.memory.remember("user-1", "preferred_language", "Python")
        self.assertEqual(
            self.memory.recall("user-1", "preferred_language"),
            "Python",
        )

    def test_memory_survives_new_instance(self):
        self.memory.remember("user-1", "preferred_language", "Python")

        restarted_memory = LongTermMemorySQLite(self.database_path)

        self.assertEqual(
            restarted_memory.recall("user-1", "preferred_language"),
            "Python",
        )

    def test_remember_overwrites_existing_value(self):
        self.memory.remember("user-1", "preferred_language", "Python")
        self.memory.remember("user-1", "preferred_language", "Rust")
        self.assertEqual(
            self.memory.recall("user-1", "preferred_language"),
            "Rust",
        )

    def test_users_are_isolated(self):
        self.memory.remember("user-1", "preferred_language", "Python")
        self.memory.remember("user-2", "preferred_language", "JavaScript")
        self.assertEqual(
            self.memory.recall("user-1", "preferred_language"),
            "Python",
        )
        self.assertEqual(
            self.memory.recall("user-2", "preferred_language"),
            "JavaScript",
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

    def test_missing_user_or_key_returns_none(self):
        self.assertIsNone(self.memory.recall("unknown-user", "key"))
        self.memory.remember("user-1", "known", "value")
        self.assertIsNone(self.memory.recall("user-1", "missing"))

    def test_json_compatible_values_round_trip(self):
        value = {"tools": ["python", "sqlite"], "active": True, "score": 3}
        self.memory.remember("user-1", "profile", value)
        self.assertEqual(self.memory.recall("user-1", "profile"), value)

    def test_empty_user_id_and_key_are_rejected(self):
        with self.assertRaises(ValueError):
            self.memory.remember("", "key", "value")
        with self.assertRaises(ValueError):
            self.memory.remember("user-1", " ", "value")
        with self.assertRaises(ValueError):
            self.memory.recall(" ", "key")
        with self.assertRaises(ValueError):
            self.memory.forget("user-1", "")

    def test_non_json_serializable_values_are_rejected(self):
        with self.assertRaises(TypeError):
            self.memory.remember("user-1", "object", object())


if __name__ == "__main__":
    unittest.main()
