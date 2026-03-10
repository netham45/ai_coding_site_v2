from __future__ import annotations

import pytest
from sqlalchemy import text

from tests.helpers.cli import CLIResult


def test_cli_runner_returns_structured_result(cli_runner) -> None:
    result = cli_runner(["admin", "doctor"])

    assert isinstance(result, CLIResult)
    assert result.exit_code == 0
    assert result.json()["missing_directories"] == []


def test_db_session_fixture_executes_queries(db_session) -> None:
    assert db_session.execute(text("select 1")).scalar_one() == 1


def test_migrated_public_schema_fixture_applies_head_revision(migrated_public_schema) -> None:
    with migrated_public_schema.connect() as connection:
        revision = connection.execute(text("select version_num from alembic_version")).scalar_one()

    assert revision == "0028_subtask_execution_results"


def test_daemon_bridge_client_routes_authenticated_requests(daemon_bridge_client) -> None:
    payload = daemon_bridge_client.request("GET", "/healthz")

    assert payload == {"status": "ok"}


def test_fixture_resource_contexts_are_deterministic(prompt_render_context, yaml_compile_context) -> None:
    assert prompt_render_context == {
        "node_id": "node-scaffold",
        "run_id": "run-scaffold",
        "session_id": "session-scaffold",
        "prompt_pack": "default",
    }
    assert yaml_compile_context == {
        "scope": "builtin",
        "resource_group": "yaml_builtin_system",
        "entrypoint": "nodes/task.yaml",
    }


def test_cli_runner_fixture_misuse_requires_valid_json() -> None:
    result = CLIResult(exit_code=0, stdout="", stderr="")

    with pytest.raises(ValueError):
        result.json()
