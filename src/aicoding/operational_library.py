from __future__ import annotations

from dataclasses import dataclass

import yaml

from aicoding.resources import ResourceCatalog
from aicoding.yaml_schemas import (
    EnvironmentPolicyDefinitionDocument,
    HookDefinitionDocument,
    PromptReferenceDefinitionDocument,
    RuntimeDefinitionDocument,
    RuntimePolicyDefinitionDocument,
    validate_yaml_document,
)


REQUIRED_OPERATIONAL_FILES: dict[str, tuple[str, ...]] = {
    "runtime": (
        "session_defaults.yaml",
        "heartbeat_policy.yaml",
        "idle_nudge_policy.yaml",
        "child_session_policy.yaml",
        "recovery_policy.yaml",
        "recover_interrupted_run.yaml",
    ),
    "hooks": (
        "default_hooks.yaml",
        "before_validation_default.yaml",
        "after_validation_default.yaml",
        "before_review_default.yaml",
        "after_review_default.yaml",
        "before_testing_default.yaml",
        "after_testing_default.yaml",
        "before_merge_children_default.yaml",
        "after_merge_children_default.yaml",
        "on_merge_conflict_default.yaml",
        "before_upstream_rectify_default.yaml",
        "after_upstream_rectify_default.yaml",
        "on_node_created_default.yaml",
        "before_node_complete_default.yaml",
        "after_node_complete_default.yaml",
        "after_subtask_default_summary.yaml",
        "after_node_complete_build_docs.yaml",
        "after_node_complete_update_provenance.yaml",
    ),
    "policies": (
        "default_runtime_policy.yaml",
        "default_node_policy.yaml",
        "default_review_policy.yaml",
        "default_testing_policy.yaml",
        "default_merge_policy.yaml",
        "default_failure_policy.yaml",
    ),
    "prompts": ("default_prompt_refs.yaml",),
    "environments": ("local_default.yaml", "isolated_test_profile.yaml"),
}

REQUIRED_OPERATIONAL_PROMPTS: tuple[str, ...] = (
    "layouts/generate_phase_layout.md",
    "layouts/generate_plan_layout.md",
    "layouts/generate_task_layout.md",
    "execution/implement_leaf_task.md",
    "execution/reconcile_parent_after_merge.md",
    "review/review_layout_against_request.md",
    "review/review_node_output.md",
    "testing/interpret_test_results.md",
    "docs/build_node_docs.md",
    "runtime/session_bootstrap.md",
    "runtime/missed_step.md",
    "runtime/command_failed.md",
    "runtime/missing_required_output.md",
    "runtime/idle_nudge.md",
    "runtime/pause_for_user.md",
    "runtime/resume_existing_session.md",
    "runtime/replacement_session_bootstrap.md",
    "runtime/delegated_child_session.md",
    "runtime/parent_pause_for_user.md",
    "runtime/parent_local_replan.md",
)

REQUIRED_PROMPT_REFERENCE_KEYS: dict[str, str] = {
    "layout.generate_phase": "layouts/generate_phase_layout.md",
    "layout.generate_plan": "layouts/generate_plan_layout.md",
    "layout.generate_task": "layouts/generate_task_layout.md",
    "execution.implement_leaf_task": "execution/implement_leaf_task.md",
    "execution.reconcile_parent_after_merge": "execution/reconcile_parent_after_merge.md",
    "review.layout_against_request": "review/review_layout_against_request.md",
    "review.node_output": "review/review_node_output.md",
    "testing.interpret_results": "testing/interpret_test_results.md",
    "docs.build_node_docs": "docs/build_node_docs.md",
    "runtime.session_bootstrap": "runtime/session_bootstrap.md",
    "runtime.missed_step": "runtime/missed_step.md",
    "runtime.command_failed": "runtime/command_failed.md",
    "runtime.missing_required_output": "runtime/missing_required_output.md",
    "runtime.idle_nudge": "runtime/idle_nudge.md",
    "runtime.pause_for_user": "runtime/pause_for_user.md",
    "runtime.resume_existing_session": "runtime/resume_existing_session.md",
    "runtime.replacement_session_bootstrap": "runtime/replacement_session_bootstrap.md",
    "runtime.delegated_child_session": "runtime/delegated_child_session.md",
    "runtime.parent_pause_for_user": "runtime/parent_pause_for_user.md",
    "runtime.parent_local_replan": "runtime/parent_local_replan.md",
}


@dataclass(frozen=True, slots=True)
class OperationalLibraryReport:
    present: dict[str, list[str]]
    missing_required: dict[str, list[str]]
    invalid_documents: list[dict[str, object]]
    broken_references: list[str]

    def to_payload(self) -> dict[str, object]:
        return {
            "present": self.present,
            "missing_required": self.missing_required,
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


def inspect_builtin_operational_library(catalog: ResourceCatalog) -> OperationalLibraryReport:
    base = catalog.yaml_builtin_system_dir
    present: dict[str, list[str]] = {}
    missing_required: dict[str, list[str]] = {}
    invalid_documents: list[dict[str, object]] = []
    broken_references: list[str] = []

    runtime_docs: dict[str, RuntimeDefinitionDocument] = {}
    hook_docs: dict[str, HookDefinitionDocument] = {}
    policy_docs: dict[str, RuntimePolicyDefinitionDocument] = {}
    env_docs: dict[str, EnvironmentPolicyDefinitionDocument] = {}
    prompt_refs: PromptReferenceDefinitionDocument | None = None

    for family, required_names in REQUIRED_OPERATIONAL_FILES.items():
        family_dir = base / family
        existing = sorted(path.name for path in family_dir.glob("*.yaml"))
        present[family] = existing
        missing_required[family] = [name for name in required_names if name not in existing]

    for relative_path in (f"runtime/{name}" for name in REQUIRED_OPERATIONAL_FILES["runtime"]):
        if relative_path.split("/")[-1] in missing_required["runtime"]:
            continue
        if not _check_document(catalog, relative_path=relative_path, invalid_documents=invalid_documents):
            continue
        document = _parse_document(RuntimeDefinitionDocument, catalog, relative_path=relative_path)
        runtime_docs[document.id] = document

    for relative_path in (f"hooks/{name}" for name in REQUIRED_OPERATIONAL_FILES["hooks"]):
        if relative_path.split("/")[-1] in missing_required["hooks"]:
            continue
        if not _check_document(catalog, relative_path=relative_path, invalid_documents=invalid_documents):
            continue
        document = _parse_document(HookDefinitionDocument, catalog, relative_path=relative_path)
        hook_docs[document.id] = document

    for relative_path in (f"policies/{name}" for name in REQUIRED_OPERATIONAL_FILES["policies"]):
        if relative_path.split("/")[-1] in missing_required["policies"]:
            continue
        if not _check_document(catalog, relative_path=relative_path, invalid_documents=invalid_documents):
            continue
        document = _parse_document(RuntimePolicyDefinitionDocument, catalog, relative_path=relative_path)
        policy_docs[document.id] = document

    for relative_path in (f"environments/{name}" for name in REQUIRED_OPERATIONAL_FILES["environments"]):
        if relative_path.split("/")[-1] in missing_required["environments"]:
            continue
        if not _check_document(catalog, relative_path=relative_path, invalid_documents=invalid_documents):
            continue
        document = _parse_document(EnvironmentPolicyDefinitionDocument, catalog, relative_path=relative_path)
        env_docs[document.id] = document

    prompt_ref_path = "prompts/default_prompt_refs.yaml"
    if "default_prompt_refs.yaml" not in missing_required["prompts"] and _check_document(
        catalog,
        relative_path=prompt_ref_path,
        invalid_documents=invalid_documents,
    ):
        prompt_refs = _parse_document(PromptReferenceDefinitionDocument, catalog, relative_path=prompt_ref_path)

    subtask_ids = {
        yaml.safe_load(path.read_text(encoding="utf-8"))["id"]
        for path in sorted((base / "subtasks").glob("*.yaml"))
    }

    for prompt_path in REQUIRED_OPERATIONAL_PROMPTS:
        if not (catalog.prompt_pack_default_dir / prompt_path).exists():
            broken_references.append(f"missing prompt asset '{prompt_path}'")

    if prompt_refs is not None:
        for key, expected_path in REQUIRED_PROMPT_REFERENCE_KEYS.items():
            actual = prompt_refs.references.get(key)
            if actual != expected_path:
                broken_references.append(
                    f"{prompt_ref_path}: expected prompt reference '{key}' -> '{expected_path}'"
                )

    for runtime_doc in runtime_docs.values():
        for action in runtime_doc.actions:
            if action not in subtask_ids:
                broken_references.append(
                    f"runtime/{runtime_doc.id}.yaml: unknown action subtask '{action}'"
                )

    valid_hook_types = {"run_command", "run_prompt", "validate", "review", "run_tests", "build_docs", "write_summary"}
    for hook in hook_docs.values():
        for step in hook.run:
            if step.type not in valid_hook_types:
                broken_references.append(f"hooks/{hook.id}.yaml: unsupported run type '{step.type}'")
            if step.prompt:
                prompt_path = step.prompt.removeprefix("prompts/")
                if not (catalog.prompt_pack_default_dir / prompt_path).exists():
                    broken_references.append(f"hooks/{hook.id}.yaml: missing prompt '{step.prompt}'")

    for policy in policy_docs.values():
        for reference in policy.runtime_policy_refs:
            ref_id = reference.split("/")[-1].removesuffix(".yaml")
            if ref_id not in runtime_docs:
                broken_references.append(f"policies/{policy.id}.yaml: missing runtime ref '{reference}'")
        for reference in policy.hook_refs:
            ref_id = reference.split("/")[-1].removesuffix(".yaml")
            if ref_id not in hook_docs:
                broken_references.append(f"policies/{policy.id}.yaml: missing hook ref '{reference}'")

    if "default_runtime_policy" in policy_docs:
        default_policy = policy_docs["default_runtime_policy"]
        expected_runtime = {
            "runtime/session_defaults.yaml",
            "runtime/heartbeat_policy.yaml",
            "runtime/idle_nudge_policy.yaml",
            "runtime/child_session_policy.yaml",
            "runtime/recovery_policy.yaml",
        }
        missing_runtime = sorted(expected_runtime - set(default_policy.runtime_policy_refs))
        if missing_runtime:
            broken_references.append(
                "policies/default_runtime_policy.yaml: missing runtime refs " + ", ".join(missing_runtime)
            )
        expected_hooks = {
            "hooks/before_validation_default.yaml",
            "hooks/before_review_default.yaml",
            "hooks/before_testing_default.yaml",
            "hooks/after_node_complete_build_docs.yaml",
            "hooks/after_node_complete_update_provenance.yaml",
        }
        missing_hooks = sorted(expected_hooks - set(default_policy.hook_refs))
        if missing_hooks:
            broken_references.append(
                "policies/default_runtime_policy.yaml: missing hook refs " + ", ".join(missing_hooks)
            )

    if "local_default" not in env_docs:
        broken_references.append("missing required environment policy 'local_default'")

    return OperationalLibraryReport(
        present=present,
        missing_required=missing_required,
        invalid_documents=invalid_documents,
        broken_references=sorted(set(broken_references)),
    )


def ensure_builtin_operational_library(catalog: ResourceCatalog) -> None:
    report = inspect_builtin_operational_library(catalog)
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
