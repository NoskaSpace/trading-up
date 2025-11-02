"""백테스트 엔진 단위 테스트."""

from __future__ import annotations

from datetime import datetime

from kis.backtest import BacktestBroker, BacktestError
from kis.models import Candle


def test_backtest_runs_and_returns_result() -> None:
    """백테스트가 정상적으로 실행되는지 확인한다."""

    broker = BacktestBroker(initial_cash=100_000)
    candles = [
        Candle(
            symbol="005930",
            timestamp=datetime(2023, 1, i + 1),
            open=100 + i,
            high=101 + i,
            low=99 + i,
            close=100 + i,
            volume=1000,
        )
        for i in range(5)
    ]

    def strategy(state, candle):
        if candle.timestamp.day == 1:
            qty = state.cash // candle.close
            return {candle.symbol: float(qty)}
        if candle.timestamp.day == 5:
            position = state.holdings.get(candle.symbol, 0.0)
            return {candle.symbol: -position}
        return {}

    result = broker.run(candles, strategy)
    assert result.final_equity > 0
    assert len(result.states) == len(candles)


def test_backtest_empty_candles_raise() -> None:
    """캔들이 없을 경우 예외가 발생하는지 확인한다."""

    broker = BacktestBroker(initial_cash=10_000)

    try:
        broker.run([], lambda state, candle: {})
    except BacktestError as exc:
        assert "캔들" in str(exc)
    else:
        raise AssertionError("BacktestError가 발생해야 한다")
