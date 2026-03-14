from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from aicoding.cli.parser import build_parser
from aicoding.config import Settings
from aicoding.relevant_user_flows import load_relevant_user_flow_inventory


REPO_ROOT = Path(__file__).resolve().parents[2]
DOCS_DIR = REPO_ROOT / "docs"
FLOW_INVENTORY_PATH = (
    REPO_ROOT / "notes" / "catalogs" / "traceability" / "relevant_user_flow_inventory.yaml"
)


def _load_frontmatter(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n"), f"{path.name} must start with YAML frontmatter"
    _, rest = text.split("---\n", 1)
    frontmatter_text, _ = rest.split("\n---\n", 1)
    data = yaml.safe_load(frontmatter_text)
    assert isinstance(data, dict), f"{path.name} frontmatter must be a mapping"
    return data


def _collect_command_paths(parser: argparse.ArgumentParser, prefix: tuple[str, ...] = ()) -> set[str]:
    paths: set[str] = set()
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            for name, child in action.choices.items():
                current = prefix + (name,)
                paths.add(" ".join(current))
                paths.update(_collect_command_paths(child, current))
    return paths


def test_docs_frontmatter_command_paths_exist_in_cli() -> None:
    parser = build_parser()
    available_paths = _collect_command_paths(parser)

    for path in sorted(DOCS_DIR.rglob("*.md")):
        if path.name == "README.md":
            continue
        metadata = _load_frontmatter(path)
        for command_path in metadata.get("command_paths", []):
            assert command_path in available_paths, f"{path.name} references missing command path {command_path!r}"


def test_configuration_doc_references_real_settings_fields() -> None:
    metadata = _load_frontmatter(DOCS_DIR / "reference" / "configuration.md")
    field_names = set(Settings.model_fields)

    for field_name in metadata.get("config_fields", []):
        assert field_name in field_names, f"configuration doc references unknown settings field {field_name!r}"

    for env_var in metadata.get("env_vars", []):
        assert env_var.startswith("AICODING_"), f"unexpected env var prefix for {env_var!r}"


def test_flow_docs_reference_real_relevant_user_flows() -> None:
    inventory = load_relevant_user_flow_inventory(FLOW_INVENTORY_PATH)
    flow_ids = {flow.flow_id for flow in inventory.flows}

    for path in sorted(DOCS_DIR.rglob("*.md")):
        if path.name == "README.md":
            continue
        metadata = _load_frontmatter(path)
        for flow_id in metadata.get("flow_ids", []):
            assert flow_id in flow_ids, f"{path.name} references unknown flow id {flow_id!r}"
