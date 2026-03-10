from __future__ import annotations

from pathlib import Path

from uuid import uuid4

from aicoding.config import get_settings
from aicoding.daemon.provenance import (
    refresh_node_provenance,
    show_entity_by_name,
    show_entity_history,
    show_entity_relations,
    show_node_rationale,
)
from aicoding.daemon.versioning import create_superseding_node_version, cutover_candidate_version
from aicoding.db.models import HierarchyNode, LogicalNodeCurrentVersion, NodeHierarchyDefinition, NodeVersion
from aicoding.db.session import create_session_factory
from aicoding.db.session import session_scope


def _write_workspace(root: Path, file_name: str, source: str) -> None:
    path = root / file_name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source, encoding="utf-8")


def _create_minimal_node_version(db_session_factory, *, title: str, prompt: str):
    node_id = uuid4()
    version_id = uuid4()
    with session_scope(db_session_factory) as session:
        if session.get(NodeHierarchyDefinition, "epic") is None:
            session.add(
                NodeHierarchyDefinition(
                    kind="epic",
                    tier="epic",
                    description="Test epic node definition.",
                    main_prompt="main",
                    entry_task="execute_node",
                    available_tasks_json=["execute_node"],
                    allow_parentless=True,
                    allowed_parent_kinds_json=[],
                    allowed_parent_tiers_json=[],
                    allowed_child_kinds_json=[],
                    allowed_child_tiers_json=[],
                    min_children=None,
                    max_children=None,
                    source_path="tests/unit/test_provenance.py",
                )
            )
            session.flush()
        session.add(
            HierarchyNode(
                node_id=node_id,
                parent_node_id=None,
                kind="epic",
                tier="epic",
                title=title,
                prompt=prompt,
                created_via="daemon",
                max_children=None,
            )
        )
        session.add(
            NodeVersion(
                id=version_id,
                logical_node_id=node_id,
                parent_node_version_id=None,
                tier="epic",
                node_kind="epic",
                title=title,
                prompt=prompt,
                description=None,
                status="authoritative",
                version_number=1,
                compiled_workflow_id=None,
                supersedes_node_version_id=None,
                active_branch_name=None,
                branch_generation_number=None,
                seed_commit_sha=None,
                final_commit_sha=None,
            )
        )
        session.flush()
        session.add(
            LogicalNodeCurrentVersion(
                logical_node_id=node_id,
                authoritative_node_version_id=version_id,
                latest_created_node_version_id=version_id,
            )
        )

    class NodeRef:
        pass

    node = NodeRef()
    node.node_id = node_id
    return node


def test_refresh_node_provenance_extracts_entities_relations_and_rationale(migrated_public_schema, tmp_path) -> None:
    db_session_factory = create_session_factory(engine=migrated_public_schema)
    _write_workspace(
        tmp_path,
        "pkg/app.py",
        "\n".join(
            [
                "def helper(name):",
                "    return name.upper()",
                "",
                "class Greeter:",
                "    def greet(self, name):",
                "        return helper(name)",
            ]
        ),
    )
    node = _create_minimal_node_version(db_session_factory, title="Provenance", prompt="track code changes")

    refreshed = refresh_node_provenance(db_session_factory, logical_node_id=node.node_id, workspace_root=tmp_path)
    entity = show_entity_by_name(db_session_factory, canonical_name="pkg.app.Greeter.greet")
    history = show_entity_history(db_session_factory, canonical_name="pkg.app.Greeter.greet")
    relations = show_entity_relations(db_session_factory, canonical_name="pkg.app.Greeter.greet")
    rationale = show_node_rationale(db_session_factory, logical_node_id=node.node_id)

    assert refreshed.entity_count >= 4
    assert refreshed.relation_count >= 3
    assert refreshed.change_counts["added"] >= 4
    assert entity.entities[0].entity_type == "method"
    assert history.history[0].change_type == "added"
    assert history.history[0].match_reason == "new_entity"
    assert relations.relations[0].relation_type in {"calls", "contains"}
    assert "track code changes" in rationale.rationale_summary


def test_provenance_preserves_exact_identity_and_marks_modified_across_cutover(migrated_public_schema, tmp_path) -> None:
    db_session_factory = create_session_factory(engine=migrated_public_schema)
    _write_workspace(tmp_path, "pkg/app.py", "def hello(name):\n    return name.upper()\n")
    node = _create_minimal_node_version(db_session_factory, title="Exact Match", prompt="p")

    refresh_node_provenance(db_session_factory, logical_node_id=node.node_id, workspace_root=tmp_path)
    first = show_entity_history(db_session_factory, canonical_name="pkg.app.hello").history

    candidate = create_superseding_node_version(db_session_factory, logical_node_id=node.node_id)
    cutover_candidate_version(db_session_factory, version_id=candidate.id)
    _write_workspace(tmp_path, "pkg/app.py", "def hello(name):\n    return name.lower()\n")

    refresh_node_provenance(db_session_factory, logical_node_id=node.node_id, workspace_root=tmp_path)
    second = show_entity_history(db_session_factory, canonical_name="pkg.app.hello").history

    assert first[0].change_type == "added"
    assert second[-1].change_type == "modified"
    assert second[0].entity_id == second[-1].entity_id
    assert second[-1].match_confidence == "high"


def test_provenance_records_heuristic_rename_or_move_match_across_cutover(migrated_public_schema, tmp_path) -> None:
    db_session_factory = create_session_factory(engine=migrated_public_schema)
    _write_workspace(tmp_path, "pkg/app.py", "def hello(name):\n    return name.upper()\n")
    node = _create_minimal_node_version(db_session_factory, title="Rename", prompt="p")

    refresh_node_provenance(db_session_factory, logical_node_id=node.node_id, workspace_root=tmp_path)

    candidate = create_superseding_node_version(db_session_factory, logical_node_id=node.node_id)
    cutover_candidate_version(db_session_factory, version_id=candidate.id)
    (tmp_path / "pkg" / "app.py").unlink()
    _write_workspace(tmp_path, "pkg/renamed.py", "def wave(name):\n    return name.upper()\n")

    refresh_node_provenance(db_session_factory, logical_node_id=node.node_id, workspace_root=tmp_path)
    history = show_entity_history(db_session_factory, canonical_name="pkg.renamed.wave").history

    assert history[0].change_type == "added"
    assert history[-1].change_type == "renamed_or_moved"
    assert history[-1].match_confidence == "medium"
    assert history[0].entity_id == history[-1].entity_id


def test_refresh_node_provenance_extracts_typescript_entities_and_relations(migrated_public_schema, tmp_path) -> None:
    db_session_factory = create_session_factory(engine=migrated_public_schema)
    _write_workspace(
        tmp_path,
        "web/app.ts",
        "\n".join(
            [
                "export function helper(name: string) {",
                "  return name.toUpperCase();",
                "}",
                "",
                "export class Greeter {",
                "  greet(name: string) {",
                "    return helper(name);",
                "  }",
                "}",
            ]
        ),
    )
    node = _create_minimal_node_version(db_session_factory, title="TypeScript Provenance", prompt="track mixed code changes")

    refreshed = refresh_node_provenance(db_session_factory, logical_node_id=node.node_id, workspace_root=tmp_path)
    entity = show_entity_by_name(db_session_factory, canonical_name="web.app.Greeter.greet")
    history = show_entity_history(db_session_factory, canonical_name="web.app.Greeter.greet")
    relations = show_entity_relations(db_session_factory, canonical_name="web.app.Greeter.greet")

    assert refreshed.entity_count >= 4
    assert refreshed.relation_count >= 3
    assert entity.entities[0].entity_type == "method"
    assert history.history[0].metadata_json["language"] == "typescript"
    assert relations.relations[0].relation_type in {"calls", "contains"}


def test_provenance_records_javascript_heuristic_rename_or_move_match_across_cutover(migrated_public_schema, tmp_path) -> None:
    db_session_factory = create_session_factory(engine=migrated_public_schema)
    _write_workspace(tmp_path, "web/app.js", "export function hello(name) {\n  return name.toUpperCase();\n}\n")
    node = _create_minimal_node_version(db_session_factory, title="JS Rename", prompt="p")

    refresh_node_provenance(db_session_factory, logical_node_id=node.node_id, workspace_root=tmp_path)

    candidate = create_superseding_node_version(db_session_factory, logical_node_id=node.node_id)
    cutover_candidate_version(db_session_factory, version_id=candidate.id)
    (tmp_path / "web" / "app.js").unlink()
    _write_workspace(tmp_path, "web/renamed.js", "export function wave(name) {\n  return name.toUpperCase();\n}\n")

    refresh_node_provenance(db_session_factory, logical_node_id=node.node_id, workspace_root=tmp_path)
    history = show_entity_history(db_session_factory, canonical_name="web.renamed.wave").history

    assert history[0].change_type == "added"
    assert history[-1].change_type == "renamed_or_moved"
    assert history[-1].match_confidence == "medium"
    assert history[-1].metadata_json["language"] == "javascript"
    assert history[0].entity_id == history[-1].entity_id


def test_refresh_node_provenance_defaults_to_configured_workspace_root(migrated_public_schema, tmp_path, monkeypatch) -> None:
    db_session_factory = create_session_factory(engine=migrated_public_schema)
    workspace_root = tmp_path / "workspace"
    _write_workspace(workspace_root, "src/defaulted.py", "def greet(name):\n    return name.upper()\n")
    node = _create_minimal_node_version(db_session_factory, title="Workspace Default", prompt="p")

    monkeypatch.setenv("AICODING_WORKSPACE_ROOT", str(workspace_root))
    get_settings.cache_clear()
    try:
        refreshed = refresh_node_provenance(db_session_factory, logical_node_id=node.node_id)
    finally:
        get_settings.cache_clear()

    assert refreshed.entity_count >= 1
    assert show_entity_by_name(db_session_factory, canonical_name="src.defaulted.greet").entities
