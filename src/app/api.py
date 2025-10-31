"""인증된 상태 확인 기능을 제공하는 FastAPI 애플리케이션."""
from __future__ import annotations

import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, FastAPI, HTTPException, status as http_status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

app = FastAPI(title="Trading MVP", version="0.1.0")


def _get_required_env(name: str) -> str:
    """필수 환경 변수를 조회하여 누락 시 명확한 오류를 발생시킨다."""

    value = os.environ.get(name)
    if value is None or value.strip() == "":
        raise RuntimeError(f"{name} 환경 변수가 설정되지 않았습니다. 실행 환경 구성을 확인하세요.")
    return value


def _get_int_env(name: str, default: int) -> int:
    """정수형 환경 변수를 파싱하면서 잘못된 설정을 조기에 감지한다."""

    raw_value = os.environ.get(name)
    if raw_value is None:
        return default
    try:
        return int(raw_value)
    except ValueError as exc:
        raise RuntimeError(f"{name} 환경 변수는 정수로 설정해야 합니다.") from exc


# 환경 변수에서 관리자 자격 증명을 불러와서 동적으로 구성한다.
ADMIN_USERNAME = _get_required_env("ADMIN_USERNAME")
ADMIN_PASSWORD = _get_required_env("ADMIN_PASSWORD")
SECRET_KEY = _get_required_env("AUTH_SECRET_KEY")
TOKEN_EXPIRE_MINUTES = _get_int_env("TOKEN_EXPIRE_MINUTES", 60)
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def _verify_credentials(username: str, password: str) -> bool:
    """환경 변수로 정의된 관리자 자격 증명과 안전하게 비교한다."""

    # timing attack을 방지하기 위해 상수 시간 비교를 사용한다.
    return secrets.compare_digest(username, ADMIN_USERNAME) and secrets.compare_digest(
        password, ADMIN_PASSWORD
    )


def _create_access_token(subject: str) -> str:
    """JWT 액세스 토큰을 생성하여 만료 정보를 포함한다."""

    expire = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def _decode_access_token(token: str) -> str:
    """토큰을 검증하고 사용자 식별자를 반환한다."""

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(status_code=http_status.HTTP_401_UNAUTHORIZED, detail="토큰이 만료되었습니다.") from exc
    except jwt.InvalidSignatureError as exc:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="토큰 서명이 올바르지 않습니다. 서버의 비밀키 설정을 확인하세요.",
        ) from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status_code=http_status.HTTP_401_UNAUTHORIZED, detail="유효하지 않은 토큰입니다.") from exc

    subject = payload.get("sub")
    if subject is None:
        raise HTTPException(status_code=http_status.HTTP_401_UNAUTHORIZED, detail="토큰 정보가 부족합니다.")
    return subject


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> str:
    """요청에 포함된 토큰을 검증하여 현재 사용자를 확인한다."""

    return _decode_access_token(token)


@app.post("/auth/token")
def issue_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> dict[str, str]:
    """관리자 로그인 요청을 처리하고 JWT를 반환한다."""

    if not _verify_credentials(form_data.username, form_data.password):
        raise HTTPException(status_code=http_status.HTTP_401_UNAUTHORIZED, detail="인증에 실패했습니다.")

    token = _create_access_token(form_data.username)
    return {"access_token": token, "token_type": "bearer"}


@app.get("/healthz")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/version")
def version() -> dict[str, str]:
    return {"version": app.version}


@app.get("/status")
def read_status(current_user: Annotated[str, Depends(get_current_user)]) -> dict[str, str]:
    """API 상태와 추가 메타데이터를 제공한다."""

    # 서버 시각을 ISO 8601 형식으로 전달하여 클라이언트에서 동기화할 수 있도록 한다.
    return {
        "status": "ok",
        "version": app.version,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user": current_user,
    }


__all__ = ["app"]
