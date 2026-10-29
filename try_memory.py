from fde_memory_lab1 import SessionManager

manager = SessionManager()

# Start a conversation.
session_id = manager.create_session()

manager.add_user_message(
    session_id,
    "Why is payment-api slow?",
)

manager.add_assistant_message(
    session_id,
    "Its P95 latency is 1420 ms.",
)

# Continue the same conversation.
manager.add_user_message(
    session_id,
    "What was its P95 latency?",
)

print(manager.get_history(session_id))