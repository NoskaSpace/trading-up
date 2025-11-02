"""단순 이동평균 교차 전략 예제."""

from __future__ import annotations

from collections import deque
from datetime import datetime, timedelta
from random import random

from kis.backtest import BacktestBroker, PortfolioState
from kis.models import Candle


def generate_mock_candles(symbol: str, days: int) -> list[Candle]:
    """랜덤 데이터를 사용해 모의 캔들을 생성한다."""

    candles: list[Candle] = []
    price = 100.0
    for day in range(days):
        price *= 1 + (random() - 0.5) * 0.02
        candles.append(
            Candle(
                symbol=symbol,
                timestamp=datetime.now() - timedelta(days=days - day),
                open=price * 0.98,
                high=price * 1.02,
                low=price * 0.97,
                close=price,
                volume=1000,
            )
        )
    return candles


def moving_average_strategy(window: int):
    """단기 이동평균이 상승하면 매수하고 그렇지 않으면 청산한다."""

    prices: deque[float] = deque(maxlen=window)

    def strategy(state: PortfolioState, candle: Candle) -> dict[str, float]:
        prices.append(candle.close)
        if len(prices) < window:
            return {}
        avg_price = sum(prices) / window
        position = state.holdings.get(candle.symbol, 0.0)
        if candle.close > avg_price and position == 0:
            qty = state.cash // candle.close
            return {candle.symbol: float(qty)}
        if candle.close < avg_price and position > 0:
            return {candle.symbol: -position}
        return {}

    return strategy


if __name__ == "__main__":
    broker = BacktestBroker(initial_cash=1_000_000)
    candles = generate_mock_candles("005930", days=120)
    result = broker.run(candles, moving_average_strategy(window=5))
    print(f"최종 수익률: {result.return_rate * 100:.2f}%")
