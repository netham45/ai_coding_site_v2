from __future__ import annotations

from pathlib import Path

import pytest

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
