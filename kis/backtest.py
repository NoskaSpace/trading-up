"""단순 백테스트 엔진 구현."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Iterable, List

from .exceptions import BacktestError
from .models import Candle


@dataclass
class PortfolioState:
    """백테스트 시점별 포트폴리오 상태."""

    cash: float
    holdings: Dict[str, float]
    equity: float


@dataclass
class BacktestResult:
    """백테스트 결과 요약."""

    states: List[PortfolioState]
    final_equity: float
    return_rate: float


class BacktestBroker:
    """캔들 시퀀스를 기반으로 매매 전략을 평가한다."""

    def __init__(self, initial_cash: float) -> None:
        self.initial_cash = initial_cash

    def run(
        self,
        candles: Iterable[Candle],
        strategy: Callable[[PortfolioState, Candle], Dict[str, float]],
    ) -> BacktestResult:
        """전략 콜백을 사용해 포트폴리오를 시뮬레이션한다."""

        cash = self.initial_cash
        holdings: Dict[str, float] = {}
        states: List[PortfolioState] = []

        for candle in candles:
            equity = cash + sum(holdings.get(candle.symbol, 0.0) * candle.close for _ in [0])
            state = PortfolioState(cash=cash, holdings=dict(holdings), equity=equity)
            order_plan = strategy(state, candle)
            if not isinstance(order_plan, dict):
                raise BacktestError("전략 콜백은 종목별 주문수량 딕셔너리를 반환해야 한다")

            price = candle.close
            for symbol, qty_delta in order_plan.items():
                if qty_delta == 0:
                    continue
                cost = price * qty_delta
                if qty_delta > 0:  # 매수
                    if cash < cost:
                        raise BacktestError("현금이 부족하여 매수할 수 없음")
                    cash -= cost
                    holdings[symbol] = holdings.get(symbol, 0.0) + qty_delta
                else:  # 매도
                    current_qty = holdings.get(symbol, 0.0)
                    if current_qty + qty_delta < -1e-8:
                        raise BacktestError("보유 수량보다 많이 매도할 수 없음")
                    holdings[symbol] = current_qty + qty_delta
                    cash -= cost

            equity = cash + sum(qty * candle.close for qty in holdings.values())
            states.append(PortfolioState(cash=cash, holdings=dict(holdings), equity=equity))

        if not states:
            raise BacktestError("캔들 데이터가 비어 있음")

        final_equity = states[-1].equity
        return_rate = (final_equity / self.initial_cash) - 1
        return BacktestResult(states=states, final_equity=final_equity, return_rate=return_rate)
