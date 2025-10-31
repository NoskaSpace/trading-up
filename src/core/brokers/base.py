"""Broker base interfaces."""
from __future__ import annotations

import datetime as dt
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

from ..portfolio.order import Order, OrderSide, Fill


@dataclass
class ExecutionReport:
    order: Order
    fill_price: float
    quantity: float
    timestamp: dt.datetime


class BrokerBase(ABC):
    """Abstract broker handling order submission and fills."""

    def __init__(self) -> None:
        self._executions: List[ExecutionReport] = []

    @abstractmethod
    def market_order(self, symbol: str, quantity: float) -> ExecutionReport:
        ...

    @abstractmethod
    def limit_order(self, symbol: str, quantity: float, price: float) -> ExecutionReport:
        ...

    def executions(self) -> List[ExecutionReport]:
        return list(self._executions)


def _create_order(symbol: str, quantity: float) -> Order:
    side = OrderSide.BUY if quantity > 0 else OrderSide.SELL
    return Order(symbol=symbol, quantity=abs(quantity), side=side, timestamp=dt.datetime.utcnow())


__all__ = ["BrokerBase", "ExecutionReport"]
