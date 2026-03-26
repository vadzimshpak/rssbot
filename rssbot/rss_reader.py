from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable, Optional

import feedparser

from rssbot.models import RssItem


@dataclass(frozen=True)
class RssReader:
    user_agent: str = "rssbot/1.0 (+https://example.com)"

    def fetch(self, url: str) -> list[RssItem]:
        feed = feedparser.parse(url, agent=self.user_agent)
        entries = getattr(feed, "entries", []) or []
        items: list[RssItem] = []
        for e in entries:
            link = (getattr(e, "link", None) or "").strip()
            item_id = (getattr(e, "id", None) or link or "").strip()
            title = (getattr(e, "title", None) or "").strip()
            author = (getattr(e, "author", None) or None)
            summary = getattr(e, "summary", None) or getattr(e, "content", None)

            published_at = self._parse_published(e)

            if not item_id or not link or not title:
                continue

            items.append(
                RssItem(
                    id=item_id,
                    title=title,
                    url=link,
                    author=str(author).strip() if author else None,
                    published_at=published_at,
                    summary_html=str(summary).strip() if summary else None,
                )
            )
        return items

    @staticmethod
    def _parse_published(entry: object) -> Optional[datetime]:
        st = getattr(entry, "published_parsed", None) or getattr(entry, "updated_parsed", None)
        if not st:
            return None
        try:
            return datetime(*st[:6], tzinfo=timezone.utc)
        except Exception:
            return None

    @staticmethod
    def newest_first(items: Iterable[RssItem]) -> list[RssItem]:
        def key(x: RssItem) -> tuple[int, str]:
            # items without timestamp go last
            ts = int(x.published_at.timestamp()) if x.published_at else -1
            return (ts, x.id)

        return sorted(list(items), key=key, reverse=True)
