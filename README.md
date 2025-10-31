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

## Docker 환경
프로젝트는 Docker 및 Docker Compose로 실행할 수 있습니다. 루트 디렉터리에 `.env.example`을 참고하여 `.env` 파일을 생성하세요.

```bash
cp .env.example .env
docker compose up --build
```

- React 대시보드: <http://localhost>
- FastAPI OpenAPI 문서: <http://localhost/docs>
- 헬스체크: <http://localhost/healthz>

`docker compose` 명령은 내부 브리지 네트워크(`trading_internal`)를 생성하여 서비스 간 통신을 안전하게 처리합니다. 프런트엔드는 Nginx로 서빙되며 `/api` 경로를 백엔드로 역방향 프록시합니다.

### 인증
React 대시보드는 `/auth/token` 엔드포인트를 통해 JWT를 발급받아 `/status` API를 조회합니다. `.env` 파일에 아래 값을 정의하여 관리자 계정을 설정하세요.

```bash
ADMIN_USERNAME=<관리자 아이디>
ADMIN_PASSWORD=<강력한 비밀번호>
AUTH_SECRET_KEY=<JWT 서명용 시크릿>
TOKEN_EXPIRE_MINUTES=60
```

프런트엔드 이미지는 `VITE_API_BASE_URL` 환경 변수를 활용해 API 경로를 주입합니다. 기본값은 `/api`이며, 외부 로드밸런서를 사용할 경우 `docker-compose.yml` 혹은 배포 환경 변수로 값을 덮어쓸 수 있습니다.

## 면책 조항
해당 프로젝트는 오픈소스 예제로 제공되며, **해당 프로젝트로 인한 투자의 책임은 본인에게 있습니다.**
