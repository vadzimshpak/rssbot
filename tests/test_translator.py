from __future__ import annotations

import os

import requests

from rssbot.translator import OpenRouterTranslator, TranslationError


class _FakeResponse:
    def __init__(self, status_code: int, json_data: dict | None = None, text: str = "") -> None:
        self.status_code = status_code
        self._json_data = json_data or {}
        self.text = text

    def json(self) -> dict:
        return self._json_data


def test_openrouter_translator_success(monkeypatch) -> None:
    def fake_post(url, headers=None, json=None, timeout=None):  # noqa: ANN001
        assert url == "https://openrouter.ai/api/v1/chat/completions"
        assert headers["Authorization"].startswith("Bearer ")
        assert json["model"]
        return _FakeResponse(
            200,
            json_data={"choices": [{"message": {"content": "Привет, мир!"}}]},
        )

    monkeypatch.setattr(requests, "post", fake_post)

    tr = OpenRouterTranslator(
        api_key=os.getenv("OPENROUTER_API_KEY", "test"),
        model=os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
    )
    out = tr.translate_to_ru("Hello, world!")
    assert out == "Привет, мир!"


def test_openrouter_translator_http_error(monkeypatch) -> None:
    def fake_post(url, headers=None, json=None, timeout=None):  # noqa: ANN001
        return _FakeResponse(429, text="rate limit")

    monkeypatch.setattr(requests, "post", fake_post)

    tr = OpenRouterTranslator(
        api_key=os.getenv("OPENROUTER_API_KEY", "test"),
        model=os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
    )
    try:
        tr.translate_to_ru("Hello")
        assert False, "Expected TranslationError"
    except TranslationError as e:
        assert "429" in str(e)


def test_openrouter_translator_request_exception(monkeypatch) -> None:
    def fake_post(url, headers=None, json=None, timeout=None):  # noqa: ANN001
        raise requests.RequestException("network down")

    monkeypatch.setattr(requests, "post", fake_post)

    tr = OpenRouterTranslator(
        api_key=os.getenv("OPENROUTER_API_KEY", "test"),
        model=os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
    )
    try:
        tr.translate_to_ru("Hello")
        assert False, "Expected TranslationError"
    except TranslationError as e:
        assert "недоступен" in str(e).lower()

