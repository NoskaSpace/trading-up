"""KIS API 설정 값을 관리하는 모듈."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict


class KISEnvironment(str, Enum):
    """KIS 환경 구분 열거형."""

    PRODUCTION = "production"
    PAPER = "paper"

    @property
    def base_urls(self) -> Dict[str, str]:
        """환경별 기본 URL 매핑을 반환한다."""

        # 한국투자증권에서 제공하는 REST 엔드포인트 도메인 정의
        return {
            "oauth": "https://openapi.koreainvestment.com:9443",  # 토큰 발급
            "rest": (
                "https://openapi.koreainvestment.com:9443"
                if self is KISEnvironment.PRODUCTION
                else "https://openapivts.koreainvestment.com:29443"
            ),
            "websocket": (
                "ws://ops.koreainvestment.com:21000"
                if self is KISEnvironment.PRODUCTION
                else "ws://ops.koreainvestment.com:21000"
            ),
        }


@dataclass
class KISConfig:
    """KIS 브로커 초기화를 위한 구성 데이터."""

    app_key: str
    app_secret: str
    account_no: str
    environment: KISEnvironment = KISEnvironment.PAPER
    trading_password: str | None = None

    @property
    def account_no_without_dash(self) -> str:
        """대시를 제거한 계좌번호를 반환한다."""

        return self.account_no.replace("-", "")

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "KISConfig":
        """사전 데이터로부터 설정 인스턴스를 생성한다."""

        return cls(
            app_key=data["app_key"],
            app_secret=data["app_secret"],
            account_no=data["account_no"],
            environment=KISEnvironment(data.get("environment", KISEnvironment.PAPER.value)),
            trading_password=data.get("trading_password"),
        )

    def base_url(self, key: str) -> str:
        """환경별 URL 중 지정된 키에 해당하는 값을 반환한다."""

        return self.environment.base_urls[key]
