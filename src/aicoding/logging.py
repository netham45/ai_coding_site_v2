from __future__ import annotations

import logging
import logging.config

from aicoding.config import Settings, get_settings


def configure_logging(settings: Settings | None = None) -> None:
    active_settings = settings or get_settings()
    normalized_log_level = active_settings.normalized_log_level
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "standard",
                    "level": normalized_log_level,
                }
            },
            "root": {
                "handlers": ["console"],
                "level": normalized_log_level,
            },
        }
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
