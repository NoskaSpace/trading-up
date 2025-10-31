"""TimescaleDB integration stubs."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class TimescaleConfig:
    dsn: str
    schema: str = "public"


class TimescaleClient:
    """Placeholder client for TimescaleDB interactions."""

    def __init__(self, config: TimescaleConfig) -> None:
        self.config = config
        self._connected = False

    def connect(self) -> None:
        # In real implementation, connect using asyncpg or psycopg.
        self._connected = True

    def is_connected(self) -> bool:
        return self._connected

    def write_bar(self, table: str, data: dict[str, Any]) -> None:
        if not self._connected:
            raise RuntimeError("Database not connected")
        # Placeholder for insert logic.
        return None


__all__ = ["TimescaleClient", "TimescaleConfig"]
