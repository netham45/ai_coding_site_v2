from __future__ import annotations

from pathlib import Path

import yaml

from aicoding.resources import load_resource_catalog
from aicoding.yaml_schemas import validate_yaml_document


def test_runtime_library_validates_and_enforces_expected_threshold_contracts() -> None:
    catalog = load_resource_catalog()
    runtime_root = catalog.yaml_builtin_system_dir / "runtime"
    expected_threshold_keys = {
        "child_session_policy.yaml": {"allow_child_sessions"},
        "heartbeat_policy.yaml": {"heartbeat_seconds"},
        "idle_nudge_policy.yaml": {"idle_nudge_after_seconds"},
        "recover_interrupted_run.yaml": {"requires_existing_cursor"},
        "recovery_policy.yaml": {"preserve_cursor"},
        "session_defaults.yaml": {"bind_once_per_run"},
    }
    seen_ids: set[str] = set()

    for path in sorted(runtime_root.glob("*.yaml")):
        relative_path = str(Path("runtime") / path.name)
        report = validate_yaml_document(catalog, source_group="yaml_builtin_system", relative_path=relative_path)

        assert report.valid is True, f"{relative_path}: {report.issues}"

        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        runtime_id = payload["id"]
        assert runtime_id not in seen_ids, f"duplicate runtime_definition id {runtime_id!r} in {relative_path}"
        seen_ids.add(runtime_id)
        assert payload["commands"], f"{relative_path}: commands must not be empty"
        assert all(command.strip() for command in payload["commands"]), f"{relative_path}: blank command entry"
        assert payload["actions"], f"{relative_path}: actions must not be empty"
        assert len(set(payload["actions"])) == len(payload["actions"]), f"{relative_path}: duplicate actions"
        assert set(payload["thresholds"].keys()) == expected_threshold_keys[path.name], (
            f"{relative_path}: unexpected threshold keys {sorted(payload['thresholds'].keys())}"
        )
