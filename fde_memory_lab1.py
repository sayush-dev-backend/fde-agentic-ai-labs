from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4
from copy import deepcopy


@dataclass
class Session:
    session_id: str
    messages: list[dict[str, Any]] = field(default_factory=list)


class SessionManager:
    def __init__(self) -> None:
        self.sessions: dict[str, Session] = {}

    def create_session(self) -> str:
        session_id = str(uuid4())

        self.sessions[session_id] = Session(
            session_id=session_id
        )

        return session_id

    def add_message(
    self,
    session_id: str,
    message: dict[str, Any],
) -> None:
        if session_id not in self.sessions:
            raise LookupError("Session not found")

        if not isinstance(message, dict):
            raise TypeError("Message must be a dictionary")

        if not isinstance(message.get("role"), str):
            raise ValueError("Message role must be a string")

        if "content" not in message:
            raise ValueError("Message must contain content")

        self.sessions[session_id].messages.append(
            deepcopy(message)
        )
    def get_history(
        self,
        session_id: str,
    ) -> list[dict[str, Any]]:
        if session_id not in self.sessions:
            raise LookupError("Session not found")

        return deepcopy(self.sessions[session_id].messages)

    def add_user_message(
        self,
        session_id: str,
        content: str,
    ) -> None:
        self.add_message(
            session_id,
            {
                "role": "user",
                "content": content,
            },
        )

    def add_assistant_message(
        self,
        session_id: str,
        content: str,
        ) -> None:
            self.add_message(
            session_id,
            {
            "role": "assistant",
            "content": content,
            },
            )