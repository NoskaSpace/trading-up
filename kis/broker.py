"""KIS 브로커 고수준 래퍼."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

from .client import KISClient
from .config import KISConfig, KISEnvironment
from .exceptions import KISAPIError
from .models import AccountBalance, OrderResponse


@dataclass
class OrderRequest:
    """주식 주문 파라미터."""

    symbol: str
    quantity: float
    price: float | None
    side: str
    order_type: str


class KISBroker:
    """한국투자증권 국내주식 주문/조회 기능."""

    def __init__(self, client: KISClient) -> None:
        self._client = client
        self._config = client._config
        if self._client.use_websocket:
            # 웹소켓 모드일 때는 주문/조회 기능이 제한됨을 미리 안내한다.
            logging.getLogger(__name__).warning(
                "웹소켓 모드에서는 REST 기반 주문/조회 API를 사용할 수 없습니다."
            )

    @classmethod
    def from_config(cls, config: KISConfig) -> "KISBroker":
        """설정에서 브로커 인스턴스를 생성한다."""

        return cls(KISClient(config))

    # ------- 내부 유틸리티 -------
    def _account_headers(self, tr_id_real: str, tr_id_paper: str) -> Dict[str, str]:
        """환경에 따라 적절한 TR ID를 셋업한다."""

        tr_id = tr_id_real if self._config.environment is KISEnvironment.PRODUCTION else tr_id_paper
        return {
            "tr_id": tr_id,
            "custtype": "P",
        }

    def _account_params(self) -> Dict[str, str]:
        """공통 계좌 파라미터."""

        return {
            "CANO": self._config.account_no_without_dash[:8],
            "ACNT_PRDT_CD": self._config.account_no_without_dash[8:10],
        }

    # ------- 주문 및 조회 -------
    def get_account_balance(self) -> AccountBalance:
        """계좌 잔고를 조회한다."""

        headers = self._account_headers("TTTC8434R", "VTTC8434R")
        params = {
            **self._account_params(),
            "AFHR_FLPR_YN": "N",
            "FNCG_AMT_AUTO_RDPT_YN": "N",
            "FUND_STTL_ICLD_YN": "N",
            "INQR_DVSN": "02",
            "OFL_YN": "",
            "PRCS_DVSN": "01",
            "UNPR_DVSN": "01",
        }

        data = self._client.get(
            "/uapi/domestic-stock/v1/trading/inquire-balance",
            headers=headers,
            params=params,
        )
        if not ({'output1', 'output2'} <= data.keys()):
            raise KISAPIError(f"잔고 조회 실패: {data}")
        return AccountBalance.from_api(data)

    def place_order(
        self,
        symbol: str,
        quantity: float,
        *,
        price: Optional[float] = None,
        side: str = "BUY",
        order_type: str = "LIMIT",
    ) -> OrderResponse:
        """시장/지정가 주문을 실행한다."""

        side = side.upper()
        order_type = order_type.upper()
        if side not in {"BUY", "SELL"}:
            raise ValueError("side는 BUY 또는 SELL 이어야 한다")
        if order_type not in {"LIMIT", "MARKET"}:
            raise ValueError("order_type은 LIMIT 또는 MARKET 이어야 한다")

        headers = self._account_headers(
            "TTTC0802U" if side == "BUY" else "TTTC0801U",
            "VTTC0802U" if side == "BUY" else "VTTC0801U",
        )
        body: Dict[str, Any] = {
            **self._account_params(),
            "PDNO": symbol,
            "ORD_DVSN": "00" if order_type == "LIMIT" else "01",
            "ORD_QTY": str(quantity),
            "ORD_UNPR": "0" if price is None else str(price),
        }
        if order_type == "LIMIT" and price is None:
            raise ValueError("지정가 주문은 price가 필요하다")

        data = self._client.post(
            "/uapi/domestic-stock/v1/trading/order-cash",
            headers=headers,
            json=body,
        )
        if "output" not in data:
            raise KISAPIError(f"주문 실패: {data}")
        return OrderResponse.from_api(data["output"])

    def get_order_status(self, order_no: str) -> Dict[str, Any]:
        """접수된 주문의 체결 현황을 반환한다."""

        headers = self._account_headers("TTTC8001R", "VTTC8001R")
        params = {
            **self._account_params(),
            "ODNO": order_no,
            "INQR_DVSN": "01",
            "PDNO": "",
            "CCLD_DVSN": "00",
            "ORD_GNO_BRNO": "",
            "ODNO_PRCS_DVSN": "00",
            "CTX_AREA_FK100": "",
            "CTX_AREA_NK100": "",
        }
        return self._client.get(
            "/uapi/domestic-stock/v1/trading/inquire-ccnl",
            headers=headers,
            params=params,
        )

    def cancel_order(self, order_no: str, symbol: str, quantity: float) -> Dict[str, Any]:
        """주문을 취소한다."""

        headers = self._account_headers("TTTC0803U", "VTTC0803U")
        body = {
            **self._account_params(),
            "PDNO": symbol,
            "ORD_DVSN": "00",
            "ORD_QTY": str(quantity),
            "ORG_ORD_NO": order_no,
        }
        return self._client.post(
            "/uapi/domestic-stock/v1/trading/order-rvsecncl",
            headers=headers,
            json=body,
        )

    # ------- 웹소켓 스트리밍 -------
    def run_websocket(
        self,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[Dict[str, Any]] = None,
        handlers: Optional["WebSocketHandlers"] = None,
        ping_interval: int = 30,
        ping_timeout: int = 10,
    ) -> None:
        """웹소켓 연결을 실행해 실시간 데이터를 수신한다."""

        if not self._client.use_websocket:
            raise RuntimeError("웹소켓 전송이 비활성화되어 있습니다. KIS_TRANSPORT 환경변수를 확인하세요.")
        from .websocket import WebSocketHandlers  # 지연 임포트로 의존성을 최소화한다.

        effective_handlers = handlers or WebSocketHandlers()
        self._client.websocket.run(
            path,
            params=params,
            headers=headers,
            body=body,
            handlers=effective_handlers,
            ping_interval=ping_interval,
            ping_timeout=ping_timeout,
        )
