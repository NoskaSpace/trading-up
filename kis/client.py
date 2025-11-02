"""KIS REST 및 웹소켓 호출을 담당하는 클라이언트."""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional

from .auth import KISAuth
from .config import KISConfig
from .websocket import KISWebSocketClient

logger = logging.getLogger(__name__)


class KISClient:
    """한국투자증권 REST 및 웹소켓 API 래퍼."""

    TRANSPORT_ENV_VAR = "KIS_TRANSPORT"

    def __init__(
        self,
        config: KISConfig,
        auth: Optional[KISAuth] = None,
        *,
        transport: Optional[str] = None,
    ) -> None:
        self._config = config
        self._auth = auth or KISAuth(config)
        env_transport = (transport or os.getenv(self.TRANSPORT_ENV_VAR, "rest")).lower()
        self._transport = env_transport
        self._ws_client: KISWebSocketClient | None = None
        if self.use_websocket:
            # 웹소켓 모드일 경우 즉시 클라이언트를 초기화한다.
            self._ws_client = KISWebSocketClient(config, self._auth)

    @property
    def auth(self) -> KISAuth:
        """현재 사용중인 인증 객체를 반환한다."""

        return self._auth

    @property
    def transport(self) -> str:
        """현재 선택된 전송 방식을 반환한다."""

        return self._transport

    @property
    def use_websocket(self) -> bool:
        """웹소켓 전송 사용 여부를 반환한다."""

        return self._transport == "websocket"

    @property
    def websocket(self) -> KISWebSocketClient:
        """웹소켓 클라이언트를 반환한다."""

        if not self.use_websocket or self._ws_client is None:
            raise RuntimeError("웹소켓 전송이 활성화되지 않았습니다. 환경변수 또는 transport 인자를 확인하세요.")
        return self._ws_client

    def request(
        self,
        method: str,
        path: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """일반화된 REST API 호출 메서드."""

        if self.use_websocket:
            raise RuntimeError("웹소켓 모드에서는 REST request를 사용할 수 없습니다.")

        url = f"{self._config.base_url('rest')}{path}"
        base_headers = self._auth.auth_headers()
        base_headers.setdefault("Content-Type", "application/json; charset=UTF-8")
        if headers:
            base_headers.update(headers)

        logger.debug("KIS 요청 %s %s", method, url)
        try:
            import requests
        except ImportError as exc:
            raise RuntimeError("requests 패키지가 필요합니다. 'pip install requests'로 설치하세요") from exc

        response = requests.request(
            method=method,
            url=url,
            headers=base_headers,
            params=params,
            json=json,
            timeout=10,
        )
        logger.debug("KIS 응답 상태 %s", response.status_code)
        response.raise_for_status()
        return response.json()

    def get(self, path: str, **kwargs: Any) -> Dict[str, Any]:
        """GET 요청을 간단히 수행한다."""

        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> Dict[str, Any]:
        """POST 요청을 간단히 수행한다."""

        return self.request("POST", path, **kwargs)
