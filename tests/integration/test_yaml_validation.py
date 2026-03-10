from __future__ import annotations

from pathlib import Path


def test_daemon_yaml_schema_endpoints_validate_and_list_families(app_client, migrated_public_schema) -> None:
    list_response = app_client.get("/api/yaml/schema-families", headers={"Authorization": "Bearer change-me"})

    assert list_response.status_code == 200
    payload = list_response.json()
    assert any(item["family"] == "node_definition" for item in payload["definitions"])

    validate_response = app_client.post(
        "/api/yaml/validate",
        headers={"Authorization": "Bearer change-me"},
        json={"source_group": "yaml_builtin_system", "relative_path": "nodes/epic.yaml"},
    )

    assert validate_response.status_code == 200
    validation_payload = validate_response.json()
    assert validation_payload["family"] == "node_definition"
    assert validation_payload["valid"] is True
    assert validation_payload["issue_count"] == 0


def test_cli_yaml_validate_and_schema_family_commands(cli_runner, daemon_bridge_client, migrated_public_schema, monkeypatch) -> None:
    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: daemon_bridge_client)

    schema_result = cli_runner(["yaml", "schema-families"])
    schema_payload = schema_result.json()
    assert schema_result.exit_code == 0
    assert any(item["family"] == "task_definition" for item in schema_payload["definitions"])

    validate_result = cli_runner(["yaml", "validate", "--path", "nodes/epic.yaml"])
    validate_payload = validate_result.json()
    assert validate_result.exit_code == 0
    assert validate_payload["valid"] is True
    assert validate_payload["family"] == "node_definition"
