"""KIS 웹소켓 스트리밍 클라이언트."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional
from urllib.parse import urlencode

from .auth import KISAuth
from .config import KISConfig

logger = logging.getLogger(__name__)


@dataclass
class WebSocketHandlers:
    """웹소켓 이벤트 콜백을 래핑하기 위한 구조체."""

    on_open: Optional[Callable[["websocket.WebSocketApp"], None]] = None
    on_message: Optional[Callable[["websocket.WebSocketApp", str], None]] = None
    on_error: Optional[Callable[["websocket.WebSocketApp", Exception], None]] = None
    on_close: Optional[Callable[["websocket.WebSocketApp", int, str], None]] = None


class KISWebSocketClient:
    """한국투자증권 실시간 데이터 수신을 위한 웹소켓 클라이언트."""

    def __init__(self, config: KISConfig, auth: KISAuth) -> None:
        self._config = config
        self._auth = auth

    def _build_headers(self, headers: Optional[Dict[str, str]] = None) -> list[str]:
        """기본 인증 헤더와 추가 헤더를 결합하여 반환한다."""

        merged = self._auth.auth_headers().copy()
        if headers:
            merged.update(headers)
        return [f"{key}: {value}" for key, value in merged.items()]

    def _compose_url(self, path: str = "/", params: Optional[Dict[str, Any]] = None) -> str:
        """요청 경로와 쿼리 파라미터를 조합해 최종 접속 URL을 생성한다."""

        base = self._config.base_url("websocket")
        url = f"{base}{path}" if path.startswith("/") else f"{base}/{path}"
        if params:
            query = urlencode(params)
            url = f"{url}?{query}"
        return url

    def run(
        self,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[Dict[str, Any]] = None,
        handlers: Optional[WebSocketHandlers] = None,
        ping_interval: int = 30,
        ping_timeout: int = 10,
    ) -> None:
        """웹소켓 연결을 맺고 실시간 메시지를 수신한다."""

        try:
            import websocket  # type: ignore
        except ImportError as exc:  # pragma: no cover - 의존성 경고는 테스트에서 확인하지 않는다.
            raise RuntimeError(
                "websocket-client 패키지가 필요합니다. 'pip install websocket-client'로 설치하세요"
            ) from exc

        url = self._compose_url(path, params)
        header_list = self._build_headers(headers)
        handlers = handlers or WebSocketHandlers()

        def _on_open(ws: "websocket.WebSocketApp") -> None:
            """연결 수립 시 호출되는 내부 핸들러."""

            logger.debug("웹소켓 연결 성공: %s", url)
            if body:
                payload = json.dumps(body)
                logger.debug("웹소켓 전송 페이로드: %s", payload)
                ws.send(payload)
            if handlers.on_open:
                handlers.on_open(ws)

        def _on_message(ws: "websocket.WebSocketApp", message: str) -> None:
            """메시지 수신 시 호출되는 내부 핸들러."""

            logger.debug("웹소켓 수신 메시지: %s", message)
            if handlers.on_message:
                handlers.on_message(ws, message)

        def _on_error(ws: "websocket.WebSocketApp", error: Exception) -> None:
            """에러 발생 시 호출되는 내부 핸들러."""

            logger.error("웹소켓 에러: %s", error)
            if handlers.on_error:
                handlers.on_error(ws, error)

        def _on_close(ws: "websocket.WebSocketApp", status_code: int, msg: str) -> None:
            """연결 종료 시 호출되는 내부 핸들러."""

            logger.info("웹소켓 연결 종료: %s (%s)", status_code, msg)
            if handlers.on_close:
                handlers.on_close(ws, status_code, msg)

        ws_app = websocket.WebSocketApp(
            url,
            header=header_list,
            on_open=_on_open,
            on_message=_on_message,
            on_error=_on_error,
            on_close=_on_close,
        )
        logger.debug("웹소켓 실행 시작: %s", url)
        ws_app.run_forever(ping_interval=ping_interval, ping_timeout=ping_timeout)
