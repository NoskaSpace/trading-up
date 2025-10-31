# Trading Up

모듈화된 자동 매매 프로그램 MVP입니다. Raspberry Pi 4 환경에서 FastAPI, Telegram 봇, TimescaleDB/Redis 확장 포인트를 염두에 두고 설계되었습니다.

## 요구 사항
- Python 3.12 이상 (권장: 3.12 최신 패치)
- 가상환경 권장 (`python3.12 -m venv .venv`)

## 설치
```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e .[test]
```

## 환경 변수 구성
자동화된 배포 시 민감 정보가 코드에 포함되지 않도록 Telegram 및 한국투자증권(KIS) API 자격 증명은 모두 환경 변수로 주입해야 합니다.

### Telegram
```bash
export TELEGRAM_BOT_TOKEN="<봇 API 토큰>"
export TELEGRAM_CHAT_ID="<알림을 받을 채팅 ID>"  # 선택 사항
```
`TelegramBotConfig.from_env()` 를 사용하면 위 변수를 자동으로 읽어옵니다. 채팅 ID가 비어 있으면 수신 전용으로 동작합니다.

### 한국투자증권(KIS)
```bash
export KIS_APP_KEY="<앱 키>"
export KIS_APP_SECRET="<시크릿>"
export KIS_ACCOUNT_NO="<계좌번호>"
export KIS_ACCOUNT_TYPE="<계좌 구분>"  # 선택 사항
```
`KISCredentials.from_env()` 가 필수 변수 존재 여부를 검증하고, 실거래 브로커 개발 시 재사용할 수 있습니다.

## 테스트
```bash
pytest -q
```

## 면책 조항
해당 프로젝트는 오픈소스 예제로 제공되며, **해당 프로젝트로 인한 투자의 책임은 본인에게 있습니다.**
