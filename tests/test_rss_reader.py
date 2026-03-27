from __future__ import annotations

from types import SimpleNamespace

import feedparser
import requests

from rssbot.rss_reader import RssReader


def test_rss_reader_fetch_parses_entries(monkeypatch) -> None:
    captured: dict = {}

    entry = SimpleNamespace(
        id="t3_abc",
        link="https://www.reddit.com/r/technology/comments/abc/test/",
        title="Test title",
        author="user",
        summary="<p>hi</p>",
        published_parsed=(2026, 3, 26, 10, 11, 53, 0, 0, 0),
    )

    class _FakeResponse:
        def __init__(self, content: bytes) -> None:
            self.content = content

        def raise_for_status(self) -> None:
            return None

    def fake_get(url, headers=None, timeout=None):  # noqa: ANN001
        captured["url"] = url
        captured["headers"] = headers
        captured["timeout"] = timeout
        return _FakeResponse(b"<rss/>")

    def fake_parse(content):  # noqa: ANN001
        captured["parse_input_type"] = type(content)
        return SimpleNamespace(entries=[entry])

    monkeypatch.setattr(requests, "get", fake_get)
    monkeypatch.setattr(feedparser, "parse", fake_parse)

    rr = RssReader(user_agent="UA", timeout_seconds=7)
    items = rr.fetch("https://example.com/feed.rss")

    assert captured["url"] == "https://example.com/feed.rss"
    assert captured["headers"]["User-Agent"] == "UA"
    assert captured["timeout"] == 7
    assert captured["parse_input_type"] is bytes
    assert len(items) == 1

    item = items[0]
    assert item.id == "t3_abc"
    assert item.url.startswith("https://www.reddit.com/")
    assert item.title == "Test title"
    assert item.author == "user"
    assert item.published_at is not None


def test_rss_reader_skips_incomplete_entries(monkeypatch) -> None:
    bad_entry = SimpleNamespace(id="", link="", title="")

    class _FakeResponse:
        def __init__(self) -> None:
            self.content = b"<rss/>"

        def raise_for_status(self) -> None:
            return None

    def fake_get(url, headers=None, timeout=None):  # noqa: ANN001
        return _FakeResponse()

    def fake_parse(content):  # noqa: ANN001
        return SimpleNamespace(entries=[bad_entry])

    monkeypatch.setattr(requests, "get", fake_get)
    monkeypatch.setattr(feedparser, "parse", fake_parse)

    rr = RssReader()
    assert rr.fetch("https://example.com/feed.rss") == []

