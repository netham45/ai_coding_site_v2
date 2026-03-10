from __future__ import annotations

import pytest

from aicoding.resources import load_resource_catalog


@pytest.fixture
def resource_catalog():
    return load_resource_catalog()


@pytest.fixture
def builtin_system_yaml_root(resource_catalog):
    return resource_catalog.yaml_builtin_dir / "system-yaml"


@pytest.fixture
def default_prompt_pack_root(resource_catalog):
    return resource_catalog.root / "prompts" / "packs" / "default"


@pytest.fixture
def prompt_render_context():
    return {
        "node_id": "node-scaffold",
        "run_id": "run-scaffold",
        "session_id": "session-scaffold",
        "prompt_pack": "default",
    }


@pytest.fixture
def yaml_compile_context():
    return {
        "scope": "builtin",
        "resource_group": "yaml_builtin_system",
        "entrypoint": "nodes/task.yaml",
    }
