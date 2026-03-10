from __future__ import annotations

from dataclasses import dataclass

import yaml

from aicoding.resources import ResourceCatalog
from aicoding.yaml_schemas import LayoutDefinitionDocument, NodeDefinitionDocument, TaskDefinitionDocument, validate_yaml_document


REQUIRED_STRUCTURAL_FILES: dict[str, tuple[str, ...]] = {
    "nodes": ("epic.yaml", "phase.yaml", "plan.yaml", "task.yaml"),
    "tasks": (
        "research_context.yaml",
        "generate_child_layout.yaml",
        "review_child_layout.yaml",
        "revise_child_layout.yaml",
        "wait_for_dependencies.yaml",
        "execute_node.yaml",
        "spawn_children.yaml",
        "wait_for_children.yaml",
        "reconcile_children.yaml",
        "validate_node.yaml",
        "review_node.yaml",
        "test_node.yaml",
        "build_node_docs.yaml",
        "update_provenance.yaml",
        "finalize_node.yaml",
        "summarize_failure.yaml",
        "pause_for_user.yaml",
        "respond_to_child_failure.yaml",
        "rectify_node_from_seed.yaml",
        "rectify_upstream.yaml",
        "reconcile_merge_conflict.yaml",
        "recover_interrupted_run.yaml",
        "nudge_idle_session.yaml",
    ),
    "subtasks": (
        "build_context.yaml",
        "run_prompt.yaml",
        "run_command.yaml",
        "validate.yaml",
        "review.yaml",
        "run_tests.yaml",
        "wait_for_children.yaml",
        "wait_for_sibling_dependency.yaml",
        "spawn_child_node.yaml",
        "spawn_child_session.yaml",
        "collect_child_summaries.yaml",
        "reset_to_seed.yaml",
        "merge_children.yaml",
        "record_merge_metadata.yaml",
        "finalize_git_state.yaml",
        "write_summary.yaml",
        "build_docs.yaml",
        "update_provenance.yaml",
        "pause_on_user_flag.yaml",
        "finalize_node.yaml",
        "rebind_session.yaml",
        "nudge_session.yaml",
        "recover_cursor.yaml",
    ),
    "layouts": ("epic_to_phases.yaml", "phase_to_plans.yaml", "plan_to_tasks.yaml"),
}

OPTIONAL_STRUCTURAL_FILES: dict[str, tuple[str, ...]] = {
    "nodes": (),
    "tasks": (),
    "subtasks": (),
    "layouts": ("manual_top_node.yaml", "research_only_breakdown.yaml", "replan_after_failure.yaml"),
}


@dataclass(frozen=True, slots=True)
class StructuralLibraryReport:
    present: dict[str, list[str]]
    missing_required: dict[str, list[str]]
    missing_optional: dict[str, list[str]]
    invalid_documents: list[dict[str, object]]
    broken_references: list[str]

    def to_payload(self) -> dict[str, object]:
        return {
            "present": self.present,
            "missing_required": self.missing_required,
            "missing_optional": self.missing_optional,
            "invalid_documents": self.invalid_documents,
            "broken_references": self.broken_references,
            "valid": not any(self.missing_required.values()) and not self.invalid_documents and not self.broken_references,
        }


def inspect_builtin_structural_library(catalog: ResourceCatalog) -> StructuralLibraryReport:
    base = catalog.yaml_builtin_system_dir
    present: dict[str, list[str]] = {}
    missing_required: dict[str, list[str]] = {}
    missing_optional: dict[str, list[str]] = {}
    invalid_documents: list[dict[str, object]] = []
    broken_references: list[str] = []

    for family, required_names in REQUIRED_STRUCTURAL_FILES.items():
        family_dir = base / family
        existing = sorted(path.name for path in family_dir.glob("*.yaml"))
        present[family] = existing
        missing_required[family] = [name for name in required_names if name not in existing]
        missing_optional[family] = [name for name in OPTIONAL_STRUCTURAL_FILES[family] if name not in existing]

    node_documents: dict[str, NodeDefinitionDocument] = {}
    task_ids: set[str] = set()
    prompt_refs: set[str] = set()

    for node_file in [*REQUIRED_STRUCTURAL_FILES["nodes"]]:
        if node_file in missing_required["nodes"]:
            continue
        relative_path = f"nodes/{node_file}"
        report = validate_yaml_document(catalog, source_group="yaml_builtin_system", relative_path=relative_path)
        if not report.valid:
            invalid_documents.append({"relative_path": relative_path, "errors": [item.model_dump() for item in report.issues]})
            continue
        document = NodeDefinitionDocument.model_validate(yaml.safe_load(catalog.read_text("yaml_builtin_system", relative_path)))
        node_documents[document.node_definition.kind] = document
        prompt_refs.add(document.node_definition.main_prompt.removeprefix("prompts/"))

    for task_file in [*REQUIRED_STRUCTURAL_FILES["tasks"]]:
        if task_file in missing_required["tasks"]:
            continue
        relative_path = f"tasks/{task_file}"
        report = validate_yaml_document(catalog, source_group="yaml_builtin_system", relative_path=relative_path)
        if not report.valid:
            invalid_documents.append({"relative_path": relative_path, "errors": [item.model_dump() for item in report.issues]})
            continue
        document = TaskDefinitionDocument.model_validate(yaml.safe_load(catalog.read_text("yaml_builtin_system", relative_path)))
        task_ids.add(document.id)
        for subtask in document.subtasks:
            if subtask.prompt:
                prompt_refs.add(subtask.prompt.removeprefix("prompts/"))

    for subtask_file in [*REQUIRED_STRUCTURAL_FILES["subtasks"]]:
        if subtask_file in missing_required["subtasks"]:
            continue
        relative_path = f"subtasks/{subtask_file}"
        report = validate_yaml_document(catalog, source_group="yaml_builtin_system", relative_path=relative_path)
        if not report.valid:
            invalid_documents.append({"relative_path": relative_path, "errors": [item.model_dump() for item in report.issues]})

    for layout_file in [*REQUIRED_STRUCTURAL_FILES["layouts"], *OPTIONAL_STRUCTURAL_FILES["layouts"]]:
        if layout_file in missing_required["layouts"] or layout_file in missing_optional["layouts"]:
            continue
        relative_path = f"layouts/{layout_file}"
        report = validate_yaml_document(catalog, source_group="yaml_builtin_system", relative_path=relative_path)
        if not report.valid:
            invalid_documents.append({"relative_path": relative_path, "errors": [item.model_dump() for item in report.issues]})
            continue
        document = LayoutDefinitionDocument.model_validate(yaml.safe_load(catalog.read_text("yaml_builtin_system", relative_path)))
        for child in document.children:
            if child.kind not in node_documents:
                broken_references.append(f"{relative_path}: unknown child node kind '{child.kind}'")

    for node in node_documents.values():
        if node.node_definition.entry_task not in task_ids:
            broken_references.append(
                f"nodes/{node.node_definition.id}.yaml: unknown entry_task '{node.node_definition.entry_task}'"
            )
        for task_id in node.node_definition.available_tasks:
            if task_id not in task_ids:
                broken_references.append(f"nodes/{node.node_definition.id}.yaml: unknown available_task '{task_id}'")
        if node.node_definition.main_prompt and not (catalog.prompt_pack_default_dir / node.node_definition.main_prompt.removeprefix("prompts/")).exists():
            broken_references.append(
                f"nodes/{node.node_definition.id}.yaml: missing prompt '{node.node_definition.main_prompt}'"
            )

    for prompt_ref in sorted(prompt_refs):
        if not (catalog.prompt_pack_default_dir / prompt_ref).exists():
            broken_references.append(f"missing prompt asset '{prompt_ref}'")

    return StructuralLibraryReport(
        present=present,
        missing_required=missing_required,
        missing_optional=missing_optional,
        invalid_documents=invalid_documents,
        broken_references=sorted(set(broken_references)),
    )


def ensure_builtin_structural_library(catalog: ResourceCatalog) -> None:
    report = inspect_builtin_structural_library(catalog)
    if report.to_payload()["valid"]:
        return
    issues: list[str] = []
    for family, names in report.missing_required.items():
        if names:
            issues.append(f"missing required {family}: {', '.join(names)}")
    if report.invalid_documents:
        issues.append("invalid documents: " + ", ".join(item["relative_path"] for item in report.invalid_documents))
    if report.broken_references:
        issues.append("broken references: " + "; ".join(report.broken_references[:5]))
    raise ValueError("; ".join(issues))
