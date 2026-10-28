import unittest

from fde_memory_lab1 import SessionManager


class TestSessionManager(unittest.TestCase):

    def test_create_two_independent_sessions(self):
        manager = SessionManager()

        session_a = manager.create_session()
        session_b = manager.create_session()

        self.assertNotEqual(session_a, session_b)

    def test_messages_stay_within_their_session(self):
        manager = SessionManager()

        session_a = manager.create_session()
        session_b = manager.create_session()

        manager.add_message(
            session_a,
            "user",
            "Investigate payment-api",
        )

        history_a = manager.get_history(session_a)
        history_b = manager.get_history(session_b)

        self.assertEqual(len(history_a), 1)
        self.assertEqual(len(history_b), 0)

    def test_unknown_session_is_rejected(self):
        manager = SessionManager()

        with self.assertRaises(LookupError):
            manager.get_history("unknown-session")


if __name__ == "__main__":
    unittest.main()