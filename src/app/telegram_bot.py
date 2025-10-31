"""Telegram bot skeleton for notifications."""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Optional

try:
    from telegram import Update
    from telegram.ext import Application, CommandHandler, ContextTypes
except Exception:  # pragma: no cover - telegram optional in MVP
    Update = object  # type: ignore
    ContextTypes = object  # type: ignore
    Application = object  # type: ignore


logger = logging.getLogger(__name__)


@dataclass
class TelegramBotConfig:
    token: str
    chat_id: Optional[int] = None

    @classmethod
    def from_env(
        cls,
        token_var: str = "TELEGRAM_BOT_TOKEN",
        chat_id_var: str = "TELEGRAM_CHAT_ID",
    ) -> "TelegramBotConfig":
        """Load Telegram bot credentials from environment variables."""

        token = os.getenv(token_var)
        if not token:
            raise RuntimeError(
                f"Missing Telegram bot token environment variable: {token_var}"
            )
        chat_id_value = os.getenv(chat_id_var)
        chat_id = int(chat_id_value) if chat_id_value else None
        return cls(token=token, chat_id=chat_id)


class TelegramBot:
    """Minimal Telegram bot wrapper for notifications."""

    def __init__(self, config: TelegramBotConfig) -> None:
        self.config = config
        if isinstance(Application, type):
            self.app = Application.builder().token(config.token).build()
            self.app.add_handler(CommandHandler("ping", self.on_ping))
        else:
            self.app = None

    async def on_ping(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:  # type: ignore[attr-defined]
        await context.bot.send_message(chat_id=update.effective_chat.id, text="pong")

    async def send_message(self, message: str) -> None:
        if self.app is None or self.config.chat_id is None:
            logger.warning("Telegram bot not configured for sending messages")
            return
        await self.app.bot.send_message(chat_id=self.config.chat_id, text=message)

    def run_polling(self) -> None:
        if self.app is None:
            logger.warning("Telegram bot dependencies not installed")
            return
        self.app.run_polling()


__all__ = ["TelegramBot", "TelegramBotConfig"]
