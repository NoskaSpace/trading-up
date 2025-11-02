"""SDK 전용 예외 클래스 정의."""


class KISAPIError(Exception):
    """KIS REST API 호출 실패를 표현하는 예외."""


class BacktestError(Exception):
    """백테스트 실행 시 발생하는 예외."""
