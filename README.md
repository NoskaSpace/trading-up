# Trading Up KIS SDK

한국투자증권(KIS) API를 활용한 주식 매매 및 백테스트 SDK 입니다. HTTP 요청은 `requests`를 사용하며, 설정값과 응답 구조는 데이터 클래스를 통해 관리합니다.

## 주요 기능

- OAuth2 기반 한국투자증권 토큰 발급 및 자동 갱신
- 실거래/모의투자 환경 전환 지원
- 주문 실행, 체결 내역, 계좌 잔고, 시세 조회 API 래퍼
- 환경변수 기반 REST/웹소켓 전송 선택 지원
- 캔들 데이터 기반 단순 백테스트 엔진과 포트폴리오 시뮬레이션

## 빠른 시작

```bash
pip install -e .
```

```python
from kis import KISBroker, BacktestBroker, KISConfig

config = KISConfig(
    app_key="발급받은 앱키",
    app_secret="발급받은 앱시크릿",
    account_no="12345678-01",
    is_paper=True,
)

broker = KISBroker.from_config(config)
print(broker.get_account_balance())
```

백테스트 예시는 `examples/backtest_ma.py`를 참고하세요.

웹소켓 기반 실시간 스트리밍을 사용하려면 `KIS_TRANSPORT=websocket` 환경변수를 설정하고, `KISBroker.run_websocket` 또는 `KISClient.websocket` 인터페이스를 통해 한국투자증권이 제공하는 TR ID, 요청 본문을 전달하면 됩니다.
