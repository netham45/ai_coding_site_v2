from __future__ import annotations

from tests.helpers.resource_loader import load_text


def test_cli_resources_command_includes_system_yaml_root(capsys) -> None:
    from aicoding.cli.app import run

    exit_code = run(["admin", "resources"])
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "yaml_builtin" in output


def test_daemon_foundation_exposes_resource_groups(app_client) -> None:
    response = app_client.get("/foundation", headers={"Authorization": "Bearer change-me"})

    assert response.status_code == 200
    assert "resource_groups" in response.json()


def test_authored_layout_asset_loads_through_test_helper() -> None:
    loaded = load_text("yaml_builtin_system", "layouts/epic_to_phases.yaml")

    assert "kind: layout_definition" in loaded.content
    assert "children:" in loaded.content
