from __future__ import annotations

import os

import requests

from rssbot.telegram_client import TelegramBotClient, TelegramError


class _FakeResponse:
    def __init__(self, status_code: int, json_data: dict | None = None, text: str = "") -> None:
        self.status_code = status_code
        self._json_data = json_data or {}
        self.text = text

    def json(self) -> dict:
        return self._json_data


def test_telegram_send_message_success(monkeypatch) -> None:
    calls: list[dict] = []

    def fake_post(url, json=None, timeout=None):  # noqa: ANN001
        calls.append({"url": url, "json": json, "timeout": timeout})
        return _FakeResponse(200, json_data={"ok": True, "result": {"message_id": 1}})

    monkeypatch.setattr(requests, "post", fake_post)

    token = os.getenv("TELEGRAM_BOT_TOKEN", "TOKEN")
    tg = TelegramBotClient(bot_token=token)
    tg.send_message(chat_id="@vshbiz", text="<b>Hi</b>", parse_mode="HTML", disable_web_page_preview=True)

    assert len(calls) == 1
    assert calls[0]["url"] == f"https://api.telegram.org/bot{token}/sendMessage"
    assert calls[0]["json"]["chat_id"] == "@vshbiz"
    assert calls[0]["json"]["text"] == "<b>Hi</b>"
    assert calls[0]["json"]["parse_mode"] == "HTML"
    assert calls[0]["json"]["disable_web_page_preview"] is True


def test_telegram_send_message_http_error(monkeypatch) -> None:
    def fake_post(url, json=None, timeout=None):  # noqa: ANN001
        return _FakeResponse(500, text="server error")

    monkeypatch.setattr(requests, "post", fake_post)

    tg = TelegramBotClient(bot_token=os.getenv("TELEGRAM_BOT_TOKEN", "TOKEN"))
    try:
        tg.send_message(chat_id="@chan", text="Hi")
        assert False, "Expected TelegramError"
    except TelegramError as e:
        assert "500" in str(e)


def test_telegram_send_message_api_not_ok(monkeypatch) -> None:
    def fake_post(url, json=None, timeout=None):  # noqa: ANN001
        return _FakeResponse(200, json_data={"ok": False, "description": "bad request"})

    monkeypatch.setattr(requests, "post", fake_post)

    tg = TelegramBotClient(bot_token=os.getenv("TELEGRAM_BOT_TOKEN", "TOKEN"))
    try:
        tg.send_message(chat_id="@vshbiz", text="Hi")
        assert False, "Expected TelegramError"
    except TelegramError:
        pass

