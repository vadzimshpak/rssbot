from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class RssItem:
    id: str
    title: str
    url: str
    author: Optional[str]
    published_at: Optional[datetime]
    summary_html: Optional[str]


@dataclass(frozen=True)
class TelegramPost:
    text: str
    disable_web_page_preview: bool = False
