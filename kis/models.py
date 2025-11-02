"""KIS 응답 모델 정의."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Iterable, List, Optional


@dataclass
class Candle:
    """단일 캔들 데이터."""

    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass
class Holding:
    """보유 종목 정보."""

    symbol: str
    quantity: float
    average_price: float
    evaluation_amount: float

    @classmethod
    def from_api(cls, data: Dict[str, str]) -> "Holding":
        """API 응답으로부터 보유 종목 정보를 생성한다."""

        return cls(
            symbol=data.get("PDNO", ""),
            quantity=float(data.get("ORD_QTY", 0)),
            average_price=float(data.get("PCHS_AVG_PRIC", 0)),
            evaluation_amount=float(data.get("EVLU_AMT", 0)),
        )


@dataclass
class AccountBalance:
    """계좌 잔고 응답."""

    account_no: str
    cash: float
    stocks: List[Holding] = field(default_factory=list)

    @classmethod
    def from_api(cls, data: Dict[str, any]) -> "AccountBalance":
        """API 응답으로부터 잔고 정보를 파싱한다."""

        stocks = [Holding.from_api(item) for item in data.get("output1", [])]
        cash = float(data.get("output2", {}).get("EVLU_TOTAMT", 0))
        account_no = data.get("output2", {}).get("CANO", "")
        return cls(account_no=account_no, cash=cash, stocks=stocks)


@dataclass
class OrderResponse:
    """주문 접수 결과."""

    order_no: str
    message: Optional[str] = None

    @classmethod
    def from_api(cls, data: Dict[str, str]) -> "OrderResponse":
        """API 응답으로부터 주문 결과를 구성한다."""

        return cls(order_no=data.get("ODNO") or data.get("ORD_NO", ""), message=data.get("MSG"))
