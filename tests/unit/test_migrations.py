from __future__ import annotations

from alembic.config import Config

from aicoding.db.migrations import (
    REVISION_ID_PATTERN,
    expected_database_revision,
    list_revision_ids,
    migration_history,
    validate_revision_identifiers,
)


def test_revision_identifier_pattern_matches_bootstrap_revision() -> None:
    assert REVISION_ID_PATTERN.match("0001_bootstrap_metadata")
    assert REVISION_ID_PATTERN.match("0002_daemon_authority_records")
    assert REVISION_ID_PATTERN.match("0003_configurable_node_hierarchy")
    assert REVISION_ID_PATTERN.match("0004_yaml_schema_records")
    assert REVISION_ID_PATTERN.match("0005_node_lifecycle_state")
    assert REVISION_ID_PATTERN.match("0006_node_version_supersession")
    assert REVISION_ID_PATTERN.match("0007_source_doc_lineage")
    assert REVISION_ID_PATTERN.match("0008_immutable_workflows")
    assert REVISION_ID_PATTERN.match("0009_dependency_admission")
    assert REVISION_ID_PATTERN.match("0010_node_run_orchestration")
    assert REVISION_ID_PATTERN.match("0011_session_binding_and_resume")
    assert REVISION_ID_PATTERN.match("0012_child_materialization")
    assert REVISION_ID_PATTERN.match("0014_rebuild_events")
    assert REVISION_ID_PATTERN.match("0017_test_results")
    assert REVISION_ID_PATTERN.match("0018_workflow_events")
    assert REVISION_ID_PATTERN.match("0019_parent_failure_counters")
    assert REVISION_ID_PATTERN.match("0020_prompt_and_summary_history")
    assert REVISION_ID_PATTERN.match("0021_code_provenance_map")
    assert REVISION_ID_PATTERN.match("0024_runtime_env_meta")
    assert REVISION_ID_PATTERN.match("0025_runtime_state_views")
    assert REVISION_ID_PATTERN.match("0026_session_history_views")
    assert REVISION_ID_PATTERN.match("0027_provenance_docs_audit_views")
    assert REVISION_ID_PATTERN.match("0029_incr_parent_merge_state")


def test_revision_identifiers_are_all_valid() -> None:
    assert validate_revision_identifiers() == []


def test_revision_history_and_heads_are_consistent() -> None:
    config = Config("alembic.ini")
    revisions = list_revision_ids()

    assert revisions == [
        "0001_bootstrap_metadata",
        "0002_daemon_authority_records",
        "0003_configurable_node_hierarchy",
        "0004_yaml_schema_records",
        "0005_node_lifecycle_state",
        "0006_node_version_supersession",
        "0007_source_doc_lineage",
        "0008_immutable_workflows",
        "0009_dependency_admission",
        "0010_node_run_orchestration",
        "0011_session_binding_and_resume",
        "0012_child_materialization",
        "0013_merge_conflict_records",
        "0014_rebuild_events",
        "0015_validation_results",
        "0016_review_results",
        "0017_test_results",
        "0018_workflow_events",
        "0019_parent_failure_counters",
        "0020_prompt_and_summary_history",
        "0021_code_provenance_map",
        "0022_documentation_outputs",
        "0023_action_automation",
        "0024_runtime_env_meta",
        "0025_runtime_state_views",
        "0026_session_history_views",
        "0027_provenance_docs_audit_views",
        "0029_incr_parent_merge_state",
    ]
    assert migration_history(config) == revisions
    assert expected_database_revision(config) == "0029_incr_parent_merge_state"
