from __future__ import annotations

import re
from html.parser import HTMLParser


class _HTMLStripper(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._chunks: list[str] = []

    def handle_data(self, data: str) -> None:  # noqa: D401
        if data:
            self._chunks.append(data)

    def get_text(self) -> str:
        return "".join(self._chunks)


def html_to_text(html: str) -> str:
    if not html:
        return ""
    s = html.strip()
    if not s:
        return ""
    stripper = _HTMLStripper()
    stripper.feed(s)
    stripper.close()
    return normalize_whitespace(stripper.get_text())


def normalize_whitespace(text: str) -> str:
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def strip_reddit_submission_footer(text: str) -> str:
    """
    Reddit RSS often contains a footer like:
    "submitted by /u/user [link] [comments]"
    We remove it to keep only the meaningful summary.
    """
    text = normalize_whitespace(text)
    if not text:
        return ""

    # English footer
    text = re.sub(
        r"\s*submitted\s+by\s+/u/\S+.*$",
        "",
        text,
        flags=re.IGNORECASE,
    ).strip()

    # Russian translation variant that can appear after translation
    text = re.sub(
        r"\s*отправлено\s+/u/\S+.*$",
        "",
        text,
        flags=re.IGNORECASE,
    ).strip()

    # Sometimes "[link] [comments]" remains as plain tokens
    text = re.sub(r"\s*\[(link|comments|ссылка|комментарии)\]\s*", " ", text, flags=re.IGNORECASE)
    return normalize_whitespace(text)


def clip(text: str, max_len: int) -> str:
    text = (text or "").strip()
    if not text:
        return ""
    if max_len <= 0:
        return ""
    if len(text) <= max_len:
        return text
    cut = text[: max(1, max_len - 1)].rstrip()
    return cut + "…"

