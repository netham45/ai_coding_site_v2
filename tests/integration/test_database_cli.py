from __future__ import annotations


def test_db_ping_command_reports_connection_details(cli_runner) -> None:
    result = cli_runner(["admin", "db", "ping"])
    payload = result.json()

    assert result.exit_code == 0
    assert payload["database_name"] == "aicoding"
    assert payload["current_user"] == "aicoding"


def test_db_upgrade_and_status_report_revision(clean_public_schema, cli_runner) -> None:
    assert cli_runner(["admin", "db", "upgrade"]).exit_code == 0

    result = cli_runner(["admin", "db", "status"])
    payload = result.json()

    assert result.exit_code == 0
    assert payload["alembic_revision"] == "0027_provenance_docs_audit_views"
    assert "bootstrap_metadata" in payload["tables"]
    assert "daemon_node_states" in payload["tables"]
    assert "node_hierarchy_definitions" in payload["tables"]
    assert "yaml_schema_validation_records" in payload["tables"]
    assert "node_lifecycle_states" in payload["tables"]
    assert "node_versions" in payload["tables"]
    assert "logical_node_current_versions" in payload["tables"]
    assert "source_documents" in payload["tables"]
    assert "node_version_source_documents" in payload["tables"]
    assert "validation_results" in payload["tables"]
    assert "review_results" in payload["tables"]
    assert "prompts" in payload["tables"]
    assert "summaries" in payload["tables"]
    assert "code_entities" in payload["tables"]
    assert "node_entity_changes" in payload["tables"]
    assert "code_relations" in payload["tables"]
    assert "sessions" in payload["tables"]
    assert "session_events" in payload["tables"]
    assert "active_node_versions" in payload["views"]
    assert "authoritative_node_versions" in payload["views"]
    assert "candidate_node_versions" in payload["views"]
    assert "latest_node_runs" in payload["views"]
    assert "current_node_cursors" in payload["views"]
    assert "pending_dependency_nodes" in payload["views"]
    assert "latest_parent_child_authority" in payload["views"]
    assert "latest_subtask_attempts" in payload["views"]
    assert "active_primary_sessions" in payload["views"]
    assert "latest_validation_results" in payload["views"]
    assert "latest_review_results" in payload["views"]
    assert "latest_test_results" in payload["views"]
    assert "latest_documentation_outputs" in payload["views"]
    assert "latest_node_entity_changes" in payload["views"]
    assert "latest_code_relations" in payload["views"]


def test_db_current_revision_command(clean_public_schema, cli_runner) -> None:
    cli_runner(["admin", "db", "upgrade"])
    result = cli_runner(["admin", "db", "current-revision"])
    payload = result.json()

    assert result.exit_code == 0
    assert payload["alembic_revision"] == "0027_provenance_docs_audit_views"


def test_db_heads_history_and_schema_check_commands(clean_public_schema, cli_runner) -> None:
    heads_result = cli_runner(["admin", "db", "heads"])
    heads_payload = heads_result.json()
    assert heads_result.exit_code == 0
    assert heads_payload == {"heads": ["0027_provenance_docs_audit_views"]}

    history_result = cli_runner(["admin", "db", "history"])
    history_payload = history_result.json()
    assert history_result.exit_code == 0
    assert history_payload == {
        "revisions": [
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
        ]
    }

    before_result = cli_runner(["admin", "db", "check-schema"])
    before_payload = before_result.json()
    assert before_result.exit_code == 0
    assert before_payload["status"] == "uninitialized"
    assert before_payload["compatible"] is False

    assert cli_runner(["admin", "db", "upgrade"]).exit_code == 0
    after_result = cli_runner(["admin", "db", "check-schema"])
    after_payload = after_result.json()
    assert after_result.exit_code == 0
    assert after_payload["status"] == "up_to_date"
    assert after_payload["compatible"] is True


def test_db_downgrade_command_reaches_base(clean_public_schema, cli_runner) -> None:
    assert cli_runner(["admin", "db", "upgrade"]).exit_code == 0

    result = cli_runner(["admin", "db", "downgrade"])
    payload = result.json()

    assert result.exit_code == 0
    assert payload == {"revision": "base", "status": "ok"}

    revision_result = cli_runner(["admin", "db", "current-revision"])
    revision_payload = revision_result.json()
    assert revision_result.exit_code == 0
    assert revision_payload["alembic_revision"] is None


def test_debug_daemon_boundary_reports_transport_contract(cli_runner) -> None:
    result = cli_runner(["debug", "daemon", "boundary"])
    payload = result.json()

    assert result.exit_code == 0
    assert payload["boundary"] == "mutating_cli_commands_must_use_daemon"
