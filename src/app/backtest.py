"""Simple backtest runner."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple

try:  # Optional pandas dependency
    import pandas as pd
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    pd = None  # type: ignore

from core.brokers.backtest import BacktestBroker
from core.data.feed import BarData, DataFeed, SyntheticTimeSeriesFeed, generate_synthetic_series
from core.portfolio.account import Portfolio
from core.strategy.base import StrategyBase, StrategyContext


@dataclass
class BacktestResult:
    equity_curve: Sequence[Tuple[dt.datetime, float]]
    logs: List[str]

    def to_series(self) -> "pd.Series":  # type: ignore[name-defined]
        if pd is None:
            raise RuntimeError("pandas is not installed")
        index = [timestamp for timestamp, _ in self.equity_curve]
        values = [value for _, value in self.equity_curve]
        return pd.Series(values, index=pd.to_datetime(index), name="equity")


def run_backtest(
    strategy: StrategyBase,
    feed: DataFeed,
    starting_cash: float = 100_000.0,
) -> BacktestResult:
    portfolio = Portfolio(starting_cash)
    broker = BacktestBroker(portfolio)
    ctx = StrategyContext(broker=broker, portfolio=portfolio, extras={"log": []})

    strategy.on_start(ctx)

    equity_values: List[Tuple[dt.datetime, float]] = []

    for i, bar in enumerate(feed.stream()):
        broker.update_price(strategy.symbol, bar.close)
        strategy.on_bar(i, bar, ctx)
        equity = portfolio.equity({strategy.symbol: bar.close})
        equity_values.append((bar.timestamp, equity))

    strategy.on_finish(ctx)
    return BacktestResult(equity_curve=equity_values, logs=ctx.extras.get("log", []))


def run_example() -> BacktestResult:
    from core.strategy.golden_cross import GoldenCrossStrategy

    bars = generate_synthetic_series(start=dt.datetime(2024, 1, 1))
    feed = SyntheticTimeSeriesFeed(bars)
    strategy = GoldenCrossStrategy(symbol="SYNTH")
    return run_backtest(strategy, feed)


__all__ = ["run_backtest", "BacktestResult", "run_example"]
