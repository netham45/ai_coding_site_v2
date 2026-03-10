from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from aicoding.daemon.app import create_app
from aicoding.daemon.admission import admit_node_run
from aicoding.daemon.branches import record_final_commit, record_seed_commit
from aicoding.daemon.errors import DaemonUnavailableError
from aicoding.daemon.hierarchy import create_hierarchy_node
from aicoding.daemon.lifecycle import seed_node_lifecycle, transition_node_lifecycle
from aicoding.daemon.manual_tree import create_manual_node
from aicoding.daemon.versioning import initialize_node_version
from aicoding.daemon.workflows import compile_node_workflow
from aicoding.db.models import CompiledSubtask, NodeRunState, Session as DurableSession
from aicoding.db.session import create_session_factory, session_scope
from aicoding.hierarchy import load_hierarchy_registry
from aicoding.resources import load_resource_catalog


def _transition_to_complete(db_session_factory, *, node_id: str) -> None:
    transition_node_lifecycle(db_session_factory, node_id=node_id, target_state="COMPILED")
    transition_node_lifecycle(db_session_factory, node_id=node_id, target_state="READY")
    transition_node_lifecycle(db_session_factory, node_id=node_id, target_state="RUNNING")
    transition_node_lifecycle(db_session_factory, node_id=node_id, target_state="COMPLETE")


def test_healthcheck_is_public(app_client) -> None:
    response = app_client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_bootstrap_endpoint_requires_bearer_token(app_client) -> None:
    response = app_client.get("/bootstrap")

    assert response.status_code == 401


def test_bootstrap_endpoint_returns_status_with_valid_token(app_client) -> None:
    response = app_client.get("/bootstrap", headers={"Authorization": "Bearer change-me"})

    assert response.status_code == 200
    assert response.json()["missing_directories"] == []


def test_daemon_startup_creates_token_file_and_reports_auth_context(tmp_path, monkeypatch) -> None:
    token_file = tmp_path / ".runtime" / "daemon.token"
    monkeypatch.setenv("AICODING_AUTH_TOKEN_FILE", str(token_file))
    monkeypatch.setenv("AICODING_AUTH_TOKEN", "startup-token")

    with TestClient(create_app()) as client:
        response = client.get("/foundation", headers={"Authorization": "Bearer startup-token"})

    assert token_file.exists()
    assert response.status_code == 200
    payload = response.json()
    assert payload["auth_token_file"] == str(token_file)
    assert payload["auth_token_source"] == "settings"


def test_generated_startup_token_file_can_authenticate_requests(tmp_path, monkeypatch) -> None:
    token_file = tmp_path / ".runtime" / "daemon.token"
    monkeypatch.setenv("AICODING_AUTH_TOKEN_FILE", str(token_file))
    monkeypatch.setenv("AICODING_AUTH_TOKEN", "   ")

    with TestClient(create_app()) as client:
        generated_token = token_file.read_text(encoding="utf-8").strip()
        response = client.get("/bootstrap", headers={"Authorization": f"Bearer {generated_token}"})

    assert response.status_code == 200
    assert generated_token


def test_invalid_bearer_token_is_rejected(app_client) -> None:
    response = app_client.get("/bootstrap", headers={"Authorization": "Bearer wrong-token"})

    assert response.status_code == 401
    assert response.json()["detail"] == "invalid bearer token"


def test_db_healthcheck_returns_database_status(app_client, clean_public_schema) -> None:
    response = app_client.get("/db/healthz", headers={"Authorization": "Bearer change-me"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["database_name"] == "aicoding"
    assert payload["current_user"] == "aicoding"


def test_db_schema_compatibility_reports_revision_state(app_client, clean_public_schema) -> None:
    response = app_client.get("/db/schema-compatibility", headers={"Authorization": "Bearer change-me"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["expected_revision"] == "0027_provenance_docs_audit_views"
    assert payload["status"] == "uninitialized"
    assert payload["compatible"] is False


def test_daemon_status_reports_background_tasks(app_client) -> None:
    response = app_client.get("/status", headers={"Authorization": "Bearer change-me"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["authority"] == "daemon"
    assert "session_recovery" in payload["background_tasks"]
    assert payload["write_probe"]["write_path"] == "available"
    assert payload["schema_compatibility"]["expected_revision"] == "0027_provenance_docs_audit_views"


def test_mutation_endpoint_accepts_valid_payload(app_client, migrated_public_schema) -> None:
    create_response = app_client.post(
        "/api/nodes/create",
        headers={"Authorization": "Bearer change-me"},
        json={"kind": "epic", "title": "Runnable", "prompt": "boot prompt"},
    )
    node_id = create_response.json()["node_id"]
    app_client.post(f"/api/nodes/{node_id}/workflow/compile", headers={"Authorization": "Bearer change-me"}, json={})
    app_client.post(
        "/api/nodes/lifecycle/transition",
        headers={"Authorization": "Bearer change-me"},
        json={"node_id": node_id, "target_state": "READY"},
    )
    response = app_client.post(
        "/api/node-runs/start",
        headers={"Authorization": "Bearer change-me"},
        json={"node_id": node_id},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["node_id"] == node_id
    assert payload["status"] == "admitted"
    assert payload["current_state"] == "RUNNING"
    assert payload["current_run_id"]
    assert payload["reason"] is None


def test_node_run_show_returns_durable_authority_state(app_client, migrated_public_schema) -> None:
    create_response = app_client.post(
        "/api/nodes/create",
        headers={"Authorization": "Bearer change-me"},
        json={"kind": "epic", "title": "Runnable", "prompt": "boot prompt"},
    )
    node_id = create_response.json()["node_id"]
    app_client.post(f"/api/nodes/{node_id}/workflow/compile", headers={"Authorization": "Bearer change-me"}, json={})
    app_client.post(
        "/api/nodes/lifecycle/transition",
        headers={"Authorization": "Bearer change-me"},
        json={"node_id": node_id, "target_state": "READY"},
    )
    start_response = app_client.post(
        "/api/node-runs/start",
        headers={"Authorization": "Bearer change-me"},
        json={"node_id": node_id},
    )
    run_id = start_response.json()["current_run_id"]

    response = app_client.get(f"/api/node-runs/{node_id}", headers={"Authorization": "Bearer change-me"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["run"]["logical_node_id"] == node_id
    assert payload["run"]["id"] == run_id
    assert payload["run"]["run_status"] == "RUNNING"
    assert payload["state"]["lifecycle_state"] == "RUNNING"
    assert payload["current_subtask"]["id"] == payload["state"]["current_compiled_subtask_id"]


def test_subtask_progress_and_workflow_advance_endpoints_work(app_client, migrated_public_schema) -> None:
    create_response = app_client.post(
        "/api/nodes/create",
        headers={"Authorization": "Bearer change-me"},
        json={"kind": "epic", "title": "Runnable", "prompt": "boot prompt"},
    )
    node_id = create_response.json()["node_id"]
    app_client.post(f"/api/nodes/{node_id}/workflow/compile", headers={"Authorization": "Bearer change-me"}, json={})
    app_client.post("/api/nodes/lifecycle/transition", headers={"Authorization": "Bearer change-me"}, json={"node_id": node_id, "target_state": "READY"})
    start_response = app_client.post("/api/node-runs/start", headers={"Authorization": "Bearer change-me"}, json={"node_id": node_id})
    current_subtask_id = app_client.get(f"/api/nodes/{node_id}/subtasks/current", headers={"Authorization": "Bearer change-me"}).json()["state"]["current_compiled_subtask_id"]

    subtask_start = app_client.post(
        "/api/subtasks/start",
        headers={"Authorization": "Bearer change-me"},
        json={"node_id": node_id, "compiled_subtask_id": current_subtask_id},
    )
    subtask_complete = app_client.post(
        "/api/subtasks/complete",
        headers={"Authorization": "Bearer change-me"},
        json={"node_id": node_id, "compiled_subtask_id": current_subtask_id, "summary": "done"},
    )
    advance = app_client.post(f"/api/nodes/{node_id}/workflow/advance", headers={"Authorization": "Bearer change-me"})

    assert start_response.status_code == 200
    assert subtask_start.status_code == 200
    assert subtask_start.json()["latest_attempt"]["status"] == "RUNNING"
    assert subtask_complete.status_code == 200
    assert subtask_complete.json()["latest_attempt"]["status"] == "COMPLETE"
    assert advance.status_code == 200

    chain_response = app_client.get(f"/api/nodes/{node_id}/workflow/chain", headers={"Authorization": "Bearer change-me"})
    assert chain_response.status_code == 200
    assert chain_response.json()["chain"][0]["derived_execution_state"] == "complete"


def test_subtask_retry_and_node_cancel_endpoints_work(app_client, migrated_public_schema) -> None:
    create_response = app_client.post(
        "/api/nodes/create",
        headers={"Authorization": "Bearer change-me"},
        json={"kind": "epic", "title": "Retryable", "prompt": "boot prompt"},
    )
    node_id = create_response.json()["node_id"]
    app_client.post(f"/api/nodes/{node_id}/workflow/compile", headers={"Authorization": "Bearer change-me"}, json={})
    app_client.post("/api/nodes/lifecycle/transition", headers={"Authorization": "Bearer change-me"}, json={"node_id": node_id, "target_state": "READY"})
    app_client.post("/api/node-runs/start", headers={"Authorization": "Bearer change-me"}, json={"node_id": node_id})
    current_subtask_id = app_client.get(f"/api/nodes/{node_id}/subtasks/current", headers={"Authorization": "Bearer change-me"}).json()["state"]["current_compiled_subtask_id"]

    started = app_client.post(
        "/api/subtasks/start",
        headers={"Authorization": "Bearer change-me"},
        json={"node_id": node_id, "compiled_subtask_id": current_subtask_id},
    )
    failed = app_client.post(
        "/api/subtasks/fail",
        headers={"Authorization": "Bearer change-me"},
        json={"node_id": node_id, "compiled_subtask_id": current_subtask_id, "summary": "boom"},
    )
    retry = app_client.post(f"/api/nodes/{node_id}/subtasks/retry", headers={"Authorization": "Bearer change-me"})
    retry_by_attempt = app_client.post(
        f"/api/subtask-attempts/{retry.json()['latest_attempt']['id']}/retry",
        headers={"Authorization": "Bearer change-me"},
    )
    cancel = app_client.post("/api/nodes/cancel", headers={"Authorization": "Bearer change-me"}, json={"node_id": node_id})
    lifecycle = app_client.get(f"/api/nodes/{node_id}/lifecycle", headers={"Authorization": "Bearer change-me"})
    events = app_client.get(f"/api/nodes/{node_id}/events", headers={"Authorization": "Bearer change-me"})

    assert started.status_code == 200
    assert failed.status_code == 200
    assert failed.json()["run"]["run_status"] == "FAILED"
    assert retry.status_code == 200
    assert retry.json()["run"]["run_status"] == "RUNNING"
    assert retry.json()["latest_attempt"]["attempt_number"] == 2
    assert retry_by_attempt.status_code == 409
    assert cancel.status_code == 200
    assert cancel.json()["current_state"] == "CANCELLED"
    assert lifecycle.status_code == 200
    assert lifecycle.json()["lifecycle_state"] == "CANCELLED"


def test_node_and_run_audit_endpoints_return_reconstructible_history(app_client, migrated_public_schema) -> None:
    create_response = app_client.post(
        "/api/nodes/create",
        headers={"Authorization": "Bearer change-me"},
        json={"kind": "epic", "title": "Audit Daemon", "prompt": "boot prompt"},
    )
    node_id = create_response.json()["node_id"]
    app_client.post(f"/api/nodes/{node_id}/workflow/compile", headers={"Authorization": "Bearer change-me"})
    app_client.post(
        "/api/nodes/lifecycle/transition",
        headers={"Authorization": "Bearer change-me"},
        json={"node_id": node_id, "target_state": "READY"},
    )
    app_client.post("/api/node-runs/start", headers={"Authorization": "Bearer change-me"}, json={"node_id": node_id})

    progress = app_client.get(f"/api/node-runs/{node_id}", headers={"Authorization": "Bearer change-me"}).json()
    current_subtask_id = progress["state"]["current_compiled_subtask_id"]
    prompt_response = app_client.get(f"/api/nodes/{node_id}/subtasks/current/prompt", headers={"Authorization": "Bearer change-me"})
    app_client.post(
        "/api/subtasks/start",
        headers={"Authorization": "Bearer change-me"},
        json={"node_id": node_id, "compiled_subtask_id": current_subtask_id},
    )
    app_client.post(
        "/api/summaries/register",
        headers={"Authorization": "Bearer change-me"},
        json={"node_id": node_id, "summary_type": "subtask", "summary_path": "notes/audit.md", "content": "audit summary"},
    )
    app_client.post(
        "/api/subtasks/complete",
        headers={"Authorization": "Bearer change-me"},
        json={"node_id": node_id, "compiled_subtask_id": current_subtask_id, "summary": "done"},
    )

    node_audit = app_client.get(f"/api/nodes/{node_id}/audit", headers={"Authorization": "Bearer change-me"})
    run_audit = app_client.get(f"/api/nodes/{node_id}/runs/latest-audit", headers={"Authorization": "Bearer change-me"})

    assert node_audit.status_code == 200
    assert run_audit.status_code == 200
    assert node_audit.json()["run_count"] == 1
    assert node_audit.json()["prompt_history"]["prompts"][0]["id"] == prompt_response.json()["prompt_id"]
    assert node_audit.json()["source_lineage"]["source_documents"]
    assert run_audit.json()["attempts"][0]["status"] == "COMPLETE"
    assert run_audit.json()["attempts"][0]["execution_environment_json"]["launch_status"] == "active"
    assert run_audit.json()["attempts"][0]["execution_environment_json"]["resolved_mode"] == "none"
    assert run_audit.json()["prompts"][0]["id"] == prompt_response.json()["prompt_id"]
    assert run_audit.json()["summaries"]


def test_environment_policy_and_attempt_environment_endpoints_work(app_client, migrated_public_schema) -> None:
    policy_response = app_client.get("/api/policies/environments", headers={"Authorization": "Bearer change-me"})
    assert policy_response.status_code == 200
    assert any(item["policy_id"] == "local_default" for item in policy_response.json()["policies"])

    create_response = app_client.post(
        "/api/nodes/create",
        headers={"Authorization": "Bearer change-me"},
        json={"kind": "epic", "title": "Environment Daemon", "prompt": "boot prompt"},
    )
    node_id = create_response.json()["node_id"]
    app_client.post(f"/api/nodes/{node_id}/workflow/compile", headers={"Authorization": "Bearer change-me"})
    app_client.post(
        "/api/nodes/lifecycle/transition",
        headers={"Authorization": "Bearer change-me"},
        json={"node_id": node_id, "target_state": "READY"},
    )
    app_client.post("/api/node-runs/start", headers={"Authorization": "Bearer change-me"}, json={"node_id": node_id})

    progress = app_client.get(f"/api/node-runs/{node_id}", headers={"Authorization": "Bearer change-me"}).json()
    current_subtask_id = progress["state"]["current_compiled_subtask_id"]
    factory = create_session_factory(engine=migrated_public_schema)
    with session_scope(factory) as session:
        subtask = session.get(CompiledSubtask, current_subtask_id)
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

    current_environment = app_client.get(
        f"/api/nodes/{node_id}/subtasks/current/environment",
        headers={"Authorization": "Bearer change-me"},
    )
    start_response = app_client.post(
        "/api/subtasks/start",
        headers={"Authorization": "Bearer change-me"},
        json={"node_id": node_id, "compiled_subtask_id": current_subtask_id},
    )
    attempt_id = start_response.json()["latest_attempt"]["id"]
    attempt_environment = app_client.get(
        f"/api/subtask-attempts/{attempt_id}/environment",
        headers={"Authorization": "Bearer change-me"},
    )

    assert current_environment.status_code == 200
    assert current_environment.json()["environment_request"]["policy_id"] == "local_default"
    assert start_response.status_code == 200
    assert start_response.json()["latest_attempt"]["execution_environment_json"]["launch_status"] == "active"
    assert attempt_environment.status_code == 200
    assert attempt_environment.json()["execution_environment"]["resolved_mode"] == "none"


def test_parent_failure_endpoints_report_counters_and_decisions(app_client, migrated_public_schema) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    factory = create_session_factory(engine=migrated_public_schema)

    parent = create_hierarchy_node(factory, registry, kind="epic", title="Parent", prompt="boot prompt")
    seed_node_lifecycle(factory, node_id=str(parent.node_id), initial_state="DRAFT")
    initialize_node_version(factory, logical_node_id=parent.node_id)
    compile_node_workflow(factory, logical_node_id=parent.node_id, catalog=catalog)
    transition_node_lifecycle(factory, node_id=str(parent.node_id), target_state="READY")
    admit_node_run(factory, node_id=parent.node_id)

    child = create_manual_node(factory, registry, kind="phase", title="Child", prompt="child prompt", parent_node_id=parent.node_id)
    compile_node_workflow(factory, logical_node_id=child.node.node_id, catalog=catalog)
    transition_node_lifecycle(factory, node_id=str(child.node.node_id), target_state="READY")
    admit_node_run(factory, node_id=child.node.node_id)
    current_subtask_id = app_client.get(
        f"/api/nodes/{child.node.node_id}/subtasks/current",
        headers={"Authorization": "Bearer change-me"},
    ).json()["state"]["current_compiled_subtask_id"]
    app_client.post(
        "/api/subtasks/start",
        headers={"Authorization": "Bearer change-me"},
        json={"node_id": str(child.node.node_id), "compiled_subtask_id": current_subtask_id},
    )
    app_client.post(
        "/api/subtasks/fail",
        headers={"Authorization": "Bearer change-me"},
        json={
            "node_id": str(child.node.node_id),
            "compiled_subtask_id": current_subtask_id,
            "summary": "environment timeout while running tool",
        },
    )

    respond = app_client.post(
        "/api/nodes/respond-to-child-failure",
        headers={"Authorization": "Bearer change-me"},
        json={"node_id": str(parent.node_id), "child_node_id": str(child.node.node_id), "requested_action": "retry_child"},
    )
    counters = app_client.get(
        f"/api/nodes/{parent.node_id}/child-failures",
        headers={"Authorization": "Bearer change-me"},
    )
    decisions = app_client.get(
        f"/api/nodes/{parent.node_id}/decision-history",
        headers={"Authorization": "Bearer change-me"},
    )

    assert respond.status_code == 200
    assert respond.json()["decision_type"] == "retry_child"
    assert counters.status_code == 200
    assert counters.json()["failure_count_from_children"] == 1
    assert counters.json()["counters"][0]["last_decision_type"] == "retry_child"
    assert decisions.status_code == 200
    assert decisions.json()["decisions"][-1]["decision_type"] == "parent_retry_child"


def test_ai_facing_prompt_context_heartbeat_and_summary_endpoints_work(app_client, migrated_public_schema, tmp_path) -> None:
    create_response = app_client.post(
        "/api/nodes/create",
        headers={"Authorization": "Bearer change-me"},
        json={"kind": "epic", "title": "Runnable", "prompt": "boot prompt"},
    )
    node_id = create_response.json()["node_id"]
    app_client.post(f"/api/nodes/{node_id}/workflow/compile", headers={"Authorization": "Bearer change-me"}, json={})
    app_client.post("/api/nodes/lifecycle/transition", headers={"Authorization": "Bearer change-me"}, json={"node_id": node_id, "target_state": "READY"})
    app_client.post("/api/node-runs/start", headers={"Authorization": "Bearer change-me"}, json={"node_id": node_id})

    current_response = app_client.get(f"/api/nodes/{node_id}/subtasks/current", headers={"Authorization": "Bearer change-me"})
    compiled_subtask_id = current_response.json()["state"]["current_compiled_subtask_id"]
    prompt_response = app_client.get(f"/api/nodes/{node_id}/subtasks/current/prompt", headers={"Authorization": "Bearer change-me"})
    context_response = app_client.get(f"/api/nodes/{node_id}/subtasks/current/context", headers={"Authorization": "Bearer change-me"})
    start_response = app_client.post(
        "/api/subtasks/start",
        headers={"Authorization": "Bearer change-me"},
        json={"node_id": node_id, "compiled_subtask_id": compiled_subtask_id},
    )
    heartbeat_response = app_client.post(
        "/api/subtasks/heartbeat",
        headers={"Authorization": "Bearer change-me"},
        json={"node_id": node_id, "compiled_subtask_id": compiled_subtask_id},
    )
    summary_file = tmp_path / "summary.md"
    summary_file.write_text("summary body", encoding="utf-8")
    summary_response = app_client.post(
        "/api/summaries/register",
        headers={"Authorization": "Bearer change-me"},
        json={"node_id": node_id, "summary_type": "subtask", "summary_path": str(summary_file), "content": "summary body"},
    )
    prompt_id = prompt_response.json()["prompt_id"]
    prompt_history_response = app_client.get(f"/api/nodes/{node_id}/prompt-history", headers={"Authorization": "Bearer change-me"})
    prompt_record_response = app_client.get(f"/api/prompts/{prompt_id}", headers={"Authorization": "Bearer change-me"})
    summary_id = summary_response.json()["summary_id"]
    summary_history_response = app_client.get(f"/api/nodes/{node_id}/summary-history", headers={"Authorization": "Bearer change-me"})
    summary_record_response = app_client.get(f"/api/summaries/{summary_id}", headers={"Authorization": "Bearer change-me"})

    assert prompt_response.status_code == 200
    assert prompt_response.json()["compiled_subtask_id"] == compiled_subtask_id
    assert prompt_id
    assert prompt_response.json()["stage_context_json"]["startup"]["node_id"] == node_id
    assert context_response.status_code == 200
    assert context_response.json()["compiled_subtask_id"] == compiled_subtask_id
    assert context_response.json()["input_context_json"]["compiled_subtask_id"] == compiled_subtask_id
    assert context_response.json()["stage_context_json"]["startup"]["node_prompt"] == "boot prompt"
    assert context_response.json()["input_context_json"]["stage_context_json"]["stage"]["compiled_subtask_id"] == compiled_subtask_id
    assert start_response.status_code == 200
    assert heartbeat_response.status_code == 200
    assert heartbeat_response.json()["latest_attempt"]["output_json"]["last_heartbeat_at"]
    assert summary_response.status_code == 200
    assert summary_id
    assert summary_response.json()["summary_type"] == "subtask"
    assert summary_response.json()["content_length"] == len("summary body")
    assert prompt_history_response.status_code == 200
    assert prompt_history_response.json()["prompts"][0]["id"] == prompt_id
    assert prompt_record_response.status_code == 200
    assert prompt_record_response.json()["id"] == prompt_id
    assert prompt_record_response.json()["content_hash"]
    assert summary_history_response.status_code == 200
    assert summary_history_response.json()["summaries"][0]["id"] == summary_id
    assert summary_record_response.status_code == 200
    assert summary_record_response.json()["id"] == summary_id
    assert summary_record_response.json()["summary_scope"] == "subtask_attempt"


def test_pause_state_and_node_event_history_endpoints_work(app_client, migrated_public_schema) -> None:
    create_response = app_client.post(
        "/api/nodes/create",
        headers={"Authorization": "Bearer change-me"},
        json={"kind": "epic", "title": "Runnable", "prompt": "boot prompt"},
    )
    node_id = create_response.json()["node_id"]
    app_client.post(f"/api/nodes/{node_id}/workflow/compile", headers={"Authorization": "Bearer change-me"}, json={})
    app_client.post("/api/nodes/lifecycle/transition", headers={"Authorization": "Bearer change-me"}, json={"node_id": node_id, "target_state": "READY"})
    app_client.post("/api/node-runs/start", headers={"Authorization": "Bearer change-me"}, json={"node_id": node_id})
    app_client.post("/api/nodes/pause", headers={"Authorization": "Bearer change-me"}, json={"node_id": node_id})

    pause_state = app_client.get(f"/api/nodes/{node_id}/pause-state", headers={"Authorization": "Bearer change-me"})
    events = app_client.get(f"/api/nodes/{node_id}/events", headers={"Authorization": "Bearer change-me"})

    assert pause_state.status_code == 200
    assert pause_state.json()["lifecycle_state"] == "PAUSED_FOR_USER"
    assert pause_state.json()["pause_flag_name"] == "manual_pause"
    assert events.status_code == 200
    assert [item["command"] for item in events.json()["events"] if item["event_scope"] == "authority"] == [
        "node.run.start",
        "node.pause",
    ]
    assert [item["command"] for item in events.json()["events"] if item["event_scope"] == "pause"] == ["pause_entered"]


def test_provenance_and_rationale_endpoints_work(app_client, migrated_public_schema) -> None:
    create_response = app_client.post(
        "/api/nodes/create",
        headers={"Authorization": "Bearer change-me"},
        json={"kind": "epic", "title": "Provenance Node", "prompt": "connect changes to rationale"},
    )
    node_id = create_response.json()["node_id"]
    app_client.post(f"/api/nodes/{node_id}/workflow/compile", headers={"Authorization": "Bearer change-me"}, json={})
    app_client.post("/api/nodes/lifecycle/transition", headers={"Authorization": "Bearer change-me"}, json={"node_id": node_id, "target_state": "READY"})
    app_client.post("/api/node-runs/start", headers={"Authorization": "Bearer change-me"}, json={"node_id": node_id})
    current_response = app_client.get(f"/api/nodes/{node_id}/subtasks/current", headers={"Authorization": "Bearer change-me"})
    compiled_subtask_id = current_response.json()["state"]["current_compiled_subtask_id"]
    app_client.get(f"/api/nodes/{node_id}/subtasks/current/prompt", headers={"Authorization": "Bearer change-me"})
    app_client.post(
        "/api/subtasks/start",
        headers={"Authorization": "Bearer change-me"},
        json={"node_id": node_id, "compiled_subtask_id": compiled_subtask_id},
    )
    summary_response = app_client.post(
        "/api/summaries/register",
        headers={"Authorization": "Bearer change-me"},
        json={"node_id": node_id, "summary_type": "subtask", "summary_path": "summary.md", "content": "implemented provenance plumbing"},
    )

    refresh_response = app_client.post(f"/api/nodes/{node_id}/provenance/refresh", headers={"Authorization": "Bearer change-me"})
    rationale_response = app_client.get(f"/api/nodes/{node_id}/rationale", headers={"Authorization": "Bearer change-me"})
    entity_response = app_client.get("/api/entities/by-name/src.aicoding.daemon.app.create_app", headers={"Authorization": "Bearer change-me"})
    history_response = app_client.get("/api/entities/by-name/src.aicoding.daemon.app.create_app/history", headers={"Authorization": "Bearer change-me"})
    changed_by_response = app_client.get("/api/entities/by-name/src.aicoding.daemon.app.create_app/changed-by", headers={"Authorization": "Bearer change-me"})
    relations_response = app_client.get("/api/entities/by-name/src.aicoding.daemon.app.create_app/relations", headers={"Authorization": "Bearer change-me"})

    assert summary_response.status_code == 200
    assert refresh_response.status_code == 200
    assert refresh_response.json()["summary_record_id"] == summary_response.json()["summary_id"]
    assert refresh_response.json()["entity_count"] > 0
    assert rationale_response.status_code == 200
    assert rationale_response.json()["change_counts"]["added"] > 0
    assert entity_response.status_code == 200
    assert entity_response.json()["entities"][0]["canonical_name"] == "src.aicoding.daemon.app.create_app"
    assert history_response.status_code == 200
    assert history_response.json()["history"]
    assert changed_by_response.status_code == 200
    assert changed_by_response.json()["history"]
    assert relations_response.status_code == 200
    assert relations_response.json()["relations"]


def test_documentation_endpoints_build_list_and_show_outputs(app_client, migrated_public_schema) -> None:
    epic = app_client.post(
        "/api/nodes/create",
        headers={"Authorization": "Bearer change-me"},
        json={"kind": "epic", "title": "Docs Epic", "prompt": "root"},
    ).json()
    phase = app_client.post(
        "/api/nodes/create",
        headers={"Authorization": "Bearer change-me"},
        json={"kind": "phase", "title": "Docs Phase", "prompt": "phase", "parent_node_id": epic["node_id"]},
    ).json()
    plan = app_client.post(
        "/api/nodes/create",
        headers={"Authorization": "Bearer change-me"},
        json={"kind": "plan", "title": "Docs Plan", "prompt": "plan", "parent_node_id": phase["node_id"]},
    ).json()
    task = app_client.post(
        "/api/nodes/create",
        headers={"Authorization": "Bearer change-me"},
        json={"kind": "task", "title": "Docs Task", "prompt": "task", "parent_node_id": plan["node_id"]},
    ).json()

    app_client.post(f"/api/nodes/{task['node_id']}/workflow/compile", headers={"Authorization": "Bearer change-me"}, json={})
    app_client.post(f"/api/nodes/{phase['node_id']}/workflow/compile", headers={"Authorization": "Bearer change-me"}, json={})

    build_node = app_client.post(f"/api/nodes/{task['node_id']}/docs/build-node-view", headers={"Authorization": "Bearer change-me"})
    build_tree = app_client.post(f"/api/nodes/{phase['node_id']}/docs/build-tree", headers={"Authorization": "Bearer change-me"})
    list_node = app_client.get(f"/api/nodes/{task['node_id']}/docs", headers={"Authorization": "Bearer change-me"})
    show_node = app_client.get(f"/api/nodes/{task['node_id']}/docs/local", headers={"Authorization": "Bearer change-me"})
    show_tree = app_client.get(f"/api/nodes/{phase['node_id']}/docs/merged", headers={"Authorization": "Bearer change-me"})

    assert build_node.status_code == 200
    assert {item["scope"] for item in build_node.json()["documents"]} >= {"local", "custom"}
    assert build_tree.status_code == 200
    assert {item["scope"] for item in build_tree.json()["documents"]} >= {"merged", "custom"}
    assert list_node.status_code == 200
    assert list_node.json()["documents"]
    assert show_node.status_code == 200
    assert "Docs Task" in show_node.json()["content"]
    assert show_tree.status_code == 200
    assert "Docs Phase" in show_tree.json()["content"]


def test_child_materialization_endpoints_materialize_and_report_scheduling(app_client, migrated_public_schema) -> None:
    create_response = app_client.post(
        "/api/nodes/create",
        headers={"Authorization": "Bearer change-me"},
        json={"kind": "epic", "title": "Parent Epic", "prompt": "boot prompt"},
    )
    node_id = create_response.json()["node_id"]

    before_response = app_client.get(
        f"/api/nodes/{node_id}/children/materialization",
        headers={"Authorization": "Bearer change-me"},
    )
    materialize_response = app_client.post(
        f"/api/nodes/{node_id}/children/materialize",
        headers={"Authorization": "Bearer change-me"},
    )
    children_response = app_client.get(
        f"/api/nodes/{node_id}/children",
        headers={"Authorization": "Bearer change-me"},
    )
    after_response = app_client.get(
        f"/api/nodes/{node_id}/children/materialization",
        headers={"Authorization": "Bearer change-me"},
    )

    assert before_response.status_code == 200
    assert before_response.json()["status"] == "not_materialized"
    assert materialize_response.status_code == 200
    assert materialize_response.json()["status"] == "created"
    assert [item["layout_child_id"] for item in materialize_response.json()["children"]] == ["discovery", "implementation"]
    assert [item["scheduling_status"] for item in materialize_response.json()["children"]] == ["ready", "blocked"]
    assert children_response.status_code == 200
    assert [item["kind"] for item in children_response.json()] == ["phase", "phase"]
    assert after_response.status_code == 200
    assert after_response.json()["status"] == "materialized"


def test_child_result_and_reconcile_endpoints_report_and_record_merge_state(
    app_client,
    db_session_factory,
    migrated_public_schema,
) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    parent = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Parent", prompt="p")
    seed_node_lifecycle(db_session_factory, node_id=str(parent.node_id), initial_state="DRAFT")
    parent_version = initialize_node_version(db_session_factory, logical_node_id=parent.node_id)
    child = create_manual_node(db_session_factory, registry, kind="phase", title="Child", prompt="c", parent_node_id=parent.node_id)
    child_version = child.node_version_id
    compile_node_workflow(db_session_factory, logical_node_id=parent.node_id, catalog=catalog)
    transition_node_lifecycle(db_session_factory, node_id=str(parent.node_id), target_state="COMPILED")
    transition_node_lifecycle(db_session_factory, node_id=str(parent.node_id), target_state="READY")
    admit_node_run(db_session_factory, node_id=parent.node_id)
    _transition_to_complete(db_session_factory, node_id=str(child.node.node_id))
    record_seed_commit(db_session_factory, version_id=parent_version.id, commit_sha="abc1234")
    record_seed_commit(db_session_factory, version_id=child_version, commit_sha="def1234")
    record_final_commit(db_session_factory, version_id=child_version, commit_sha="def5678")

    child_results = app_client.get(f"/api/nodes/{parent.node_id}/child-results", headers={"Authorization": "Bearer change-me"})
    reconcile_before = app_client.get(f"/api/nodes/{parent.node_id}/reconcile", headers={"Authorization": "Bearer change-me"})
    merge_response = app_client.post(f"/api/nodes/{parent.node_id}/git/merge-children", headers={"Authorization": "Bearer change-me"})

    assert child_results.status_code == 200
    assert child_results.json()["status"] == "ready_for_reconcile"
    assert child_results.json()["children"][0]["merge_order"] == 1
    assert reconcile_before.status_code == 200
    assert reconcile_before.json()["prompt_relative_path"] == "execution/reconcile_parent_after_merge.md"
    assert merge_response.status_code == 200
    assert merge_response.json()["status"] == "merged"
    assert merge_response.json()["merge_events"][0]["child_final_commit_sha"] == "def5678"


def test_illegal_node_mutations_are_rejected(app_client, migrated_public_schema) -> None:
    create_response = app_client.post(
        "/api/nodes/create",
        headers={"Authorization": "Bearer change-me"},
        json={"kind": "epic", "title": "Conflict", "prompt": "boot prompt"},
    )
    node_id = create_response.json()["node_id"]
    response = app_client.post(
        "/api/nodes/pause",
        headers={"Authorization": "Bearer change-me"},
        json={"node_id": node_id},
    )
    assert response.status_code == 404

    app_client.post(f"/api/nodes/{node_id}/workflow/compile", headers={"Authorization": "Bearer change-me"}, json={})
    app_client.post(
        "/api/nodes/lifecycle/transition",
        headers={"Authorization": "Bearer change-me"},
        json={"node_id": node_id, "target_state": "READY"},
    )
    first_start = app_client.post(
        "/api/node-runs/start",
        headers={"Authorization": "Bearer change-me"},
        json={"node_id": node_id},
    )
    assert first_start.status_code == 200
    assert first_start.json()["status"] == "admitted"

    second_start = app_client.post(
        "/api/node-runs/start",
        headers={"Authorization": "Bearer change-me"},
        json={"node_id": node_id},
    )
    assert second_start.status_code == 200
    assert second_start.json()["status"] == "blocked"
    assert second_start.json()["reason"] == "active_run_conflict"

    pause_response = app_client.post(
        "/api/nodes/pause",
        headers={"Authorization": "Bearer change-me"},
        json={"node_id": node_id},
    )
    assert pause_response.status_code == 200
    assert pause_response.json()["current_state"] == "PAUSED_FOR_USER"

    second_pause = app_client.post(
        "/api/nodes/pause",
        headers={"Authorization": "Bearer change-me"},
        json={"node_id": node_id},
    )
    assert second_pause.status_code == 409

    resume_response = app_client.post(
        "/api/nodes/resume",
        headers={"Authorization": "Bearer change-me"},
        json={"node_id": node_id},
    )
    assert resume_response.status_code == 200
    assert resume_response.json()["current_state"] == "RUNNING"


def test_mutation_endpoint_returns_structured_validation_error(app_client) -> None:
    response = app_client.post(
        "/api/node-runs/start",
        headers={"Authorization": "Bearer change-me"},
        json={"wrong": "shape"},
    )

    assert response.status_code == 422
    payload = response.json()
    assert payload["error"] == "request_validation_failed"
    assert payload["details"]


def test_db_unavailable_is_reported_as_service_unavailable(monkeypatch) -> None:
    app = create_app()
    app.dependency_overrides = {}
    from aicoding.daemon.dependencies import ensure_database_available

    app.dependency_overrides[ensure_database_available] = lambda: (_ for _ in ()).throw(DaemonUnavailableError())

    with TestClient(app) as client:
        response = client.get("/db/healthz", headers={"Authorization": "Bearer change-me"})

    assert response.status_code == 503
    assert response.json() == {"error": "daemon_unavailable", "message": "database unavailable"}


def test_session_show_current_reports_none_before_binding(monkeypatch, migrated_public_schema) -> None:
    monkeypatch.setenv("AICODING_SESSION_BACKEND", "fake")
    with TestClient(create_app()) as client:
        response = client.get("/api/sessions/show-current", headers={"Authorization": "Bearer change-me"})

    assert response.status_code == 200
    assert response.json()["status"] == "none"


def test_session_bind_attach_and_resume_endpoints_work(monkeypatch, migrated_public_schema) -> None:
    monkeypatch.setenv("AICODING_SESSION_BACKEND", "fake")
    with TestClient(create_app()) as client:
        create_response = client.post(
            "/api/nodes/create",
            headers={"Authorization": "Bearer change-me"},
            json={"kind": "epic", "title": "Session Node", "prompt": "boot prompt"},
        )
        node_id = create_response.json()["node_id"]
        client.post(f"/api/nodes/{node_id}/workflow/compile", headers={"Authorization": "Bearer change-me"}, json={})
        client.post(
            "/api/nodes/lifecycle/transition",
            headers={"Authorization": "Bearer change-me"},
            json={"node_id": node_id, "target_state": "READY"},
        )
        client.post("/api/node-runs/start", headers={"Authorization": "Bearer change-me"}, json={"node_id": node_id})

        bind_response = client.post(
            "/api/sessions/bind",
            headers={"Authorization": "Bearer change-me"},
            json={"node_id": node_id},
        )
        assert bind_response.status_code == 200
        assert bind_response.json()["status"] == "bound"
        assert bind_response.json()["session_id"]
        assert bind_response.json()["logical_node_id"] == node_id
        assert bind_response.json()["node_kind"] == "epic"
        assert bind_response.json()["node_title"] == "Session Node"
        assert bind_response.json()["run_status"] == "RUNNING"
        assert bind_response.json()["recommended_action"] == "attach_existing_session"
        assert bind_response.json()["provider_session_id"] == bind_response.json()["session_name"]
        assert bind_response.json()["cwd"]
        assert bind_response.json()["tmux_session_exists"] is True
        assert bind_response.json()["screen_state"]["classification"] == "active"
        session_id = bind_response.json()["session_id"]

        attach_response = client.post(
            "/api/sessions/attach",
            headers={"Authorization": "Bearer change-me"},
            json={"node_id": node_id},
        )
        assert attach_response.status_code == 200
        assert attach_response.json()["status"] == "attached"

        resume_response = client.post(
            "/api/sessions/resume",
            headers={"Authorization": "Bearer change-me"},
            json={"node_id": node_id},
        )
        assert resume_response.status_code == 200
        assert resume_response.json()["status"] in {"reused_existing_session", "replacement_session_created"}
        assert resume_response.json()["recovery_status"]["recovery_classification"] in {"healthy", "detached", "stale_but_recoverable", "lost"}
        assert resume_response.json()["session"]["status"] == "resumed"

        show_response = client.get(f"/api/nodes/{node_id}/sessions/current", headers={"Authorization": "Bearer change-me"})
        list_response = client.get(f"/api/nodes/{node_id}/sessions", headers={"Authorization": "Bearer change-me"})
        events_response = client.get(f"/api/sessions/{session_id}/events", headers={"Authorization": "Bearer change-me"})
        recovery_response = client.get(f"/api/nodes/{node_id}/recovery-status", headers={"Authorization": "Bearer change-me"})

        assert show_response.status_code == 200
        assert show_response.json()["session_id"] == session_id
        assert show_response.json()["logical_node_id"] == node_id
        assert show_response.json()["screen_state"]["classification"] in {"active", "quiet"}
        assert list_response.status_code == 200
        assert len(list_response.json()["sessions"]) == 1
        assert events_response.status_code == 200
        assert recovery_response.status_code == 200
        assert recovery_response.json()["recovery_classification"] in {"healthy", "stale_but_recoverable", "detached"}
        assert [item["event_type"] for item in events_response.json()["events"]][:2] == ["bound", "attached"]
        assert events_response.json()["events"][0]["payload_json"]["launch_command"]


def test_session_show_current_reports_binding_metadata_and_stale_recovery(monkeypatch, migrated_public_schema) -> None:
    monkeypatch.setenv("AICODING_SESSION_BACKEND", "fake")
    with TestClient(create_app()) as client:
        create_response = client.post(
            "/api/nodes/create",
            headers={"Authorization": "Bearer change-me"},
            json={"kind": "epic", "title": "Stale Session Node", "prompt": "boot prompt"},
        )
        node_id = create_response.json()["node_id"]
        client.post(f"/api/nodes/{node_id}/workflow/compile", headers={"Authorization": "Bearer change-me"}, json={})
        client.post(
            "/api/nodes/lifecycle/transition",
            headers={"Authorization": "Bearer change-me"},
            json={"node_id": node_id, "target_state": "READY"},
        )
        client.post("/api/node-runs/start", headers={"Authorization": "Bearer change-me"}, json={"node_id": node_id})
        bind_response = client.post(
            "/api/sessions/bind",
            headers={"Authorization": "Bearer change-me"},
            json={"node_id": node_id},
        )
        session_name = bind_response.json()["session_name"]

        current_response = client.get("/api/sessions/show-current", headers={"Authorization": "Bearer change-me"})
        assert current_response.status_code == 200
        assert current_response.json()["logical_node_id"] == node_id
        assert current_response.json()["node_title"] == "Stale Session Node"
        assert current_response.json()["recovery_classification"] == "detached"
        assert current_response.json()["recommended_action"] == "attach_existing_session"

        client.app.state.session_adapter.advance_idle(session_name, seconds=30.0)
        stale_response = client.get("/api/sessions/show-current", headers={"Authorization": "Bearer change-me"})

    assert stale_response.status_code == 200
    assert stale_response.json()["logical_node_id"] == node_id
    assert stale_response.json()["recovery_classification"] == "stale_but_recoverable"
    assert stale_response.json()["recommended_action"] == "resume_existing_session"


def test_session_bind_detects_duplicate_active_primary_sessions(monkeypatch, migrated_public_schema) -> None:
    monkeypatch.setenv("AICODING_SESSION_BACKEND", "fake")
    factory = create_session_factory(engine=migrated_public_schema)
    with TestClient(create_app()) as client:
        create_response = client.post(
            "/api/nodes/create",
            headers={"Authorization": "Bearer change-me"},
            json={"kind": "epic", "title": "Duplicate Session Node", "prompt": "boot prompt"},
        )
        node_id = create_response.json()["node_id"]
        client.post(f"/api/nodes/{node_id}/workflow/compile", headers={"Authorization": "Bearer change-me"}, json={})
        client.post(
            "/api/nodes/lifecycle/transition",
            headers={"Authorization": "Bearer change-me"},
            json={"node_id": node_id, "target_state": "READY"},
        )
        client.post("/api/node-runs/start", headers={"Authorization": "Bearer change-me"}, json={"node_id": node_id})
        bind_response = client.post("/api/sessions/bind", headers={"Authorization": "Bearer change-me"}, json={"node_id": node_id})

        with session_scope(factory) as session:
            original = session.get(DurableSession, bind_response.json()["session_id"])
            assert original is not None
            session.add(
                DurableSession(
                    id=uuid4(),
                    node_version_id=original.node_version_id,
                    node_run_id=original.node_run_id,
                    session_role="primary",
                    parent_session_id=None,
                    provider=original.provider,
                    provider_session_id="duplicate-provider",
                    tmux_session_name="duplicate-session",
                    cwd=original.cwd,
                    status="BOUND",
                    started_at=original.started_at,
                    last_heartbeat_at=original.last_heartbeat_at,
                    ended_at=None,
                )
            )

        duplicate_response = client.post("/api/sessions/bind", headers={"Authorization": "Bearer change-me"}, json={"node_id": node_id})

    assert duplicate_response.status_code == 409
    assert "duplicate active primary sessions detected" in str(duplicate_response.json())


def test_session_bind_rejects_missing_active_run(monkeypatch, migrated_public_schema) -> None:
    monkeypatch.setenv("AICODING_SESSION_BACKEND", "fake")
    with TestClient(create_app()) as client:
        create_response = client.post(
            "/api/nodes/create",
            headers={"Authorization": "Bearer change-me"},
            json={"kind": "epic", "title": "No Run Node", "prompt": "boot prompt"},
        )
        node_id = create_response.json()["node_id"]

        response = client.post(
            "/api/sessions/bind",
            headers={"Authorization": "Bearer change-me"},
            json={"node_id": node_id},
        )

    assert response.status_code == 409


def test_recovery_status_reports_missing_session_and_non_resumable(monkeypatch, migrated_public_schema) -> None:
    monkeypatch.setenv("AICODING_SESSION_BACKEND", "fake")
    factory = create_session_factory(engine=migrated_public_schema)
    with TestClient(create_app()) as client:
        create_response = client.post(
            "/api/nodes/create",
            headers={"Authorization": "Bearer change-me"},
            json={"kind": "epic", "title": "Recover Node", "prompt": "boot prompt"},
        )
        node_id = create_response.json()["node_id"]
        client.post(f"/api/nodes/{node_id}/workflow/compile", headers={"Authorization": "Bearer change-me"}, json={})
        client.post(
            "/api/nodes/lifecycle/transition",
            headers={"Authorization": "Bearer change-me"},
            json={"node_id": node_id, "target_state": "READY"},
        )
        client.post("/api/node-runs/start", headers={"Authorization": "Bearer change-me"}, json={"node_id": node_id})

        missing_response = client.get(f"/api/nodes/{node_id}/recovery-status", headers={"Authorization": "Bearer change-me"})
        assert missing_response.status_code == 200
        assert missing_response.json()["recovery_classification"] == "missing"

        client.post("/api/sessions/bind", headers={"Authorization": "Bearer change-me"}, json={"node_id": node_id})
        with session_scope(factory) as session:
            state = session.query(NodeRunState).one()
            state.is_resumable = False
        rejected_response = client.post(
            "/api/sessions/resume",
            headers={"Authorization": "Bearer change-me"},
            json={"node_id": node_id},
        )

    assert rejected_response.status_code == 200
    assert rejected_response.json()["status"] == "recovery_rejected"
    assert rejected_response.json()["recovery_status"]["recovery_classification"] == "non_resumable"


def test_session_nudge_endpoint_nudges_then_escalates(monkeypatch, migrated_public_schema) -> None:
    monkeypatch.setenv("AICODING_SESSION_BACKEND", "fake")
    monkeypatch.setenv("AICODING_SESSION_IDLE_THRESHOLD_SECONDS", "5")
    monkeypatch.setenv("AICODING_SESSION_MAX_NUDGE_COUNT", "2")
    with TestClient(create_app()) as client:
        create_response = client.post(
            "/api/nodes/create",
            headers={"Authorization": "Bearer change-me"},
            json={"kind": "epic", "title": "Idle Node", "prompt": "boot prompt"},
        )
        node_id = create_response.json()["node_id"]
        client.post(f"/api/nodes/{node_id}/workflow/compile", headers={"Authorization": "Bearer change-me"}, json={})
        client.post(
            "/api/nodes/lifecycle/transition",
            headers={"Authorization": "Bearer change-me"},
            json={"node_id": node_id, "target_state": "READY"},
        )
        client.post("/api/node-runs/start", headers={"Authorization": "Bearer change-me"}, json={"node_id": node_id})
        bind_response = client.post("/api/sessions/bind", headers={"Authorization": "Bearer change-me"}, json={"node_id": node_id})
        session_name = bind_response.json()["session_name"]
        adapter = client.app.state.session_adapter
        adapter.advance_idle(session_name, seconds=30.0)

        first = client.post("/api/sessions/nudge", headers={"Authorization": "Bearer change-me"}, json={"node_id": node_id})
        adapter.advance_idle(session_name, seconds=30.0)
        second = client.post("/api/sessions/nudge", headers={"Authorization": "Bearer change-me"}, json={"node_id": node_id})
        adapter.advance_idle(session_name, seconds=30.0)
        third = client.post("/api/sessions/nudge", headers={"Authorization": "Bearer change-me"}, json={"node_id": node_id})
        pause_state = client.get(f"/api/nodes/{node_id}/pause-state", headers={"Authorization": "Bearer change-me"})

    assert first.status_code == 200
    assert first.json()["status"] == "nudged"
    assert first.json()["screen_state"]["classification"] == "idle"
    assert second.json()["prompt_relative_path"] == "recovery/repeated_missed_step.md"
    assert third.json()["status"] == "escalated_to_pause"
    assert pause_state.json()["pause_flag_name"] == "idle_nudge_limit_exceeded"


def test_child_session_push_pop_and_result_endpoints_work(monkeypatch, migrated_public_schema) -> None:
    monkeypatch.setenv("AICODING_SESSION_BACKEND", "fake")
    with TestClient(create_app()) as client:
        create_response = client.post(
            "/api/nodes/create",
            headers={"Authorization": "Bearer change-me"},
            json={"kind": "epic", "title": "Child Node", "prompt": "boot prompt"},
        )
        node_id = create_response.json()["node_id"]
        client.post(f"/api/nodes/{node_id}/workflow/compile", headers={"Authorization": "Bearer change-me"}, json={})
        client.post(
            "/api/nodes/lifecycle/transition",
            headers={"Authorization": "Bearer change-me"},
            json={"node_id": node_id, "target_state": "READY"},
        )
        client.post("/api/node-runs/start", headers={"Authorization": "Bearer change-me"}, json={"node_id": node_id})
        client.post("/api/sessions/bind", headers={"Authorization": "Bearer change-me"}, json={"node_id": node_id})

        push_response = client.post(
            "/api/sessions/push",
            headers={"Authorization": "Bearer change-me"},
            json={"node_id": node_id, "reason": "research_context"},
        )
        child_session_id = push_response.json()["session_id"]
        pop_response = client.post(
            "/api/sessions/pop",
            headers={"Authorization": "Bearer change-me"},
            json={
                "session_id": child_session_id,
                "status": "success",
                "summary": "research done",
                "findings": ["one"],
                "artifacts": [{"path": "notes/research.md", "type": "notes"}],
                "suggested_next_actions": ["continue"],
            },
        )
        result_response = client.get(f"/api/sessions/{child_session_id}/result", headers={"Authorization": "Bearer change-me"})
        context_response = client.get(f"/api/nodes/{node_id}/subtasks/current/context", headers={"Authorization": "Bearer change-me"})

    assert push_response.status_code == 200
    assert push_response.json()["reason"] == "research_context"
    assert pop_response.status_code == 200
    assert pop_response.json()["status"] == "success"
    assert result_response.status_code == 200
    assert result_response.json()["summary"] == "research done"
    assert context_response.json()["input_context_json"]["child_session_results"][0]["child_session_id"] == child_session_id
