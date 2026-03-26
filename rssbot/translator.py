from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import requests


class TranslationError(RuntimeError):
    pass


@dataclass(frozen=True)
class OpenRouterTranslator:
    api_key: str
    model: str
    timeout_seconds: int = 60

    def translate_to_ru(self, text: str, *, max_chars: int = 8000) -> str:
        text = (text or "").strip()
        if not text:
            return ""

        clipped = text[:max_chars]
        prompt = (
            "Переведи на русский язык. Сохрани смысл и стиль. "
            "Не добавляй факты от себя. "
            "Если в тексте есть ссылки — оставь их как есть.\n\n"
            f"Текст:\n{clipped}"
        )

        content = self._chat(prompt)
        return (content or "").strip()

    def _chat(self, prompt: str) -> str:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "Ты помощник-переводчик."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        }

        try:
            r = requests.post(url, headers=headers, json=payload, timeout=self.timeout_seconds)
        except requests.RequestException as e:
            raise TranslationError(f"OpenRouter недоступен: {e}") from e

        if r.status_code >= 400:
            raise TranslationError(f"OpenRouter вернул {r.status_code}: {r.text[:500]}")

        data = r.json()
        content = _safe_get_content(data)
        if not content:
            raise TranslationError("OpenRouter: пустой ответ (нет choices[0].message.content).")
        return content


def _safe_get_content(data: object) -> Optional[str]:
    try:
        choices = data["choices"]
        msg = choices[0]["message"]
        return msg.get("content")
    except Exception:
        return None
