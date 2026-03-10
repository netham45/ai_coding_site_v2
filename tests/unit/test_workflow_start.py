from __future__ import annotations

from aicoding.daemon.errors import DaemonConflictError
from aicoding.daemon.workflow_start import start_top_level_workflow
from aicoding.hierarchy import load_hierarchy_registry
from aicoding.resources import load_resource_catalog


def test_start_top_level_workflow_creates_compiles_and_starts_run(db_session_factory, migrated_public_schema) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)

    started = start_top_level_workflow(
        db_session_factory,
        hierarchy_registry=registry,
        resource_catalog=catalog,
        kind="epic",
        title=None,
        prompt="Create a top level epic for workflow start coverage.",
        start_run=True,
    )

    assert started.status == "started"
    assert started.node["kind"] == "epic"
    assert started.compile.status == "compiled"
    assert started.lifecycle["lifecycle_state"] == "RUNNING"
    assert started.run_admission is not None
    assert started.run_admission["status"] == "admitted"
    assert started.run_progress is not None
    assert started.run_progress["run"]["trigger_reason"] == "workflow_start"


def test_start_top_level_workflow_can_compile_without_starting_run(db_session_factory, migrated_public_schema) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)

    started = start_top_level_workflow(
        db_session_factory,
        hierarchy_registry=registry,
        resource_catalog=catalog,
        kind="epic",
        title="Compile Only Epic",
        prompt="Compile only workflow startup coverage.",
        start_run=False,
    )

    assert started.status == "compiled"
    assert started.compile.status == "compiled"
    assert started.lifecycle["lifecycle_state"] == "READY"
    assert started.run_admission is None
    assert started.run_progress is None


def test_start_top_level_workflow_rejects_non_top_level_kinds(db_session_factory, migrated_public_schema) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)

    try:
        start_top_level_workflow(
            db_session_factory,
            hierarchy_registry=registry,
            resource_catalog=catalog,
            kind="task",
            title="Not Top Level",
            prompt="This should be rejected.",
            start_run=True,
        )
    except DaemonConflictError as exc:
        assert "not a top-level kind" in str(exc)
    else:
        raise AssertionError("Expected top-level workflow creation to reject non-top-level kinds")


def test_start_top_level_workflow_returns_compile_failure_without_run(db_session_factory, migrated_public_schema) -> None:
    base_catalog = load_resource_catalog()
    registry = load_hierarchy_registry(base_catalog)

    class BrokenCatalog:
        yaml_project_policies_dir = base_catalog.yaml_project_policies_dir
        yaml_project_dir = base_catalog.yaml_project_dir
        yaml_builtin_system_dir = base_catalog.yaml_builtin_system_dir
        yaml_overrides_dir = base_catalog.yaml_overrides_dir

        def read_text(self, group: str, relative_path: str) -> str:
            if group == "yaml_builtin_system" and relative_path == "tasks/execute_node.yaml":
                return "kind: task_definition\nid: execute_node\n"
            return base_catalog.read_text(group, relative_path)

        def __getattr__(self, name: str):
            return getattr(base_catalog, name)

    started = start_top_level_workflow(
        db_session_factory,
        hierarchy_registry=registry,
        resource_catalog=BrokenCatalog(),
        kind="epic",
        title="Broken Start",
        prompt="This compile should fail.",
        start_run=True,
    )

    assert started.status == "compile_failed"
    assert started.compile.status == "failed"
    assert started.compile.compile_failure is not None
    assert started.lifecycle["lifecycle_state"] == "COMPILE_FAILED"
    assert started.run_admission is None
    assert started.run_progress is None
