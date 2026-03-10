from __future__ import annotations

from pathlib import Path

from aicoding.config import Settings, get_settings
from aicoding.errors import ConfigurationError


def read_token_file(path: Path) -> str | None:
    if not path.exists() or path.is_dir():
        return None

    token = path.read_text(encoding="utf-8").strip()
    return token or None


def load_auth_token(*, settings: Settings | None = None, prefer_file: bool = True) -> str:
    active_settings = settings or get_settings()
    auth_settings = active_settings.auth

    if prefer_file:
        file_token = read_token_file(auth_settings.token_file)
        if file_token is not None:
            return file_token

    token = auth_settings.token.strip()
    if token:
        return token

    raise ConfigurationError(
        message="No daemon authentication token is configured.",
        code="auth_token_missing",
        details={"auth_token_file": str(auth_settings.token_file)},
    )
