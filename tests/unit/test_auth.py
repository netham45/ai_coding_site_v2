from __future__ import annotations

from pathlib import Path

import pytest

from aicoding.auth import load_auth_token, read_token_file
from aicoding.config import Settings
from aicoding.daemon.auth import auth_token_file_mode, get_runtime_bearer_token, initialize_auth_context
from aicoding.errors import ConfigurationError


def test_read_token_file_returns_none_for_missing_path(tmp_path: Path) -> None:
    assert read_token_file(tmp_path / "missing.token") is None


def test_load_auth_token_prefers_file_when_present(tmp_path: Path) -> None:
    token_file = tmp_path / "daemon.token"
    token_file.write_text("file-token\n", encoding="utf-8")
    settings = Settings(
        auth_token="settings-token",
        auth_token_file=token_file,
    )

    assert load_auth_token(settings=settings) == "file-token"


def test_load_auth_token_falls_back_to_settings_value(tmp_path: Path) -> None:
    settings = Settings(
        auth_token="settings-token",
        auth_token_file=tmp_path / "daemon.token",
    )

    assert load_auth_token(settings=settings) == "settings-token"


def test_load_auth_token_raises_when_no_value_exists(tmp_path: Path) -> None:
    settings = Settings(
        auth_token="   ",
        auth_token_file=tmp_path / "daemon.token",
    )

    with pytest.raises(ConfigurationError) as exc:
        load_auth_token(settings=settings)

    assert exc.value.code == "auth_token_missing"


def test_initialize_auth_context_writes_seed_token_file(tmp_path: Path) -> None:
    token_file = tmp_path / ".runtime" / "daemon.token"
    settings = Settings(auth_token="seed-token", auth_token_file=token_file)

    context = initialize_auth_context(settings)

    assert context.token_source == "settings"
    assert read_token_file(token_file) == "seed-token"


def test_initialize_auth_context_generates_token_when_missing_seed(tmp_path: Path) -> None:
    token_file = tmp_path / ".runtime" / "daemon.token"
    settings = Settings(auth_token="   ", auth_token_file=token_file)

    context = initialize_auth_context(settings)
    created = read_token_file(token_file)

    assert context.token_source == "generated"
    assert created is not None
    assert len(created) >= 20


def test_initialize_auth_context_reuses_existing_file_token(tmp_path: Path) -> None:
    token_file = tmp_path / ".runtime" / "daemon.token"
    token_file.parent.mkdir(parents=True)
    token_file.write_text("existing-token\n", encoding="utf-8")
    settings = Settings(auth_token="seed-token", auth_token_file=token_file)

    context = initialize_auth_context(settings)

    assert context.token_source == "file"
    assert read_token_file(token_file) == "existing-token"


def test_initialize_auth_context_rejects_directory_token_path(tmp_path: Path) -> None:
    token_dir = tmp_path / "daemon.token"
    token_dir.mkdir()
    settings = Settings(auth_token="seed-token", auth_token_file=token_dir)

    with pytest.raises(ConfigurationError) as exc:
        initialize_auth_context(settings)

    assert exc.value.code == "auth_token_path_invalid"


def test_auth_token_file_mode_reports_file_permissions(tmp_path: Path) -> None:
    token_file = tmp_path / ".runtime" / "daemon.token"
    initialize_auth_context(Settings(auth_token="seed-token", auth_token_file=token_file))

    mode = auth_token_file_mode(token_file)

    assert mode is not None
    assert mode & 0o077 == 0


def test_get_runtime_bearer_token_reads_from_request_state(tmp_path: Path) -> None:
    token_file = tmp_path / ".runtime" / "daemon.token"
    initialize_auth_context(Settings(auth_token="seed-token", auth_token_file=token_file))

    class AppState:
        settings = Settings(auth_token="ignored", auth_token_file=token_file)

    class App:
        state = AppState()

    class Request:
        app = App()

    assert get_runtime_bearer_token(Request()) == "seed-token"
