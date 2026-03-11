from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from aicoding.daemon.errors import DaemonConflictError
from aicoding.hierarchy import HierarchyRegistry
from aicoding.resources import ResourceCatalog, load_resource_catalog
from aicoding.yaml_schemas import ProjectPolicyDefinitionDocument, RuntimePolicyDefinitionDocument


@dataclass(frozen=True, slots=True)
class ProjectPolicySnapshot:
    relative_path: str
    policy_id: str
    description: str
    defaults: dict[str, object]
    runtime_policy_refs: list[str]
    hook_refs: list[str]
    review_refs: list[str]
    testing_refs: list[str]
    docs_refs: list[str]
    enabled_node_kinds: list[str]
    prompt_pack: str
    environment_profiles: list[str]

    def to_payload(self) -> dict[str, object]:
        return {
            "relative_path": self.relative_path,
            "policy_id": self.policy_id,
            "description": self.description,
            "defaults": self.defaults,
            "runtime_policy_refs": self.runtime_policy_refs,
            "hook_refs": self.hook_refs,
            "review_refs": self.review_refs,
            "testing_refs": self.testing_refs,
            "docs_refs": self.docs_refs,
            "enabled_node_kinds": self.enabled_node_kinds,
            "prompt_pack": self.prompt_pack,
            "environment_profiles": self.environment_profiles,
        }


@dataclass(frozen=True, slots=True)
class EffectivePolicySnapshot:
    base_policy_id: str
    project_policy_ids: list[str]
    defaults: dict[str, object]
    runtime_policy_refs: list[str]
    hook_refs: list[str]
    review_refs: list[str]
    testing_refs: list[str]
    docs_refs: list[str]
    enabled_node_kinds: list[str]
    prompt_pack: str
    environment_profiles: list[str]

    def to_payload(self) -> dict[str, object]:
        return {
            "base_policy_id": self.base_policy_id,
            "project_policy_ids": self.project_policy_ids,
            "defaults": self.defaults,
            "runtime_policy_refs": self.runtime_policy_refs,
            "hook_refs": self.hook_refs,
            "review_refs": self.review_refs,
            "testing_refs": self.testing_refs,
            "docs_refs": self.docs_refs,
            "enabled_node_kinds": self.enabled_node_kinds,
            "prompt_pack": self.prompt_pack,
            "environment_profiles": self.environment_profiles,
        }


@dataclass(frozen=True, slots=True)
class PolicyImpactSnapshot:
    node_kind: str
    project_policy_ids: list[str]
    changed_defaults: dict[str, object]
    added_runtime_policy_refs: list[str]
    added_hook_refs: list[str]
    added_review_refs: list[str]
    added_testing_refs: list[str]
    added_docs_refs: list[str]
    enabled_for_node_kind: bool
    prompt_pack: str

    def to_payload(self) -> dict[str, object]:
        return {
            "node_kind": self.node_kind,
            "project_policy_ids": self.project_policy_ids,
            "changed_defaults": self.changed_defaults,
            "added_runtime_policy_refs": self.added_runtime_policy_refs,
            "added_hook_refs": self.added_hook_refs,
            "added_review_refs": self.added_review_refs,
            "added_testing_refs": self.added_testing_refs,
            "added_docs_refs": self.added_docs_refs,
            "enabled_for_node_kind": self.enabled_for_node_kind,
            "prompt_pack": self.prompt_pack,
        }


def list_project_policies(
    catalog: ResourceCatalog | None = None,
    *,
    hierarchy_registry: HierarchyRegistry | None = None,
    documents: list[tuple[str, ProjectPolicyDefinitionDocument]] | None = None,
) -> list[ProjectPolicySnapshot]:
    resource_catalog = catalog or load_resource_catalog()
    policies: list[ProjectPolicySnapshot] = []
    if documents is None:
        root = resource_catalog.yaml_project_policies_dir
        if not root.exists():
            return policies
        for path in sorted(root.glob("*.yaml")):
            relative_path = str(Path("project-policies") / path.name)
            document = ProjectPolicyDefinitionDocument.model_validate(
                yaml.safe_load(path.read_text(encoding="utf-8"))["project_policy_definition"]
            )
            policies.append(_snapshot(relative_path, document))
    else:
        for relative_path, document in documents:
            policies.append(_snapshot(relative_path, document))
    if hierarchy_registry is not None:
        for item in policies:
            _validate_policy_snapshot(item, resource_catalog, hierarchy_registry)
    return policies


def resolve_effective_policy(
    catalog: ResourceCatalog | None = None,
    *,
    hierarchy_registry: HierarchyRegistry,
    base_policy_document: RuntimePolicyDefinitionDocument | None = None,
    project_policy_documents: list[tuple[str, ProjectPolicyDefinitionDocument]] | None = None,
) -> EffectivePolicySnapshot:
    resource_catalog = catalog or load_resource_catalog()
    base = base_policy_document or _load_runtime_policy(resource_catalog, "policies/default_runtime_policy.yaml")
    project_policies = list_project_policies(
        resource_catalog,
        hierarchy_registry=hierarchy_registry,
        documents=project_policy_documents,
    )

    defaults = dict(base.defaults)
    runtime_policy_refs = list(base.runtime_policy_refs)
    hook_refs = list(base.hook_refs)
    review_refs = list(base.review_refs)
    testing_refs = list(base.testing_refs)
    docs_refs = list(base.docs_refs)
    enabled_node_kinds = sorted(hierarchy_registry.definitions.keys())
    prompt_pack = "default"
    environment_profiles: list[str] = []

    for policy in project_policies:
        defaults.update(policy.defaults)
        runtime_policy_refs = _merge_unique(runtime_policy_refs, policy.runtime_policy_refs)
        hook_refs = _merge_unique(hook_refs, policy.hook_refs)
        review_refs = _merge_unique(review_refs, policy.review_refs)
        testing_refs = _merge_unique(testing_refs, policy.testing_refs)
        docs_refs = _merge_unique(docs_refs, policy.docs_refs)
        if policy.enabled_node_kinds:
            enabled_node_kinds = sorted(set(policy.enabled_node_kinds))
        prompt_pack = policy.prompt_pack
        environment_profiles = _merge_unique(environment_profiles, policy.environment_profiles)

    return EffectivePolicySnapshot(
        base_policy_id=base.id,
        project_policy_ids=[item.policy_id for item in project_policies],
        defaults=defaults,
        runtime_policy_refs=runtime_policy_refs,
        hook_refs=hook_refs,
        review_refs=review_refs,
        testing_refs=testing_refs,
        docs_refs=docs_refs,
        enabled_node_kinds=enabled_node_kinds,
        prompt_pack=prompt_pack,
        environment_profiles=environment_profiles,
    )


def policy_impact_for_node_kind(
    node_kind: str,
    catalog: ResourceCatalog | None = None,
    *,
    hierarchy_registry: HierarchyRegistry,
    base_policy_document: RuntimePolicyDefinitionDocument | None = None,
    project_policy_documents: list[tuple[str, ProjectPolicyDefinitionDocument]] | None = None,
) -> PolicyImpactSnapshot:
    resource_catalog = catalog or load_resource_catalog()
    base = base_policy_document or _load_runtime_policy(resource_catalog, "policies/default_runtime_policy.yaml")
    effective = resolve_effective_policy(
        resource_catalog,
        hierarchy_registry=hierarchy_registry,
        base_policy_document=base,
        project_policy_documents=project_policy_documents,
    )
    return PolicyImpactSnapshot(
        node_kind=node_kind,
        project_policy_ids=effective.project_policy_ids,
        changed_defaults={key: value for key, value in effective.defaults.items() if base.defaults.get(key) != value},
        added_runtime_policy_refs=[item for item in effective.runtime_policy_refs if item not in base.runtime_policy_refs],
        added_hook_refs=[item for item in effective.hook_refs if item not in base.hook_refs],
        added_review_refs=[item for item in effective.review_refs if item not in base.review_refs],
        added_testing_refs=[item for item in effective.testing_refs if item not in base.testing_refs],
        added_docs_refs=[item for item in effective.docs_refs if item not in base.docs_refs],
        enabled_for_node_kind=node_kind in effective.enabled_node_kinds,
        prompt_pack=effective.prompt_pack,
    )


def _snapshot(relative_path: str, document: ProjectPolicyDefinitionDocument) -> ProjectPolicySnapshot:
    return ProjectPolicySnapshot(
        relative_path=relative_path,
        policy_id=document.id,
        description=document.description,
        defaults=document.defaults,
        runtime_policy_refs=document.runtime_policy_refs,
        hook_refs=document.hook_refs,
        review_refs=document.review_refs,
        testing_refs=document.testing_refs,
        docs_refs=document.docs_refs,
        enabled_node_kinds=document.enabled_node_kinds,
        prompt_pack=document.prompt_pack,
        environment_profiles=document.environment_profiles,
    )


def _validate_policy_snapshot(
    snapshot: ProjectPolicySnapshot,
    catalog: ResourceCatalog,
    hierarchy_registry: HierarchyRegistry,
) -> None:
    ref_groups = {
        "runtime_policy_refs": ("runtime", snapshot.runtime_policy_refs),
        "hook_refs": ("hooks", snapshot.hook_refs),
        "review_refs": ("reviews", snapshot.review_refs),
        "testing_refs": ("testing", snapshot.testing_refs),
        "docs_refs": ("docs", snapshot.docs_refs),
    }
    for field_name, (directory, refs) in ref_groups.items():
        for ref in refs:
            normalized = _normalize_relative_yaml_ref(ref, directory)
            if not _project_policy_asset_exists(catalog, normalized):
                raise DaemonConflictError(
                    f"project policy references missing {field_name} asset '{normalized}'"
                )
    for profile in snapshot.environment_profiles:
        normalized = _normalize_relative_yaml_ref(profile, "environments")
        if not _project_policy_asset_exists(catalog, normalized):
            raise DaemonConflictError(
                f"project policy references missing environment profile '{normalized}'"
            )
    for node_kind in snapshot.enabled_node_kinds:
        if node_kind not in hierarchy_registry.definitions:
            raise DaemonConflictError(f"project policy references unknown node kind '{node_kind}'")
    if snapshot.prompt_pack not in {"default", "project"}:
        raise DaemonConflictError(f"unsupported prompt pack '{snapshot.prompt_pack}'")
    if snapshot.prompt_pack == "project" and not catalog.prompt_project_dir.exists():
        raise DaemonConflictError("project prompt pack requested but no project prompt directory exists")


def _load_runtime_policy(catalog: ResourceCatalog, relative_path: str) -> RuntimePolicyDefinitionDocument:
    return RuntimePolicyDefinitionDocument.model_validate(yaml.safe_load(catalog.read_text("yaml_builtin_system", relative_path)))


def _merge_unique(existing: list[str], additions: list[str]) -> list[str]:
    merged = list(existing)
    for item in additions:
        if item not in merged:
            merged.append(item)
    return merged


def _normalize_relative_yaml_ref(reference: str, directory: str) -> str:
    relative_path = reference.removeprefix(f"{directory}/")
    if not relative_path.endswith(".yaml"):
        relative_path = f"{relative_path}.yaml"
    return f"{directory}/{relative_path}"


def _project_policy_asset_exists(catalog: ResourceCatalog, normalized_relative_path: str) -> bool:
    return (
        catalog.resolve("yaml_builtin_system", normalized_relative_path).exists()
        or catalog.resolve("yaml_project", normalized_relative_path).exists()
    )
