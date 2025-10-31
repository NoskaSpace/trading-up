"""Backtest broker implementation."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass

from .base import BrokerBase, ExecutionReport, _create_order
from ..portfolio.account import Portfolio
from ..portfolio.order import Fill


@dataclass
class SlippageModel:
    bps: float = 1.0

    def apply(self, price: float, side: int) -> float:
        return price * (1 + self.bps / 10_000 * side)


class BacktestBroker(BrokerBase):
    """Simulate order execution for backtests."""

    def __init__(self, portfolio: Portfolio, slippage: SlippageModel | None = None) -> None:
        super().__init__()
        self.portfolio = portfolio
        self.slippage = slippage or SlippageModel()
        self.last_price: dict[str, float] = {}

    def update_price(self, symbol: str, price: float) -> None:
        self.last_price[symbol] = price

    def _fill(self, symbol: str, quantity: float, price: float) -> ExecutionReport:
        order = _create_order(symbol, quantity)
        side = 1 if quantity > 0 else -1
        executed_price = self.slippage.apply(price, side)
        report = ExecutionReport(
            order=order,
            fill_price=executed_price,
            quantity=quantity,
            timestamp=dt.datetime.utcnow(),
        )
        self._executions.append(report)
        fill = Fill(order=order, fill_price=executed_price, quantity=quantity, timestamp=report.timestamp)
        self.portfolio.update_on_fill(fill)
        return report

    def market_order(self, symbol: str, quantity: float) -> ExecutionReport:
        price = self.last_price.get(symbol)
        if price is None:
            raise ValueError(f"No market price available for {symbol}")
        return self._fill(symbol, quantity, price)

    def limit_order(self, symbol: str, quantity: float, price: float) -> ExecutionReport:
        # For MVP, assume limit orders execute immediately if price is favorable.
        market_price = self.last_price.get(symbol, price)
        executed_price = price if (quantity > 0 and price <= market_price) or (quantity < 0 and price >= market_price) else market_price
        return self._fill(symbol, quantity, executed_price)


__all__ = ["BacktestBroker", "SlippageModel"]
