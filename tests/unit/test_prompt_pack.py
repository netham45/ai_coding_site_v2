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


def _collect_daemon_owned_prompt_selectors(source_root: Path) -> set[str]:
    pattern = re.compile(r'(?:load_text|resolve)\("prompt_pack_default", "([^"]+)"\)')
    found: set[str] = set()
    for path in sorted(source_root.rglob("*.py")):
        found.update(pattern.findall(path.read_text(encoding="utf-8")))
    return found


def test_default_prompt_reference_catalog_resolves_to_real_prompt_assets() -> None:
    catalog = load_resource_catalog()
    refs_path = catalog.yaml_builtin_system_dir / "prompts" / "default_prompt_refs.yaml"
    document = yaml.safe_load(refs_path.read_text(encoding="utf-8"))
    references = document["references"]

    for expected_key in (
        "layout.generate_phase",
        "execution.implement_leaf_task",
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


def test_default_prompt_pack_has_no_unbound_prompt_files(default_prompt_pack_root) -> None:
    catalog = load_resource_catalog()
    yaml_bound_prompts: set[str] = set()

    for path in sorted(catalog.yaml_builtin_system_dir.rglob("*.yaml")):
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        yaml_bound_prompts.update(_collect_prompt_refs(payload))

    daemon_owned_prompts = _collect_daemon_owned_prompt_selectors(Path("src/aicoding"))
    active_prompt_bindings = yaml_bound_prompts | daemon_owned_prompts
    prompt_files = {path.relative_to(default_prompt_pack_root).as_posix() for path in _prompt_files(default_prompt_pack_root)}
    unbound_prompts = sorted(prompt_files - active_prompt_bindings)

    assert not unbound_prompts, f"Unbound prompt files: {unbound_prompts}"


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
    assert "subtask succeed --node node-123 --compiled-subtask CURRENT_COMPILED_SUBTASK_ID --summary-file summaries/implementation.md" in rendered.rendered_text
    assert "summary register --node node-123 --file summaries/implementation.md --type subtask" not in rendered.rendered_text
    assert 'subtask complete --node node-123 --compiled-subtask CURRENT_COMPILED_SUBTASK_ID --summary "Implemented the leaf task."' not in rendered.rendered_text
    assert "workflow advance --node node-123" not in rendered.rendered_text
    assert "subtask current --node node-123" not in rendered.rendered_text
    assert "if this extra context read is unavailable or times out, continue with the compiled context already embedded in this prompt instead of blocking the workflow" in rendered.rendered_text
    assert "PYTHONPATH=src python3 -m aicoding.cli.main subtask prompt --node node-123" in rendered.rendered_text
    assert "continue in the same session" in rendered.rendered_text
    assert "stop and do not probe the closed run" in rendered.rendered_text


def test_layout_generation_prompts_require_explicit_layout_registration() -> None:
    catalog = load_resource_catalog()
    context = _render_context()

    for relative_path in (
        "layouts/generate_phase_layout.md",
        "layouts/generate_plan_layout.md",
        "layouts/generate_task_layout.md",
    ):
        content = catalog.resolve("prompt_pack_default", relative_path).read_text(encoding="utf-8")
        rendered = render_text(content, context=context, field_name="prompt")

        assert "node register-layout" in rendered.rendered_text
        assert "--node node-123" in rendered.rendered_text
        assert "--file layouts/generated/node-123.yaml" in rendered.rendered_text
        assert "do not assume the daemon will discover" in rendered.rendered_text
        assert "kind: layout_definition" in rendered.rendered_text
        assert "children:" in rendered.rendered_text
        assert "Use the current compiled subtask UUID from this prompt" in rendered.rendered_text
        assert "CURRENT_COMPILED_SUBTASK_ID" in rendered.rendered_text
        assert "subtask current --node node-123" not in rendered.rendered_text
        assert "subtask start --node node-123 --compiled-subtask CURRENT_COMPILED_SUBTASK_ID" in rendered.rendered_text
        assert "subtask context --node node-123" in rendered.rendered_text
        assert "if this extra context read is unavailable or times out, continue with the compiled context already embedded in this prompt instead of blocking the workflow" in rendered.rendered_text
        assert "subtask succeed --node node-123 --compiled-subtask CURRENT_COMPILED_SUBTASK_ID --summary-file summaries/layout_generation.md" in rendered.rendered_text
        if relative_path == "layouts/generate_phase_layout.md":
            assert "if the user request specifies an exact child count, honor that exact count" in rendered.rendered_text
            assert "if the user request specifies a direct dependency shape between siblings, preserve that exact shape" in rendered.rendered_text
            assert "do not add coordination, setup, or verification phases" in rendered.rendered_text
        if relative_path == "layouts/generate_plan_layout.md":
            assert "default to exactly one implementation plan" in rendered.rendered_text
            assert "do not split concrete implementation work into separate diagnosis, discovery, reproduction, or verification-only plans" in rendered.rendered_text
            assert "do not preserve ancestor decomposition patterns" in rendered.rendered_text
        if relative_path == "layouts/generate_task_layout.md":
            assert "create exactly one implementation task by default" in rendered.rendered_text
            assert "do not split concrete implementation work into separate diagnosis, discovery, reproduction, or verification-only tasks" in rendered.rendered_text
            assert "do not preserve ancestor dependency shapes" in rendered.rendered_text
        assert "summary register --node node-123 --file summaries/layout_generation.md --type subtask" not in rendered.rendered_text
        assert "subtask complete --node node-123 --compiled-subtask CURRENT_COMPILED_SUBTASK_ID" not in rendered.rendered_text
        assert "workflow advance --node node-123" not in rendered.rendered_text
        assert "PYTHONPATH=src python3 -m aicoding.cli.main subtask prompt --node node-123" in rendered.rendered_text
        assert "stop and do not probe the closed parent run" in rendered.rendered_text


def test_runtime_cli_bootstrap_prompt_requires_foreground_subtask_startup_sequence() -> None:
    catalog = load_resource_catalog()
    context = _render_context()
    content = catalog.resolve("prompt_pack_default", "runtime/cli_bootstrap.md").read_text(encoding="utf-8")
    rendered = render_text(content, context=context, field_name="prompt")

    assert "Use the current compiled subtask UUID already provided in this prompt" in rendered.rendered_text
    assert "subtask current --node node-123" not in rendered.rendered_text
    assert "state.current_compiled_subtask_id" not in rendered.rendered_text
    assert "subtask start --node node-123 --compiled-subtask CURRENT_COMPILED_SUBTASK_ID" in rendered.rendered_text
    assert "subtask context --node node-123" in rendered.rendered_text
    assert "If that extra context read is unavailable or times out, continue with the prompt and compiled context already in this session instead of blocking the workflow." in rendered.rendered_text
    assert "Finish the concrete work for the current subtask instead of repeatedly reloading the prompt" in rendered.rendered_text
    assert "subtask succeed --node node-123 --compiled-subtask CURRENT_COMPILED_SUBTASK_ID --summary-file PATH_TO_SUMMARY" in rendered.rendered_text
    assert "subtask fail --node node-123 --compiled-subtask CURRENT_COMPILED_SUBTASK_ID --summary-file PATH_TO_FAILURE_SUMMARY" in rendered.rendered_text
    assert "follow the daemon-routed next stage instead of looping back through `subtask prompt`" in rendered.rendered_text
    assert "do not leave short-lived CLI commands waiting in a background terminal" in rendered.rendered_text


def test_runtime_session_bootstrap_prompt_requires_single_pass_bootstrap_and_handoff() -> None:
    catalog = load_resource_catalog()
    context = _render_context()
    content = catalog.resolve("prompt_pack_default", "runtime/session_bootstrap.md").read_text(encoding="utf-8")
    rendered = render_text(content, context=context, field_name="prompt")

    assert "do the bootstrap checks once, then stop reloading this prompt" in rendered.rendered_text
    assert "record the result through the daemon-provided `subtask succeed` or `subtask fail` command path" in rendered.rendered_text
    assert "continue from the routed next stage instead of fetching this bootstrap prompt again" in rendered.rendered_text


def test_review_prompts_require_review_run_submission() -> None:
    catalog = load_resource_catalog()
    context = _render_context()

    for relative_path in (
        "review/review_layout_against_request.md",
        "review/review_node_output.md",
    ):
        content = catalog.resolve("prompt_pack_default", relative_path).read_text(encoding="utf-8")
        rendered = render_text(content, context=context, field_name="prompt")

        assert "review run --node node-123 --status pass" in rendered.rendered_text
        assert "--status revise" in rendered.rendered_text
        assert "--status fail" in rendered.rendered_text
        assert "--findings-file reviews/findings.json" in rendered.rendered_text
        assert "--criteria-file reviews/criteria.json" in rendered.rendered_text
        if relative_path == "review/review_layout_against_request.md":
            assert "diagnosis, discovery, reproduction, or verification-only children" in rendered.rendered_text
            assert "concrete file/module target and exact validation command" in rendered.rendered_text
            assert "Revise the layout instead of passing it" in rendered.rendered_text
