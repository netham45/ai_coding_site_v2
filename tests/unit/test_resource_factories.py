from __future__ import annotations

from tests.factories.resources import compiler_input_fixture, runtime_simulation_fixture


def test_compiler_input_fixture_provides_expected_keys() -> None:
    payload = compiler_input_fixture()

    assert payload["node_kind"] == "task"
    assert payload["resource_pack"] == "default"


def test_runtime_simulation_fixture_provides_expected_keys() -> None:
    payload = runtime_simulation_fixture()

    assert payload["run_id"] == "run-scaffold"
    assert payload["compiled_subtask_id"] == "subtask-scaffold"

