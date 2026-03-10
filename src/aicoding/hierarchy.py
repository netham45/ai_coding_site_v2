from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import Field

from aicoding.models.base import AICodingModel
from aicoding.resources import ResourceCatalog, load_resource_catalog


class NodeConstraintSet(AICodingModel):
    allowed_kinds: list[str] = Field(default_factory=list)
    allowed_tiers: list[int | str] = Field(default_factory=list)
    allow_parentless: bool = False
    min_children: int | None = None
    max_children: int | None = None


class NodePolicies(AICodingModel):
    max_node_regenerations: int
    max_subtask_retries: int
    child_failure_threshold_total: int
    child_failure_threshold_consecutive: int
    child_failure_threshold_per_child: int
    require_review_before_finalize: bool
    require_testing_before_finalize: bool
    require_docs_before_finalize: bool
    auto_run_children: bool
    auto_rectify_upstream: bool
    auto_merge_to_parent: bool
    auto_merge_to_base: bool


class NodeDefinition(AICodingModel):
    id: str
    kind: str
    tier: int | str
    description: str
    main_prompt: str
    entry_task: str
    available_tasks: list[str]
    parent_constraints: NodeConstraintSet
    child_constraints: NodeConstraintSet
    policies: NodePolicies
    hooks: list[str]


class NodeDefinitionDocument(AICodingModel):
    node_definition: NodeDefinition


class HierarchyDefinitionRecord(AICodingModel):
    source_group: str
    relative_path: str
    definition: NodeDefinition


class HierarchyRegistry(AICodingModel):
    definitions: dict[str, HierarchyDefinitionRecord]

    def get(self, kind: str) -> NodeDefinition:
        return self.definitions[kind].definition

    def top_level_kinds(self) -> list[str]:
        return sorted(kind for kind, record in self.definitions.items() if record.definition.parent_constraints.allow_parentless)

    def validate_parent_child(self, *, parent_kind: str | None, child_kind: str) -> None:
        child = self.get(child_kind)
        if parent_kind is None:
            if not child.parent_constraints.allow_parentless:
                raise ValueError(f"Node kind '{child_kind}' requires a parent.")
            return

        parent = self.get(parent_kind)
        if child.parent_constraints.allowed_kinds and parent.kind not in child.parent_constraints.allowed_kinds:
            raise ValueError(f"Node kind '{child_kind}' does not allow parent kind '{parent.kind}'.")
        if child.parent_constraints.allowed_tiers and parent.tier not in child.parent_constraints.allowed_tiers:
            raise ValueError(f"Node kind '{child_kind}' does not allow parent tier '{parent.tier}'.")
        if parent.child_constraints.allowed_kinds and child.kind not in parent.child_constraints.allowed_kinds:
            raise ValueError(f"Node kind '{parent.kind}' does not allow child kind '{child.kind}'.")
        if parent.child_constraints.allowed_tiers and child.tier not in parent.child_constraints.allowed_tiers:
            raise ValueError(f"Node kind '{parent.kind}' does not allow child tier '{child.tier}'.")


def load_hierarchy_registry(catalog: ResourceCatalog | None = None) -> HierarchyRegistry:
    resource_catalog = catalog or load_resource_catalog()
    definitions: dict[str, HierarchyDefinitionRecord] = {}
    root = resource_catalog.yaml_builtin_system_dir / "nodes"
    for path in sorted(root.glob("*.yaml")):
        relative_path = str(Path("nodes") / path.name)
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        document = NodeDefinitionDocument.model_validate(payload)
        definitions[document.node_definition.kind] = HierarchyDefinitionRecord(
            source_group="yaml_builtin_system",
            relative_path=relative_path,
            definition=document.node_definition,
        )
    return HierarchyRegistry(definitions=definitions)
