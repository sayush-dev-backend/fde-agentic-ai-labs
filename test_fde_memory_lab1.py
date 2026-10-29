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
                {
                    "role": "user",
                    "content": "Investigate payment-api",
                },
            )

        history_a = manager.get_history(session_a)
        history_b = manager.get_history(session_b)

        self.assertEqual(len(history_a), 1)
        self.assertEqual(len(history_b), 0)

    def test_unknown_session_is_rejected(self):
        manager = SessionManager()

        with self.assertRaises(LookupError):
            manager.get_history("unknown-session")

    def test_stores_structured_tool_message(self):
        manager = SessionManager()
        session_id = manager.create_session()

        tool_result = {
            "ok": True,
            "data": {
                "service": "payment-api",
                "p95_latency_ms": 1420,
            },
        }

        manager.add_message(
            session_id,
            {
                "role": "tool",
                "content": tool_result,
                "trust_level": "untrusted",
            },
        )

        history = manager.get_history(session_id)

        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["role"], "tool")
        self.assertEqual(history[0]["content"], tool_result)
        self.assertEqual(history[0]["trust_level"], "untrusted")

    def test_modifying_returned_history_does_not_change_stored_messages(self):
        manager = SessionManager()
        session_id = manager.create_session()

        manager.add_user_message(
            session_id,
            "Investigate payment-api",
        )

        history = manager.get_history(session_id)

        history[0]["content"] = "Investigate authentication-api"

        updated_history = manager.get_history(session_id)

        self.assertEqual(
            updated_history[0]["content"],
            "Investigate payment-api",
        )


if __name__ == "__main__":
    unittest.main()