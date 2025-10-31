"""Strategy interfaces and utilities."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Optional

from ..data.feed import BarData


@dataclass
class StrategyContext:
    """Runtime context passed to strategy callbacks."""

    broker: "BrokerInterface"
    portfolio: "Portfolio"
    extras: Dict[str, object]


class BrokerInterface(ABC):
    """Minimal broker interface exposed to strategies."""

    @abstractmethod
    def market_order(self, symbol: str, quantity: float) -> None:
        ...

    @abstractmethod
    def limit_order(self, symbol: str, quantity: float, price: float) -> None:
        ...


class Portfolio(ABC):  # pragma: no cover - type placeholder
    """Protocol-like placeholder to avoid circular imports."""

    @abstractmethod
    def position(self, symbol: str) -> float:
        ...


class StrategyBase(ABC):
    """Base class for trading strategies."""

    symbol: str

    def __init__(self, symbol: str, name: Optional[str] = None) -> None:
        self.symbol = symbol
        self.name = name or self.__class__.__name__

    @abstractmethod
    def on_bar(self, index: int, bar: BarData, ctx: StrategyContext) -> None:
        """Process new bar and optionally submit orders."""

    def on_start(self, ctx: StrategyContext) -> None:
        """Called before backtest/live session starts."""

    def on_finish(self, ctx: StrategyContext) -> None:
        """Called after session ends."""


__all__ = ["StrategyBase", "StrategyContext", "BrokerInterface", "Portfolio"]
