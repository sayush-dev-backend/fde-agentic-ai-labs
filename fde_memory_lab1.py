from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4


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
        role: str,
        content: str,
    ) -> None:
        if session_id not in self.sessions:
            raise LookupError("Session not found")

        message = {
            "role": role,
            "content": content,
        }

        self.sessions[session_id].messages.append(message)

    def get_history(
        self,
        session_id: str,
    ) -> list[dict[str, Any]]:
        if session_id not in self.sessions:
            raise LookupError("Session not found")

        return list(self.sessions[session_id].messages)