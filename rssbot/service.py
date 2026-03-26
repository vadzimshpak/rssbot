from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass
from datetime import datetime, timezone

from rssbot.formatter import TelegramFormatter
from rssbot.models import RssItem
from rssbot.rss_reader import RssReader
from rssbot.storage import SqliteStorage
from rssbot.telegram_client import TelegramBotClient
from rssbot.text_utils import clip, html_to_text, strip_reddit_submission_footer
from rssbot.translator import OpenRouterTranslator


@dataclass(frozen=True)
class RssToTelegramService:
    rss_reader: RssReader
    translator: OpenRouterTranslator
    telegram: TelegramBotClient
    storage: SqliteStorage
    add_source_link: bool
    summary_max_chars: int
    translate_summary: bool

    def poll_and_post(self, *, rss_urls: list[str], chat_id: str, max_items: int) -> int:
        urls = [u.strip() for u in (rss_urls or []) if u and u.strip()]
        if not urls:
            return 0

        candidates: list[tuple[str, RssItem]] = []
        for rss_url in urls:
            items = self.rss_reader.newest_first(self.rss_reader.fetch(rss_url))
            for item in items:
                candidates.append((rss_url, item))

        if not candidates:
            return 0

        # Filter out items already posted (dedupe across all sources)
        new_items: list[tuple[str, RssItem, str]] = []
        for rss_url, item in candidates:
            storage_key = _storage_key(rss_url=rss_url, item=item)
            if not self.storage.was_posted(storage_key):
                new_items.append((rss_url, item, storage_key))

        if not new_items:
            return 0

        random.shuffle(new_items)
        limit = max(1, int(max_items or 1))
        to_post = new_items[:limit]

        posted = 0
        for _rss_url, item, storage_key in to_post:
            text_ru = self._build_message(item)
            self.telegram.send_message(
                chat_id=chat_id,
                text=text_ru,
                parse_mode="HTML",
                disable_web_page_preview=False,
            )
            self.storage.mark_posted(storage_key, posted_at_iso=_now_iso())
            posted += 1

        return posted

    def _build_message(self, item: RssItem) -> str:
        title_ru = self.translator.translate_to_ru(item.title)

        summary_clean = strip_reddit_submission_footer(html_to_text(item.summary_html or ""))
        summary_src = clip(summary_clean, self.summary_max_chars)
        if self.translate_summary and summary_src:
            summary_ru = self.translator.translate_to_ru(summary_src)
        else:
            summary_ru = summary_src

        formatter = TelegramFormatter(add_source_link=self.add_source_link)
        return formatter.format_post(item=item, title_ru=title_ru, summary_ru=summary_ru)

def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def _storage_key(*, rss_url: str, item: RssItem) -> str:
    raw = f"{rss_url}|{item.id}|{item.url}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
