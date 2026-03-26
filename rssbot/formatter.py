from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from rssbot.models import RssItem


@dataclass(frozen=True)
class TelegramFormatter:
    add_source_link: bool = True

    def format_post(
        self,
        *,
        item: RssItem,
        title_ru: str,
        summary_ru: str,
    ) -> str:
        title_ru = _escape_html(title_ru)
        summary_ru = _escape_html(summary_ru)

        parts: list[str] = []
        parts.append(f"<b>{title_ru}</b>")

        if summary_ru:
            parts.append(f"\n\n{summary_ru}")

        meta = self._format_meta(author=item.author, published_at=item.published_at)
        if meta:
            parts.append(f"\n\n<i>{_escape_html(meta)}</i>")

        if self.add_source_link:
            parts.append(f'\n<a href="{_escape_attr(item.url)}">Читать источник</a>')

        return "".join(parts).strip()

    @staticmethod
    def _format_meta(*, author: Optional[str], published_at: Optional[datetime]) -> str:
        chunks: list[str] = []
        if author:
            chunks.append(author.strip())
        if published_at:
            chunks.append(_format_date_ru(published_at))
        return " • ".join([c for c in chunks if c])


def _format_date_ru(dt: datetime) -> str:
    try:
        return dt.astimezone().strftime("%d.%m.%Y %H:%M")
    except Exception:
        return dt.isoformat()


def _escape_html(s: str) -> str:
    import html

    return html.escape(s or "", quote=False)


def _escape_attr(s: str) -> str:
    import html

    return html.escape(s or "", quote=True)

