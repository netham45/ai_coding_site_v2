from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Mapping


_CANONICAL_SENTINEL_OPEN = "\u0000render-open\u0000"
_CANONICAL_SENTINEL_CLOSE = "\u0000render-close\u0000"
_LEGACY_SENTINEL_OPEN = "\u0000legacy-open\u0000"
_LEGACY_SENTINEL_CLOSE = "\u0000legacy-close\u0000"

_CANONICAL_PATTERN = re.compile(r"\{\{\s*([A-Za-z0-9_.-]+)\s*\}\}")
_LEGACY_PATTERN = re.compile(r"<([A-Za-z0-9_.-]+)>")
_POTENTIAL_PATTERN = re.compile(r"\{\{|\}\}|<([A-Za-z0-9_.-]+)>")


class TemplateRenderError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class RenderContext:
    values: dict[str, str]
    scopes: dict[str, dict[str, str]]


@dataclass(frozen=True, slots=True)
class RenderResult:
    source_text: str
    rendered_text: str
    variables_used: list[str]
    source_syntaxes: list[str]


def build_render_context(*, scopes: Mapping[str, Mapping[str, object]]) -> RenderContext:
    flattened_scopes: dict[str, dict[str, str]] = {}
    values: dict[str, str] = {}
    for scope_name, payload in scopes.items():
        scope_values = _flatten_mapping(payload)
        flattened_scopes[scope_name] = scope_values
        for key, value in scope_values.items():
            scoped_key = f"{scope_name}.{key}"
            values[scoped_key] = value
            values[key] = value
    return RenderContext(values=values, scopes=flattened_scopes)


def render_text(
    template_text: str,
    *,
    context: RenderContext,
    field_name: str,
    allowed_syntaxes: tuple[str, ...] = ("canonical", "legacy"),
) -> RenderResult:
    prepared = (
        template_text.replace("{{{{", _CANONICAL_SENTINEL_OPEN)
        .replace("}}}}", _CANONICAL_SENTINEL_CLOSE)
        .replace("<<", _LEGACY_SENTINEL_OPEN)
        .replace(">>", _LEGACY_SENTINEL_CLOSE)
    )
    variables_used: list[str] = []
    source_syntaxes: list[str] = []

    if "canonical" in allowed_syntaxes:
        prepared, canonical_variables = _substitute(prepared, _CANONICAL_PATTERN, context, field_name=field_name)
        if canonical_variables:
            source_syntaxes.append("canonical")
            variables_used.extend(canonical_variables)
    if "legacy" in allowed_syntaxes:
        prepared, legacy_variables = _substitute(prepared, _LEGACY_PATTERN, context, field_name=field_name)
        if legacy_variables:
            source_syntaxes.append("legacy")
            variables_used.extend(legacy_variables)

    rendered = (
        prepared.replace(_CANONICAL_SENTINEL_OPEN, "{{")
        .replace(_CANONICAL_SENTINEL_CLOSE, "}}")
        .replace(_LEGACY_SENTINEL_OPEN, "<")
        .replace(_LEGACY_SENTINEL_CLOSE, ">")
    )
    variables_used = sorted(set(variables_used))
    source_syntaxes = sorted(set(source_syntaxes))
    return RenderResult(
        source_text=template_text,
        rendered_text=rendered,
        variables_used=variables_used,
        source_syntaxes=source_syntaxes,
    )


def contains_template_syntax(value: object) -> bool:
    if isinstance(value, str):
        return bool(_POTENTIAL_PATTERN.search(value))
    if isinstance(value, Mapping):
        return any(contains_template_syntax(item) for item in value.values())
    if isinstance(value, list):
        return any(contains_template_syntax(item) for item in value)
    return False


def _substitute(
    template_text: str,
    pattern: re.Pattern[str],
    context: RenderContext,
    *,
    field_name: str,
) -> tuple[str, list[str]]:
    seen_variables: list[str] = []

    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in context.values:
            available = ", ".join(sorted(context.values))
            raise TemplateRenderError(
                f"missing render variable '{key}' for {field_name}; available variables: {available}"
            )
        seen_variables.append(key)
        return context.values[key]

    return pattern.sub(replace, template_text), seen_variables


def _flatten_mapping(
    payload: Mapping[str, object],
    *,
    prefix: str = "",
) -> dict[str, str]:
    flattened: dict[str, str] = {}
    for key, value in payload.items():
        normalized_key = str(key)
        composite_key = normalized_key if not prefix else f"{prefix}.{normalized_key}"
        if isinstance(value, Mapping):
            nested = _flatten_mapping(value, prefix=composite_key)
            flattened.update(nested)
            continue
        flattened[composite_key] = _stringify(value)
    return flattened


def _stringify(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)
