"""Redis/Celery queue stubs."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional


@dataclass
class QueueConfig:
    url: str


class TaskQueue:
    """Placeholder for task queue integration."""

    def __init__(self, config: QueueConfig) -> None:
        self.config = config

    def enqueue(self, task_name: str, *args, **kwargs) -> None:
        # Replace with Celery or RQ logic later.
        return None

    def register_handler(self, task_name: str, handler: Callable[..., None]) -> None:
        # Placeholder for handler registration.
        return None


__all__ = ["TaskQueue", "QueueConfig"]
