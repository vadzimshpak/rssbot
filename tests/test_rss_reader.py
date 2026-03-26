from __future__ import annotations

from types import SimpleNamespace

import feedparser

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

    def fake_parse(url, agent=None):  # noqa: ANN001
        captured["url"] = url
        captured["agent"] = agent
        return SimpleNamespace(entries=[entry])

    monkeypatch.setattr(feedparser, "parse", fake_parse)

    rr = RssReader(user_agent="UA")
    items = rr.fetch("https://example.com/feed.rss")

    assert captured["url"] == "https://example.com/feed.rss"
    assert captured["agent"] == "UA"
    assert len(items) == 1

    item = items[0]
    assert item.id == "t3_abc"
    assert item.url.startswith("https://www.reddit.com/")
    assert item.title == "Test title"
    assert item.author == "user"
    assert item.published_at is not None


def test_rss_reader_skips_incomplete_entries(monkeypatch) -> None:
    bad_entry = SimpleNamespace(id="", link="", title="")

    def fake_parse(url, agent=None):  # noqa: ANN001
        return SimpleNamespace(entries=[bad_entry])

    monkeypatch.setattr(feedparser, "parse", fake_parse)

    rr = RssReader()
    assert rr.fetch("https://example.com/feed.rss") == []

