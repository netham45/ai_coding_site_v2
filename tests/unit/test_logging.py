from __future__ import annotations

import logging

from aicoding.config import Settings
from aicoding.logging import configure_logging, get_logger


def test_configure_logging_sets_root_level() -> None:
    configure_logging(Settings(log_level="debug"))

    assert logging.getLogger().level == logging.DEBUG


def test_get_logger_returns_named_logger() -> None:
    logger = get_logger("aicoding.test")

    assert logger.name == "aicoding.test"

