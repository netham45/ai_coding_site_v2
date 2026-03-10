from __future__ import annotations

from dataclasses import dataclass

import yaml

from aicoding.resources import ResourceCatalog
from aicoding.yaml_schemas import (
    DocsDefinitionDocument,
    NodeDefinitionDocument,
    PromptReferenceDefinitionDocument,
    ReviewDefinitionDocument,
    TaskDefinitionDocument,
    TestingDefinitionDocument,
    ValidationDefinitionDocument,
    validate_yaml_document,
)


REQUIRED_QUALITY_FILES: dict[str, tuple[str, ...]] = {
    "validations": (
        "file_exists.yaml",
        "file_updated.yaml",
        "command_exit_code.yaml",
        "json_schema.yaml",
        "yaml_schema.yaml",
        "ai_json_status.yaml",
        "file_contains.yaml",
        "git_clean.yaml",
        "git_dirty.yaml",
        "summary_written.yaml",
        "docs_built.yaml",
        "provenance_updated.yaml",
        "session_bound.yaml",
        "dependencies_satisfied.yaml",
    ),
    "reviews": (
        "layout_against_prompt.yaml",
        "node_against_requirements.yaml",
        "reconcile_output.yaml",
        "pre_finalize.yaml",
    ),
    "testing": (
        "default_unit_test_gate.yaml",
        "default_integration_test_gate.yaml",
        "default_smoke_test_gate.yaml",
    ),
    "docs": (
        "build_local_node_docs.yaml",
        "build_merged_tree_docs.yaml",
        "default_doc_views.yaml",
    ),
}

OPTIONAL_QUALITY_FILES: dict[str, tuple[str, ...]] = {
    "validations": (),
    "reviews": (
        "merge_result_review.yaml",
        "docs_quality_review.yaml",
        "policy_compliance_review.yaml",
    ),
    "testing": (
        "test_retry_policy.yaml",
        "test_failure_summary.yaml",
        "project_command_suite.yaml",
        "pytest_suite.yaml",
    ),
    "docs": (
        "build_docs.yaml",
        "static_analysis_scope.yaml",
        "rationale_merge_rules.yaml",
        "entity_history_view.yaml",
    ),
}

REQUIRED_QUALITY_TASKS: dict[str, str] = {
    "validate_node.yaml": "validate",
    "review_child_layout.yaml": "review",
    "review_node.yaml": "review",
    "test_node.yaml": "run_tests",
    "build_node_docs.yaml": "build_docs",
}

REQUIRED_QUALITY_PROMPTS: tuple[str, ...] = (
    "review/review_layout_against_request.md",
    "review/review_node_output.md",
    "testing/interpret_test_results.md",
    "docs/build_node_docs.md",
)

REQUIRED_PROMPT_REFERENCE_KEYS: dict[str, str] = {
    "review.layout_against_request": "review/review_layout_against_request.md",
    "review.node_output": "review/review_node_output.md",
    "testing.interpret_results": "testing/interpret_test_results.md",
    "docs.build_node_docs": "docs/build_node_docs.md",
}

GATE_ORDER: tuple[str, ...] = (
    "validate_node",
    "review_node",
    "test_node",
    "build_node_docs",
    "update_provenance",
    "finalize_node",
)


@dataclass(frozen=True, slots=True)
class QualityLibraryReport:
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


def _parse_document(model, catalog: ResourceCatalog, *, relative_path: str):
    payload = yaml.safe_load(catalog.read_text("yaml_builtin_system", relative_path))
    return model.model_validate(payload)


def _check_document(
    catalog: ResourceCatalog,
    *,
    relative_path: str,
    invalid_documents: list[dict[str, object]],
) -> bool:
    report = validate_yaml_document(catalog, source_group="yaml_builtin_system", relative_path=relative_path)
    if report.valid:
        return True
    invalid_documents.append({"relative_path": relative_path, "errors": [item.model_dump() for item in report.issues]})
    return False


def inspect_builtin_quality_library(catalog: ResourceCatalog) -> QualityLibraryReport:
    base = catalog.yaml_builtin_system_dir
    present: dict[str, list[str]] = {}
    missing_required: dict[str, list[str]] = {}
    missing_optional: dict[str, list[str]] = {}
    invalid_documents: list[dict[str, object]] = []
    broken_references: list[str] = []

    review_docs: dict[str, ReviewDefinitionDocument] = {}
    testing_docs: dict[str, TestingDefinitionDocument] = {}
    docs_docs: dict[str, DocsDefinitionDocument] = {}
    validation_docs: dict[str, ValidationDefinitionDocument] = {}
    node_docs: dict[str, NodeDefinitionDocument] = {}
    task_docs: dict[str, TaskDefinitionDocument] = {}

    for family, required_names in REQUIRED_QUALITY_FILES.items():
        family_dir = base / family
        existing = sorted(path.name for path in family_dir.glob("*.yaml"))
        present[family] = existing
        missing_required[family] = [name for name in required_names if name not in existing]
        missing_optional[family] = [name for name in OPTIONAL_QUALITY_FILES[family] if name not in existing]

    for node_file in ("epic.yaml", "phase.yaml", "plan.yaml", "task.yaml"):
        relative_path = f"nodes/{node_file}"
        if _check_document(catalog, relative_path=relative_path, invalid_documents=invalid_documents):
            document = _parse_document(NodeDefinitionDocument, catalog, relative_path=relative_path)
            node_docs[document.node_definition.id] = document

    for family, names in REQUIRED_QUALITY_FILES.items():
        for name in (*names, *OPTIONAL_QUALITY_FILES[family]):
            if name in missing_required[family] or name in missing_optional[family]:
                continue
            relative_path = f"{family}/{name}"
            if not _check_document(catalog, relative_path=relative_path, invalid_documents=invalid_documents):
                continue
            if family == "validations":
                document = _parse_document(ValidationDefinitionDocument, catalog, relative_path=relative_path)
                validation_docs[document.id] = document
            elif family == "reviews":
                document = _parse_document(ReviewDefinitionDocument, catalog, relative_path=relative_path)
                review_docs[document.id] = document
            elif family == "testing":
                document = _parse_document(TestingDefinitionDocument, catalog, relative_path=relative_path)
                testing_docs[document.id] = document
            elif family == "docs":
                document = _parse_document(DocsDefinitionDocument, catalog, relative_path=relative_path)
                docs_docs[document.id] = document

    for task_file, expected_subtask_type in REQUIRED_QUALITY_TASKS.items():
        relative_path = f"tasks/{task_file}"
        if not _check_document(catalog, relative_path=relative_path, invalid_documents=invalid_documents):
            continue
        document = _parse_document(TaskDefinitionDocument, catalog, relative_path=relative_path)
        task_docs[document.id] = document
        if not any(subtask.type == expected_subtask_type for subtask in document.subtasks):
            broken_references.append(f"{relative_path}: expected at least one '{expected_subtask_type}' subtask")

    prompt_ref_path = "prompts/default_prompt_refs.yaml"
    prompt_refs: PromptReferenceDefinitionDocument | None = None
    if _check_document(catalog, relative_path=prompt_ref_path, invalid_documents=invalid_documents):
        prompt_refs = _parse_document(PromptReferenceDefinitionDocument, catalog, relative_path=prompt_ref_path)

    for prompt_path in REQUIRED_QUALITY_PROMPTS:
        if not (catalog.prompt_pack_default_dir / prompt_path).exists():
            broken_references.append(f"missing prompt asset '{prompt_path}'")

    if prompt_refs is not None:
        for key, expected_path in REQUIRED_PROMPT_REFERENCE_KEYS.items():
            actual_path = prompt_refs.references.get(key)
            if actual_path != expected_path:
                broken_references.append(
                    f"{prompt_ref_path}: expected prompt reference '{key}' -> '{expected_path}'"
                )

    for review in review_docs.values():
        prompt_path = review.prompt.removeprefix("prompts/")
        if not (catalog.prompt_pack_default_dir / prompt_path).exists():
            broken_references.append(f"reviews/{review.id}.yaml: missing prompt '{review.prompt}'")

    for task_id, document in task_docs.items():
        if task_id in {"review_child_layout", "review_node"}:
            if not document.uses_reviews:
                broken_references.append(f"tasks/{task_id}.yaml: expected uses_reviews bindings")
            for reference in document.uses_reviews:
                review = review_docs.get(reference.split("/")[-1].removesuffix(".yaml"))
                if review is None:
                    broken_references.append(f"tasks/{task_id}.yaml: missing review binding '{reference}'")
                    continue
                if task_id not in review.applies_to.task_ids:
                    broken_references.append(
                        f"tasks/{task_id}.yaml: review '{review.id}' does not apply to task '{task_id}'"
                    )
        if task_id == "test_node":
            if not document.uses_testing:
                broken_references.append("tasks/test_node.yaml: expected uses_testing bindings")
            for reference in document.uses_testing:
                test_doc = testing_docs.get(reference.split("/")[-1].removesuffix(".yaml"))
                if test_doc is None:
                    broken_references.append(f"tasks/test_node.yaml: missing testing binding '{reference}'")
                    continue
                if "test_node" not in test_doc.applies_to.task_ids:
                    broken_references.append(
                        f"tasks/test_node.yaml: testing definition '{test_doc.id}' does not apply to task 'test_node'"
                    )
        if task_id == "build_node_docs":
            if not document.uses_docs:
                broken_references.append("tasks/build_node_docs.yaml: expected uses_docs bindings")
            for reference in document.uses_docs:
                doc_definition = docs_docs.get(reference.split("/")[-1].removesuffix(".yaml"))
                if doc_definition is None:
                    broken_references.append(f"tasks/build_node_docs.yaml: missing docs binding '{reference}'")
                    continue
                if "build_node_docs" not in doc_definition.applies_to.task_ids:
                    broken_references.append(
                        f"tasks/build_node_docs.yaml: docs definition '{doc_definition.id}' does not apply to task 'build_node_docs'"
                    )
        if task_id == "validate_node":
            validate_subtasks = [subtask for subtask in document.subtasks if subtask.type == "validate"]
            if not validate_subtasks:
                broken_references.append("tasks/validate_node.yaml: expected validate subtasks")
            known_check_types = {item.check.type for item in validation_docs.values()}
            for subtask in validate_subtasks:
                for check in subtask.checks:
                    if check.type not in known_check_types:
                        broken_references.append(
                            f"tasks/validate_node.yaml: unknown validation check type '{check.type}'"
                        )

    for node in node_docs.values():
        available = node.node_definition.available_tasks
        indexed = {task_id: available.index(task_id) for task_id in available if task_id in GATE_ORDER}
        for earlier, later in zip(GATE_ORDER, GATE_ORDER[1:]):
            if earlier in indexed and later in indexed and indexed[earlier] > indexed[later]:
                broken_references.append(
                    f"nodes/{node.node_definition.id}.yaml: task '{earlier}' must appear before '{later}'"
                )

    return QualityLibraryReport(
        present=present,
        missing_required=missing_required,
        missing_optional=missing_optional,
        invalid_documents=invalid_documents,
        broken_references=sorted(set(broken_references)),
    )


def ensure_builtin_quality_library(catalog: ResourceCatalog) -> None:
    report = inspect_builtin_quality_library(catalog)
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
