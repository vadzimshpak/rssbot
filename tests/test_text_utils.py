from __future__ import annotations

from rssbot.text_utils import strip_reddit_submission_footer


def test_strip_reddit_submission_footer_english() -> None:
    src = "Some summary text submitted by /u/testuser [link] [comments]"
    assert strip_reddit_submission_footer(src) == "Some summary text"


def test_strip_reddit_submission_footer_russian() -> None:
    src = "Краткое описание отправлено /u/testuser [ссылка] [комментарии]"
    assert strip_reddit_submission_footer(src) == "Краткое описание"

