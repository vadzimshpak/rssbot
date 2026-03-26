from __future__ import annotations

import os

from rssbot.config import AppConfig


def test_config_parses_rss_urls_from_rss_urls_env(monkeypatch) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "x")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "x")
    monkeypatch.setenv("TELEGRAM_CHAT_USERNAME", "@chan")

    monkeypatch.setenv("RSS_URLS", "https://a.example/rss, https://b.example/rss\nhttps://c.example/rss")
    monkeypatch.delenv("RSS_URL", raising=False)

    cfg = AppConfig.from_env()
    assert cfg.rss_urls == ["https://a.example/rss", "https://b.example/rss", "https://c.example/rss"]


def test_config_falls_back_to_rss_url(monkeypatch) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "x")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "x")
    monkeypatch.setenv("TELEGRAM_CHAT_USERNAME", "@chan")

    monkeypatch.delenv("RSS_URLS", raising=False)
    monkeypatch.setenv("RSS_URL", "https://only.example/rss")

    cfg = AppConfig.from_env()
    assert cfg.rss_urls == ["https://only.example/rss"]

