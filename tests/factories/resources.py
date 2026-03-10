from __future__ import annotations


def compiler_input_fixture() -> dict[str, object]:
    return {
        "node_id": "node-scaffold",
        "node_kind": "task",
        "resource_pack": "default",
        "yaml_scope": "builtin",
    }


def runtime_simulation_fixture() -> dict[str, object]:
    return {
        "node_id": "node-scaffold",
        "run_id": "run-scaffold",
        "compiled_subtask_id": "subtask-scaffold",
    }

