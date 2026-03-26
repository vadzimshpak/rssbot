from __future__ import annotations

import time

from dotenv import load_dotenv

from rssbot.config import AppConfig
from rssbot.rss_reader import RssReader
from rssbot.service import RssToTelegramService
from rssbot.storage import SqliteStorage
from rssbot.telegram_client import TelegramBotClient
from rssbot.translator import OpenRouterTranslator


def main() -> None:
    load_dotenv()
    cfg = AppConfig.from_env()

    storage = SqliteStorage(cfg.db_path)
    storage.init()

    service = RssToTelegramService(
        rss_reader=RssReader(user_agent="rssbot/1.0 (telegram rss poster)"),
        translator=OpenRouterTranslator(api_key=cfg.openrouter_api_key, model=cfg.openrouter_model),
        telegram=TelegramBotClient(bot_token=cfg.telegram_bot_token),
        storage=storage,
        add_source_link=cfg.add_source_link,
        summary_max_chars=cfg.summary_max_chars,
        translate_summary=cfg.translate_summary,
    )

    while True:
        service.poll_and_post(
            rss_urls=cfg.rss_urls,
            chat_id=cfg.telegram_chat_username,
            max_items=cfg.max_items_per_poll,
        )
        time.sleep(cfg.poll_interval_seconds)


if __name__ == "__main__":
    main()
