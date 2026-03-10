from __future__ import annotations

import pytest

from aicoding.rendering import TemplateRenderError, build_render_context, render_text


def test_render_text_supports_canonical_and_legacy_placeholders() -> None:
    context = build_render_context(
        scopes={
            "node": {"id": "node-123", "title": "Compile Title"},
            "compat": {"node_title": "Compile Title"},
            "invoker": {"mode": "fast"},
        }
    )

    result = render_text(
        "Node {{node.id}} / <node_title> / {{mode}}",
        context=context,
        field_name="prompt",
    )

    assert result.rendered_text == "Node node-123 / Compile Title / fast"
    assert result.variables_used == ["mode", "node.id", "node_title"]
    assert result.source_syntaxes == ["canonical", "legacy"]


def test_render_text_honors_last_scope_for_unqualified_aliases() -> None:
    context = build_render_context(
        scopes={
            "node": {"id": "node-123"},
            "compat": {"node_id": "node-123"},
            "invoker": {"node_id": "override-node"},
        }
    )

    result = render_text("{{node_id}}", context=context, field_name="prompt")

    assert result.rendered_text == "override-node"


def test_render_text_supports_literal_escape_sequences() -> None:
    context = build_render_context(scopes={"node": {"id": "node-123"}})

    result = render_text("{{{{node.id}}}} <<node_id>>", context=context, field_name="prompt")

    assert result.rendered_text == "{{node.id}} <node_id>"
    assert result.variables_used == []


def test_render_text_raises_on_missing_variable() -> None:
    context = build_render_context(scopes={"node": {"id": "node-123"}})

    with pytest.raises(TemplateRenderError, match="missing render variable 'node.title'"):
        render_text("{{node.title}}", context=context, field_name="prompt")
