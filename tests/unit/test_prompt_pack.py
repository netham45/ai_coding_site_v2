from __future__ import annotations

import re
from pathlib import Path

import yaml

from aicoding.rendering import build_render_context, render_text
from aicoding.resources import load_resource_catalog


_LEGACY_PLACEHOLDER_PATTERN = re.compile(r"<[A-Za-z0-9_.-]+>")


def _prompt_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*.md") if path.name != "README.md")


def _render_context():
    return build_render_context(
        scopes={
            "node": {
                "id": "node-123",
                "kind": "task",
                "title": "Implement durable prompt pack",
                "prompt": "Wait silently until nudged, then emit the done notification commands.",
            },
            "task": {
                "key": "execute_node",
                "name": "Execute Node",
                "description": "Perform the main implementation work for a leaf task node.",
            },
            "subtask": {
                "key": "run_leaf_prompt",
                "id": "run_leaf_prompt",
            },
            "compat": {
                "node_id": "node-123",
                "compiled_subtask_id": "subtask-456",
                "user_request": "Author the built-in default prompt pack.",
                "acceptance_criteria": "Prompt assets are authored, loadable, and renderable.",
                "layout_path": "artifacts/layout.yaml",
                "summary_path": "artifacts/summary.json",
            },
            "invoker": {
                "compiled_subtask_id": "subtask-456",
            },
        }
    )


def _collect_prompt_refs(payload: object) -> set[str]:
    found: set[str] = set()
    if isinstance(payload, dict):
        for value in payload.values():
            found.update(_collect_prompt_refs(value))
    elif isinstance(payload, list):
        for item in payload:
            found.update(_collect_prompt_refs(item))
    elif isinstance(payload, str) and payload.startswith("prompts/"):
        found.add(payload.removeprefix("prompts/"))
    return found


def test_default_prompt_reference_catalog_resolves_to_real_prompt_assets() -> None:
    catalog = load_resource_catalog()
    refs_path = catalog.yaml_builtin_system_dir / "prompts" / "default_prompt_refs.yaml"
    document = yaml.safe_load(refs_path.read_text(encoding="utf-8"))
    references = document["references"]

    for expected_key in (
        "layout.generate_phase",
        "execution.implement_leaf_task",
        "recovery.recover_interrupted_session",
        "runtime.session_bootstrap",
        "testing.interpret_results",
    ):
        assert expected_key in references

    for relative_path in references.values():
        assert catalog.resolve("prompt_pack_default", relative_path).exists(), relative_path


def test_default_prompt_pack_assets_are_authored_and_renderable(default_prompt_pack_root) -> None:
    context = _render_context()

    for path in _prompt_files(default_prompt_pack_root):
        content = path.read_text(encoding="utf-8")

        assert "placeholder" not in content.lower(), path.name
        assert "intentionally short" not in content.lower(), path.name
        assert len(content.strip()) >= 120, path.name
        assert content.count("\n") >= 3, path.name
        assert _LEGACY_PLACEHOLDER_PATTERN.search(content) is None, path.name

        rendered = render_text(content, context=context, field_name="prompt")
        assert rendered.rendered_text.strip()
        assert "missing render variable" not in rendered.rendered_text


def test_builtin_yaml_prompt_bindings_resolve_to_authored_prompt_pack(builtin_system_yaml_root) -> None:
    catalog = load_resource_catalog()
    referenced_prompts: set[str] = set()

    for path in sorted(builtin_system_yaml_root.rglob("*.yaml")):
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        referenced_prompts.update(_collect_prompt_refs(payload))

    assert referenced_prompts
    for relative_path in sorted(referenced_prompts):
        prompt_path = catalog.resolve("prompt_pack_default", relative_path)
        assert prompt_path.exists(), relative_path
        render_text(prompt_path.read_text(encoding="utf-8"), context=_render_context(), field_name="prompt")


def test_execution_prompt_includes_original_node_request() -> None:
    catalog = load_resource_catalog()
    prompt_path = catalog.resolve("prompt_pack_default", "execution/implement_leaf_task.md")
    content = prompt_path.read_text(encoding="utf-8")

    assert "{{node.prompt}}" in content
    rendered = render_text(content, context=_render_context(), field_name="prompt")

    assert "Wait silently until nudged" in rendered.rendered_text
    assert "wait instruction overrides the default workflow ordering" in rendered.rendered_text
    assert "do not convert \"waiting\" into shell activity" in rendered.rendered_text
    assert "do not register that as a durable summary" in rendered.rendered_text
    assert "--type subtask" in rendered.rendered_text
    assert "--type implementation" not in rendered.rendered_text
    assert "--result-file summaries/implementation.md" not in rendered.rendered_text
    assert "--result-file summaries/failure.md" not in rendered.rendered_text
