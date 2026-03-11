from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest
import yaml

from aicoding.resources import load_resource_catalog
from aicoding.yaml_schemas import (
    identify_yaml_family,
    latest_yaml_validation_report,
    persist_yaml_validation_report,
    schema_family_descriptors,
    validate_builtin_yaml_set,
    validate_yaml_document,
)


def test_schema_family_descriptors_cover_current_builtin_families() -> None:
    families = [item.family for item in schema_family_descriptors()]

    assert families == [
        "node_definition",
        "task_definition",
        "subtask_definition",
        "layout_definition",
        "validation_definition",
        "review_definition",
        "testing_definition",
        "docs_definition",
        "hook_definition",
        "rectification_definition",
        "runtime_definition",
        "runtime_policy_definition",
        "environment_policy_definition",
        "prompt_reference_definition",
        "project_policy_definition",
        "override_definition",
    ]


def test_validate_yaml_document_accepts_builtin_node_definition() -> None:
    catalog = load_resource_catalog()

    report = validate_yaml_document(catalog, source_group="yaml_builtin_system", relative_path="nodes/epic.yaml")

    assert report.valid is True
    assert report.family == "node_definition"
    assert report.issue_count == 0


def test_validate_yaml_document_rejects_invalid_yaml_shape(tmp_path: Path) -> None:
    root = tmp_path / "resources"
    (root / "yaml" / "builtin" / "system-yaml" / "nodes").mkdir(parents=True)
    invalid_path = root / "yaml" / "builtin" / "system-yaml" / "nodes" / "bad.yaml"
    invalid_path.write_text("node_definition:\n  id: bad\n", encoding="utf-8")

    class Catalog:
        def read_text(self, group: str, relative_path: str) -> str:
            assert group == "yaml_builtin_system"
            assert relative_path == "nodes/bad.yaml"
            return invalid_path.read_text(encoding="utf-8")

    report = validate_yaml_document(Catalog(), source_group="yaml_builtin_system", relative_path="nodes/bad.yaml")

    assert report.valid is False
    assert report.issue_count > 0


def test_validate_builtin_yaml_set_returns_reports_for_current_library() -> None:
    reports = validate_builtin_yaml_set()

    assert reports
    assert all(report.valid for report in reports)
    assert len(reports) >= 100
    assert identify_yaml_family("layouts/epic_to_phases.yaml") == "layout_definition"
    assert identify_yaml_family("environments/local_default.yaml") == "environment_policy_definition"
    assert identify_yaml_family("project-policies/default_project_policy.yaml", "yaml_project") == "project_policy_definition"
    assert identify_yaml_family("nodes/epic_available_tasks.yaml", "yaml_overrides") == "override_definition"


def test_validate_yaml_document_accepts_environment_policy_definition() -> None:
    catalog = load_resource_catalog()

    report = validate_yaml_document(catalog, source_group="yaml_builtin_system", relative_path="environments/local_default.yaml")

    assert report.valid is True
    assert report.family == "environment_policy_definition"


def test_validate_yaml_document_accepts_authored_task_definition() -> None:
    catalog = load_resource_catalog()

    report = validate_yaml_document(catalog, source_group="yaml_builtin_system", relative_path="tasks/execute_node.yaml")

    assert report.valid is True
    assert report.family == "task_definition"
    assert report.issue_count == 0


def test_validate_yaml_document_accepts_project_policy_definition() -> None:
    catalog = load_resource_catalog()

    report = validate_yaml_document(
        catalog,
        source_group="yaml_project",
        relative_path="project-policies/default_project_policy.yaml",
    )

    assert report.valid is True
    assert report.family == "project_policy_definition"


def test_validate_yaml_document_accepts_override_definition(tmp_path: Path) -> None:
    root = tmp_path / "resources"
    (root / "yaml" / "overrides" / "nodes").mkdir(parents=True)
    override_path = root / "yaml" / "overrides" / "nodes" / "epic_tasks.yaml"
    override_path.write_text(
        "\n".join(
            [
                "target_family: node_definition",
                "target_id: epic",
                "compatibility:",
                "  min_schema_version: 2",
                "  built_in_version: builtin-system-v1",
                "merge_mode: replace_list",
                "value:",
                "  available_tasks:",
                "    - research_context",
                "    - execute_node",
            ]
        ),
        encoding="utf-8",
    )

    class Catalog:
        def read_text(self, group: str, relative_path: str) -> str:
            assert group == "yaml_overrides"
            assert relative_path == "nodes/epic_tasks.yaml"
            return override_path.read_text(encoding="utf-8")

    report = validate_yaml_document(Catalog(), source_group="yaml_overrides", relative_path="nodes/epic_tasks.yaml")

    assert report.valid is True
    assert report.family == "override_definition"


def test_persist_and_load_latest_yaml_validation_report(db_session_factory, migrated_public_schema) -> None:
    report = validate_yaml_document(load_resource_catalog(), source_group="yaml_builtin_system", relative_path="nodes/epic.yaml")

    persist_yaml_validation_report(db_session_factory, report)
    latest = latest_yaml_validation_report(
        db_session_factory,
        source_group="yaml_builtin_system",
        relative_path="nodes/epic.yaml",
    )

    assert latest is not None
    assert latest.record_id == report.record_id
    assert latest.valid is True


def _catalog_with_yaml(tmp_path: Path, *, relative_path: str, content: str):
    base = load_resource_catalog()
    builtin_root = tmp_path / "yaml" / "builtin" / "system-yaml"
    target_path = builtin_root / relative_path
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(content, encoding="utf-8")
    prompt_root = tmp_path / "prompts" / "packs" / "default"
    prompt_root.mkdir(parents=True, exist_ok=True)
    for path in base.prompt_pack_default_dir.rglob("*.md"):
        target = prompt_root / path.relative_to(base.prompt_pack_default_dir)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    return replace(
        base,
        yaml_builtin_system_dir=builtin_root,
        yaml_builtin_dir=tmp_path / "yaml" / "builtin",
        root=tmp_path,
        prompt_pack_default_dir=prompt_root,
    )


@pytest.mark.parametrize(
    ("relative_path", "content", "expected_message"),
    [
        (
            "validations/bad_validation.yaml",
            "\n".join(
                [
                    "kind: validation_definition",
                    "id: bad_validation",
                    "name: Bad Validation",
                    "description: Missing pattern.",
                    "check:",
                    "  type: file_contains",
                    "  path: docs/generated/node.md",
                ]
            ),
            "pattern is required",
        ),
        (
            "reviews/bad_review.yaml",
            "\n".join(
                [
                    "kind: review_definition",
                    "id: bad_review",
                    "name: Bad Review",
                    "applies_to: {node_kinds: [], task_ids: [], lifecycle_points: []}",
                    "scope: node_output",
                    "description: Missing selectors.",
                    "inputs: {include_parent_requirements: true}",
                    'prompt: "prompts/review/review_node_output.md"',
                    "criteria: []",
                    "on_result: {pass_action: continue, revise_action: rerun_task, fail_action: pause_for_user}",
                ]
            ),
            "at least one applies_to selector is required",
        ),
        (
            "testing/bad_testing.yaml",
            "\n".join(
                [
                    "kind: testing_definition",
                    "id: bad_testing",
                    "name: Bad Testing",
                    "applies_to: {node_kinds: [task], task_ids: [test_node], lifecycle_points: [after_task]}",
                    "scope: unit",
                    "description: Missing command text.",
                    "commands:",
                    "  - command: ''",
                    "    working_directory: .",
                    "    env: {}",
                    "retry_policy: {max_attempts: 1, rerun_failed_only: false}",
                    "pass_rules: {require_exit_code_zero: true, max_failed_tests: 0}",
                    "on_result: {pass_action: continue, fail_action: fail_to_parent}",
                ]
            ),
            "command must not be empty",
        ),
        (
            "docs/bad_docs.yaml",
            "\n".join(
                [
                    "kind: docs_definition",
                    "id: bad_docs",
                    "name: Bad Docs",
                    "applies_to: {node_kinds: [task], task_ids: [build_node_docs], lifecycle_points: [after_task]}",
                    "scope: local",
                    "description: Missing output path.",
                    "inputs: {include_node_summaries: true}",
                    "outputs:",
                    "  - path: ''",
                    "    view: local_node",
                ]
            ),
            "path must not be empty",
        ),
        (
            "rectification/bad_rectification.yaml",
            "\n".join(
                [
                    "kind: rectification_definition",
                    "id: bad_rectification",
                    "name: Bad Rectification",
                    "description: Duplicate subtasks.",
                    "trigger: merge_conflict",
                    "entry_task: reconcile_merge_conflict",
                    "subtasks: [reset_to_seed, reset_to_seed]",
                ]
            ),
            "rectification subtasks must be unique",
        ),
        (
            "rectification/missing_trigger.yaml",
            "\n".join(
                [
                    "kind: rectification_definition",
                    "id: missing_trigger",
                    "name: Missing Trigger",
                    "description: Empty trigger.",
                    "trigger: ''",
                    "entry_task: reconcile_merge_conflict",
                    "subtasks: [reset_to_seed]",
                ]
            ),
            "trigger must not be empty",
        ),
        (
            "rectification/missing_entry_task.yaml",
            "\n".join(
                [
                    "kind: rectification_definition",
                    "id: missing_entry_task",
                    "name: Missing Entry Task",
                    "description: Empty entry task.",
                    "trigger: merge_conflict",
                    "entry_task: ''",
                    "subtasks: [reset_to_seed]",
                ]
            ),
            "entry_task must not be empty",
        ),
        (
            "runtime/bad_runtime.yaml",
            "\n".join(
                [
                    "kind: runtime_definition",
                    "id: bad_runtime",
                    "name: Bad Runtime",
                    "description: Missing required runtime fields.",
                    "commands: []",
                    "thresholds: {}",
                    "actions: []",
                ]
            ),
            "runtime definitions must declare at least one command",
        ),
        (
            "environments/bad_environment_mode.yaml",
            "\n".join(
                [
                    "kind: environment_policy_definition",
                    "id: bad_environment_mode",
                    "isolation_mode: imaginary_mode",
                    "allow_network: false",
                    "mandatory: false",
                ]
            ),
            "unsupported isolation_mode",
        ),
        (
            "environments/missing_profile.yaml",
            "\n".join(
                [
                    "kind: environment_policy_definition",
                    "id: missing_profile",
                    "isolation_mode: custom_profile",
                    "allow_network: false",
                    "mandatory: true",
                ]
            ),
            "runtime_profile is required",
        ),
        (
            "environments/spurious_profile.yaml",
            "\n".join(
                [
                    "kind: environment_policy_definition",
                    "id: spurious_profile",
                    "isolation_mode: none",
                    "allow_network: true",
                    "runtime_profile: should_not_be_here",
                    "mandatory: false",
                ]
            ),
            "runtime_profile is only valid",
        ),
        (
            "validations/missing_exit_code.yaml",
            "\n".join(
                [
                    "kind: validation_definition",
                    "id: missing_exit_code",
                    "name: Missing Exit Code",
                    "description: Missing exit code for command validation.",
                    "check:",
                    "  type: command_exit_code",
                ]
            ),
            "exit_code is required",
        ),
        (
            "validations/missing_schema_name.yaml",
            "\n".join(
                [
                    "kind: validation_definition",
                    "id: missing_schema_name",
                    "name: Missing Schema Name",
                    "description: Missing schema name for yaml schema validation.",
                    "check:",
                    "  type: yaml_schema",
                ]
            ),
            "schema is required",
        ),
        (
            "validations/missing_status_value.yaml",
            "\n".join(
                [
                    "kind: validation_definition",
                    "id: missing_status_value",
                    "name: Missing Status Value",
                    "description: Missing status value for AI status validation.",
                    "check:",
                    "  type: ai_json_status",
                ]
            ),
            "value is required",
        ),
        (
            "policies/bad_runtime_policy.yaml",
            "\n".join(
                [
                    "kind: runtime_policy_definition",
                    "id: bad_runtime_policy",
                    "name: Bad Runtime Policy",
                    "description: Missing referenced hook.",
                    "defaults: {auto_run_children: true}",
                    "runtime_policy_refs: []",
                    "hook_refs: [hooks/not_real.yaml]",
                    "review_refs: []",
                    "testing_refs: []",
                    "docs_refs: []",
                ]
            ),
            "references missing YAML asset",
        ),
        (
            "prompts/bad_prompt_refs.yaml",
            "\n".join(
                [
                    "kind: prompt_reference_definition",
                    "id: bad_prompt_refs",
                    "name: Bad Prompt Refs",
                    "description: Invalid prompt reference format.",
                    "references:",
                    "  runtime_bad: prompts/runtime/cli_bootstrap.md",
                ]
            ),
            "prompt reference keys must use dotted identifiers",
        ),
    ],
)
def test_validate_yaml_document_rejects_invalid_higher_order_family_fields(
    tmp_path: Path,
    relative_path: str,
    content: str,
    expected_message: str,
) -> None:
    catalog = _catalog_with_yaml(tmp_path, relative_path=relative_path, content=content)

    report = validate_yaml_document(catalog, source_group="yaml_builtin_system", relative_path=relative_path)

    assert report.valid is False
    assert any(expected_message in issue.message for issue in report.issues)


def test_validate_yaml_document_rejects_missing_review_prompt_asset(tmp_path: Path) -> None:
    catalog = _catalog_with_yaml(
        tmp_path,
        relative_path="reviews/missing_prompt.yaml",
        content="\n".join(
            [
                "kind: review_definition",
                "id: missing_prompt",
                "name: Missing Prompt",
                "applies_to: {node_kinds: [task], task_ids: [review_node], lifecycle_points: [after_task]}",
                "scope: node_output",
                "description: References a prompt that does not exist.",
                "inputs: {include_parent_requirements: true}",
                'prompt: "prompts/review/not_real.md"',
                "criteria: ['Output is coherent.']",
                "on_result: {pass_action: continue, revise_action: rerun_task, fail_action: pause_for_user}",
            ]
        ),
    )

    report = validate_yaml_document(catalog, source_group="yaml_builtin_system", relative_path="reviews/missing_prompt.yaml")

    assert report.valid is False
    assert any("references missing prompt asset" in issue.message for issue in report.issues)


def test_validate_yaml_document_rejects_missing_hook_prompt_asset(tmp_path: Path) -> None:
    catalog = _catalog_with_yaml(
        tmp_path,
        relative_path="hooks/bad_hook.yaml",
        content="\n".join(
            [
                "kind: hook_definition",
                "id: bad_hook",
                "when: before_review",
                "applies_to: {tiers: [task], node_kinds: [], task_ids: [], subtask_types: []}",
                "if: {changed_entity_types: [], paths_match: []}",
                "run:",
                "  - type: run_prompt",
                '    prompt: "prompts/runtime/missing_asset.md"',
            ]
        ),
    )

    report = validate_yaml_document(catalog, source_group="yaml_builtin_system", relative_path="hooks/bad_hook.yaml")

    assert report.valid is False
    assert any("references missing prompt asset" in issue.message for issue in report.issues)


def test_validate_yaml_document_rejects_missing_prompt_reference_asset(tmp_path: Path) -> None:
    catalog = _catalog_with_yaml(
        tmp_path,
        relative_path="prompts/missing_target.yaml",
        content="\n".join(
            [
                "kind: prompt_reference_definition",
                "id: missing_target",
                "name: Missing Target",
                "description: References a prompt that does not exist.",
                "references:",
                "  runtime.cli_bootstrap: runtime/not_real.md",
            ]
        ),
    )

    report = validate_yaml_document(catalog, source_group="yaml_builtin_system", relative_path="prompts/missing_target.yaml")

    assert report.valid is False
    assert any("references missing prompt asset" in issue.message for issue in report.issues)


def test_schema_descriptor_files_cover_higher_order_families() -> None:
    catalog = load_resource_catalog()
    expected = {
        "validation_definition",
        "review_definition",
        "testing_definition",
        "docs_definition",
        "rectification_definition",
    }

    families = set()
    for path in catalog.yaml_schemas_dir.glob("*.yaml"):
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        schema_family = payload["schema_family"]
        families.add(schema_family["family"])

    assert expected.issubset(families)
