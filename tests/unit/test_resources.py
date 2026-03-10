from __future__ import annotations

from pathlib import Path

import pytest

from aicoding.config import Settings
from aicoding.errors import ConfigurationError
from aicoding.resources import load_resource_catalog


def test_load_resource_catalog_resolves_expected_groups() -> None:
    catalog = load_resource_catalog()

    groups = catalog.group_paths()
    assert sorted(groups) == [
        "docs",
        "prompt_execution",
        "prompt_layouts",
        "prompt_pack_default",
        "prompt_project",
        "prompt_quality",
        "prompt_recovery",
        "yaml_builtin",
        "yaml_builtin_system",
        "yaml_overrides",
        "yaml_project",
        "yaml_project_policies",
        "yaml_schemas",
    ]
    assert groups["prompt_layouts"].is_dir()


def test_resource_resolve_rejects_path_escape() -> None:
    catalog = load_resource_catalog()

    with pytest.raises(ConfigurationError) as exc:
        catalog.resolve("prompt_layouts", "../execution/README.md")

    assert exc.value.code == "resource_path_escape"


def test_resource_read_text_reads_prompt_asset() -> None:
    catalog = load_resource_catalog()

    content = catalog.read_text("prompt_layouts", "README.md")

    assert "Layout-generation prompt assets" in content


def test_resource_load_text_returns_typed_payload() -> None:
    catalog = load_resource_catalog()

    loaded = catalog.load_text("yaml_builtin_system", "nodes/epic.yaml")

    assert loaded.descriptor.group == "yaml_builtin_system"
    assert loaded.descriptor.relative_path == "nodes/epic.yaml"
    assert "node_definition:" in loaded.content


def test_load_resource_catalog_uses_workspace_root_for_project_resources(tmp_path: Path) -> None:
    workspace_root = tmp_path / "workspace"
    project_policy_dir = workspace_root / "resources" / "yaml" / "project" / "project-policies"
    overrides_dir = workspace_root / "resources" / "yaml" / "overrides"
    project_policy_dir.mkdir(parents=True)
    overrides_dir.mkdir(parents=True)

    catalog = load_resource_catalog(
        Settings(
            database_url="postgresql+psycopg://example",
            workspace_root=workspace_root,
        )
    )

    assert catalog.root.name == "resources"
    assert catalog.yaml_builtin_system_dir.is_dir()
    assert catalog.yaml_project_dir == workspace_root / "resources" / "yaml" / "project"
    assert catalog.yaml_project_policies_dir == project_policy_dir
    assert catalog.yaml_overrides_dir == overrides_dir
    assert catalog.prompt_project_dir == workspace_root / "resources" / "prompts" / "project"
    assert catalog.docs_dir == workspace_root / "resources" / "docs"
