from __future__ import annotations

import logging
from dataclasses import dataclass
from logging.handlers import RotatingFileHandler
from pathlib import Path


@dataclass(frozen=True)
class LoggingConfig:
    level: str = "DEBUG"
    file_path: Path = Path("./rssbot.log")
    max_bytes: int = 5 * 1024 * 1024
    backup_count: int = 3


def setup_logging(cfg: LoggingConfig) -> None:
    level = _parse_level(cfg.level)

    root = logging.getLogger()
    root.setLevel(level)

    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Avoid duplicate handlers if setup called multiple times
    if not any(isinstance(h, logging.StreamHandler) for h in root.handlers):
        sh = logging.StreamHandler()
        sh.setLevel(level)
        sh.setFormatter(fmt)
        root.addHandler(sh)

    cfg.file_path.parent.mkdir(parents=True, exist_ok=True)
    if not any(isinstance(h, RotatingFileHandler) for h in root.handlers):
        fh = RotatingFileHandler(
            filename=str(cfg.file_path),
            maxBytes=cfg.max_bytes,
            backupCount=cfg.backup_count,
            encoding="utf-8",
        )
        fh.setLevel(level)
        fh.setFormatter(fmt)
        root.addHandler(fh)


def _parse_level(level: str) -> int:
    lvl = (level or "").strip().upper()
    return getattr(logging, lvl, logging.DEBUG)

