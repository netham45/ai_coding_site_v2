from __future__ import annotations

import pytest

from aicoding.config import get_settings
from tests.fixtures.cli import cli_runner
from tests.fixtures.daemon import app_client, auth_headers, daemon_bridge_client, daemon_token, live_daemon_token
from tests.fixtures.db import (
    clean_public_schema,
    db_engine,
    db_session,
    db_session_factory,
    isolated_database_url,
    isolated_schema,
    migrated_public_schema,
)
from tests.fixtures.e2e import real_daemon_harness, real_daemon_harness_factory
from tests.fixtures.resources import (
    builtin_system_yaml_root,
    default_prompt_pack_root,
    prompt_render_context,
    resource_catalog,
    yaml_compile_context,
)


@pytest.fixture(autouse=True)
def clear_settings_cache(monkeypatch):
    monkeypatch.setenv("AICODING_SESSION_BACKEND", "fake")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


__all__ = [
    "app_client",
    "auth_headers",
    "builtin_system_yaml_root",
    "clean_public_schema",
    "cli_runner",
    "daemon_bridge_client",
    "daemon_token",
    "db_engine",
    "db_session",
    "db_session_factory",
    "default_prompt_pack_root",
    "isolated_schema",
    "isolated_database_url",
    "live_daemon_token",
    "migrated_public_schema",
    "prompt_render_context",
    "real_daemon_harness",
    "real_daemon_harness_factory",
    "resource_catalog",
    "yaml_compile_context",
]
