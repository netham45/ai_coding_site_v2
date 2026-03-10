from __future__ import annotations

from dataclasses import replace
from uuid import UUID

from aicoding.db.models import CompiledSubtask, Session as DurableSession
from aicoding.db.session import create_session_factory, session_scope
from aicoding.resources import load_resource_catalog


def test_session_bind_and_show_current_round_trip(cli_runner, daemon_bridge_client, monkeypatch, migrated_public_schema) -> None:
    monkeypatch.setenv("AICODING_SESSION_BACKEND", "fake")
    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: daemon_bridge_client)

    create_result = cli_runner(["node", "create", "--kind", "epic", "--title", "Session CLI", "--prompt", "boot prompt"])
    node_id = create_result.json()["node_id"]
    assert cli_runner(["workflow", "compile", "--node", node_id]).exit_code == 0
    assert cli_runner(["node", "lifecycle", "transition", "--node", node_id, "--state", "READY"]).exit_code == 0
    assert cli_runner(["node", "run", "start", "--node", node_id]).exit_code == 0

    bind_result = cli_runner(["session", "bind", "--node", node_id])
    bind_payload = bind_result.json()
    assert bind_result.exit_code == 0
    assert bind_payload["status"] == "bound"
    assert bind_payload["session_id"]

    current_result = cli_runner(["session", "show-current"])
    current_payload = current_result.json()
    assert current_result.exit_code == 0
    assert current_payload["status"] == "bound"
    assert current_payload["logical_node_id"] == node_id
    assert current_payload["node_kind"] == "epic"
    assert current_payload["node_title"] == "Session CLI"
    assert current_payload["run_status"] == "RUNNING"
    assert current_payload["recommended_action"] == "attach_existing_session"
    assert current_payload["session_name"].startswith("aicoding-pri-r1-")
    assert current_payload["screen_state"]["classification"] == "active"


def test_session_show_current_reports_stale_binding_for_bootstrap(
    cli_runner,
    daemon_bridge_client,
    monkeypatch,
    migrated_public_schema,
) -> None:
    monkeypatch.setenv("AICODING_SESSION_BACKEND", "fake")
    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: daemon_bridge_client)

    create_result = cli_runner(["node", "create", "--kind", "epic", "--title", "Stale CLI", "--prompt", "boot prompt"])
    node_id = create_result.json()["node_id"]
    assert cli_runner(["workflow", "compile", "--node", node_id]).exit_code == 0
    assert cli_runner(["node", "lifecycle", "transition", "--node", node_id, "--state", "READY"]).exit_code == 0
    assert cli_runner(["node", "run", "start", "--node", node_id]).exit_code == 0

    bind_result = cli_runner(["session", "bind", "--node", node_id])
    session_name = bind_result.json()["session_name"]
    daemon_bridge_client.client.app.state.session_adapter.advance_idle(session_name, seconds=30.0)

    current_result = cli_runner(["session", "show-current"])

    assert current_result.exit_code == 0
    assert current_result.json()["logical_node_id"] == node_id
    assert current_result.json()["recovery_classification"] == "stale_but_recoverable"
    assert current_result.json()["recommended_action"] == "resume_existing_session"


def test_session_attach_and_resume_commands_round_trip(cli_runner, daemon_bridge_client, monkeypatch, migrated_public_schema) -> None:
    monkeypatch.setenv("AICODING_SESSION_BACKEND", "fake")
    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: daemon_bridge_client)

    create_result = cli_runner(["node", "create", "--kind", "epic", "--title", "Attach CLI", "--prompt", "boot prompt"])
    node_id = create_result.json()["node_id"]
    assert cli_runner(["workflow", "compile", "--node", node_id]).exit_code == 0
    assert cli_runner(["node", "lifecycle", "transition", "--node", node_id, "--state", "READY"]).exit_code == 0
    assert cli_runner(["node", "run", "start", "--node", node_id]).exit_code == 0
    first_bind = cli_runner(["session", "bind", "--node", node_id])
    session_id = first_bind.json()["session_id"]

    attach_result = cli_runner(["session", "attach", "--node", node_id])
    attach_payload = attach_result.json()
    assert attach_result.exit_code == 0
    assert attach_payload["status"] == "attached"

    resume_result = cli_runner(["session", "resume", "--node", node_id])
    resume_payload = resume_result.json()
    assert resume_result.exit_code == 0
    assert resume_payload["status"] in {"reused_existing_session", "replacement_session_created"}
    assert resume_payload["session"]["status"] == "resumed"
    assert resume_payload["session"]["idle_seconds"] is not None

    show_result = cli_runner(["session", "show", "--node", node_id])
    events_result = cli_runner(["session", "events", "--session", session_id])
    list_result = cli_runner(["session", "list", "--node", node_id])
    recovery_result = cli_runner(["node", "recovery-status", "--node", node_id])

    assert show_result.exit_code == 0
    assert show_result.json()["session_id"] == session_id
    assert events_result.exit_code == 0
    assert [item["event_type"] for item in events_result.json()["events"]][:2] == ["bound", "attached"]
    assert "subtask prompt --node" in events_result.json()["events"][0]["payload_json"]["prompt_cli_command"]
    assert "prompt_logs" in events_result.json()["events"][0]["payload_json"]["prompt_log_path"]
    assert list_result.exit_code == 0
    assert len(list_result.json()["sessions"]) == 1
    assert recovery_result.exit_code == 0
    assert recovery_result.json()["recommended_action"] in {"attach_existing_session", "resume_existing_session"}


def test_session_provider_resume_and_provider_recovery_status_round_trip(
    cli_runner,
    daemon_bridge_client,
    monkeypatch,
    migrated_public_schema,
) -> None:
    monkeypatch.setenv("AICODING_SESSION_BACKEND", "fake")
    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: daemon_bridge_client)

    create_result = cli_runner(["node", "create", "--kind", "epic", "--title", "Provider CLI", "--prompt", "boot prompt"])
    node_id = create_result.json()["node_id"]
    assert cli_runner(["workflow", "compile", "--node", node_id]).exit_code == 0
    assert cli_runner(["node", "lifecycle", "transition", "--node", node_id, "--state", "READY"]).exit_code == 0
    assert cli_runner(["node", "run", "start", "--node", node_id]).exit_code == 0

    bind_result = cli_runner(["session", "bind", "--node", node_id])
    session_id = bind_result.json()["session_id"]
    provider_session_id = bind_result.json()["provider_session_id"]

    factory = create_session_factory(engine=migrated_public_schema)
    with session_scope(factory) as session:
        durable = session.get(DurableSession, UUID(session_id))
        assert durable is not None
        durable.tmux_session_name = "missing-session-name"

    provider_status_result = cli_runner(["node", "recovery-provider-status", "--node", node_id])
    provider_resume_result = cli_runner(["session", "provider-resume", "--node", node_id])
    show_result = cli_runner(["session", "show", "--node", node_id])

    assert provider_status_result.exit_code == 0
    assert provider_status_result.json()["provider_rebind_possible"] is True
    assert provider_status_result.json()["provider_recommended_action"] == "rebind_provider_session"
    assert provider_status_result.json()["provider_session_id"] == provider_session_id
    assert provider_resume_result.exit_code == 0
    assert provider_resume_result.json()["status"] == "provider_session_rebound"
    assert provider_resume_result.json()["session"]["session_id"] == session_id
    assert show_result.exit_code == 0
    assert show_result.json()["session_name"] == provider_session_id


def test_cli_subtask_prompt_and_context_include_stage_start_context(cli_runner, daemon_bridge_client, monkeypatch, migrated_public_schema) -> None:
    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: daemon_bridge_client)

    create_result = cli_runner(["workflow", "start", "--kind", "epic", "--prompt", "boot prompt"])
    payload = create_result.json()
    node_id = payload["node"]["node_id"]

    prompt_result = cli_runner(["subtask", "prompt", "--node", node_id])
    context_result = cli_runner(["subtask", "context", "--node", node_id])

    assert prompt_result.exit_code == 0
    assert prompt_result.json()["stage_context_json"]["startup"]["node_id"] == node_id
    assert prompt_result.json()["stage_context_json"]["startup"]["trigger_reason"] == "workflow_start"
    assert prompt_result.json()["prompt_text"]
    assert "boot prompt" in prompt_result.json()["prompt_text"]

    assert context_result.exit_code == 0
    assert context_result.json()["stage_context_json"]["startup"]["node_prompt"] == "boot prompt"
    assert context_result.json()["input_context_json"]["stage_context_json"]["stage"]["compiled_subtask_id"] == context_result.json()["compiled_subtask_id"]


def test_session_nudge_command_round_trip(cli_runner, daemon_bridge_client, monkeypatch, migrated_public_schema) -> None:
    monkeypatch.setenv("AICODING_SESSION_BACKEND", "fake")
    monkeypatch.setenv("AICODING_SESSION_IDLE_THRESHOLD_SECONDS", "5")
    monkeypatch.setenv("AICODING_SESSION_MAX_NUDGE_COUNT", "2")
    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: daemon_bridge_client)

    create_result = cli_runner(["node", "create", "--kind", "epic", "--title", "Nudge CLI", "--prompt", "boot prompt"])
    node_id = create_result.json()["node_id"]
    assert cli_runner(["workflow", "compile", "--node", node_id]).exit_code == 0
    assert cli_runner(["node", "lifecycle", "transition", "--node", node_id, "--state", "READY"]).exit_code == 0
    assert cli_runner(["node", "run", "start", "--node", node_id]).exit_code == 0
    bind_result = cli_runner(["session", "bind", "--node", node_id])
    session_name = bind_result.json()["session_name"]
    daemon_bridge_client.client.app.state.session_adapter.advance_idle(session_name, seconds=30.0)

    nudge_result = cli_runner(["session", "nudge", "--node", node_id])

    assert nudge_result.exit_code == 0
    assert nudge_result.json()["status"] == "nudged"
    assert nudge_result.json()["screen_state"]["classification"] == "idle"


def test_child_session_push_pop_and_result_cli_round_trip(cli_runner, daemon_bridge_client, monkeypatch, migrated_public_schema, tmp_path) -> None:
    monkeypatch.setenv("AICODING_SESSION_BACKEND", "fake")
    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: daemon_bridge_client)

    create_result = cli_runner(["node", "create", "--kind", "epic", "--title", "Child CLI", "--prompt", "boot prompt"])
    node_id = create_result.json()["node_id"]
    assert cli_runner(["workflow", "compile", "--node", node_id]).exit_code == 0
    assert cli_runner(["node", "lifecycle", "transition", "--node", node_id, "--state", "READY"]).exit_code == 0
    assert cli_runner(["node", "run", "start", "--node", node_id]).exit_code == 0
    assert cli_runner(["session", "bind", "--node", node_id]).exit_code == 0

    push_result = cli_runner(["session", "push", "--node", node_id, "--reason", "research_context"])
    child_session_id = push_result.json()["session_id"]
    result_file = tmp_path / "child-result.json"
    result_file.write_text(
        '{"status":"success","summary":"research done","findings":["one"],"artifacts":[{"path":"notes/research.md","type":"notes"}],"suggested_next_actions":["continue"]}',
        encoding="utf-8",
    )
    pop_result = cli_runner(["session", "pop", "--session", child_session_id, "--file", str(result_file)])
    show_result = cli_runner(["session", "result", "show", "--session", child_session_id])
    context_result = cli_runner(["subtask", "context", "--node", node_id])

    assert push_result.exit_code == 0
    assert push_result.json()["reason"] == "research_context"
    assert pop_result.exit_code == 0
    assert pop_result.json()["status"] == "success"
    assert show_result.exit_code == 0
    assert show_result.json()["summary"] == "research done"
    assert context_result.json()["input_context_json"]["child_session_results"][0]["child_session_id"] == child_session_id


def test_node_run_show_round_trip_uses_durable_daemon_state(cli_runner, daemon_bridge_client, migrated_public_schema, monkeypatch) -> None:
    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: daemon_bridge_client)

    create_result = cli_runner(["node", "create", "--kind", "epic", "--title", "Show Node", "--prompt", "boot prompt"])
    node_id = create_result.json()["node_id"]

    assert cli_runner(["workflow", "compile", "--node", node_id]).exit_code == 0
    assert cli_runner(["node", "lifecycle", "transition", "--node", node_id, "--state", "COMPILED"]).exit_code == 0
    assert cli_runner(["node", "lifecycle", "transition", "--node", node_id, "--state", "READY"]).exit_code == 0
    assert cli_runner(["node", "run", "start", "--node", node_id]).exit_code == 0
    show_result = cli_runner(["node", "run", "show", "--node", node_id])
    payload = show_result.json()

    assert show_result.exit_code == 0
    assert payload["run"]["logical_node_id"] == node_id
    assert payload["run"]["run_status"] == "RUNNING"
    assert payload["state"]["lifecycle_state"] == "RUNNING"


def test_operator_structure_and_state_commands_round_trip(cli_runner, migrated_public_schema, daemon_bridge_client, monkeypatch) -> None:
    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: daemon_bridge_client)

    create_result = cli_runner(["node", "create", "--kind", "epic", "--title", "Operator Root", "--prompt", "boot prompt"])
    node_id = create_result.json()["node_id"]
    child_result = cli_runner(
        ["node", "child", "create", "--parent", node_id, "--kind", "phase", "--title", "Child Phase", "--prompt", "child prompt"]
    )
    child_id = child_result.json()["node_id"]

    assert cli_runner(["workflow", "compile", "--node", node_id]).exit_code == 0
    assert cli_runner(["node", "lifecycle", "transition", "--node", node_id, "--state", "READY"]).exit_code == 0
    assert cli_runner(["node", "run", "start", "--node", node_id]).exit_code == 0

    tree_result = cli_runner(["tree", "show", "--node", node_id, "--full"])
    ancestors_result = cli_runner(["node", "ancestors", "--node", child_id, "--to-root"])
    children_result = cli_runner(["node", "children", "--node", node_id, "--versions"])
    task_list_result = cli_runner(["task", "list", "--node", node_id])
    task_current_result = cli_runner(["task", "current", "--node", node_id])
    subtask_list_result = cli_runner(["subtask", "list", "--node", node_id])

    assert tree_result.exit_code == 0
    assert tree_result.json()["full_view"] is True
    assert {item["node_id"] for item in tree_result.json()["nodes"]} >= {node_id, child_id}

    assert ancestors_result.exit_code == 0
    assert ancestors_result.json()["to_root"] is True
    assert ancestors_result.json()["ancestors"][-1]["node_id"] == node_id

    assert children_result.exit_code == 0
    assert children_result.json()["include_versions"] is True
    assert children_result.json()["children"][0]["node_id"] == child_id
    assert children_result.json()["children"][0]["authoritative_node_version_id"] is not None

    assert task_list_result.exit_code == 0
    assert task_list_result.json()["tasks"]
    assert any(item["is_current"] for item in task_list_result.json()["tasks"])

    assert task_current_result.exit_code == 0
    assert task_current_result.json()["current_task"] is not None

    assert subtask_list_result.exit_code == 0
    assert subtask_list_result.json()["subtasks"]
    assert any(item["is_current"] for item in subtask_list_result.json()["subtasks"])


def test_yaml_sources_command_uses_daemon_backed_node_lineage(cli_runner, migrated_public_schema, daemon_bridge_client, monkeypatch) -> None:
    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: daemon_bridge_client)

    create_result = cli_runner(["node", "create", "--kind", "epic", "--title", "YAML Sources", "--prompt", "boot prompt"])
    node_id = create_result.json()["node_id"]

    sources_result = cli_runner(["yaml", "sources", "--node", node_id])

    assert sources_result.exit_code == 0
    assert sources_result.json()["node_version_id"] is not None
    assert sources_result.json()["source_documents"]


def test_workflow_source_discovery_command_returns_deterministic_compile_inputs(
    cli_runner, migrated_public_schema, daemon_bridge_client, monkeypatch
) -> None:
    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: daemon_bridge_client)

    create_result = cli_runner(["node", "create", "--kind", "epic", "--title", "Source Discovery", "--prompt", "boot prompt"])
    node_id = create_result.json()["node_id"]
    assert cli_runner(["workflow", "compile", "--node", node_id]).exit_code == 0

    discovery_result = cli_runner(["workflow", "source-discovery", "--node", node_id])

    assert discovery_result.exit_code == 0
    assert discovery_result.json()["compiled_workflow_id"] is not None
    assert discovery_result.json()["discovery_order"]
    assert discovery_result.json()["resolved_documents"]
    assert discovery_result.json()["discovery_order"][0]["ordinal"] == 1


def test_workflow_schema_validation_command_returns_validated_inventory(
    cli_runner, migrated_public_schema, daemon_bridge_client, monkeypatch
) -> None:
    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: daemon_bridge_client)

    create_result = cli_runner(["node", "create", "--kind", "epic", "--title", "Schema Validation", "--prompt", "boot prompt"])
    node_id = create_result.json()["node_id"]
    assert cli_runner(["workflow", "compile", "--node", node_id]).exit_code == 0

    schema_result = cli_runner(["workflow", "schema-validation", "--node", node_id])

    assert schema_result.exit_code == 0
    assert schema_result.json()["validated_document_count"] > 0
    assert schema_result.json()["family_counts"]["node_definition"] >= 1
    assert schema_result.json()["validated_documents"][0]["doc_family"]


def test_workflow_override_resolution_command_returns_stage_payload(
    cli_runner, migrated_public_schema, daemon_bridge_client, monkeypatch
) -> None:
    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: daemon_bridge_client)

    create_result = cli_runner(["node", "create", "--kind", "epic", "--title", "Override Resolution", "--prompt", "boot prompt"])
    node_id = create_result.json()["node_id"]
    assert cli_runner(["workflow", "compile", "--node", node_id]).exit_code == 0

    override_result = cli_runner(["workflow", "override-resolution", "--node", node_id])

    assert override_result.exit_code == 0
    assert override_result.json()["resolved_document_count"] > 0
    assert "applied_overrides" in override_result.json()
    assert "warnings" in override_result.json()


def test_workflow_hook_policy_command_returns_stage_payload(
    cli_runner, migrated_public_schema, daemon_bridge_client, monkeypatch
) -> None:
    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: daemon_bridge_client)

    create_result = cli_runner(["node", "create", "--kind", "epic", "--title", "Hook Policy", "--prompt", "boot prompt"])
    node_id = create_result.json()["node_id"]
    assert cli_runner(["workflow", "compile", "--node", node_id]).exit_code == 0

    hook_policy_result = cli_runner(["workflow", "hook-policy", "--node", node_id])

    assert hook_policy_result.exit_code == 0
    assert hook_policy_result.json()["compiled_workflow_id"] is not None
    assert "effective_policy" in hook_policy_result.json()
    assert "policy_impact" in hook_policy_result.json()
    assert "selected_hooks" in hook_policy_result.json()
    assert "expanded_steps" in hook_policy_result.json()


def test_workflow_rendering_command_returns_frozen_payloads(
    cli_runner, migrated_public_schema, daemon_bridge_client, monkeypatch
) -> None:
    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: daemon_bridge_client)

    create_result = cli_runner(["node", "create", "--kind", "epic", "--title", "Rendering", "--prompt", "boot prompt"])
    node_id = create_result.json()["node_id"]
    assert cli_runner(["workflow", "compile", "--node", node_id]).exit_code == 0

    rendering_result = cli_runner(["workflow", "rendering", "--node", node_id])

    assert rendering_result.exit_code == 0
    assert rendering_result.json()["compiled_workflow_id"] is not None
    assert rendering_result.json()["compiled_subtask_count"] > 0
    assert rendering_result.json()["canonical_syntax"] == "{{variable}}"
    assert rendering_result.json()["compiled_subtasks"][0]["rendered_fields"]


def test_workflow_version_target_commands_support_candidate_compile_variants(
    cli_runner, migrated_public_schema, daemon_bridge_client, monkeypatch
) -> None:
    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: daemon_bridge_client)

    create_result = cli_runner(["node", "create", "--kind", "epic", "--title", "Candidate Variant", "--prompt", "boot prompt"])
    node_id = create_result.json()["node_id"]
    supersede_result = cli_runner(["node", "supersede", "--node", node_id, "--title", "Candidate Variant v2"])
    version_id = supersede_result.json()["id"]

    compile_result = cli_runner(["workflow", "compile", "--version", version_id])
    show_result = cli_runner(["workflow", "show", "--version", version_id])
    discovery_result = cli_runner(["workflow", "source-discovery", "--version", version_id])

    assert compile_result.exit_code == 0
    assert compile_result.json()["compile_context"]["compile_variant"] == "candidate"
    assert show_result.exit_code == 0
    assert show_result.json()["compile_context"]["compile_variant"] == "candidate"
    assert discovery_result.exit_code == 0
    assert discovery_result.json()["compile_context"]["compile_variant"] == "candidate"


def test_workflow_version_target_commands_support_rebuild_compile_variants(
    cli_runner, migrated_public_schema, daemon_bridge_client, monkeypatch
) -> None:
    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: daemon_bridge_client)

    create_result = cli_runner(["node", "create", "--kind", "epic", "--title", "Rebuild Variant", "--prompt", "boot prompt"])
    node_id = create_result.json()["node_id"]
    regenerate_result = cli_runner(["node", "regenerate", "--node", node_id])
    rebuild_version_id = regenerate_result.json()["created_candidate_version_ids"][0]

    compile_result = cli_runner(["workflow", "compile", "--version", rebuild_version_id])
    rendering_result = cli_runner(["workflow", "rendering", "--version", rebuild_version_id])
    failures_result = cli_runner(["workflow", "compile-failures", "--version", rebuild_version_id])

    assert compile_result.exit_code == 0
    assert compile_result.json()["compile_context"]["compile_variant"] == "rebuild_candidate"
    assert compile_result.json()["compile_context"]["rebuild_context"]["scope"] == "subtree"
    assert rendering_result.exit_code == 0
    assert rendering_result.json()["compile_context"]["compile_variant"] == "rebuild_candidate"
    assert failures_result.exit_code == 0
    assert failures_result.json()["failures"] == []


def test_cli_subtask_progress_and_workflow_advance_round_trip(cli_runner, daemon_bridge_client, migrated_public_schema, monkeypatch) -> None:
    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: daemon_bridge_client)

    create_result = cli_runner(["node", "create", "--kind", "epic", "--title", "Progress Node", "--prompt", "boot prompt"])
    node_id = create_result.json()["node_id"]

    assert cli_runner(["workflow", "compile", "--node", node_id]).exit_code == 0
    assert cli_runner(["node", "lifecycle", "transition", "--node", node_id, "--state", "READY"]).exit_code == 0
    assert cli_runner(["node", "run", "start", "--node", node_id]).exit_code == 0

    current_result = cli_runner(["subtask", "current", "--node", node_id])
    compiled_subtask_id = current_result.json()["state"]["current_compiled_subtask_id"]
    start_result = cli_runner(["subtask", "start", "--node", node_id, "--compiled-subtask", compiled_subtask_id])
    complete_result = cli_runner(
        ["subtask", "complete", "--node", node_id, "--compiled-subtask", compiled_subtask_id, "--summary", "done"]
    )
    advance_result = cli_runner(["workflow", "advance", "--node", node_id])

    assert current_result.exit_code == 0
    assert start_result.exit_code == 0
    assert start_result.json()["latest_attempt"]["status"] == "RUNNING"
    assert complete_result.exit_code == 0
    assert complete_result.json()["latest_attempt"]["status"] == "COMPLETE"
    assert advance_result.exit_code == 0


def test_cli_subtask_result_capture_and_attempt_reads_round_trip(
    cli_runner,
    daemon_bridge_client,
    migrated_public_schema,
    monkeypatch,
    tmp_path,
) -> None:
    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: daemon_bridge_client)

    create_result = cli_runner(["node", "create", "--kind", "epic", "--title", "Result Node", "--prompt", "boot prompt"])
    node_id = create_result.json()["node_id"]

    assert cli_runner(["workflow", "compile", "--node", node_id]).exit_code == 0
    assert cli_runner(["node", "lifecycle", "transition", "--node", node_id, "--state", "READY"]).exit_code == 0
    assert cli_runner(["node", "run", "start", "--node", node_id]).exit_code == 0

    current_result = cli_runner(["subtask", "current", "--node", node_id])
    compiled_subtask_id = current_result.json()["state"]["current_compiled_subtask_id"]
    assert cli_runner(["subtask", "start", "--node", node_id, "--compiled-subtask", compiled_subtask_id]).exit_code == 0

    result_file = tmp_path / "result.json"
    result_file.write_text('{"exit_code": 0, "stdout": "done"}', encoding="utf-8")
    complete_result = cli_runner(
        [
            "subtask",
            "complete",
            "--node",
            node_id,
            "--compiled-subtask",
            compiled_subtask_id,
            "--summary",
            "done",
            "--result-file",
            str(result_file),
        ]
    )
    attempts_result = cli_runner(["subtask", "attempts", "--node", node_id])
    attempt_id = complete_result.json()["latest_attempt"]["id"]
    attempt_show_result = cli_runner(["subtask", "attempt-show", "--attempt", attempt_id])

    assert complete_result.exit_code == 0
    assert complete_result.json()["latest_attempt"]["execution_result_json"] == {"exit_code": 0, "stdout": "done"}
    assert complete_result.json()["latest_attempt"]["output_json"]["exit_code"] == 0
    assert attempts_result.exit_code == 0
    assert attempts_result.json()["attempts"][0]["execution_result_json"] == {"exit_code": 0, "stdout": "done"}
    assert attempt_show_result.exit_code == 0
    assert attempt_show_result.json()["execution_result_json"] == {"exit_code": 0, "stdout": "done"}


def test_ai_facing_cli_prompt_context_heartbeat_and_summary_round_trip(
    cli_runner,
    daemon_bridge_client,
    migrated_public_schema,
    monkeypatch,
    tmp_path,
) -> None:
    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: daemon_bridge_client)

    create_result = cli_runner(["node", "create", "--kind", "epic", "--title", "AI CLI Node", "--prompt", "boot prompt"])
    node_id = create_result.json()["node_id"]

    assert cli_runner(["workflow", "compile", "--node", node_id]).exit_code == 0
    assert cli_runner(["node", "lifecycle", "transition", "--node", node_id, "--state", "READY"]).exit_code == 0
    assert cli_runner(["node", "run", "start", "--node", node_id]).exit_code == 0

    current_result = cli_runner(["subtask", "current", "--node", node_id])
    compiled_subtask_id = current_result.json()["state"]["current_compiled_subtask_id"]
    prompt_result = cli_runner(["subtask", "prompt", "--node", node_id])
    context_result = cli_runner(["subtask", "context", "--node", node_id])
    assert cli_runner(["subtask", "start", "--node", node_id, "--compiled-subtask", compiled_subtask_id]).exit_code == 0
    heartbeat_result = cli_runner(["subtask", "heartbeat", "--node", node_id, "--compiled-subtask", compiled_subtask_id])
    summary_file = tmp_path / "summary.md"
    summary_file.write_text("summary body", encoding="utf-8")
    summary_result = cli_runner(["summary", "register", "--node", node_id, "--file", str(summary_file), "--type", "subtask"])
    prompt_history_result = cli_runner(["prompts", "history", "--node", node_id])
    prompt_show_result = cli_runner(["prompts", "delivered-show", "--prompt", prompt_result.json()["prompt_id"]])
    summary_history_result = cli_runner(["summary", "history", "--node", node_id])
    summary_show_result = cli_runner(["summary", "show", "--summary", summary_result.json()["summary_id"]])
    pause_result = cli_runner(["workflow", "pause", "--node", node_id])
    resume_result = cli_runner(["workflow", "resume", "--node", node_id])

    assert prompt_result.exit_code == 0
    assert prompt_result.json()["compiled_subtask_id"] == compiled_subtask_id
    assert prompt_result.json()["prompt_id"]
    assert context_result.exit_code == 0
    assert context_result.json()["compiled_subtask_id"] == compiled_subtask_id
    assert heartbeat_result.exit_code == 0
    assert heartbeat_result.json()["latest_attempt"]["output_json"]["last_heartbeat_at"]
    assert summary_result.exit_code == 0
    assert summary_result.json()["summary_id"]
    assert summary_result.json()["summary_type"] == "subtask"
    assert prompt_history_result.exit_code == 0
    assert prompt_history_result.json()["prompts"][0]["id"] == prompt_result.json()["prompt_id"]
    assert prompt_show_result.exit_code == 0
    assert prompt_show_result.json()["id"] == prompt_result.json()["prompt_id"]
    assert summary_history_result.exit_code == 0
    assert summary_history_result.json()["summaries"][0]["id"] == summary_result.json()["summary_id"]
    assert summary_show_result.exit_code == 0
    assert summary_show_result.json()["id"] == summary_result.json()["summary_id"]
    assert pause_result.exit_code == 0
    assert pause_result.json()["current_state"] == "PAUSED_FOR_USER"
    assert resume_result.exit_code == 0


def test_cli_subtask_fail_accepts_summary_file(
    cli_runner,
    daemon_bridge_client,
    migrated_public_schema,
    monkeypatch,
    tmp_path,
) -> None:
    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: daemon_bridge_client)

    create_result = cli_runner(["node", "create", "--kind", "epic", "--title", "Fail File Node", "--prompt", "boot prompt"])
    node_id = create_result.json()["node_id"]

    assert cli_runner(["workflow", "compile", "--node", node_id]).exit_code == 0
    assert cli_runner(["node", "lifecycle", "transition", "--node", node_id, "--state", "READY"]).exit_code == 0
    assert cli_runner(["node", "run", "start", "--node", node_id]).exit_code == 0

    current_result = cli_runner(["subtask", "current", "--node", node_id])
    compiled_subtask_id = current_result.json()["state"]["current_compiled_subtask_id"]
    assert cli_runner(["subtask", "start", "--node", node_id, "--compiled-subtask", compiled_subtask_id]).exit_code == 0

    summary_file = tmp_path / "failure.md"
    summary_file.write_text("failure from file", encoding="utf-8")
    failed_result = cli_runner(
        ["subtask", "fail", "--node", node_id, "--compiled-subtask", compiled_subtask_id, "--summary-file", str(summary_file)]
    )

    assert failed_result.exit_code == 0
    assert failed_result.json()["run"]["run_status"] == "FAILED"
    assert failed_result.json()["latest_attempt"]["summary"] == "failure from file"


def test_cli_node_create_and_show_use_hierarchy_paths(cli_runner, daemon_bridge_client, migrated_public_schema, monkeypatch) -> None:
    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: daemon_bridge_client)

    create_result = cli_runner(["node", "create", "--kind", "epic", "--title", "CLI Epic", "--prompt", "top prompt"])
    create_payload = create_result.json()
    assert create_result.exit_code == 0
    assert create_payload["kind"] == "epic"


def test_cli_provenance_and_rationale_commands_round_trip(cli_runner, daemon_bridge_client, migrated_public_schema, monkeypatch, tmp_path) -> None:
    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: daemon_bridge_client)

    create_result = cli_runner(["node", "create", "--kind", "epic", "--title", "CLI Provenance", "--prompt", "track rationale"])
    node_id = create_result.json()["node_id"]
    assert cli_runner(["workflow", "compile", "--node", node_id]).exit_code == 0
    assert cli_runner(["node", "lifecycle", "transition", "--node", node_id, "--state", "READY"]).exit_code == 0
    assert cli_runner(["node", "run", "start", "--node", node_id]).exit_code == 0
    current_result = cli_runner(["subtask", "current", "--node", node_id])
    compiled_subtask_id = current_result.json()["state"]["current_compiled_subtask_id"]
    assert cli_runner(["subtask", "prompt", "--node", node_id]).exit_code == 0
    assert cli_runner(["subtask", "start", "--node", node_id, "--compiled-subtask", compiled_subtask_id]).exit_code == 0

    summary_file = tmp_path / "prov-summary.md"
    summary_file.write_text("implemented provenance plumbing", encoding="utf-8")
    assert cli_runner(["summary", "register", "--node", node_id, "--file", str(summary_file), "--type", "subtask"]).exit_code == 0

    refresh_result = cli_runner(["node", "provenance-refresh", "--node", node_id])
    rationale_result = cli_runner(["rationale", "show", "--node", node_id])
    entity_result = cli_runner(["entity", "show", "--name", "src.aicoding.daemon.app.create_app"])
    history_result = cli_runner(["entity", "history", "--name", "src.aicoding.daemon.app.create_app"])
    changed_by_result = cli_runner(["entity", "changed-by", "--name", "src.aicoding.daemon.app.create_app"])
    relations_result = cli_runner(["entity", "relations", "--name", "src.aicoding.daemon.app.create_app"])

    assert refresh_result.exit_code == 0
    assert refresh_result.json()["entity_count"] > 0
    assert rationale_result.exit_code == 0
    assert rationale_result.json()["entity_history"]
    assert entity_result.exit_code == 0
    assert entity_result.json()["entities"][0]["canonical_name"] == "src.aicoding.daemon.app.create_app"
    assert history_result.exit_code == 0
    assert history_result.json()["history"]
    assert changed_by_result.exit_code == 0
    assert changed_by_result.json()["history"]
    assert relations_result.exit_code == 0
    assert relations_result.json()["relations"]

    kinds_result = cli_runner(["node", "kinds"])
    kinds_payload = kinds_result.json()
    assert kinds_result.exit_code == 0
    assert "epic" in kinds_payload["top_level_kinds"]

    show_result = cli_runner(["node", "show", "--node", node_id])
    children_result = cli_runner(["node", "children", "--node", node_id])
    ancestors_result = cli_runner(["node", "ancestors", "--node", node_id])
    tree_result = cli_runner(["tree", "show", "--node", node_id])

    assert show_result.json()["title"] == "CLI Provenance"
    assert show_result.json()["lifecycle_state"] == "RUNNING"
    assert children_result.json() == {"children": []}
    assert ancestors_result.json() == {"ancestors": [], "to_root": False}
    assert tree_result.exit_code == 0
    assert tree_result.json()["nodes"][0]["title"] == "CLI Provenance"


def test_cli_docs_commands_round_trip(cli_runner, daemon_bridge_client, migrated_public_schema, monkeypatch) -> None:
    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: daemon_bridge_client)

    epic_id = cli_runner(["node", "create", "--kind", "epic", "--title", "Docs Epic", "--prompt", "root"]).json()["node_id"]
    phase_id = cli_runner(["node", "create", "--kind", "phase", "--title", "Docs Phase", "--prompt", "phase", "--parent", epic_id]).json()["node_id"]
    plan_id = cli_runner(["node", "create", "--kind", "plan", "--title", "Docs Plan", "--prompt", "plan", "--parent", phase_id]).json()["node_id"]
    task_id = cli_runner(["node", "create", "--kind", "task", "--title", "Docs Task", "--prompt", "task", "--parent", plan_id]).json()["node_id"]

    assert cli_runner(["workflow", "compile", "--node", task_id]).exit_code == 0
    assert cli_runner(["workflow", "compile", "--node", phase_id]).exit_code == 0

    build_node = cli_runner(["docs", "build-node-view", "--node", task_id])
    build_tree = cli_runner(["docs", "build-tree", "--node", phase_id])
    list_docs = cli_runner(["docs", "list", "--node", task_id])
    show_local = cli_runner(["docs", "show", "--node", task_id, "--scope", "local"])
    show_merged = cli_runner(["docs", "show", "--node", phase_id, "--scope", "merged"])

    assert build_node.exit_code == 0
    assert {item["scope"] for item in build_node.json()["documents"]} >= {"local", "custom"}
    assert build_tree.exit_code == 0
    assert {item["scope"] for item in build_tree.json()["documents"]} >= {"merged", "custom"}
    assert list_docs.exit_code == 0
    assert list_docs.json()["documents"]
    assert show_local.exit_code == 0
    assert "Docs Task" in show_local.json()["content"]
    assert show_merged.exit_code == 0
    assert "Docs Phase" in show_merged.json()["content"]


def test_cli_regenerate_and_rebuild_history_round_trip(cli_runner, daemon_bridge_client, migrated_public_schema, monkeypatch) -> None:
    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: daemon_bridge_client)

    root_result = cli_runner(["node", "create", "--kind", "epic", "--title", "Rebuild Root", "--prompt", "root prompt"])
    root_id = root_result.json()["node_id"]
    child_result = cli_runner(["node", "create", "--kind", "phase", "--title", "Rebuild Child", "--prompt", "child prompt", "--parent", root_id])
    child_id = child_result.json()["node_id"]

    regenerate_result = cli_runner(["node", "regenerate", "--node", root_id])
    rectify_result = cli_runner(["node", "rectify-upstream", "--node", child_id])
    history_result = cli_runner(["node", "rebuild-history", "--node", child_id])
    rebuild_show_result = cli_runner(["rebuild", "show", "--node", child_id])

    assert regenerate_result.exit_code == 0
    assert regenerate_result.json()["scope"] == "subtree"
    assert rectify_result.exit_code == 0
    assert rectify_result.json()["scope"] == "upstream"
    assert history_result.exit_code == 0
    assert {event["scope"] for event in history_result.json()["events"]} >= {"subtree", "upstream"}
    assert rebuild_show_result.exit_code == 0
    assert rebuild_show_result.json() == history_result.json()


def test_cli_rebuild_coordination_and_cutover_readiness_round_trip(
    cli_runner,
    daemon_bridge_client,
    db_session_factory,
    migrated_public_schema,
    monkeypatch,
) -> None:
    from aicoding.daemon.lifecycle import seed_node_lifecycle, transition_node_lifecycle
    from aicoding.daemon.orchestration import apply_authority_mutation

    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: daemon_bridge_client)

    create_result = cli_runner(["node", "create", "--kind", "epic", "--title", "CLI Coordination", "--prompt", "boot prompt"])
    node_id = create_result.json()["node_id"]
    supersede_result = cli_runner(["node", "supersede", "--node", node_id, "--title", "CLI Coordination v2"])
    candidate_version_id = supersede_result.json()["id"]

    seed_node_lifecycle(db_session_factory, node_id=node_id, initial_state="DRAFT")
    transition_node_lifecycle(db_session_factory, node_id=node_id, target_state="COMPILED")
    transition_node_lifecycle(db_session_factory, node_id=node_id, target_state="READY")
    apply_authority_mutation(db_session_factory, node_id=node_id, command="node.run.start")

    coordination_result = cli_runner(["node", "rebuild-coordination", "--node", node_id, "--scope", "subtree"])
    readiness_result = cli_runner(["node", "version", "cutover-readiness", "--version", candidate_version_id])

    assert coordination_result.exit_code == 0
    assert coordination_result.json()["status"] == "blocked"
    assert readiness_result.exit_code == 0
    assert readiness_result.json()["status"] == "blocked"
    assert any(item["blocker_type"] == "authoritative_active_run" for item in readiness_result.json()["blockers"])


def test_cli_node_and_run_audit_round_trip(cli_runner, daemon_bridge_client, migrated_public_schema, monkeypatch, tmp_path) -> None:
    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: daemon_bridge_client)

    create_result = cli_runner(["node", "create", "--kind", "epic", "--title", "Audit CLI", "--prompt", "boot prompt"])
    node_id = create_result.json()["node_id"]
    assert cli_runner(["workflow", "compile", "--node", node_id]).exit_code == 0
    assert cli_runner(["node", "lifecycle", "transition", "--node", node_id, "--state", "READY"]).exit_code == 0
    assert cli_runner(["node", "run", "start", "--node", node_id]).exit_code == 0

    current_result = cli_runner(["subtask", "current", "--node", node_id])
    compiled_subtask_id = current_result.json()["state"]["current_compiled_subtask_id"]
    prompt_result = cli_runner(["subtask", "prompt", "--node", node_id])
    assert cli_runner(["subtask", "start", "--node", node_id, "--compiled-subtask", compiled_subtask_id]).exit_code == 0
    summary_file = tmp_path / "audit-summary.md"
    summary_file.write_text("cli audit summary", encoding="utf-8")
    assert cli_runner(["summary", "register", "--node", node_id, "--type", "subtask", "--file", str(summary_file)]).exit_code == 0
    assert cli_runner(["subtask", "complete", "--node", node_id, "--compiled-subtask", compiled_subtask_id, "--summary", "done"]).exit_code == 0

    node_audit_result = cli_runner(["node", "audit", "--node", node_id])
    run_audit_by_node = cli_runner(["node", "run", "audit", "--node", node_id])
    run_id = run_audit_by_node.json()["node_run_id"]
    run_audit_by_run = cli_runner(["node", "run", "audit", "--run", run_id])

    assert node_audit_result.exit_code == 0
    assert node_audit_result.json()["run_count"] == 1
    assert node_audit_result.json()["prompt_history"]["prompts"][0]["id"] == prompt_result.json()["prompt_id"]
    assert node_audit_result.json()["source_lineage"]["source_documents"]
    assert run_audit_by_node.exit_code == 0
    assert run_audit_by_node.json()["attempts"][0]["status"] == "COMPLETE"
    assert run_audit_by_node.json()["prompts"][0]["id"] == prompt_result.json()["prompt_id"]
    assert run_audit_by_run.exit_code == 0
    assert run_audit_by_run.json() == run_audit_by_node.json()


def test_cli_environment_policy_and_attempt_environment_round_trip(cli_runner, daemon_bridge_client, migrated_public_schema, monkeypatch) -> None:
    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: daemon_bridge_client)

    policy_result = cli_runner(["environment", "policies"])
    assert policy_result.exit_code == 0
    assert any(item["policy_id"] == "local_default" for item in policy_result.json()["policies"])

    create_result = cli_runner(["node", "create", "--kind", "epic", "--title", "Environment CLI", "--prompt", "boot prompt"])
    node_id = create_result.json()["node_id"]
    assert cli_runner(["workflow", "compile", "--node", node_id]).exit_code == 0
    assert cli_runner(["node", "lifecycle", "transition", "--node", node_id, "--state", "READY"]).exit_code == 0
    assert cli_runner(["node", "run", "start", "--node", node_id]).exit_code == 0

    current_result = cli_runner(["subtask", "current", "--node", node_id])
    compiled_subtask_id = current_result.json()["state"]["current_compiled_subtask_id"]
    factory = create_session_factory(engine=migrated_public_schema)
    with session_scope(factory) as session:
        subtask = session.get(CompiledSubtask, compiled_subtask_id)
        assert subtask is not None
        subtask.environment_policy_ref = "environments/local_default.yaml"
        subtask.environment_request_json = {
            "policy_ref": "environments/local_default.yaml",
            "policy_id": "local_default",
            "isolation_mode": "none",
            "allow_network": True,
            "runtime_profile": None,
            "mandatory": False,
        }

    current_environment_result = cli_runner(["subtask", "environment", "--node", node_id])
    start_result = cli_runner(["subtask", "start", "--node", node_id, "--compiled-subtask", compiled_subtask_id])
    attempt_id = start_result.json()["latest_attempt"]["id"]
    attempt_environment_result = cli_runner(["environment", "show", "--attempt", attempt_id])

    assert current_environment_result.exit_code == 0
    assert current_environment_result.json()["environment_request"]["policy_id"] == "local_default"
    assert start_result.exit_code == 0
    assert start_result.json()["latest_attempt"]["execution_environment_json"]["launch_status"] == "active"
    assert attempt_environment_result.exit_code == 0
    assert attempt_environment_result.json()["execution_environment"]["resolved_mode"] == "none"


def test_cli_subtask_retry_and_node_cancel_round_trip(cli_runner, daemon_bridge_client, migrated_public_schema, monkeypatch) -> None:
    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: daemon_bridge_client)

    create_result = cli_runner(["node", "create", "--kind", "epic", "--title", "Retry CLI", "--prompt", "boot prompt"])
    node_id = create_result.json()["node_id"]
    assert cli_runner(["workflow", "compile", "--node", node_id]).exit_code == 0
    assert cli_runner(["node", "lifecycle", "transition", "--node", node_id, "--state", "READY"]).exit_code == 0
    assert cli_runner(["node", "run", "start", "--node", node_id]).exit_code == 0

    current_result = cli_runner(["subtask", "current", "--node", node_id])
    compiled_subtask_id = current_result.json()["state"]["current_compiled_subtask_id"]
    assert cli_runner(["subtask", "start", "--node", node_id, "--compiled-subtask", compiled_subtask_id]).exit_code == 0
    failed_result = cli_runner(["subtask", "fail", "--node", node_id, "--compiled-subtask", compiled_subtask_id, "--summary", "boom"])
    retry_result = cli_runner(["subtask", "retry", "--node", node_id])
    retry_attempt_id = retry_result.json()["latest_attempt"]["id"]
    retry_by_attempt_result = cli_runner(["subtask", "retry", "--attempt", retry_attempt_id])
    cancel_result = cli_runner(["node", "cancel", "--node", node_id])
    workflow_cancel_result = cli_runner(["workflow", "cancel", "--node", node_id])
    lifecycle_result = cli_runner(["node", "lifecycle", "show", "--node", node_id])

    assert failed_result.exit_code == 0
    assert failed_result.json()["run"]["run_status"] == "FAILED"
    assert retry_result.exit_code == 0
    assert retry_result.json()["latest_attempt"]["attempt_number"] == 2
    assert retry_result.json()["run"]["run_status"] == "RUNNING"
    assert retry_by_attempt_result.exit_code == 4
    assert retry_by_attempt_result.stderr_json()["error"] == "daemon_conflict"
    assert cancel_result.exit_code == 0
    assert cancel_result.json()["current_state"] == "CANCELLED"
    assert workflow_cancel_result.exit_code == 4
    assert workflow_cancel_result.stderr_json()["error"] == "not_found"
    assert lifecycle_result.exit_code == 0
    assert lifecycle_result.json()["lifecycle_state"] == "CANCELLED"


def test_cli_validation_show_and_results_round_trip(cli_runner, daemon_bridge_client, migrated_public_schema, monkeypatch) -> None:
    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: daemon_bridge_client)

    create_result = cli_runner(["node", "create", "--kind", "epic", "--title", "Validation CLI", "--prompt", "boot prompt"])
    node_id = create_result.json()["node_id"]
    assert cli_runner(["workflow", "compile", "--node", node_id]).exit_code == 0
    assert cli_runner(["node", "lifecycle", "transition", "--node", node_id, "--state", "READY"]).exit_code == 0
    assert cli_runner(["node", "run", "start", "--node", node_id]).exit_code == 0

    current_payload = cli_runner(["subtask", "current", "--node", node_id]).json()
    while not current_payload["current_subtask"]["source_subtask_key"].startswith("validate_node."):
        current_subtask = current_payload["state"]["current_compiled_subtask_id"]
        assert cli_runner(["subtask", "start", "--node", node_id, "--compiled-subtask", current_subtask]).exit_code == 0
        assert cli_runner(["subtask", "complete", "--node", node_id, "--compiled-subtask", current_subtask, "--summary", "done"]).exit_code == 0
        assert cli_runner(["workflow", "advance", "--node", node_id]).exit_code == 0
        current_payload = cli_runner(["subtask", "current", "--node", node_id]).json()

    validation_subtask = current_payload["state"]["current_compiled_subtask_id"]
    start_result = cli_runner(["subtask", "start", "--node", node_id, "--compiled-subtask", validation_subtask])
    complete_result = daemon_bridge_client.request(
        "POST",
        "/api/subtasks/complete",
        json_payload={"node_id": node_id, "compiled_subtask_id": validation_subtask, "output_json": {"exit_code": 0}, "summary": "validated"},
    )
    advance_result = cli_runner(["workflow", "advance", "--node", node_id])
    show_result = cli_runner(["validation", "show", "--node", node_id])
    results_result = cli_runner(["validation", "results", "--node", node_id])

    assert start_result.exit_code == 0
    assert complete_result["latest_attempt"]["output_json"]["exit_code"] == 0
    assert advance_result.exit_code == 0
    assert show_result.exit_code == 0
    assert show_result.json()["status"] == "passed"
    assert results_result.exit_code == 0
    assert results_result.json()["results"][0]["check_type"] == "command_exit_code"


def test_cli_review_run_show_and_results_round_trip(cli_runner, daemon_bridge_client, migrated_public_schema, monkeypatch, tmp_path) -> None:
    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: daemon_bridge_client)

    create_result = cli_runner(["node", "create", "--kind", "epic", "--title", "Review CLI", "--prompt", "boot prompt"])
    node_id = create_result.json()["node_id"]
    assert cli_runner(["workflow", "compile", "--node", node_id]).exit_code == 0
    assert cli_runner(["node", "lifecycle", "transition", "--node", node_id, "--state", "READY"]).exit_code == 0
    assert cli_runner(["node", "run", "start", "--node", node_id]).exit_code == 0

    current_payload = cli_runner(["subtask", "current", "--node", node_id]).json()
    while not current_payload["current_subtask"]["source_subtask_key"].startswith("review_node."):
        current_subtask = current_payload["state"]["current_compiled_subtask_id"]
        assert cli_runner(["subtask", "start", "--node", node_id, "--compiled-subtask", current_subtask]).exit_code == 0
        payload = {"exit_code": 0} if current_payload["current_subtask"]["source_subtask_key"].startswith("validate_node.") else None
        if payload is None:
            assert cli_runner(["subtask", "complete", "--node", node_id, "--compiled-subtask", current_subtask, "--summary", "done"]).exit_code == 0
        else:
            daemon_bridge_client.request(
                "POST",
                "/api/subtasks/complete",
                json_payload={"node_id": node_id, "compiled_subtask_id": current_subtask, "output_json": payload, "summary": "validated"},
            )
        assert cli_runner(["workflow", "advance", "--node", node_id]).exit_code == 0
        current_payload = cli_runner(["subtask", "current", "--node", node_id]).json()

    findings_path = tmp_path / "review_findings.json"
    findings_path.write_text('[{"message":"looks good"}]', encoding="utf-8")
    criteria_path = tmp_path / "review_criteria.json"
    criteria_path.write_text('[{"criterion":"Requirements are satisfied.","status":"passed"}]', encoding="utf-8")

    run_result = cli_runner(
        [
            "review",
            "run",
            "--node",
            node_id,
            "--status",
            "pass",
            "--summary",
            "approved",
            "--findings-file",
            str(findings_path),
            "--criteria-file",
            str(criteria_path),
        ]
    )
    show_result = cli_runner(["review", "show", "--node", node_id])
    results_result = cli_runner(["review", "results", "--node", node_id])

    assert run_result.exit_code == 0
    assert run_result.json()["run"]["run_status"] == "COMPLETE"
    assert show_result.exit_code == 0
    assert show_result.json()["status"] == "passed"
    assert show_result.json()["action"] == "continue"
    assert results_result.exit_code == 0
    assert results_result.json()["results"][0]["review_definition_id"] == "node_against_requirements"


def _testing_catalog(tmp_path):
    base_catalog = load_resource_catalog()
    project_root = tmp_path / "project"
    (project_root / "project-policies").mkdir(parents=True)
    (project_root / "testing").mkdir(parents=True)
    (project_root / "project-policies" / "default_project_policy.yaml").write_text(
        "\n".join(
            [
                "project_policy_definition:",
                "  id: default_project_policy",
                "  description: CLI testing fixture policy.",
                "  defaults:",
                "    auto_run_children: true",
                "    auto_merge_to_parent: false",
                "    auto_merge_to_base: false",
                "    require_review_before_finalize: true",
                "    require_testing_before_finalize: true",
                "    require_docs_before_finalize: false",
                "  runtime_policy_refs: []",
                "  hook_refs:",
                "    - hooks/default_hooks.yaml",
                "  review_refs: []",
                "  testing_refs:",
                "    - testing/custom_retry_gate.yaml",
                "  docs_refs: []",
                "  enabled_node_kinds: [epic, phase, plan, task]",
                "  prompt_pack: default",
                "  environment_profiles: []",
            ]
        ),
        encoding="utf-8",
    )
    (project_root / "testing" / "custom_retry_gate.yaml").write_text(
        "\n".join(
            [
                "kind: testing_definition",
                "id: custom_retry_gate",
                "name: Custom Retry Gate",
                "applies_to:",
                "  node_kinds: [epic, phase, plan, task]",
                "  task_ids: [test_node]",
                "  lifecycle_points: [after_task]",
                "scope: project_custom",
                "description: CLI durable test gate.",
                "commands:",
                "  - command: python3 -m pytest tests/unit -q",
                "    working_directory: .",
                "    env: {}",
                "retry_policy:",
                "  max_attempts: 2",
                "  rerun_failed_only: true",
                "pass_rules:",
                "  require_exit_code_zero: true",
                "  max_failed_tests: 0",
                "on_result:",
                "  pass_action: continue",
                "  fail_action: fail_to_parent",
            ]
        ),
        encoding="utf-8",
    )
    overrides_root = tmp_path / "overrides"
    (overrides_root / "nodes").mkdir(parents=True)
    (overrides_root / "nodes" / "epic_test_node.yaml").write_text(
        "\n".join(
            [
                "target_family: node_definition",
                "target_id: epic",
                "compatibility:",
                "  min_schema_version: 2",
                "  built_in_version: builtin-system-v1",
                "merge_mode: replace_list",
                "value:",
                "  available_tasks:",
                "    - research_context",
                "    - execute_node",
                "    - validate_node",
                "    - review_node",
                "    - test_node",
            ]
        ),
        encoding="utf-8",
    )
    return replace(
        base_catalog,
        yaml_project_dir=project_root,
        yaml_project_policies_dir=project_root / "project-policies",
        yaml_overrides_dir=overrides_root,
    )


def _pause_gate_catalog(tmp_path):
    base_catalog = load_resource_catalog()
    overrides_root = tmp_path / "overrides"
    (overrides_root / "nodes").mkdir(parents=True)
    (overrides_root / "nodes" / "epic_pause_gate.yaml").write_text(
        "\n".join(
            [
                "target_family: node_definition",
                "target_id: epic",
                "compatibility:",
                "  min_schema_version: 2",
                "  built_in_version: builtin-system-v1",
                "merge_mode: replace_list",
                "value:",
                "  available_tasks:",
                "    - research_context",
                "    - execute_node",
                "    - pause_for_user",
                "    - validate_node",
                "    - review_node",
            ]
        ),
        encoding="utf-8",
    )
    return replace(base_catalog, yaml_overrides_dir=overrides_root)


def test_cli_testing_run_show_and_results_round_trip(
    cli_runner,
    daemon_bridge_client,
    app_client,
    migrated_public_schema,
    monkeypatch,
    tmp_path,
) -> None:
    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: daemon_bridge_client)
    app_client.app.state.resource_catalog = _testing_catalog(tmp_path)

    create_result = cli_runner(["node", "create", "--kind", "epic", "--title", "Testing CLI", "--prompt", "boot prompt"])
    node_id = create_result.json()["node_id"]
    assert cli_runner(["workflow", "compile", "--node", node_id]).exit_code == 0
    assert cli_runner(["node", "lifecycle", "transition", "--node", node_id, "--state", "READY"]).exit_code == 0
    assert cli_runner(["node", "run", "start", "--node", node_id]).exit_code == 0

    current_payload = cli_runner(["subtask", "current", "--node", node_id]).json()
    while current_payload["current_subtask"]["subtask_type"] != "run_tests":
        current_subtask = current_payload["state"]["current_compiled_subtask_id"]
        assert cli_runner(["subtask", "start", "--node", node_id, "--compiled-subtask", current_subtask]).exit_code == 0
        if current_payload["current_subtask"]["subtask_type"] == "validate":
            payload = {"exit_code": 0}
        elif current_payload["current_subtask"]["subtask_type"] == "review":
            payload = {"status": "pass", "findings": [{"message": "ok"}], "criteria_results": [{"criterion": "ok", "status": "passed"}]}
        else:
            payload = None
        if payload is None:
            assert cli_runner(["subtask", "complete", "--node", node_id, "--compiled-subtask", current_subtask, "--summary", "done"]).exit_code == 0
        else:
            daemon_bridge_client.request(
                "POST",
                "/api/subtasks/complete",
                json_payload={"node_id": node_id, "compiled_subtask_id": current_subtask, "output_json": payload, "summary": "validated"},
            )
        assert cli_runner(["workflow", "advance", "--node", node_id]).exit_code == 0
        current_payload = cli_runner(["subtask", "current", "--node", node_id]).json()

    testing_subtask = current_payload["state"]["current_compiled_subtask_id"]
    start_result = cli_runner(["subtask", "start", "--node", node_id, "--compiled-subtask", testing_subtask])
    complete_result = daemon_bridge_client.request(
        "POST",
        "/api/subtasks/complete",
        json_payload={
            "node_id": node_id,
            "compiled_subtask_id": testing_subtask,
            "output_json": {
                "test_suites": [
                    {
                        "testing_definition_id": "default_unit_test_gate",
                        "suite_name": "Default Unit Test Gate",
                        "exit_code": 0,
                        "failed_tests": 0,
                        "summary": "unit tests passed",
                    },
                    {
                        "testing_definition_id": "default_integration_test_gate",
                        "suite_name": "Default Integration Test Gate",
                        "exit_code": 0,
                        "failed_tests": 0,
                        "summary": "integration tests passed",
                    },
                    {
                        "testing_definition_id": "custom_retry_gate",
                        "suite_name": "Custom Retry Gate",
                        "exit_code": 0,
                        "failed_tests": 0,
                        "summary": "tests passed",
                    }
                ]
            },
            "summary": "tests passed",
        },
    )
    run_result = cli_runner(["testing", "run", "--node", node_id])
    advance_result = cli_runner(["workflow", "advance", "--node", node_id])
    show_result = cli_runner(["testing", "show", "--node", node_id])
    results_result = cli_runner(["testing", "results", "--node", node_id])

    assert start_result.exit_code == 0
    assert complete_result["latest_attempt"]["summary"] == "tests passed"
    assert run_result.exit_code == 0
    assert run_result.json()["status"] == "passed"
    assert advance_result.exit_code == 0
    assert show_result.exit_code == 0
    assert show_result.json()["status"] == "passed"
    assert results_result.exit_code == 0
    assert {item["testing_definition_id"] for item in results_result.json()["results"]} >= {
        "default_unit_test_gate",
        "default_integration_test_gate",
        "custom_retry_gate",
    }


def test_cli_quality_chain_runs_turnkey_flow(
    cli_runner,
    daemon_bridge_client,
    app_client,
    migrated_public_schema,
    monkeypatch,
    tmp_path,
) -> None:
    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: daemon_bridge_client)
    app_client.app.state.resource_catalog = _testing_catalog(tmp_path)

    create_result = cli_runner(["node", "create", "--kind", "epic", "--title", "Quality Chain CLI", "--prompt", "boot prompt"])
    node_id = create_result.json()["node_id"]
    assert cli_runner(["workflow", "compile", "--node", node_id]).exit_code == 0
    assert cli_runner(["node", "lifecycle", "transition", "--node", node_id, "--state", "READY"]).exit_code == 0
    assert cli_runner(["node", "run", "start", "--node", node_id]).exit_code == 0

    current_payload = cli_runner(["subtask", "current", "--node", node_id]).json()
    while current_payload["current_subtask"]["subtask_type"] != "validate":
        current_subtask = current_payload["state"]["current_compiled_subtask_id"]
        assert cli_runner(["subtask", "start", "--node", node_id, "--compiled-subtask", current_subtask]).exit_code == 0
        assert cli_runner(["subtask", "complete", "--node", node_id, "--compiled-subtask", current_subtask, "--summary", "done"]).exit_code == 0
        assert cli_runner(["workflow", "advance", "--node", node_id]).exit_code == 0
        current_payload = cli_runner(["subtask", "current", "--node", node_id]).json()

    chain_result = cli_runner(["node", "quality-chain", "--node", node_id])
    validation_result = cli_runner(["validation", "show", "--node", node_id])
    review_result = cli_runner(["review", "show", "--node", node_id])
    testing_result = cli_runner(["testing", "show", "--node", node_id])
    docs_result = cli_runner(["docs", "list", "--node", node_id])
    summaries_result = cli_runner(["summary", "history", "--node", node_id])

    assert chain_result.exit_code == 0
    assert chain_result.json()["executed_stage_types"] == ["validate", "review", "run_tests"]
    assert chain_result.json()["run_status"] == "COMPLETE"
    assert chain_result.json()["provenance"]["entity_count"] > 0
    assert chain_result.json()["docs"]
    assert chain_result.json()["final_summary"]["summary_path"] == "summaries/final.md"
    assert validation_result.json()["status"] == "passed"
    assert review_result.json()["status"] == "passed"
    assert testing_result.json()["status"] == "passed"
    assert docs_result.json()["documents"]
    assert any(item["summary_type"] == "node" and item["summary_path"] == "summaries/final.md" for item in summaries_result.json()["summaries"])


def test_cli_pause_approval_and_resume_flow(
    cli_runner,
    daemon_bridge_client,
    app_client,
    migrated_public_schema,
    monkeypatch,
    tmp_path,
) -> None:
    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: daemon_bridge_client)
    app_client.app.state.resource_catalog = _pause_gate_catalog(tmp_path)

    create_result = cli_runner(["node", "create", "--kind", "epic", "--title", "Pause CLI", "--prompt", "boot prompt"])
    node_id = create_result.json()["node_id"]
    assert cli_runner(["workflow", "compile", "--node", node_id]).exit_code == 0
    assert cli_runner(["node", "lifecycle", "transition", "--node", node_id, "--state", "READY"]).exit_code == 0
    assert cli_runner(["node", "run", "start", "--node", node_id]).exit_code == 0

    progress = cli_runner(["node", "run", "show", "--node", node_id]).json()
    paused_result = None
    while progress["run"]["run_status"] == "RUNNING" and not progress["current_subtask"]["source_subtask_key"].startswith("pause_for_user."):
        compiled_subtask_id = progress["state"]["current_compiled_subtask_id"]
        assert cli_runner(["subtask", "start", "--node", node_id, "--compiled-subtask", compiled_subtask_id]).exit_code == 0
        assert cli_runner(["subtask", "complete", "--node", node_id, "--compiled-subtask", compiled_subtask_id]).exit_code == 0
        paused_result = cli_runner(["workflow", "advance", "--node", node_id])
        progress = cli_runner(["node", "run", "show", "--node", node_id]).json()

    assert paused_result is not None
    interventions_result = cli_runner(["node", "interventions", "--node", node_id])
    pause_state_result = cli_runner(["node", "pause-state", "--node", node_id])
    blocked_resume = cli_runner(["workflow", "resume", "--node", node_id])
    approve_result = cli_runner(
        [
            "node",
            "intervention-apply",
            "--node",
            node_id,
            "--kind",
            "pause_approval",
            "--action",
            "approve_pause",
            "--pause-flag",
            "user_guidance_required",
            "--summary",
            "approved",
        ]
    )
    approved_pause_state = cli_runner(["node", "pause-state", "--node", node_id])
    resume_result = cli_runner(["workflow", "resume", "--node", node_id])
    events_result = cli_runner(["node", "events", "--node", node_id])

    assert paused_result.exit_code == 0
    assert interventions_result.exit_code == 0
    assert any(item["kind"] == "pause_approval" for item in interventions_result.json()["interventions"])
    assert paused_result.json()["run"]["run_status"] == "PAUSED"
    assert pause_state_result.exit_code == 0
    assert pause_state_result.json()["pause_flag_name"] == "user_guidance_required"
    assert pause_state_result.json()["approval_required"] is True
    assert blocked_resume.exit_code == 4
    assert blocked_resume.stderr_json()["error"] == "daemon_conflict"
    assert "requires explicit approval" in blocked_resume.stderr_json()["details"]["response"]["detail"]
    assert approve_result.exit_code == 0
    assert approve_result.json()["result_json"]["approved"] is True
    assert approved_pause_state.json()["approved"] is True
    assert resume_result.exit_code == 0
    assert resume_result.json()["status"] == "accepted"
    assert [item["command"] for item in events_result.json()["events"] if item["event_scope"] == "pause"] == [
        "pause_entered",
        "pause_cleared",
        "pause_resumed",
    ]


def test_cli_child_materialization_round_trip(cli_runner, daemon_bridge_client, migrated_public_schema, monkeypatch) -> None:
    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: daemon_bridge_client)

    create_result = cli_runner(["node", "create", "--kind", "epic", "--title", "CLI Parent", "--prompt", "top prompt"])
    node_id = create_result.json()["node_id"]

    before_result = cli_runner(["node", "child-materialization", "--node", node_id])
    materialize_result = cli_runner(["node", "materialize-children", "--node", node_id])
    after_result = cli_runner(["node", "child-materialization", "--node", node_id])

    assert before_result.exit_code == 0
    assert before_result.json()["status"] == "not_materialized"
    assert materialize_result.exit_code == 0
    assert materialize_result.json()["status"] == "created"
    assert [item["layout_child_id"] for item in materialize_result.json()["children"]] == ["discovery", "implementation"]
    assert all("scheduling_reason" in item for item in materialize_result.json()["children"])
    assert all("blockers" in item for item in materialize_result.json()["children"])
    assert after_result.exit_code == 0
    assert after_result.json()["status"] == "materialized"


def test_cli_child_materialization_reports_dependency_blocked_children(cli_runner, daemon_bridge_client, migrated_public_schema, monkeypatch) -> None:
    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: daemon_bridge_client)

    create_result = cli_runner(["node", "create", "--kind", "epic", "--title", "CLI Blocked Parent", "--prompt", "top prompt"])
    node_id = create_result.json()["node_id"]
    materialize_result = cli_runner(["node", "materialize-children", "--node", node_id])
    children = materialize_result.json()["children"]
    implementation_child = next(item for item in children if item["layout_child_id"] == "implementation")
    tree_result = cli_runner(["tree", "show", "--node", node_id, "--full"])

    assert materialize_result.exit_code == 0
    assert implementation_child["scheduling_status"] == "blocked_on_dependency"
    assert implementation_child["scheduling_reason"] == "blocked_on_dependency"
    assert implementation_child["blockers"]
    implementation_tree_row = next(item for item in tree_result.json()["nodes"] if item["node_id"] == implementation_child["node_id"])
    assert implementation_tree_row["scheduling_status"] == "blocked"
    assert implementation_tree_row["blocker_count"] >= 1


def test_cli_manual_child_create_round_trip_updates_manual_authority(cli_runner, daemon_bridge_client, migrated_public_schema, monkeypatch) -> None:
    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: daemon_bridge_client)

    create_result = cli_runner(["node", "create", "--kind", "epic", "--title", "CLI Manual Parent", "--prompt", "top prompt"])
    parent_id = create_result.json()["node_id"]

    child_result = cli_runner(
        ["node", "child", "create", "--parent", parent_id, "--kind", "phase", "--title", "Manual Child", "--prompt", "child prompt"]
    )
    materialization_result = cli_runner(["node", "child-materialization", "--node", parent_id])

    assert child_result.exit_code == 0
    assert child_result.json()["parent_node_id"] == parent_id
    assert materialization_result.exit_code == 0
    assert materialization_result.json()["authority_mode"] == "manual"
    assert materialization_result.json()["status"] == "manual"


def test_cli_child_reconciliation_round_trip_preserves_manual_structure(cli_runner, daemon_bridge_client, migrated_public_schema, monkeypatch) -> None:
    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: daemon_bridge_client)

    create_result = cli_runner(["node", "create", "--kind", "epic", "--title", "CLI Hybrid Parent", "--prompt", "top prompt"])
    parent_id = create_result.json()["node_id"]

    materialize_result = cli_runner(["node", "materialize-children", "--node", parent_id])
    assert materialize_result.exit_code == 0

    child_result = cli_runner(
        ["node", "child", "create", "--parent", parent_id, "--kind", "phase", "--title", "Manual Child", "--prompt", "child prompt"]
    )
    assert child_result.exit_code == 0

    inspection_result = cli_runner(["node", "child-reconciliation", "--node", parent_id])
    reconcile_result = cli_runner(["node", "reconcile-children", "--node", parent_id, "--decision", "preserve_manual"])
    materialization_result = cli_runner(["node", "child-materialization", "--node", parent_id])

    assert inspection_result.exit_code == 0
    assert inspection_result.json()["authority_mode"] == "hybrid"
    assert inspection_result.json()["available_decisions"] == ["preserve_manual"]
    assert reconcile_result.exit_code == 0
    assert reconcile_result.json()["authority_mode"] == "manual"
    assert reconcile_result.json()["materialization_status"] == "manual"
    assert reconcile_result.json()["manual_child_count"] == 3
    assert reconcile_result.json()["layout_generated_child_count"] == 0
    assert materialization_result.exit_code == 0
    assert materialization_result.json()["authority_mode"] == "manual"
    assert materialization_result.json()["status"] == "manual"


def test_cli_child_results_and_reconcile_round_trip(cli_runner, daemon_bridge_client, migrated_public_schema, monkeypatch) -> None:
    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: daemon_bridge_client)

    parent_result = cli_runner(["node", "create", "--kind", "epic", "--title", "CLI Reconcile Parent", "--prompt", "boot prompt"])
    parent_id = parent_result.json()["node_id"]
    child_result = cli_runner(
        ["node", "child", "create", "--parent", parent_id, "--kind", "phase", "--title", "CLI Reconcile Child", "--prompt", "child prompt"]
    )
    child_id = child_result.json()["node_id"]
    parent_version_id = cli_runner(["node", "versions", "--node", parent_id]).json()["versions"][0]["id"]
    child_version_id = cli_runner(["node", "versions", "--node", child_id]).json()["versions"][0]["id"]

    assert cli_runner(["workflow", "compile", "--node", parent_id]).exit_code == 0
    assert cli_runner(["node", "lifecycle", "transition", "--node", parent_id, "--state", "READY"]).exit_code == 0
    assert cli_runner(["node", "run", "start", "--node", parent_id]).exit_code == 0
    assert cli_runner(["node", "lifecycle", "transition", "--node", child_id, "--state", "COMPILED"]).exit_code == 0
    assert cli_runner(["node", "lifecycle", "transition", "--node", child_id, "--state", "READY"]).exit_code == 0
    assert cli_runner(["node", "lifecycle", "transition", "--node", child_id, "--state", "RUNNING"]).exit_code == 0
    assert cli_runner(["node", "lifecycle", "transition", "--node", child_id, "--state", "COMPLETE"]).exit_code == 0

    from uuid import UUID

    from aicoding.daemon.live_git import bootstrap_live_git_repo, stage_live_git_change

    factory = daemon_bridge_client.client.app.state.db_session_factory
    bootstrap_live_git_repo(factory, version_id=UUID(parent_version_id), files={"shared.txt": "base\n"}, replace_existing=True)
    bootstrap_live_git_repo(factory, version_id=UUID(child_version_id), files={"shared.txt": "base\n"}, replace_existing=True)
    child_status = stage_live_git_change(
        factory,
        version_id=UUID(child_version_id),
        files={"shared.txt": "base\nchild change\n"},
        message="Child final",
        record_as_final=True,
    )

    child_results = cli_runner(["node", "child-results", "--node", parent_id])
    reconcile_result = cli_runner(["node", "reconcile", "--node", parent_id])
    merge_result = cli_runner(["git", "merge-children", "--node", parent_id])
    finalize_result = cli_runner(["git", "finalize-node", "--node", parent_id])
    status_result = cli_runner(["git", "status", "show", "--version", parent_version_id])

    assert child_results.exit_code == 0
    assert child_results.json()["status"] == "ready_for_reconcile"
    assert child_results.json()["children"][0]["final_commit_sha"] == child_status.final_commit_sha
    assert reconcile_result.exit_code == 0
    assert reconcile_result.json()["prompt_relative_path"] == "execution/reconcile_parent_after_merge.md"
    assert merge_result.exit_code == 0
    assert merge_result.json()["status"] == "merged"
    assert merge_result.json()["merge_events"][0]["child_final_commit_sha"] == child_status.final_commit_sha
    assert finalize_result.exit_code == 0
    assert finalize_result.json()["status"] == "finalized"
    assert status_result.exit_code == 0
    assert status_result.json()["working_tree_state"] == "finalized_clean"


def test_cli_merge_conflict_round_trip_blocks_then_allows_cutover(
    cli_runner,
    daemon_bridge_client,
    migrated_public_schema,
    monkeypatch,
) -> None:
    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: daemon_bridge_client)

    parent_result = cli_runner(["node", "create", "--kind", "epic", "--title", "CLI Conflict Parent", "--prompt", "boot prompt"])
    parent_id = parent_result.json()["node_id"]
    child_result = cli_runner(
        ["node", "child", "create", "--parent", parent_id, "--kind", "phase", "--title", "CLI Conflict Child", "--prompt", "child prompt"]
    )
    child_id = child_result.json()["node_id"]
    child_version_id = cli_runner(["node", "versions", "--node", child_id]).json()["versions"][0]["id"]
    candidate_result = cli_runner(["node", "supersede", "--node", parent_id, "--title", "CLI Conflict Parent v2"])
    candidate_version_id = candidate_result.json()["id"]

    record_result = cli_runner(
        [
            "git",
            "merge-conflicts",
            "record",
            "--parent-version",
            candidate_version_id,
            "--child-version",
            child_version_id,
            "--child-final-commit",
            "childfinal123",
            "--parent-before",
            "seed123",
            "--parent-after",
            "mergeattempt123",
            "--merge-order",
            "1",
            "--file",
            "src/conflicted.py",
        ]
    )
    conflicts_result = cli_runner(["git", "merge-conflicts", "show", "--node", parent_id])
    blocked_cutover = cli_runner(["node", "version", "cutover", "--version", candidate_version_id])
    resolve_result = cli_runner(
        [
            "git",
            "merge-conflicts",
            "resolve",
            "--conflict",
            record_result.json()["id"],
            "--summary",
            "Resolved manually.",
        ]
    )
    merge_events_result = cli_runner(["git", "merge-events", "show", "--node", parent_id])
    cutover_result = cli_runner(["node", "version", "cutover", "--version", candidate_version_id])

    assert record_result.exit_code == 0
    assert conflicts_result.exit_code == 0
    assert conflicts_result.json()["conflicts"][0]["resolution_status"] == "unresolved"
    assert blocked_cutover.exit_code == 4
    assert blocked_cutover.stderr_json()["error"] == "daemon_conflict"
    assert "unresolved merge conflicts" in blocked_cutover.stderr_json()["details"]["response"]["detail"]
    assert resolve_result.exit_code == 0
    assert merge_events_result.exit_code == 0
    assert merge_events_result.json()["events"][0]["had_conflict"] is True
    assert cutover_result.exit_code == 0


def test_operator_pause_state_and_events_round_trip(cli_runner, daemon_bridge_client, migrated_public_schema, monkeypatch) -> None:
    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: daemon_bridge_client)

    create_result = cli_runner(["node", "create", "--kind", "epic", "--title", "Ops Node", "--prompt", "boot prompt"])
    node_id = create_result.json()["node_id"]

    assert cli_runner(["workflow", "compile", "--node", node_id]).exit_code == 0
    assert cli_runner(["node", "lifecycle", "transition", "--node", node_id, "--state", "READY"]).exit_code == 0
    assert cli_runner(["node", "run", "start", "--node", node_id]).exit_code == 0
    assert cli_runner(["node", "pause", "--node", node_id]).exit_code == 0

    pause_state_result = cli_runner(["node", "pause-state", "--node", node_id])
    events_result = cli_runner(["node", "events", "--node", node_id])

    assert pause_state_result.exit_code == 0
    assert pause_state_result.json()["pause_flag_name"] == "manual_pause"
    assert pause_state_result.json()["approval_required"] is False
    assert events_result.exit_code == 0
    assert {item["command"] for item in events_result.json()["events"]} >= {"node.run.start", "node.pause", "pause_entered"}
