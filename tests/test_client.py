"""KISClient 동작 관련 테스트."""

from __future__ import annotations

import pytest

from kis.client import KISClient
from kis.config import KISConfig, KISEnvironment


@pytest.fixture()
def sample_config() -> KISConfig:
    """테스트용 기본 설정을 생성한다."""

    return KISConfig(
        app_key="test-app-key",
        app_secret="test-app-secret",
        account_no="12345678-01",
        environment=KISEnvironment.PAPER,
    )


def test_transport_env_switch(monkeypatch: pytest.MonkeyPatch, sample_config: KISConfig) -> None:
    """환경변수에 따라 웹소켓 모드가 활성화되는지 확인한다."""

    monkeypatch.setenv(KISClient.TRANSPORT_ENV_VAR, "websocket")
    client = KISClient(sample_config)
    assert client.use_websocket is True
    with pytest.raises(RuntimeError):
        client.get("/uapi/test")


def test_rest_default_transport(monkeypatch: pytest.MonkeyPatch, sample_config: KISConfig) -> None:
    """환경변수가 없을 때 기본적으로 REST 모드를 사용한다."""

    monkeypatch.delenv(KISClient.TRANSPORT_ENV_VAR, raising=False)
    client = KISClient(sample_config)
    assert client.use_websocket is False
    assert client.transport == "rest"
