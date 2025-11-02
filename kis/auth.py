"""KIS 인증 토큰 발급 및 갱신 로직."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict

from .config import KISConfig


@dataclass
class KISToken:
    """발급받은 KIS 액세스 토큰 정보를 표현한다."""

    access_token: str
    token_type: str
    expires_in: int
    scope: str
    issued_at: float

    @property
    def is_expired(self) -> bool:
        """토큰이 만료되었는지 여부를 반환한다."""

        # 유효기간의 30초 전에 미리 갱신하도록 조정
        return time.time() >= self.issued_at + self.expires_in - 30


class KISAuth:
    """토큰 발급과 저장을 담당하는 인증 관리자."""

    def __init__(self, config: KISConfig) -> None:
        self._config = config
        self._token: KISToken | None = None

    def _request_token(self) -> KISToken:
        """REST API를 호출하여 새로운 토큰을 발급받는다."""

        url = f"{self._config.base_url('oauth')}/oauth2/tokenP"
        payload = {
            "grant_type": "client_credentials",
            "appkey": self._config.app_key,
            "appsecret": self._config.app_secret,
        }

        try:
            import requests
        except ImportError as exc:
            raise RuntimeError("requests 패키지가 필요합니다. 'pip install requests'로 설치하세요") from exc

        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        data: Dict[str, Any] = response.json()

        return KISToken(
            access_token=data["access_token"],
            token_type=data.get("token_type", "Bearer"),
            expires_in=int(data.get("expires_in", 0)),
            scope=data.get("scope", ""),
            issued_at=time.time(),
        )

    def get_token(self, force_refresh: bool = False) -> KISToken:
        """현재 토큰을 반환하고, 필요 시 자동으로 갱신한다."""

        if force_refresh or self._token is None or self._token.is_expired:
            self._token = self._request_token()
        return self._token

    def auth_headers(self) -> Dict[str, str]:
        """API 호출에 필요한 공통 인증 헤더를 생성한다."""

        token = self.get_token()
        return {
            "authorization": f"{token.token_type} {token.access_token}",
            "appkey": self._config.app_key,
            "appsecret": self._config.app_secret,
        }
