"""Portfolio accounting models."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from typing import Dict

from .order import Fill


@dataclass
class Position:
    symbol: str
    quantity: float = 0.0
    avg_price: float = 0.0

    def update(self, fill: Fill) -> None:
        signed_qty = fill.quantity
        new_qty = self.quantity + signed_qty
        if new_qty == 0:
            self.quantity = 0.0
            self.avg_price = 0.0
            return
        if self.quantity == 0:
            self.avg_price = fill.fill_price
        else:
            self.avg_price = (
                self.avg_price * self.quantity + fill.fill_price * signed_qty
            ) / new_qty
        self.quantity = new_qty


@dataclass
class PortfolioState:
    cash: float
    positions: Dict[str, Position] = field(default_factory=dict)
    realized_pnl: float = 0.0


class Portfolio:
    """Track portfolio balances and positions."""

    def __init__(self, starting_cash: float = 100_000.0) -> None:
        self.state = PortfolioState(cash=starting_cash)

    def position(self, symbol: str) -> float:
        return self.state.positions.get(symbol, Position(symbol)).quantity

    def update_on_fill(self, fill: Fill) -> None:
        signed_qty = fill.quantity
        cost = fill.fill_price * signed_qty
        self.state.cash -= cost
        pos = self.state.positions.setdefault(fill.order.symbol, Position(fill.order.symbol))
        pre_qty = pos.quantity
        pos.update(fill)
        if pre_qty != 0 and (pre_qty > 0 > pos.quantity or pre_qty < 0 < pos.quantity):
            # Position flip implies realized pnl
            self.state.realized_pnl += (fill.fill_price - pos.avg_price) * signed_qty

    def equity(self, mark_prices: Dict[str, float]) -> float:
        total = self.state.cash
        for symbol, pos in self.state.positions.items():
            price = mark_prices.get(symbol, pos.avg_price)
            total += pos.quantity * price
        return total

    def snapshot(self) -> PortfolioState:
        return PortfolioState(
            cash=self.state.cash,
            positions={k: Position(v.symbol, v.quantity, v.avg_price) for k, v in self.state.positions.items()},
            realized_pnl=self.state.realized_pnl,
        )


__all__ = ["Portfolio", "PortfolioState", "Position"]
