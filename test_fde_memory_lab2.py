import unittest
from fde_memory_lab2 import LongTermMemory

class TestLongTermMemory(unittest.TestCase):
    def setUp(self):
        self.memory = LongTermMemory()

    def test_remember_and_recall(self):
        self.memory.remember("user1", "preferred_language", "Python")
        self.assertEqual(self.memory.recall("user1", "preferred_language"), "Python")

    def test_forget(self):
        self.memory.remember("user1", "key2", "value2")
        self.memory.forget("user1", "key2")
        self.assertIsNone(self.memory.recall("user1", "key2"))

    def test_recall_nonexistent_key(self):
        self.assertIsNone(self.memory.recall("user1", "nonexistent_key"))

    def test_remember_overwrites_existing_value(self):
        self.memory.remember("user1", "preferred_language", "Python")
        self.memory.remember("user1", "preferred_language", "JavaScript")
        self.assertEqual(self.memory.recall("user1", "preferred_language"), "JavaScript")

    def test_memory_isolation_between_instances(self):
        memory1 = LongTermMemory()
        memory2 = LongTermMemory()
        memory1.remember("user1", "key1", "value1")
        memory2.remember("user2", "key2", "value2")
        self.assertEqual(memory1.recall("user1", "key1"), "value1")
        self.assertEqual(memory2.recall("user2", "key2"), "value2")
        self.assertIsNone(memory2.recall("user1", "key1"))
   
    def test_memory_isolation_between_users(self):
        self.memory.remember("user1", "preferred_language", "Python")
        self.memory.remember("user2", "preferred_language", "Java")

        self.assertEqual(
            self.memory.recall("user1", "preferred_language"),
            "Python",
        )
        self.assertEqual(
            self.memory.recall("user2", "preferred_language"),
            "Java",
        )
