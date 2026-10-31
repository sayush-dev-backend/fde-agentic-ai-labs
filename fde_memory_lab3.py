"""SQLite-backed persistent long-term memory for the FDE agent.

Values are stored as JSON so common Python data types (strings, numbers,
booleans, lists, dictionaries, and None) can be round-tripped safely.
Use a file path for database_path; each operation opens its own connection,
so a new LongTermMemorySQLite instance can access the same stored records.
"""

import json
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any


class LongTermMemorySQLite:
    """Store JSON-compatible memories in SQLite, scoped by trusted user ID."""

    def __init__(self, database_path: str | Path) -> None:
        if not isinstance(database_path, (str, Path)) or not str(database_path).strip():
            raise ValueError("database_path must be a non-empty file path")

        self.database_path = str(database_path)
        if self.database_path == ":memory:":
            raise ValueError(
                "Use a database file path; per-operation connections do not share :memory: databases"
            )

        with closing(sqlite3.connect(self.database_path)) as connection:
            with connection:
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS memories (
                        user_id TEXT NOT NULL,
                        key TEXT NOT NULL,
                        value_json TEXT NOT NULL,
                        PRIMARY KEY (user_id, key)
                    )
                    """
                )

    @staticmethod
    def _validate_identity(user_id: str, key: str) -> None:
        if not isinstance(user_id, str) or not user_id.strip():
            raise ValueError("user_id must be a non-empty string")
        if not isinstance(key, str) or not key.strip():
            raise ValueError("key must be a non-empty string")

    def remember(self, user_id: str, key: str, value: Any) -> None:
        self._validate_identity(user_id, key)
        serialized_value = json.dumps(value, allow_nan=False)

        with closing(sqlite3.connect(self.database_path)) as connection:
            with connection:
                connection.execute(
                    """
                    INSERT INTO memories (user_id, key, value_json)
                    VALUES (?, ?, ?)
                    ON CONFLICT(user_id, key)
                    DO UPDATE SET value_json = excluded.value_json
                    """,
                    (user_id, key, serialized_value),
                )

    def recall(self, user_id: str, key: str) -> Any | None:
        self._validate_identity(user_id, key)

        with closing(sqlite3.connect(self.database_path)) as connection:
            row = connection.execute(
                """
                SELECT value_json
                FROM memories
                WHERE user_id = ? AND key = ?
                """,
                (user_id, key),
            ).fetchone()

        if row is None:
            return None
        return json.loads(row[0])

    def forget(self, user_id: str, key: str) -> None:
        self._validate_identity(user_id, key)

        with closing(sqlite3.connect(self.database_path)) as connection:
            with connection:
                connection.execute(
                    "DELETE FROM memories WHERE user_id = ? AND key = ?",
                    (user_id, key),
                )
