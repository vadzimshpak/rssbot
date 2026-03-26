from __future__ import annotations

from dataclasses import dataclass

import requests


class TelegramError(RuntimeError):
    pass


@dataclass(frozen=True)
class TelegramBotClient:
    bot_token: str
    timeout_seconds: int = 30

    def send_message(
        self,
        *,
        chat_id: str,
        text: str,
        parse_mode: str = "HTML",
        disable_web_page_preview: bool = False,
    ) -> None:
        text = (text or "").strip()
        if not text:
            return

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": disable_web_page_preview,
        }

        try:
            r = requests.post(url, json=payload, timeout=self.timeout_seconds)
        except requests.RequestException as e:
            raise TelegramError(f"Telegram недоступен: {e}") from e

        if r.status_code >= 400:
            raise TelegramError(f"Telegram вернул {r.status_code}: {r.text[:500]}")

        data = r.json()
        if not data.get("ok", False):
            raise TelegramError(f"Telegram ошибка: {str(data)[:500]}")
