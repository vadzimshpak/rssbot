from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from rssbot.text_utils import normalize_whitespace


def _getenv_str(name: str, default: Optional[str] = None) -> Optional[str]:
    import os

    val = os.getenv(name)
    if val is None:
        return default
    val = val.strip()
    return val if val else default


def _getenv_int(name: str, default: int) -> int:
    raw = _getenv_str(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _getenv_bool(name: str, default: bool) -> bool:
    raw = _getenv_str(name)
    if raw is None:
        return default
    return raw.lower() in {"1", "true", "yes", "y", "on"}


def _getenv_list(name: str) -> list[str]:
    raw = _getenv_str(name)
    if not raw:
        return []
    raw = raw.replace("\r\n", "\n").replace("\r", "\n")
    parts: list[str] = []
    for line in raw.split("\n"):
        for piece in line.split(","):
            piece = normalize_whitespace(piece)
            if piece:
                parts.append(piece)
    return parts


@dataclass(frozen=True)
class AppConfig:
    rss_urls: list[str]
    poll_interval_seconds: int
    max_items_per_poll: int
    add_source_link: bool
    summary_max_chars: int
    translate_summary: bool
    cron_schedules: list[str]

    openrouter_api_key: str
    openrouter_model: str

    telegram_bot_token: str
    telegram_chat_username: str

    db_path: Path

    @staticmethod
    def from_env() -> "AppConfig":
        rss_urls = _getenv_list("RSS_URLS")
        if not rss_urls:
            rss_urls = [_getenv_str("RSS_URL", "https://www.reddit.com/r/technology/.rss")]

        poll_interval_seconds = _getenv_int("POLL_INTERVAL_SECONDS", 300)
        max_items_per_poll = _getenv_int("MAX_ITEMS_PER_POLL", 5)
        add_source_link = _getenv_bool("ADD_SOURCE_LINK", True)
        summary_max_chars = _getenv_int("SUMMARY_MAX_CHARS", 420)
        translate_summary = _getenv_bool("TRANSLATE_SUMMARY", True)
        cron_schedules = _getenv_list("CRON_SCHEDULES")

        openrouter_api_key = _getenv_str("OPENROUTER_API_KEY")
        openrouter_model = _getenv_str("OPENROUTER_MODEL", "openai/gpt-4o-mini")

        telegram_bot_token = _getenv_str("TELEGRAM_BOT_TOKEN")
        telegram_chat_username = _getenv_str("TELEGRAM_CHAT_USERNAME") or _getenv_str("TELEGRAM_CHAT_ID")

        db_path = Path(_getenv_str("DB_PATH", "./rssbot.sqlite3"))

        missing = []
        if not openrouter_api_key:
            missing.append("OPENROUTER_API_KEY")
        if not telegram_bot_token:
            missing.append("TELEGRAM_BOT_TOKEN")
        if not telegram_chat_username:
            missing.append("TELEGRAM_CHAT_USERNAME (или TELEGRAM_CHAT_ID)")
        if not rss_urls or not all(rss_urls):
            missing.append("RSS_URLS (или RSS_URL)")

        if missing:
            raise RuntimeError(
                "Не заданы переменные окружения: " + ", ".join(missing) + ". "
                "Скопируй .env.example в .env и заполни значения."
            )

        return AppConfig(
            rss_urls=rss_urls,
            poll_interval_seconds=max(10, poll_interval_seconds),
            max_items_per_poll=max(1, max_items_per_poll),
            add_source_link=add_source_link,
            summary_max_chars=max(0, summary_max_chars),
            translate_summary=translate_summary,
            cron_schedules=cron_schedules,
            openrouter_api_key=openrouter_api_key,
            openrouter_model=openrouter_model or "openai/gpt-4o-mini",
            telegram_bot_token=telegram_bot_token,
            telegram_chat_username=telegram_chat_username,
            db_path=db_path,
        )
