from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from hashlib import sha256

import yaml
from pydantic import ValidationError

from aicoding.yaml_schemas import (
    FAMILY_MODELS,
    OverrideDefinitionDocument,
    identify_yaml_family,
    unwrap_yaml_document_payload,
    wrap_yaml_document_payload,
)

CURRENT_YAML_SCHEMA_VERSION = 2


class OverrideResolutionError(Exception):
    def __init__(
        self,
        *,
        failure_class: str,
        summary: str,
        details_json: dict[str, object] | None = None,
        target_family: str | None = None,
        target_id: str | None = None,
    ) -> None:
        super().__init__(summary)
        self.failure_class = failure_class
        self.summary = summary
        self.details_json = details_json or {}
        self.target_family = target_family
        self.target_id = target_id


@dataclass(frozen=True, slots=True)
class OverrideSourceSnapshot:
    relative_path: str
    document: OverrideDefinitionDocument
    content_hash: str


@dataclass(frozen=True, slots=True)
class ResolvedDocumentSnapshot:
    target_family: str
    target_id: str
    relative_path: str
    source_group: str
    source_role: str
    resolved_document: dict[str, object]
    applied_override_paths: list[str]

    def to_payload(self) -> dict[str, object]:
        return {
            "target_family": self.target_family,
            "target_id": self.target_id,
            "relative_path": self.relative_path,
            "source_group": self.source_group,
            "source_role": self.source_role,
            "resolved_document": self.resolved_document,
            "applied_override_paths": self.applied_override_paths,
        }


@dataclass(frozen=True, slots=True)
class OverrideApplicationSnapshot:
    override_relative_path: str
    override_id: str | None
    target_family: str
    target_id: str
    merge_mode: str
    field_names: list[str]
    compatibility: dict[str, object]
    warnings: list[str]

    def to_payload(self) -> dict[str, object]:
        return {
            "override_relative_path": self.override_relative_path,
            "override_id": self.override_id,
            "target_family": self.target_family,
            "target_id": self.target_id,
            "merge_mode": self.merge_mode,
            "field_names": self.field_names,
            "compatibility": self.compatibility,
            "warnings": self.warnings,
        }


@dataclass(frozen=True, slots=True)
class OverrideResolutionSnapshot:
    resolved_documents: list[ResolvedDocumentSnapshot]
    applied_overrides: list[OverrideApplicationSnapshot]
    warnings: list[str]

    def document_for(self, target_family: str, target_id: str) -> ResolvedDocumentSnapshot | None:
        for item in self.resolved_documents:
            if item.target_family == target_family and item.target_id == target_id:
                return item
        return None

    def to_payload(self) -> dict[str, object]:
        return {
            "resolved_documents": [item.to_payload() for item in self.resolved_documents],
            "applied_overrides": [item.to_payload() for item in self.applied_overrides],
            "warnings": self.warnings,
        }


@dataclass(frozen=True, slots=True)
class SourceDocumentInput:
    source_group: str
    relative_path: str
    source_role: str
    content: str
    content_hash: str


@dataclass
class _BaseDocument:
    target_family: str
    target_id: str
    relative_path: str
    source_group: str
    source_role: str
    document: dict[str, object]
    applied_override_paths: list[str]


FAMILY_FIELD_MERGE_RULES: dict[str, dict[str, str]] = {
    "node_definition": {
        "id": "replace",
        "kind": "replace",
        "tier": "replace",
        "description": "replace",
        "main_prompt": "replace",
        "entry_task": "replace",
        "parent_constraints": "deep_merge",
        "child_constraints": "deep_merge",
        "policies": "deep_merge",
        "hooks": "append_list",
        "available_tasks": "replace_list",
    },
    "task_definition": {
        "id": "replace",
        "name": "replace",
        "description": "replace",
        "policy": "deep_merge",
        "uses_reviews": "append_list",
        "uses_testing": "append_list",
        "uses_docs": "append_list",
        "subtasks": "replace_list",
        "applies_to_kinds": "replace_list",
    },
    "layout_definition": {
        "id": "replace",
        "name": "replace",
        "description": "replace",
        "children": "replace_list",
    },
    "hook_definition": {
        "id": "replace",
        "when": "replace",
        "applies_to": "deep_merge",
        "if": "deep_merge",
        "run": "replace_list",
    },
    "review_definition": {
        "id": "replace",
        "name": "replace",
        "scope": "replace",
        "description": "replace",
        "prompt": "replace",
        "applies_to": "deep_merge",
        "inputs": "deep_merge",
        "on_result": "deep_merge",
        "criteria": "replace_list",
    },
    "testing_definition": {
        "id": "replace",
        "name": "replace",
        "scope": "replace",
        "description": "replace",
        "applies_to": "deep_merge",
        "retry_policy": "deep_merge",
        "pass_rules": "deep_merge",
        "on_result": "deep_merge",
        "commands": "replace_list",
    },
    "docs_definition": {
        "id": "replace",
        "name": "replace",
        "scope": "replace",
        "description": "replace",
        "applies_to": "deep_merge",
        "inputs": "deep_merge",
        "outputs": "replace_list",
    },
    "rectification_definition": {
        "id": "replace",
        "name": "replace",
        "description": "replace",
        "trigger": "replace",
        "entry_task": "replace",
        "subtasks": "replace_list",
    },
    "project_policy_definition": {
        "id": "replace",
        "description": "replace",
        "defaults": "deep_merge",
        "runtime_policy_refs": "append_list",
        "hook_refs": "append_list",
        "review_refs": "append_list",
        "testing_refs": "append_list",
        "docs_refs": "append_list",
        "enabled_node_kinds": "replace_list",
        "prompt_pack": "replace",
        "environment_profiles": "append_list",
    },
    "runtime_policy_definition": {
        "id": "replace",
        "name": "replace",
        "description": "replace",
        "defaults": "deep_merge",
        "runtime_policy_refs": "append_list",
        "hook_refs": "append_list",
        "review_refs": "append_list",
        "testing_refs": "append_list",
        "docs_refs": "append_list",
    },
    "environment_policy_definition": {
        "id": "replace",
        "isolation_mode": "replace",
        "allow_network": "replace",
        "runtime_profile": "replace",
        "mandatory": "replace",
    },
    "prompt_reference_definition": {
        "id": "replace",
        "name": "replace",
        "description": "replace",
        "references": "deep_merge",
    },
}


IMMUTABLE_IDENTITY_FIELDS = {
    "node_definition": {"id", "kind"},
    "task_definition": {"id"},
    "layout_definition": {"id"},
    "hook_definition": {"id"},
    "review_definition": {"id"},
    "testing_definition": {"id"},
    "docs_definition": {"id"},
    "rectification_definition": {"id"},
    "project_policy_definition": {"id"},
    "runtime_policy_definition": {"id"},
    "environment_policy_definition": {"id"},
    "prompt_reference_definition": {"id"},
}


def list_override_documents(catalog) -> list[OverrideSourceSnapshot]:
    root = catalog.yaml_overrides_dir
    if not root.exists():
        return []
    documents: list[OverrideSourceSnapshot] = []
    for path in sorted(root.rglob("*.yaml")):
        relative_path = str(path.relative_to(root))
        content = path.read_text(encoding="utf-8")
        raw = yaml.safe_load(content) or {}
        document = OverrideDefinitionDocument.model_validate(raw)
        documents.append(
            OverrideSourceSnapshot(
                relative_path=relative_path,
                document=document,
                content_hash=sha256(content.encode("utf-8")).hexdigest(),
            )
        )
    return documents


def build_base_document_index(source_documents: list[SourceDocumentInput]) -> dict[tuple[str, str], _BaseDocument]:
    index: dict[tuple[str, str], _BaseDocument] = {}
    for source in source_documents:
        if not source.source_group.startswith("yaml_") or source.source_group == "yaml_overrides":
            continue
        family = identify_yaml_family(source.relative_path, source.source_group)
        raw = yaml.safe_load(source.content) or {}
        document = unwrap_yaml_document_payload(family, raw)
        target_id = _document_id(document, family, source.relative_path)
        key = (family, target_id)
        if key in index:
            raise OverrideResolutionError(
                failure_class="duplicate_source_ambiguity",
                summary=f"Multiple source documents resolve to {family}:{target_id}.",
                details_json={
                    "target_family": family,
                    "target_id": target_id,
                    "relative_paths": [index[key].relative_path, source.relative_path],
                },
                target_family=family,
                target_id=target_id,
            )
        index[key] = _BaseDocument(
            target_family=family,
            target_id=target_id,
            relative_path=source.relative_path,
            source_group=source.source_group,
            source_role=source.source_role,
            document=document,
            applied_override_paths=[],
        )
    return index


def resolve_overrides(
    base_documents: dict[tuple[str, str], _BaseDocument],
    override_documents: list[OverrideSourceSnapshot],
    *,
    built_in_library_version: str,
    allowed_targets: set[tuple[str, str]] | None = None,
) -> OverrideResolutionSnapshot:
    resolved = {
        key: _BaseDocument(
            target_family=value.target_family,
            target_id=value.target_id,
            relative_path=value.relative_path,
            source_group=value.source_group,
            source_role=value.source_role,
            document=deepcopy(value.document),
            applied_override_paths=list(value.applied_override_paths),
        )
        for key, value in base_documents.items()
    }
    applied: list[OverrideApplicationSnapshot] = []
    warnings: list[str] = []

    for override in override_documents:
        key = (override.document.target_family, override.document.target_id)
        if allowed_targets is not None and key not in allowed_targets:
            continue
        if key not in resolved:
            raise OverrideResolutionError(
                failure_class="override_missing_target",
                summary=f"Override target {override.document.target_family}:{override.document.target_id} was not found.",
                details_json={
                    "override_relative_path": override.relative_path,
                    "target_family": override.document.target_family,
                    "target_id": override.document.target_id,
                    "merge_mode": override.document.merge_mode,
                },
                target_family=override.document.target_family,
                target_id=override.document.target_id,
            )
        record = resolved[key]
        merged, override_warnings = _apply_override(
            record.document,
            override,
            built_in_library_version=built_in_library_version,
        )
        try:
            FAMILY_MODELS[record.target_family].model_validate(
                wrap_yaml_document_payload(record.target_family, merged)
            )
        except ValidationError as exc:
            raise OverrideResolutionError(
                failure_class="override_merge_conflict",
                summary=f"Override produced an invalid merged document for {record.target_family}:{record.target_id}.",
                details_json={
                    "override_relative_path": override.relative_path,
                    "errors": exc.errors(),
                    "merge_mode": override.document.merge_mode,
                },
                target_family=record.target_family,
                target_id=record.target_id,
            ) from exc
        record.document = merged
        record.applied_override_paths.append(override.relative_path)
        applied.append(
            OverrideApplicationSnapshot(
                override_relative_path=override.relative_path,
                override_id=override.document.id,
                target_family=record.target_family,
                target_id=record.target_id,
                merge_mode=override.document.merge_mode,
                field_names=sorted(override.document.value.keys()),
                compatibility=override.document.compatibility.model_dump(exclude_none=True),
                warnings=override_warnings,
            )
        )
        warnings.extend(override_warnings)

    return OverrideResolutionSnapshot(
        resolved_documents=[
            ResolvedDocumentSnapshot(
                target_family=item.target_family,
                target_id=item.target_id,
                relative_path=item.relative_path,
                source_group=item.source_group,
                source_role=item.source_role,
                resolved_document=item.document,
                applied_override_paths=item.applied_override_paths,
            )
            for _, item in sorted(resolved.items(), key=lambda entry: (entry[1].target_family, entry[1].target_id))
        ],
        applied_overrides=applied,
        warnings=warnings,
    )


def _apply_override(
    base_document: dict[str, object],
    override: OverrideSourceSnapshot,
    *,
    built_in_library_version: str,
) -> tuple[dict[str, object], list[str]]:
    family = override.document.target_family
    merged = deepcopy(base_document)
    warnings = _compatibility_warnings(override.document, built_in_library_version=built_in_library_version)
    rules = FAMILY_FIELD_MERGE_RULES.get(family)
    if rules is None:
        raise OverrideResolutionError(
            failure_class="override_merge_conflict",
            summary=f"No override merge rules are defined for {family}.",
            details_json={"override_relative_path": override.relative_path},
            target_family=family,
            target_id=override.document.target_id,
        )
    for field_name, override_value in override.document.value.items():
        expected_mode = rules.get(field_name, "replace")
        if expected_mode != override.document.merge_mode:
            raise OverrideResolutionError(
                failure_class="override_merge_conflict",
                summary=f"Field '{field_name}' on {family} requires merge mode '{expected_mode}'.",
                details_json={
                    "override_relative_path": override.relative_path,
                    "field_name": field_name,
                    "expected_merge_mode": expected_mode,
                    "actual_merge_mode": override.document.merge_mode,
                },
                target_family=family,
                target_id=override.document.target_id,
            )
        if field_name in IMMUTABLE_IDENTITY_FIELDS.get(family, set()) and merged.get(field_name) != override_value:
            raise OverrideResolutionError(
                failure_class="override_merge_conflict",
                summary=f"Override cannot change identity field '{field_name}' on {family}:{override.document.target_id}.",
                details_json={
                    "override_relative_path": override.relative_path,
                    "field_name": field_name,
                    "current_value": merged.get(field_name),
                    "override_value": override_value,
                },
                target_family=family,
                target_id=override.document.target_id,
            )
        current_value = merged.get(field_name)
        if override.document.merge_mode == "replace":
            merged[field_name] = deepcopy(override_value)
        elif override.document.merge_mode == "deep_merge":
            if not isinstance(current_value, dict) or not isinstance(override_value, dict):
                raise OverrideResolutionError(
                    failure_class="override_merge_conflict",
                    summary=f"Field '{field_name}' on {family} does not support deep_merge for the provided value.",
                    details_json={
                        "override_relative_path": override.relative_path,
                        "field_name": field_name,
                    },
                    target_family=family,
                    target_id=override.document.target_id,
                )
            merged[field_name] = _deep_merge_dicts(current_value, override_value)
        elif override.document.merge_mode == "append_list":
            if not isinstance(current_value, list) or not isinstance(override_value, list):
                raise OverrideResolutionError(
                    failure_class="override_merge_conflict",
                    summary=f"Field '{field_name}' on {family} does not support append_list for the provided value.",
                    details_json={
                        "override_relative_path": override.relative_path,
                        "field_name": field_name,
                    },
                    target_family=family,
                    target_id=override.document.target_id,
                )
            merged[field_name] = [*current_value, *deepcopy(override_value)]
        elif override.document.merge_mode == "replace_list":
            if not isinstance(override_value, list):
                raise OverrideResolutionError(
                    failure_class="override_merge_conflict",
                    summary=f"Field '{field_name}' on {family} requires a list replacement value.",
                    details_json={
                        "override_relative_path": override.relative_path,
                        "field_name": field_name,
                    },
                    target_family=family,
                    target_id=override.document.target_id,
                )
            merged[field_name] = deepcopy(override_value)
    return merged, warnings


def _compatibility_warnings(
    document: OverrideDefinitionDocument,
    *,
    built_in_library_version: str,
) -> list[str]:
    warnings: list[str] = []
    if document.compatibility.min_schema_version is not None:
        try:
            min_schema = int(document.compatibility.min_schema_version)
        except (TypeError, ValueError):
            min_schema = CURRENT_YAML_SCHEMA_VERSION + 1
        if min_schema > CURRENT_YAML_SCHEMA_VERSION:
            raise OverrideResolutionError(
                failure_class="override_incompatible_version",
                summary=(
                    f"Override for {document.target_family}:{document.target_id} requires schema version "
                    f"{document.compatibility.min_schema_version}."
                ),
                details_json={"compatibility": document.compatibility.model_dump(exclude_none=True)},
                target_family=document.target_family,
                target_id=document.target_id,
            )
    else:
        warnings.append("override compatibility does not declare min_schema_version")
    if document.compatibility.built_in_version is None:
        warnings.append("override compatibility does not declare built_in_version")
    elif document.compatibility.built_in_version != built_in_library_version:
        warnings.append(
            "override compatibility built_in_version "
            f"'{document.compatibility.built_in_version}' does not match '{built_in_library_version}'"
        )
    return warnings


def _deep_merge_dicts(left: dict[str, object], right: dict[str, object]) -> dict[str, object]:
    merged = deepcopy(left)
    for key, value in right.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge_dicts(merged[key], value)  # type: ignore[index]
        else:
            merged[key] = deepcopy(value)
    return merged


def _document_id(document: dict[str, object], family: str, relative_path: str) -> str:
    target_id = document.get("id")
    if isinstance(target_id, str) and target_id:
        return target_id
    raise OverrideResolutionError(
        failure_class="schema_validation_failure",
        summary=f"Document {relative_path} in family {family} has no stable id.",
        details_json={"relative_path": relative_path, "target_family": family},
        target_family=family,
    )
