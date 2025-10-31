"""Example Golden Cross strategy implementation."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Deque
from collections import deque

from .base import StrategyBase, StrategyContext
from ..data.feed import BarData


@dataclass
class MovingAverageState:
    short_window: int
    long_window: int
    short_values: Deque[float] = field(default_factory=deque)
    long_values: Deque[float] = field(default_factory=deque)
    last_signal: str = "flat"

    def update(self, price: float) -> None:
        self.short_values.append(price)
        self.long_values.append(price)
        if len(self.short_values) > self.short_window:
            self.short_values.popleft()
        if len(self.long_values) > self.long_window:
            self.long_values.popleft()

    @property
    def short_ma(self) -> float:
        return sum(self.short_values) / len(self.short_values)

    @property
    def long_ma(self) -> float:
        return sum(self.long_values) / len(self.long_values)

    def ready(self) -> bool:
        return len(self.short_values) == self.short_window and len(self.long_values) == self.long_window


class GoldenCrossStrategy(StrategyBase):
    """Simple moving average crossover strategy."""

    def __init__(self, symbol: str, short_window: int = 5, long_window: int = 20) -> None:
        if short_window >= long_window:
            raise ValueError("short_window must be < long_window")
        super().__init__(symbol)
        self.state = MovingAverageState(short_window, long_window)

    def on_start(self, ctx: StrategyContext) -> None:
        ctx.extras.setdefault("log", []).append(f"Starting {self.name} for {self.symbol}")

    def on_bar(self, index: int, bar: BarData, ctx: StrategyContext) -> None:
        self.state.update(bar.close)
        if not self.state.ready():
            return

        short_ma = self.state.short_ma
        long_ma = self.state.long_ma

        log = ctx.extras.setdefault("log", [])
        log.append(
            f"[{bar.timestamp.isoformat()}] short_ma={short_ma:.2f} long_ma={long_ma:.2f}"
        )

        if short_ma > long_ma and self.state.last_signal != "long":
            ctx.broker.market_order(self.symbol, quantity=1)
            self.state.last_signal = "long"
            log.append("Entered long position")
        elif short_ma < long_ma and self.state.last_signal != "flat":
            ctx.broker.market_order(self.symbol, quantity=-1)
            self.state.last_signal = "flat"
            log.append("Exited to flat")

    def on_finish(self, ctx: StrategyContext) -> None:
        ctx.extras.setdefault("log", []).append(f"Finished {self.name}")


__all__ = ["GoldenCrossStrategy", "MovingAverageState"]
