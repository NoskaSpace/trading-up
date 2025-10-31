"""Order and trade domain models."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum


class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


@dataclass
class Order:
    symbol: str
    quantity: float
    side: OrderSide
    price: float | None = None
    timestamp: dt.datetime | None = None


@dataclass
class Fill:
    order: Order
    fill_price: float
    quantity: float
    timestamp: dt.datetime


__all__ = ["Order", "OrderSide", "Fill"]
