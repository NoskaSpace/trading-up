"""Korea Investment & Securities broker scaffolding."""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class KISCredentials:
    """Credentials required for accessing the KIS open API."""

    app_key: str
    app_secret: str
    account_no: str
    account_type: Optional[str] = None

    @classmethod
    def from_env(
        cls,
        app_key_var: str = "KIS_APP_KEY",
        app_secret_var: str = "KIS_APP_SECRET",
        account_var: str = "KIS_ACCOUNT_NO",
        account_type_var: str = "KIS_ACCOUNT_TYPE",
    ) -> "KISCredentials":
        """Load KIS API credentials from environment variables."""

        app_key = os.getenv(app_key_var)
        app_secret = os.getenv(app_secret_var)
        account_no = os.getenv(account_var)
        if not app_key or not app_secret or not account_no:
            missing = [
                name
                for name, value in (
                    (app_key_var, app_key),
                    (app_secret_var, app_secret),
                    (account_var, account_no),
                )
                if not value
            ]
            raise RuntimeError(
                "Missing required KIS API environment variables: " + ", ".join(missing)
            )
        account_type = os.getenv(account_type_var)
        return cls(
            app_key=app_key,
            app_secret=app_secret,
            account_no=account_no,
            account_type=account_type,
        )


__all__ = ["KISCredentials"]
