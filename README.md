# rssbot (Reddit RSS → Telegram с переводом на русский)

Скрипт читает один или несколько RSS (например, Reddit `https://www.reddit.com/r/technology/.rss`), переводит заголовки на русский через OpenRouter и публикует в Telegram-канал от имени бота.  
Логика разнесена по модулям: RSS, перевод, Telegram, хранилище, сервис-оркестратор.

## Установка

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Настройка

1) Скопируй `.env.example` в `.env` и заполни:
- `OPENROUTER_API_KEY`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_USERNAME` (например `@my_channel`)
 - `RSS_URLS` (одна или несколько RSS-ссылок, через запятую или с новой строки)

2) Убедись, что бот — админ канала (и может писать сообщения).

## Запуск

```bash
python main.py
```

По умолчанию запуск идёт **по cron** (см. `CRON_SCHEDULES` в `.env`).

Если нужно выполнить один проход вручную:

```bash
RUN_MODE=once python main.py
```

## Структура

- `rssbot/rss_reader.py`: `RssReader` читает RSS и нормализует элементы
- `rssbot/translator.py`: `OpenRouterTranslator` переводит текст на русский через OpenRouter
- `rssbot/telegram_client.py`: `TelegramBotClient` отправляет сообщения через Telegram Bot API
- `rssbot/storage.py`: `SqliteStorage` хранит `item_id`, чтобы не постить дубли
- `rssbot/service.py`: `RssToTelegramService` связывает всё вместе
- `main.py`: загрузка конфига и бесконечный polling-цикл

