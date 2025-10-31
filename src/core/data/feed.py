"""Data feed module providing market data interfaces."""
from __future__ import annotations

import datetime as dt
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable, Iterator, List, Sequence

try:  # Optional pandas dependency
    import pandas as pd
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    pd = None  # type: ignore


class DataFeed(ABC):
    """Abstract base class for market data feeds."""

    @abstractmethod
    def stream(self) -> Iterable["BarData"]:
        """Yield bar data sequentially."""


@dataclass(frozen=True)
class BarData:
    """Represents a single OHLCV bar."""

    timestamp: dt.datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


class SyntheticTimeSeriesFeed(DataFeed):
    """Generates synthetic OHLCV bars from various data containers."""

    def __init__(self, data: Sequence[BarData] | "pd.DataFrame") -> None:  # type: ignore[name-defined]
        if pd is not None and isinstance(data, pd.DataFrame):  # pragma: no cover - exercised when pandas available
            self._bars = list(_bars_from_dataframe(data))
        else:
            self._bars = list(data)
        if not self._bars:
            raise ValueError("Synthetic feed requires at least one bar")

    def stream(self) -> Iterable[BarData]:
        return iter(self._bars)


def _bars_from_dataframe(df: "pd.DataFrame") -> Iterator[BarData]:  # type: ignore[name-defined]
    required = {"open", "high", "low", "close", "volume"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    if not isinstance(df.index, pd.DatetimeIndex):
        raise TypeError("DataFrame index must be a DatetimeIndex")
    for timestamp, row in df.sort_index().iterrows():
        yield BarData(
            timestamp=timestamp.to_pydatetime(),
            open=float(row["open"]),
            high=float(row["high"]),
            low=float(row["low"]),
            close=float(row["close"]),
            volume=float(row["volume"]),
        )


def generate_synthetic_series(
    start: dt.datetime,
    periods: int = 100,
    freq: dt.timedelta | None = None,
    base_price: float = 100.0,
    volatility: float = 1.0,
) -> List[BarData]:
    """Create deterministic synthetic bars for testing."""

    if freq is None:
        freq = dt.timedelta(hours=1)
    bars: List[BarData] = []
    price = base_price
    for i in range(periods):
        timestamp = start + freq * i
        drift = (i % 10 - 5) * volatility * 0.1
        price = max(1.0, price + drift)
        high = price + volatility * 0.5
        low = max(0.1, price - volatility * 0.5)
        open_price = bars[-1].close if bars else price
        bar = BarData(
            timestamp=timestamp,
            open=open_price,
            high=high,
            low=low,
            close=price,
            volume=1000,
        )
        bars.append(bar)
    return bars


__all__ = ["BarData", "SyntheticTimeSeriesFeed", "generate_synthetic_series"]
