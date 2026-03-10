from __future__ import annotations

import os
import secrets
import stat
from pathlib import Path

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from aicoding.auth import read_token_file
from aicoding.config import Settings
from aicoding.daemon.models import AuthContextResponse
from aicoding.errors import ConfigurationError

bearer_scheme = HTTPBearer(auto_error=False)


def _set_local_only_permissions(path: Path, *, file_mode: int) -> None:
    try:
        os.chmod(path, file_mode)
    except OSError:
        return


def _write_token_file(path: Path, token: str) -> None:
    if path.exists() and path.is_dir():
        raise ConfigurationError(
            message="Daemon auth token path points to a directory.",
            code="auth_token_path_invalid",
            details={"auth_token_file": str(path)},
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    _set_local_only_permissions(path.parent, file_mode=0o700)
    path.write_text(f"{token}\n", encoding="utf-8")
    _set_local_only_permissions(path, file_mode=0o600)


def initialize_auth_context(settings: Settings) -> AuthContextResponse:
    token_file = settings.auth.token_file
    file_token = read_token_file(token_file)
    if file_token:
        _set_local_only_permissions(token_file, file_mode=0o600)
        return AuthContextResponse(token_file=str(token_file), token_source="file")

    seed_token = settings.auth.token.strip()
    token = seed_token or secrets.token_urlsafe(32)
    source = "settings" if seed_token else "generated"
    _write_token_file(token_file, token)
    return AuthContextResponse(token_file=str(token_file), token_source=source)


def get_auth_context(request: Request) -> AuthContextResponse:
    return request.app.state.auth_context


def get_runtime_bearer_token(request: Request) -> str:
    token_file = request.app.state.settings.auth.token_file
    token = read_token_file(token_file)
    if token is None:
        raise ConfigurationError(
            message="Daemon auth token file is missing.",
            code="auth_token_missing",
            details={"auth_token_file": str(token_file)},
        )
    return token


def require_bearer_token(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> None:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing bearer token",
        )

    expected = get_runtime_bearer_token(request)
    if credentials.credentials != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid bearer token",
        )


def auth_token_file_mode(path: Path) -> int | None:
    if not path.exists():
        return None
    return stat.S_IMODE(path.stat().st_mode)
