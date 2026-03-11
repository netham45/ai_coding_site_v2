from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
import time
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from aicoding.config import get_settings
from aicoding.daemon.app import create_app
from aicoding.daemon.admission import admit_node_run
from aicoding.daemon.branches import record_final_commit, record_seed_commit
from aicoding.daemon.errors import DaemonUnavailableError
from aicoding.daemon.hierarchy import create_hierarchy_node, sync_hierarchy_definitions
from aicoding.daemon.incremental_parent_merge import process_next_incremental_child_merge, record_completed_child_for_incremental_merge
from aicoding.daemon.lifecycle import seed_node_lifecycle, transition_node_lifecycle
from aicoding.daemon.live_git import (
    abort_live_merge,
    bootstrap_live_git_repo,
    execute_live_merge_children,
    show_live_git_status,
    stage_live_git_change,
)
from aicoding.daemon.manual_tree import create_manual_node
from aicoding.daemon.run_orchestration import register_summary, start_subtask_attempt
from aicoding.daemon.session_records import inspect_primary_session_screen_state, nudge_primary_session
from aicoding.daemon.versioning import initialize_node_version
from aicoding.daemon.workflows import compile_node_workflow
from aicoding.db.models import CompiledSubtask, NodeRunState, Session as DurableSession
from aicoding.db.session import create_session_factory, session_scope
from aicoding.hierarchy import load_hierarchy_registry
from aicoding.resources import load_resource_catalog


def _write_generated_child_layout(
    workspace_root: Path,
    *,
    layout_id: str,
    child_specs: list[dict[str, object]],
) -> Path:
    layout_path = workspace_root / "drafts" / f"{layout_id}.yaml"
    layout_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "kind: layout_definition",
        f"id: {layout_id}",
        "name: Generated Integration Layout",
        "description: Generated child layout for daemon integration testing.",
        "children:",
    ]
    for index, child in enumerate(child_specs, start=1):
        dependencies = list(child.get("dependencies", []))
        lines.extend(
            [
                f"  - id: {child['id']}",
                "    kind: phase",
                "    tier: 2",
                f"    name: {child['name']}",
                f"    ordinal: {index}",
                f"    goal: {child['goal']}",
                f"    rationale: {child['rationale']}",
            ]
        )
        if dependencies:
            lines.append("    dependencies:")
            lines.extend(f"      - {dependency}" for dependency in dependencies)
        else:
            lines.append("    dependencies: []")
    layout_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return layout_path


def _create_parent_with_generated_children(
    client: TestClient,
    *,
    layout_path: Path,
    title: str,
) -> tuple[str, dict[str, dict[str, object]]]:
    headers = {"Authorization": "Bearer change-me"}
    create_response = client.post(
        "/api/nodes/create",
        headers=headers,
        json={"kind": "epic", "title": title, "prompt": "boot prompt"},
    )
    assert create_response.status_code == 200
    node_id = str(create_response.json()["node_id"])
    compile_response = client.post(f"/api/nodes/{node_id}/workflow/compile", headers=headers, json={})
    ready_response = client.post(
        "/api/nodes/lifecycle/transition",
        headers=headers,
        json={"node_id": node_id, "target_state": "READY"},
    )
    register_response = client.post(
        f"/api/nodes/{node_id}/children/register-layout",
        headers=headers,
        json={"file_path": str(layout_path)},
    )
    materialize_response = client.post(
        f"/api/nodes/{node_id}/children/materialize",
        headers=headers,
        json={},
    )
    assert compile_response.status_code == 200
    assert ready_response.status_code == 200
    assert register_response.status_code == 200
    assert materialize_response.status_code == 200
    children = {
        str(child["layout_child_id"]): child
        for child in materialize_response.json()["children"]
    }
    return node_id, children


def _child_runtime_snapshot(client: TestClient, *, node_id: str) -> dict[str, object]:
    headers = {"Authorization": "Bearer change-me"}
    runs_response = client.get(f"/api/nodes/{node_id}/runs", headers=headers)
    sessions_response = client.get(f"/api/nodes/{node_id}/sessions", headers=headers)
    dependency_response = client.get(f"/api/nodes/{node_id}/dependency-status", headers=headers)
    assert runs_response.status_code == 200
    assert sessions_response.status_code == 200
    assert dependency_response.status_code == 200
    return {
        "runs": runs_response.json()["runs"],
        "sessions": sessions_response.json()["sessions"],
        "dependency_status": dependency_response.json()["status"],
        "dependency_blockers": dependency_response.json()["blockers"],
    }


def _current_node_version_id(client: TestClient, *, node_id: str) -> str:
    response = client.get(
        f"/api/nodes/{node_id}/versions",
        headers={"Authorization": "Bearer change-me"},
    )
    assert response.status_code == 200
    return str(response.json()["versions"][0]["id"])


def _wait_for_child_auto_start_state(
    client: TestClient,
    *,
    started_node_ids: set[str],
    blocked_node_ids: set[str],
    timeout_seconds: float = 5.0,
) -> dict[str, dict[str, object]]:
    deadline = time.time() + timeout_seconds
    last_snapshots: dict[str, dict[str, object]] = {}
    target_node_ids = started_node_ids | blocked_node_ids
    while time.time() < deadline:
        last_snapshots = {
            node_id: _child_runtime_snapshot(client, node_id=node_id)
            for node_id in target_node_ids
        }
        started_ok = all(
            snapshot["sessions"]
            and (
                (snapshot["runs"] and snapshot["runs"][0]["trigger_reason"] == "auto_run_child")
                or any(item["blocker_kind"] == "already_running" for item in snapshot["dependency_blockers"])
            )
            for node_id, snapshot in last_snapshots.items()
            if node_id in started_node_ids
        )
        blocked_ok = all(
            snapshot["runs"] == []
            and snapshot["sessions"] == []
            and snapshot["dependency_status"] == "blocked"
            for node_id, snapshot in last_snapshots.items()
            if node_id in blocked_node_ids
        )
        if started_ok and blocked_ok:
            return last_snapshots
        time.sleep(0.1)
    raise AssertionError(
        f"Timed out waiting for child auto-start state. started={started_node_ids} blocked={blocked_node_ids} snapshots={last_snapshots}"
    )


def _transition_child_to_complete(client: TestClient, *, node_id: str) -> None:
    headers = {"Authorization": "Bearer change-me"}
    complete_response = client.post(
        "/api/nodes/lifecycle/transition",
        headers=headers,
        json={"node_id": node_id, "target_state": "COMPLETE"},
    )
    assert complete_response.status_code == 200


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


def _write_parent_decomposition_workspace_overrides(workspace_root) -> None:
    overrides_root = workspace_root / "resources" / "yaml" / "overrides" / "nodes"
    overrides_root.mkdir(parents=True, exist_ok=True)
    for node_kind in ("epic", "phase", "plan"):
        (overrides_root / f"{node_kind}_entry_task.yaml").write_text(
            "\n".join(
                [
                    "target_family: node_definition",
                    f"target_id: {node_kind}",
                    "compatibility:",
                    "  min_schema_version: 2",
                    "  built_in_version: builtin-system-v1",
                    "merge_mode: replace",
                    "value:",
                    "  entry_task: generate_child_layout",
                ]
            ),
            encoding="utf-8",
        )
        (overrides_root / f"{node_kind}_available_tasks.yaml").write_text(
            "\n".join(
                [
                    "target_family: node_definition",
                    f"target_id: {node_kind}",
                    "compatibility:",
                    "  min_schema_version: 2",
                    "  built_in_version: builtin-system-v1",
                    "merge_mode: replace_list",
                    "value:",
                    "  available_tasks:",
                    "    - generate_child_layout",
                    "    - review_child_layout",
                    "    - spawn_children",
                ]
            ),
            encoding="utf-8",
        )


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
    assert payload["database_name"] == clean_public_schema.url.database
    assert payload["current_user"] == "aicoding"


def test_db_schema_compatibility_reports_revision_state(app_client, clean_public_schema) -> None:
    response = app_client.get("/db/schema-compatibility", headers={"Authorization": "Bearer change-me"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["expected_revision"] == "0029_incr_parent_merge_state"
    assert payload["status"] == "up_to_date"
    assert payload["compatible"] is True


def test_daemon_status_reports_background_tasks(app_client) -> None:
    response = app_client.get("/status", headers={"Authorization": "Bearer change-me"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["authority"] == "daemon"
    assert "session_recovery" in payload["background_tasks"]
    assert payload["write_probe"]["write_path"] == "available"
    assert payload["schema_compatibility"]["expected_revision"] == "0029_incr_parent_merge_state"


def test_background_loops_skip_cleanly_until_runtime_tables_exist(clean_public_schema, daemon_token: str, caplog, monkeypatch) -> None:
    monkeypatch.setenv("AICODING_SESSION_BACKEND", "fake")
    monkeypatch.setenv("AICODING_SESSION_POLL_INTERVAL_SECONDS", "0.05")
    caplog.set_level("ERROR", logger="aicoding.daemon.app")

    with TestClient(create_app()) as client:
        time.sleep(0.15)
        response = client.get("/status", headers={"Authorization": "Bearer change-me"})

    assert response.status_code == 200
    assert "Idle nudge background loop iteration failed." not in caplog.text
    assert "Child auto-start background loop iteration failed." not in caplog.text


def test_register_layout_endpoint_makes_generated_layout_authoritative(migrated_public_schema, tmp_path, monkeypatch) -> None:
    workspace_root = tmp_path / "workspace"
    layout_path = workspace_root / "drafts" / "phase_layout.yaml"
    layout_path.parent.mkdir(parents=True, exist_ok=True)
    layout_path.write_text(
        "\n".join(
            [
                "kind: layout_definition",
                "id: generated_epic_layout",
                "name: Generated Epic Layout",
                "description: Registered generated layout for daemon integration testing.",
                "children:",
                "  - id: custom_phase",
                "    kind: phase",
                "    tier: 2",
                "    name: Generated Discovery",
                "    ordinal: 1",
                "    goal: Build the generated phase first.",
                "    rationale: Prove the registration endpoint makes the generated layout authoritative.",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("AICODING_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("AICODING_AUTH_TOKEN", "change-me")
    from aicoding.config import get_settings

    get_settings.cache_clear()
    try:
        with TestClient(create_app()) as client:
            session_factory = client.app.state.db_session_factory
            registry = client.app.state.hierarchy_registry
            sync_hierarchy_definitions(session_factory, registry)
            parent = create_hierarchy_node(session_factory, registry, kind="epic", title="Layout Parent", prompt="boot prompt")
            initialize_node_version(session_factory, logical_node_id=parent.node_id)
            node_id = str(parent.node_id)

            register_response = client.post(
                f"/api/nodes/{node_id}/children/register-layout",
                headers={"Authorization": "Bearer change-me"},
                json={"file_path": str(layout_path)},
            )
            materialize_response = client.post(
                f"/api/nodes/{node_id}/children/materialize",
                headers={"Authorization": "Bearer change-me"},
                json={},
            )

            assert register_response.status_code == 200
            assert register_response.json()["status"] == "registered"
            assert register_response.json()["layout_relative_path"] == "layouts/generated_layout.yaml"
            assert register_response.json()["child_count"] == 1
            assert materialize_response.status_code == 200
            assert materialize_response.json()["layout_relative_path"] == "layouts/generated_layout.yaml"
            assert [item["layout_child_id"] for item in materialize_response.json()["children"]] == ["custom_phase"]
    finally:
        get_settings.cache_clear()


def test_daemon_compile_endpoint_reads_scoped_parent_decomposition_overrides_from_workspace(
    migrated_public_schema,
    tmp_path,
    monkeypatch,
) -> None:
    workspace_root = tmp_path / "workspace"
    _write_parent_decomposition_workspace_overrides(workspace_root)
    monkeypatch.setenv("AICODING_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("AICODING_AUTH_TOKEN", "change-me")
    get_settings.cache_clear()

    try:
        with TestClient(create_app()) as client:
            session_factory = client.app.state.db_session_factory
            registry = client.app.state.hierarchy_registry
            sync_hierarchy_definitions(session_factory, registry)
            epic = create_hierarchy_node(session_factory, registry, kind="epic", title="Scoped Epic", prompt="build cat")
            phase = create_hierarchy_node(
                session_factory,
                registry,
                kind="phase",
                title="Scoped Phase",
                prompt="build cat",
                parent_node_id=epic.node_id,
            )
            plan = create_hierarchy_node(
                session_factory,
                registry,
                kind="plan",
                title="Scoped Plan",
                prompt="build cat",
                parent_node_id=phase.node_id,
            )

            for node in (epic, phase, plan):
                initialize_node_version(session_factory, logical_node_id=node.node_id)
                response = client.post(
                    f"/api/nodes/{node.node_id}/workflow/compile",
                    headers={"Authorization": "Bearer change-me"},
                    json={},
                )

                assert response.status_code == 200
                payload = response.json()["compiled_workflow"]
                assert [item["task_key"] for item in payload["tasks"]] == [
                    "generate_child_layout",
                    "review_child_layout",
                    "spawn_children",
                ]
                generate_subtask = next(
                    subtask
                    for subtask in payload["tasks"][0]["subtasks"]
                    if subtask["inserted_by_hook"] is False
                )
                assert "node register-layout" in generate_subtask["prompt_text"]
                assert "--file layouts/generated_layout.yaml" in generate_subtask["prompt_text"]
    finally:
        get_settings.cache_clear()
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


def test_subtask_succeed_endpoint_records_summary_and_routes_workflow(app_client, migrated_public_schema) -> None:
    with TestClient(create_app()) as client:
        session_factory = create_session_factory(engine=migrated_public_schema)
        client.app.state.db_session_factory = session_factory
        registry = client.app.state.hierarchy_registry
        sync_hierarchy_definitions(session_factory, registry)

        create_response = client.post(
            "/api/nodes/create",
            headers={"Authorization": "Bearer change-me"},
            json={"kind": "epic", "title": "Composite Success", "prompt": "boot prompt"},
        )
        node_id = create_response.json()["node_id"]
        client.post(f"/api/nodes/{node_id}/workflow/compile", headers={"Authorization": "Bearer change-me"}, json={})
        client.post("/api/nodes/lifecycle/transition", headers={"Authorization": "Bearer change-me"}, json={"node_id": node_id, "target_state": "READY"})
        client.post("/api/node-runs/start", headers={"Authorization": "Bearer change-me"}, json={"node_id": node_id})
        current_subtask_id = client.get(f"/api/nodes/{node_id}/subtasks/current", headers={"Authorization": "Bearer change-me"}).json()["state"]["current_compiled_subtask_id"]

        start_response = client.post(
            "/api/subtasks/start",
            headers={"Authorization": "Bearer change-me"},
            json={"node_id": node_id, "compiled_subtask_id": current_subtask_id},
        )
        succeed_response = client.post(
            "/api/subtasks/succeed",
            headers={"Authorization": "Bearer change-me"},
            json={
                "node_id": node_id,
                "compiled_subtask_id": current_subtask_id,
                "summary_path": "summaries/implementation.md",
                "content": "# Done\n\nImplemented the current slice.\n",
            },
        )
        summary_history = client.get(f"/api/nodes/{node_id}/summary-history", headers={"Authorization": "Bearer change-me"})

        assert start_response.status_code == 200
        assert succeed_response.status_code == 200
        assert succeed_response.json()["accepted_compiled_subtask_id"] == current_subtask_id
        assert succeed_response.json()["accepted_subtask_type"] == "run_prompt"
        assert succeed_response.json()["recorded_summary_path"] == "summaries/implementation.md"
        assert succeed_response.json()["outcome"] in {"next_stage", "completed", "paused"}
        assert succeed_response.json()["progress"]["state"]["last_completed_compiled_subtask_id"] == current_subtask_id
        assert summary_history.status_code == 200
        assert summary_history.json()["summaries"][0]["id"] == succeed_response.json()["recorded_summary_id"]


def test_subtask_report_command_endpoint_routes_command_stage(app_client, migrated_public_schema) -> None:
    with TestClient(create_app()) as client:
        session_factory = create_session_factory(engine=migrated_public_schema)
        client.app.state.db_session_factory = session_factory
        registry = client.app.state.hierarchy_registry
        sync_hierarchy_definitions(session_factory, registry)

        create_response = client.post(
            "/api/nodes/create",
            headers={"Authorization": "Bearer change-me"},
            json={"kind": "epic", "title": "Composite Command", "prompt": "boot prompt"},
        )
        node_id = create_response.json()["node_id"]
        client.post(f"/api/nodes/{node_id}/workflow/compile", headers={"Authorization": "Bearer change-me"}, json={})
        client.post("/api/nodes/lifecycle/transition", headers={"Authorization": "Bearer change-me"}, json={"node_id": node_id, "target_state": "READY"})
        client.post("/api/node-runs/start", headers={"Authorization": "Bearer change-me"}, json={"node_id": node_id})
        current_subtask_id = client.get(f"/api/nodes/{node_id}/subtasks/current", headers={"Authorization": "Bearer change-me"}).json()["state"]["current_compiled_subtask_id"]

        with session_scope(session_factory) as session:
            subtask = session.get(CompiledSubtask, UUID(current_subtask_id))
            assert subtask is not None
            subtask.command_text = "printf 'ok'"
            subtask.subtask_type = "build_docs"

        start_response = client.post(
            "/api/subtasks/start",
            headers={"Authorization": "Bearer change-me"},
            json={"node_id": node_id, "compiled_subtask_id": current_subtask_id},
        )
        report_response = client.post(
            "/api/subtasks/report-command",
            headers={"Authorization": "Bearer change-me"},
            json={
                "node_id": node_id,
                "compiled_subtask_id": current_subtask_id,
                "execution_result_json": {"exit_code": 0, "stdout": "ok"},
            },
        )

        assert start_response.status_code == 200
        assert report_response.status_code == 200
        assert report_response.json()["accepted_compiled_subtask_id"] == current_subtask_id
        assert report_response.json()["accepted_subtask_type"] == "build_docs"
        assert report_response.json()["recorded_summary_path"] == "summaries/command_result.json"
        assert report_response.json()["outcome"] in {"next_stage", "completed", "paused"}
        assert report_response.json()["progress"]["state"]["last_completed_compiled_subtask_id"] == current_subtask_id


def test_subtask_attempt_result_capture_and_reads_work(app_client, migrated_public_schema) -> None:
    create_response = app_client.post(
        "/api/nodes/create",
        headers={"Authorization": "Bearer change-me"},
        json={"kind": "epic", "title": "Attempt Reads", "prompt": "boot prompt"},
    )
    node_id = create_response.json()["node_id"]
    app_client.post(f"/api/nodes/{node_id}/workflow/compile", headers={"Authorization": "Bearer change-me"}, json={})
    app_client.post("/api/nodes/lifecycle/transition", headers={"Authorization": "Bearer change-me"}, json={"node_id": node_id, "target_state": "READY"})
    app_client.post("/api/node-runs/start", headers={"Authorization": "Bearer change-me"}, json={"node_id": node_id})
    current_subtask_id = app_client.get(f"/api/nodes/{node_id}/subtasks/current", headers={"Authorization": "Bearer change-me"}).json()["state"]["current_compiled_subtask_id"]

    app_client.post(
        "/api/subtasks/start",
        headers={"Authorization": "Bearer change-me"},
        json={"node_id": node_id, "compiled_subtask_id": current_subtask_id},
    )
    completed = app_client.post(
        "/api/subtasks/complete",
        headers={"Authorization": "Bearer change-me"},
        json={
            "node_id": node_id,
            "compiled_subtask_id": current_subtask_id,
            "summary": "done",
            "execution_result_json": {"exit_code": 0, "stdout": "done"},
        },
    )
    attempt_id = completed.json()["latest_attempt"]["id"]
    attempts = app_client.get(f"/api/nodes/{node_id}/subtask-attempts", headers={"Authorization": "Bearer change-me"})
    attempt_show = app_client.get(f"/api/subtask-attempts/{attempt_id}", headers={"Authorization": "Bearer change-me"})

    assert completed.status_code == 200
    assert completed.json()["latest_attempt"]["execution_result_json"] == {"exit_code": 0, "stdout": "done"}
    assert attempts.status_code == 200
    assert attempts.json()["attempts"][0]["execution_result_json"] == {"exit_code": 0, "stdout": "done"}
    assert attempt_show.status_code == 200
    assert attempt_show.json()["execution_result_json"] == {"exit_code": 0, "stdout": "done"}


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
    assert respond.json()["decision_reason"] == "operator override selected 'retry_child'"
    assert respond.json()["options_considered"] == ["retry_child", "regenerate_child", "replan_parent", "pause_for_user"]
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


def test_intervention_catalog_and_pause_apply_endpoints_work(app_client, migrated_public_schema, tmp_path) -> None:
    app_client.app.state.resource_catalog = _pause_gate_catalog(tmp_path)
    create_response = app_client.post(
        "/api/nodes/create",
        headers={"Authorization": "Bearer change-me"},
        json={"kind": "epic", "title": "Intervention Pause", "prompt": "boot prompt"},
    )
    node_id = create_response.json()["node_id"]
    app_client.post(f"/api/nodes/{node_id}/workflow/compile", headers={"Authorization": "Bearer change-me"}, json={})
    app_client.post("/api/nodes/lifecycle/transition", headers={"Authorization": "Bearer change-me"}, json={"node_id": node_id, "target_state": "READY"})
    app_client.post("/api/node-runs/start", headers={"Authorization": "Bearer change-me"}, json={"node_id": node_id})

    progress = app_client.get(f"/api/nodes/{node_id}/subtasks/current", headers={"Authorization": "Bearer change-me"}).json()
    while not progress["current_subtask"]["source_subtask_key"].startswith("pause_for_user."):
        compiled_subtask_id = progress["state"]["current_compiled_subtask_id"]
        app_client.post(
            "/api/subtasks/start",
            headers={"Authorization": "Bearer change-me"},
            json={"node_id": node_id, "compiled_subtask_id": compiled_subtask_id},
        )
        app_client.post(
            "/api/subtasks/complete",
            headers={"Authorization": "Bearer change-me"},
            json={"node_id": node_id, "compiled_subtask_id": compiled_subtask_id},
        )
        app_client.post(f"/api/nodes/{node_id}/workflow/advance", headers={"Authorization": "Bearer change-me"}, json={})
        progress = app_client.get(f"/api/nodes/{node_id}/subtasks/current", headers={"Authorization": "Bearer change-me"}).json()

    catalog_response = app_client.get(f"/api/nodes/{node_id}/interventions", headers={"Authorization": "Bearer change-me"})
    apply_response = app_client.post(
        "/api/nodes/interventions/apply",
        headers={"Authorization": "Bearer change-me"},
        json={
            "node_id": node_id,
            "intervention_kind": "pause_approval",
            "action": "approve_pause",
            "pause_flag_name": "user_guidance_required",
            "summary": "approved",
        },
    )

    assert catalog_response.status_code == 200
    assert any(item["kind"] == "pause_approval" for item in catalog_response.json()["interventions"])
    assert apply_response.status_code == 200
    assert apply_response.json()["result_json"]["approved"] is True


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
    assert [item["scheduling_status"] for item in materialize_response.json()["children"]] == [
        "ready",
        "blocked_on_dependency",
    ]
    assert children_response.status_code == 200
    assert [item["kind"] for item in children_response.json()] == ["phase", "phase"]


def test_background_child_auto_run_loop_binds_ready_child_without_starting_blocked_sibling(
    monkeypatch, migrated_public_schema
) -> None:
    monkeypatch.setenv("AICODING_SESSION_BACKEND", "fake")
    monkeypatch.setenv("AICODING_SESSION_POLL_INTERVAL_SECONDS", "0.05")
    with TestClient(create_app()) as client:
        create_response = client.post(
            "/api/nodes/create",
            headers={"Authorization": "Bearer change-me"},
            json={"kind": "epic", "title": "Auto Child Parent", "prompt": "boot prompt"},
        )
        node_id = create_response.json()["node_id"]
        client.post(f"/api/nodes/{node_id}/workflow/compile", headers={"Authorization": "Bearer change-me"}, json={})
        client.post(
            "/api/nodes/lifecycle/transition",
            headers={"Authorization": "Bearer change-me"},
            json={"node_id": node_id, "target_state": "READY"},
        )

        materialize_response = client.post(
            f"/api/nodes/{node_id}/children/materialize",
            headers={"Authorization": "Bearer change-me"},
            json={},
        )
        assert materialize_response.status_code == 200
        children_response = client.get(
            f"/api/nodes/{node_id}/children",
            headers={"Authorization": "Bearer change-me"},
        )
        assert children_response.status_code == 200
        children = children_response.json()
        ready_child_id = children[0]["node_id"]
        blocked_child_id = children[1]["node_id"]

        ready_sessions = None
        ready_runs = None
        deadline = time.time() + 5.0
        while time.time() < deadline:
            candidate_sessions = client.get(
                f"/api/nodes/{ready_child_id}/sessions",
                headers={"Authorization": "Bearer change-me"},
            )
            candidate_runs = client.get(
                f"/api/nodes/{ready_child_id}/runs",
                headers={"Authorization": "Bearer change-me"},
            )
            if candidate_sessions.status_code == 200 and candidate_sessions.json()["sessions"]:
                ready_sessions = candidate_sessions
                ready_runs = candidate_runs
                break
            time.sleep(0.1)

        assert ready_sessions is not None
        assert ready_runs is not None
        blocked_sessions = client.get(
            f"/api/nodes/{blocked_child_id}/sessions",
            headers={"Authorization": "Bearer change-me"},
        )
        blocked_runs = client.get(
            f"/api/nodes/{blocked_child_id}/runs",
            headers={"Authorization": "Bearer change-me"},
        )
        ready_session_id = ready_sessions.json()["sessions"][0]["session_id"]
        ready_events = client.get(
            f"/api/sessions/{ready_session_id}/events",
            headers={"Authorization": "Bearer change-me"},
        )

    assert ready_runs.status_code == 200
    assert ready_runs.json()["runs"][0]["trigger_reason"] == "auto_run_child"
    assert ready_sessions.json()["sessions"][0]["session_role"] == "primary"
    assert ready_events.status_code == 200
    assert any(item["event_type"] == "auto_child_bound" for item in ready_events.json()["events"])
    assert blocked_sessions.status_code == 200
    assert blocked_sessions.json()["sessions"] == []
    assert blocked_runs.status_code == 200
    assert blocked_runs.json()["runs"] == []


def test_background_child_auto_run_loop_starts_multiple_independent_siblings(
    monkeypatch, migrated_public_schema, tmp_path
) -> None:
    workspace_root = tmp_path / "workspace"
    layout_path = _write_generated_child_layout(
        workspace_root,
        layout_id="independent_siblings",
        child_specs=[
            {
                "id": "sibling_one",
                "name": "Sibling One",
                "goal": "Run the first sibling independently.",
                "rationale": "The backend should not wait on unrelated siblings.",
                "dependencies": [],
            },
            {
                "id": "sibling_two",
                "name": "Sibling Two",
                "goal": "Run the second sibling independently.",
                "rationale": "The backend should admit both ready siblings.",
                "dependencies": [],
            },
        ],
    )
    monkeypatch.setenv("AICODING_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("AICODING_SESSION_BACKEND", "fake")
    monkeypatch.setenv("AICODING_SESSION_POLL_INTERVAL_SECONDS", "0.05")
    monkeypatch.setenv("AICODING_AUTH_TOKEN", "change-me")
    get_settings.cache_clear()
    try:
        with TestClient(create_app()) as client:
            _, children = _create_parent_with_generated_children(
                client,
                layout_path=layout_path,
                title="Independent Sibling Parent",
            )
            assert {child["scheduling_status"] for child in children.values()} == {"ready"}

            snapshots = _wait_for_child_auto_start_state(
                client,
                started_node_ids={str(child["node_id"]) for child in children.values()},
                blocked_node_ids=set(),
            )

            assert all(
                "blocked_on_dependency"
                not in {item["blocker_kind"] for item in snapshot["dependency_blockers"]}
                for snapshot in snapshots.values()
            )
    finally:
        get_settings.cache_clear()


def test_background_child_auto_run_loop_blocks_simple_chain_until_dependency_completes(
    monkeypatch, migrated_public_schema, tmp_path
) -> None:
    workspace_root = tmp_path / "workspace"
    layout_path = _write_generated_child_layout(
        workspace_root,
        layout_id="simple_chain",
        child_specs=[
            {
                "id": "sibling_one",
                "name": "Sibling One",
                "goal": "Finish first.",
                "rationale": "The dependent sibling must wait.",
                "dependencies": [],
            },
            {
                "id": "sibling_two",
                "name": "Sibling Two",
                "goal": "Wait on sibling one.",
                "rationale": "Prove dependency gating blocks auto-start.",
                "dependencies": ["sibling_one"],
            },
        ],
    )
    monkeypatch.setenv("AICODING_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("AICODING_SESSION_BACKEND", "fake")
    monkeypatch.setenv("AICODING_SESSION_POLL_INTERVAL_SECONDS", "0.05")
    monkeypatch.setenv("AICODING_AUTH_TOKEN", "change-me")
    get_settings.cache_clear()
    try:
        with TestClient(create_app()) as client:
            parent_id, children = _create_parent_with_generated_children(
                client,
                layout_path=layout_path,
                title="Simple Chain Parent",
            )
            first = children["sibling_one"]
            second = children["sibling_two"]
            assert first["scheduling_status"] == "ready"
            assert second["scheduling_status"] == "blocked_on_dependency"

            session_factory = client.app.state.db_session_factory
            parent_version_id = UUID(_current_node_version_id(client, node_id=parent_id))
            first_version_id = UUID(_current_node_version_id(client, node_id=str(first["node_id"])))
            second_version_id = UUID(_current_node_version_id(client, node_id=str(second["node_id"])))
            bootstrap_live_git_repo(session_factory, version_id=parent_version_id, files={"shared.txt": "seed\n"})
            bootstrap_live_git_repo(session_factory, version_id=first_version_id)
            bootstrap_live_git_repo(session_factory, version_id=second_version_id)

            _wait_for_child_auto_start_state(
                client,
                started_node_ids={str(first["node_id"])},
                blocked_node_ids={str(second["node_id"])},
            )
            stage_live_git_change(
                session_factory,
                version_id=first_version_id,
                files={"shared.txt": "from sibling one\n"},
                message="Sibling one final",
                record_as_final=True,
            )
            _transition_child_to_complete(client, node_id=str(first["node_id"]))
            record_completed_child_for_incremental_merge(session_factory, child_node_version_id=first_version_id)

            snapshots = _wait_for_child_auto_start_state(
                client,
                started_node_ids={str(first["node_id"]), str(second["node_id"])},
                blocked_node_ids=set(),
            )

            assert "blocked_on_incremental_merge" not in {
                item["blocker_kind"] for item in snapshots[str(second["node_id"])]["dependency_blockers"]
            }
            assert "blocked_on_parent_refresh" not in {
                item["blocker_kind"] for item in snapshots[str(second["node_id"])]["dependency_blockers"]
            }

            merge_events_response = client.get(
                f"/api/nodes/{parent_id}/git/merge-events",
                headers={"Authorization": "Bearer change-me"},
            )
            assert merge_events_response.status_code == 200
            merge_events_payload = merge_events_response.json()
            assert len(merge_events_payload["events"]) == 1
            merged_parent_head = merge_events_payload["events"][0]["parent_commit_after"]
            second_git = show_live_git_status(session_factory, version_id=second_version_id)
            assert second_git.seed_commit_sha == merged_parent_head
    finally:
        get_settings.cache_clear()


def test_background_child_auto_run_loop_unblocks_fan_out_siblings_together_after_shared_prerequisite(
    monkeypatch, migrated_public_schema, tmp_path
) -> None:
    workspace_root = tmp_path / "workspace"
    layout_path = _write_generated_child_layout(
        workspace_root,
        layout_id="fan_out_chain",
        child_specs=[
            {
                "id": "sibling_one",
                "name": "Sibling One",
                "goal": "Finish before the fan-out dependents.",
                "rationale": "The shared prerequisite should gate both followers.",
                "dependencies": [],
            },
            {
                "id": "sibling_two",
                "name": "Sibling Two",
                "goal": "Wait on sibling one.",
                "rationale": "First follower for fan-out coverage.",
                "dependencies": ["sibling_one"],
            },
            {
                "id": "sibling_three",
                "name": "Sibling Three",
                "goal": "Also wait on sibling one.",
                "rationale": "Second follower should unblock in the same scheduling window.",
                "dependencies": ["sibling_one"],
            },
        ],
    )
    monkeypatch.setenv("AICODING_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("AICODING_SESSION_BACKEND", "fake")
    monkeypatch.setenv("AICODING_SESSION_POLL_INTERVAL_SECONDS", "0.05")
    monkeypatch.setenv("AICODING_AUTH_TOKEN", "change-me")
    get_settings.cache_clear()
    try:
        with TestClient(create_app()) as client:
            parent_id, children = _create_parent_with_generated_children(
                client,
                layout_path=layout_path,
                title="Fan Out Parent",
            )
            first = children["sibling_one"]
            second = children["sibling_two"]
            third = children["sibling_three"]
            assert first["scheduling_status"] == "ready"
            assert second["scheduling_status"] == "blocked_on_dependency"
            assert third["scheduling_status"] == "blocked_on_dependency"

            session_factory = client.app.state.db_session_factory
            parent_version_id = UUID(_current_node_version_id(client, node_id=parent_id))
            first_version_id = UUID(_current_node_version_id(client, node_id=str(first["node_id"])))
            second_version_id = UUID(_current_node_version_id(client, node_id=str(second["node_id"])))
            third_version_id = UUID(_current_node_version_id(client, node_id=str(third["node_id"])))
            bootstrap_live_git_repo(session_factory, version_id=parent_version_id, files={"shared.txt": "seed\n"})
            bootstrap_live_git_repo(session_factory, version_id=first_version_id)
            bootstrap_live_git_repo(session_factory, version_id=second_version_id)
            bootstrap_live_git_repo(session_factory, version_id=third_version_id)

            _wait_for_child_auto_start_state(
                client,
                started_node_ids={str(first["node_id"])},
                blocked_node_ids={str(second["node_id"]), str(third["node_id"])},
            )
            stage_live_git_change(
                session_factory,
                version_id=first_version_id,
                files={"shared.txt": "from shared prerequisite\n"},
                message="Sibling one final",
                record_as_final=True,
            )
            _transition_child_to_complete(client, node_id=str(first["node_id"]))
            record_completed_child_for_incremental_merge(session_factory, child_node_version_id=first_version_id)

            snapshots = _wait_for_child_auto_start_state(
                client,
                started_node_ids={str(first["node_id"]), str(second["node_id"]), str(third["node_id"])},
                blocked_node_ids=set(),
            )

            assert "blocked_on_incremental_merge" not in {
                item["blocker_kind"] for item in snapshots[str(second["node_id"])]["dependency_blockers"]
            }
            assert "blocked_on_parent_refresh" not in {
                item["blocker_kind"] for item in snapshots[str(second["node_id"])]["dependency_blockers"]
            }
            assert "blocked_on_incremental_merge" not in {
                item["blocker_kind"] for item in snapshots[str(third["node_id"])]["dependency_blockers"]
            }
            assert "blocked_on_parent_refresh" not in {
                item["blocker_kind"] for item in snapshots[str(third["node_id"])]["dependency_blockers"]
            }
    finally:
        get_settings.cache_clear()


def test_background_child_auto_run_loop_starts_independent_siblings_while_leaving_dependent_third_blocked(
    monkeypatch, migrated_public_schema, tmp_path
) -> None:
    workspace_root = tmp_path / "workspace"
    layout_path = _write_generated_child_layout(
        workspace_root,
        layout_id="mixed_siblings",
        child_specs=[
            {
                "id": "sibling_one",
                "name": "Sibling One",
                "goal": "Run independently.",
                "rationale": "Independent sibling should not be blocked by sibling three.",
                "dependencies": [],
            },
            {
                "id": "sibling_two",
                "name": "Sibling Two",
                "goal": "Run independently and unblock sibling three later.",
                "rationale": "Sibling three depends only on this child.",
                "dependencies": [],
            },
            {
                "id": "sibling_three",
                "name": "Sibling Three",
                "goal": "Wait on sibling two.",
                "rationale": "The third sibling should stay blocked while the first two auto-start.",
                "dependencies": ["sibling_two"],
            },
        ],
    )
    monkeypatch.setenv("AICODING_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("AICODING_SESSION_BACKEND", "fake")
    monkeypatch.setenv("AICODING_SESSION_POLL_INTERVAL_SECONDS", "0.05")
    monkeypatch.setenv("AICODING_AUTH_TOKEN", "change-me")
    get_settings.cache_clear()
    try:
        with TestClient(create_app()) as client:
            parent_id, children = _create_parent_with_generated_children(
                client,
                layout_path=layout_path,
                title="Mixed Sibling Parent",
            )
            first = children["sibling_one"]
            second = children["sibling_two"]
            third = children["sibling_three"]
            assert first["scheduling_status"] == "ready"
            assert second["scheduling_status"] == "ready"
            assert third["scheduling_status"] == "blocked_on_dependency"

            session_factory = client.app.state.db_session_factory
            parent_version_id = UUID(_current_node_version_id(client, node_id=parent_id))
            first_version_id = UUID(_current_node_version_id(client, node_id=str(first["node_id"])))
            second_version_id = UUID(_current_node_version_id(client, node_id=str(second["node_id"])))
            third_version_id = UUID(_current_node_version_id(client, node_id=str(third["node_id"])))
            bootstrap_live_git_repo(session_factory, version_id=parent_version_id, files={"shared.txt": "seed\n"})
            bootstrap_live_git_repo(session_factory, version_id=first_version_id)
            bootstrap_live_git_repo(session_factory, version_id=second_version_id)
            bootstrap_live_git_repo(session_factory, version_id=third_version_id)

            _wait_for_child_auto_start_state(
                client,
                started_node_ids={str(first["node_id"]), str(second["node_id"])},
                blocked_node_ids={str(third["node_id"])},
            )
            stage_live_git_change(
                session_factory,
                version_id=second_version_id,
                files={"shared.txt": "from sibling two\n"},
                message="Sibling two final",
                record_as_final=True,
            )
            _transition_child_to_complete(client, node_id=str(second["node_id"]))
            record_completed_child_for_incremental_merge(session_factory, child_node_version_id=second_version_id)

            snapshots = _wait_for_child_auto_start_state(
                client,
                started_node_ids={str(first["node_id"]), str(second["node_id"]), str(third["node_id"])},
                blocked_node_ids=set(),
            )

            assert "blocked_on_incremental_merge" not in {
                item["blocker_kind"] for item in snapshots[str(third["node_id"])]["dependency_blockers"]
            }
            assert "blocked_on_parent_refresh" not in {
                item["blocker_kind"] for item in snapshots[str(third["node_id"])]["dependency_blockers"]
            }
    finally:
        get_settings.cache_clear()


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
    bootstrap_live_git_repo(db_session_factory, version_id=parent_version.id, files={"shared.txt": "base\n"}, replace_existing=True)
    bootstrap_live_git_repo(db_session_factory, version_id=child_version, files={"shared.txt": "base\n"}, replace_existing=True)
    child_status = stage_live_git_change(
        db_session_factory,
        version_id=child_version,
        files={"shared.txt": "base\nchild change\n"},
        message="Child final",
        record_as_final=True,
    )
    record_completed_child_for_incremental_merge(db_session_factory, child_node_version_id=child_version)
    process_next_incremental_child_merge(db_session_factory, parent_node_version_id=parent_version.id)

    child_results = app_client.get(f"/api/nodes/{parent.node_id}/child-results", headers={"Authorization": "Bearer change-me"})
    reconcile_before = app_client.get(f"/api/nodes/{parent.node_id}/reconcile", headers={"Authorization": "Bearer change-me"})
    merge_events = app_client.get(f"/api/nodes/{parent.node_id}/git/merge-events", headers={"Authorization": "Bearer change-me"})

    assert child_results.status_code == 200
    assert child_results.json()["status"] == "ready_for_reconcile"
    assert child_results.json()["children"][0]["merge_order"] == 1
    assert reconcile_before.status_code == 200
    assert reconcile_before.json()["prompt_relative_path"] == "execution/reconcile_parent_after_merge.md"
    assert reconcile_before.json()["status"] == "ready_for_reconcile"
    assert reconcile_before.json()["merge_events"][0]["child_final_commit_sha"] == child_status.final_commit_sha
    assert merge_events.status_code == 200
    assert merge_events.json()["events"][0]["child_final_commit_sha"] == child_status.final_commit_sha


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
        assert "subtask prompt --node" in events_response.json()["events"][0]["payload_json"]["prompt_cli_command"]
        assert "prompt_logs" in events_response.json()["events"][0]["payload_json"]["prompt_log_path"]


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


def test_node_audit_endpoint_accepts_rich_durable_session_payload(monkeypatch, migrated_public_schema) -> None:
    monkeypatch.setenv("AICODING_SESSION_BACKEND", "fake")
    with TestClient(create_app()) as client:
        create_response = client.post(
            "/api/nodes/create",
            headers={"Authorization": "Bearer change-me"},
            json={"kind": "epic", "title": "Audit Session Node", "prompt": "boot prompt"},
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

        audit_response = client.get(
            f"/api/nodes/{node_id}/audit",
            headers={"Authorization": "Bearer change-me"},
        )

    assert bind_response.status_code == 200
    assert audit_response.status_code == 200
    payload = audit_response.json()
    assert payload["node_id"] == node_id
    assert payload["sessions"]
    session_payload = payload["sessions"][0]["session"]
    assert session_payload["session_id"] == bind_response.json()["session_id"]
    assert session_payload["logical_node_id"] == node_id
    assert session_payload["node_kind"] == "epic"
    assert session_payload["node_title"] == "Audit Session Node"
    assert session_payload["run_status"] == "RUNNING"
    assert session_payload["screen_state"] is None
    assert session_payload["recommended_action"] is None


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


def test_live_git_conflict_can_be_aborted_via_api(
    app_client,
    db_session_factory,
    migrated_public_schema,
) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    parent = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Parent Conflict", prompt="p")
    seed_node_lifecycle(db_session_factory, node_id=str(parent.node_id), initial_state="DRAFT")
    parent_version = initialize_node_version(db_session_factory, logical_node_id=parent.node_id)
    child_a = create_manual_node(db_session_factory, registry, kind="phase", title="Child A", prompt="a", parent_node_id=parent.node_id)
    child_b = create_manual_node(db_session_factory, registry, kind="phase", title="Child B", prompt="b", parent_node_id=parent.node_id)

    bootstrap_live_git_repo(db_session_factory, version_id=parent_version.id, files={"shared.txt": "base\n"}, replace_existing=True)
    bootstrap_live_git_repo(db_session_factory, version_id=child_a.node_version_id, files={"shared.txt": "base\n"}, replace_existing=True)
    bootstrap_live_git_repo(db_session_factory, version_id=child_b.node_version_id, files={"shared.txt": "base\n"}, replace_existing=True)
    stage_live_git_change(
        db_session_factory,
        version_id=child_a.node_version_id,
        files={"shared.txt": "base\nchild a\n"},
        message="Child A final",
        record_as_final=True,
    )
    stage_live_git_change(
        db_session_factory,
        version_id=child_b.node_version_id,
        files={"shared.txt": "base\nchild b\n"},
        message="Child B final",
        record_as_final=True,
    )

    merge_response = app_client.post(f"/api/nodes/{parent.node_id}/git/merge-children", headers={"Authorization": "Bearer change-me"})
    conflicts_response = app_client.get(f"/api/nodes/{parent.node_id}/git/merge-conflicts", headers={"Authorization": "Bearer change-me"})
    abort_response = app_client.post(f"/api/nodes/{parent.node_id}/git/abort-merge", headers={"Authorization": "Bearer change-me"})

    assert merge_response.status_code == 409
    assert conflicts_response.status_code == 200
    assert conflicts_response.json()["conflicts"]
    assert abort_response.status_code == 200
    assert abort_response.json()["working_tree_state"] == "seed_ready"


def test_intervention_catalog_reports_merge_conflict_and_abort_action(
    app_client,
    db_session_factory,
    migrated_public_schema,
) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    parent = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Parent Intervention Conflict", prompt="p")
    seed_node_lifecycle(db_session_factory, node_id=str(parent.node_id), initial_state="DRAFT")
    parent_version = initialize_node_version(db_session_factory, logical_node_id=parent.node_id)
    child_a = create_manual_node(db_session_factory, registry, kind="phase", title="Child A", prompt="a", parent_node_id=parent.node_id)
    child_b = create_manual_node(db_session_factory, registry, kind="phase", title="Child B", prompt="b", parent_node_id=parent.node_id)

    bootstrap_live_git_repo(db_session_factory, version_id=parent_version.id, files={"shared.txt": "base\n"}, replace_existing=True)
    bootstrap_live_git_repo(db_session_factory, version_id=child_a.node_version_id, files={"shared.txt": "base\n"}, replace_existing=True)
    bootstrap_live_git_repo(db_session_factory, version_id=child_b.node_version_id, files={"shared.txt": "base\n"}, replace_existing=True)
    child_a_status = stage_live_git_change(
        db_session_factory,
        version_id=child_a.node_version_id,
        files={"shared.txt": "base\nchild a\n"},
        message="Child A final",
        record_as_final=True,
    )
    child_b_status = stage_live_git_change(
        db_session_factory,
        version_id=child_b.node_version_id,
        files={"shared.txt": "base\nchild b\n"},
        message="Child B final",
        record_as_final=True,
    )
    execute_live_merge_children(
        db_session_factory,
        logical_node_id=parent.node_id,
        ordered_child_versions=[
            (child_a.node_version_id, child_a_status.final_commit_sha, 1),
            (child_b.node_version_id, child_b_status.final_commit_sha, 2),
        ],
    )

    catalog_response = app_client.get(f"/api/nodes/{parent.node_id}/interventions", headers={"Authorization": "Bearer change-me"})
    apply_response = app_client.post(
        "/api/nodes/interventions/apply",
        headers={"Authorization": "Bearer change-me"},
        json={
            "node_id": str(parent.node_id),
            "intervention_kind": "merge_conflict",
            "action": "abort_merge",
        },
    )

    assert catalog_response.status_code == 200
    assert any(item["kind"] == "merge_conflict" for item in catalog_response.json()["interventions"])
    assert apply_response.status_code == 200
    assert apply_response.json()["result_json"]["working_tree_state"] == "seed_ready"


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


def test_provider_recovery_status_and_provider_resume_rebind_restorable_session(monkeypatch, migrated_public_schema) -> None:
    monkeypatch.setenv("AICODING_SESSION_BACKEND", "fake")
    factory = create_session_factory(engine=migrated_public_schema)
    with TestClient(create_app()) as client:
        create_response = client.post(
            "/api/nodes/create",
            headers={"Authorization": "Bearer change-me"},
            json={"kind": "epic", "title": "Provider Recovery Node", "prompt": "boot prompt"},
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
        session_id = bind_response.json()["session_id"]
        provider_session_id = bind_response.json()["provider_session_id"]

        with session_scope(factory) as session:
            durable = session.get(DurableSession, UUID(session_id))
            assert durable is not None
            durable.tmux_session_name = "missing-session-name"

        provider_status_response = client.get(
            f"/api/nodes/{node_id}/recovery-provider-status",
            headers={"Authorization": "Bearer change-me"},
        )
        provider_resume_response = client.post(
            "/api/sessions/provider-resume",
            headers={"Authorization": "Bearer change-me"},
            json={"node_id": node_id},
        )
        show_response = client.get(f"/api/nodes/{node_id}/sessions/current", headers={"Authorization": "Bearer change-me"})

    assert provider_status_response.status_code == 200
    assert provider_status_response.json()["provider_rebind_possible"] is True
    assert provider_status_response.json()["provider_recommended_action"] == "rebind_provider_session"
    assert provider_status_response.json()["provider_session_id"] == provider_session_id
    assert provider_resume_response.status_code == 200
    assert provider_resume_response.json()["status"] == "provider_session_rebound"
    assert provider_resume_response.json()["session"]["session_id"] == session_id
    assert provider_resume_response.json()["session"]["provider_session_id"] == provider_session_id
    assert show_response.status_code == 200
    assert show_response.json()["session_id"] == session_id
    assert show_response.json()["session_name"] == provider_session_id


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


def test_session_nudge_endpoint_does_not_nudge_when_active_work_marker_is_visible(monkeypatch, migrated_public_schema) -> None:
    monkeypatch.setenv("AICODING_SESSION_BACKEND", "fake")
    monkeypatch.setenv("AICODING_SESSION_IDLE_THRESHOLD_SECONDS", "5")
    with TestClient(create_app()) as client:
        create_response = client.post(
            "/api/nodes/create",
            headers={"Authorization": "Bearer change-me"},
            json={"kind": "epic", "title": "Busy Node", "prompt": "boot prompt"},
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
        adapter._sessions[session_name].pane_text = (
            "• Working (3s • esc to interrupt) · 1 background terminal running · /ps to view · /clean to close\n"
            "• Messages to be submitted after next tool call (press esc to interrupt and send immediately)\n"
        )
        adapter.advance_idle(session_name, seconds=30.0)

        nudge_response = client.post("/api/sessions/nudge", headers={"Authorization": "Bearer change-me"}, json={"node_id": node_id})

    assert nudge_response.status_code == 200
    assert nudge_response.json()["status"] == "not_idle"
    assert nudge_response.json()["screen_state"]["classification"] == "active"
    assert nudge_response.json()["screen_state"]["reason"] == "active_work_indicator_present"


def test_session_nudge_endpoint_can_nudge_idle_alt_screen_session(monkeypatch, migrated_public_schema) -> None:
    monkeypatch.setenv("AICODING_SESSION_BACKEND", "fake")
    monkeypatch.setenv("AICODING_SESSION_IDLE_THRESHOLD_SECONDS", "5")
    with TestClient(create_app()) as client:
        create_response = client.post(
            "/api/nodes/create",
            headers={"Authorization": "Bearer change-me"},
            json={"kind": "epic", "title": "Idle Alt Screen Node", "prompt": "boot prompt"},
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
        adapter.set_alt_screen(session_name, True)
        adapter._sessions[session_name].pane_text = "• Waiting; no subtask work has started.\n"
        adapter.advance_idle(session_name, seconds=30.0)

        nudge_response = client.post("/api/sessions/nudge", headers={"Authorization": "Bearer change-me"}, json={"node_id": node_id})

    assert nudge_response.status_code == 200
    assert nudge_response.json()["status"] == "nudged"
    assert nudge_response.json()["screen_state"]["classification"] == "idle"
    assert nudge_response.json()["screen_state"]["reason"] in {
        "first_sample_idle_threshold_exceeded",
        "unchanged_screen_past_idle_threshold",
    }
    assert nudge_response.json()["in_alt_screen"] is True


def test_session_nudge_endpoint_skips_when_current_subtask_summary_is_already_registered(monkeypatch, migrated_public_schema) -> None:
    monkeypatch.setenv("AICODING_SESSION_BACKEND", "fake")
    monkeypatch.setenv("AICODING_SESSION_IDLE_THRESHOLD_SECONDS", "5")
    with TestClient(create_app()) as client:
        create_response = client.post(
            "/api/nodes/create",
            headers={"Authorization": "Bearer change-me"},
            json={"kind": "epic", "title": "Summarized Node", "prompt": "boot prompt"},
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
        db_session_factory = client.app.state.db_session_factory
        progress_response = client.get(f"/api/node-runs/{node_id}", headers={"Authorization": "Bearer change-me"})
        compiled_subtask_id = progress_response.json()["state"]["current_compiled_subtask_id"]
        start_subtask_attempt(db_session_factory, logical_node_id=UUID(node_id), compiled_subtask_id=UUID(compiled_subtask_id))
        register_summary(
            db_session_factory,
            logical_node_id=UUID(node_id),
            summary_type="subtask",
            summary_path="summaries/implementation.md",
            content="done enough",
        )
        adapter = client.app.state.session_adapter
        adapter._sessions[session_name].pane_text = "• Waiting; no subtask work has started.\n"
        adapter.advance_idle(session_name, seconds=30.0)

        nudge_response = client.post("/api/sessions/nudge", headers={"Authorization": "Bearer change-me"}, json={"node_id": node_id})

    assert nudge_response.status_code == 200
    assert nudge_response.json()["status"] == "summary_registered"
    assert nudge_response.json()["action"] == "none"


def test_nudge_primary_session_can_nudge_after_confirmed_idle_screen_state(monkeypatch, migrated_public_schema) -> None:
    monkeypatch.setenv("AICODING_SESSION_BACKEND", "fake")
    monkeypatch.setenv("AICODING_SESSION_IDLE_THRESHOLD_SECONDS", "1")
    monkeypatch.setenv("AICODING_SESSION_POLL_INTERVAL_SECONDS", "0.05")
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
        session_id = bind_response.json()["session_id"]
        session_name = bind_response.json()["session_name"]
        adapter = client.app.state.session_adapter
        adapter.advance_idle(session_name, seconds=30.0)
        resource_catalog = client.app.state.resource_catalog
        with session_scope(client.app.state.db_session_factory) as session:
            durable = session.get(DurableSession, UUID(session_id))
            assert durable is not None
            durable.last_heartbeat_at = datetime.now(timezone.utc) - timedelta(seconds=10)

        inspect_primary_session_screen_state(
            client.app.state.db_session_factory,
            logical_node_id=UUID(node_id),
            adapter=adapter,
            poller=client.app.state.session_poller,
            persist=True,
        )
        inspect_primary_session_screen_state(
            client.app.state.db_session_factory,
            logical_node_id=UUID(node_id),
            adapter=adapter,
            poller=client.app.state.session_poller,
            persist=True,
        )
        nudge_response = nudge_primary_session(
            client.app.state.db_session_factory,
            logical_node_id=UUID(node_id),
            adapter=adapter,
            poller=client.app.state.session_poller,
            max_nudge_count=2,
            idle_nudge_text=resource_catalog.load_text("prompt_pack_default", "recovery/idle_nudge.md").content,
            repeated_nudge_text=resource_catalog.load_text("prompt_pack_default", "recovery/repeated_missed_step.md").content,
        )
        events_response = client.get(f"/api/sessions/{session_id}/events", headers={"Authorization": "Bearer change-me"})

    assert nudge_response.status == "nudged"
    assert events_response is not None
    assert events_response.status_code == 200
    event_types = [item["event_type"] for item in events_response.json()["events"]]
    assert "nudged" in event_types


def test_nudge_primary_session_skips_after_summary_registration(
    monkeypatch, migrated_public_schema
) -> None:
    monkeypatch.setenv("AICODING_SESSION_BACKEND", "fake")
    monkeypatch.setenv("AICODING_SESSION_IDLE_THRESHOLD_SECONDS", "1")
    monkeypatch.setenv("AICODING_SESSION_POLL_INTERVAL_SECONDS", "0.05")
    monkeypatch.setenv("AICODING_SESSION_MAX_NUDGE_COUNT", "2")
    with TestClient(create_app()) as client:
        create_response = client.post(
            "/api/nodes/create",
            headers={"Authorization": "Bearer change-me"},
            json={"kind": "epic", "title": "Summarized Idle Node", "prompt": "boot prompt"},
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
        session_id = bind_response.json()["session_id"]
        session_name = bind_response.json()["session_name"]
        db_session_factory = client.app.state.db_session_factory
        progress_response = client.get(f"/api/node-runs/{node_id}", headers={"Authorization": "Bearer change-me"})
        compiled_subtask_id = progress_response.json()["state"]["current_compiled_subtask_id"]
        start_subtask_attempt(db_session_factory, logical_node_id=UUID(node_id), compiled_subtask_id=UUID(compiled_subtask_id))
        register_summary(
            db_session_factory,
            logical_node_id=UUID(node_id),
            summary_type="subtask",
            summary_path="summaries/implementation.md",
            content="done enough",
        )
        adapter = client.app.state.session_adapter
        adapter._sessions[session_name].pane_text = "• Waiting; no subtask work has started.\n"
        adapter.advance_idle(session_name, seconds=30.0)
        resource_catalog = client.app.state.resource_catalog
        with session_scope(client.app.state.db_session_factory) as session:
            durable = session.get(DurableSession, UUID(session_id))
            assert durable is not None
            durable.last_heartbeat_at = datetime.now(timezone.utc) - timedelta(seconds=10)

        inspect_primary_session_screen_state(
            client.app.state.db_session_factory,
            logical_node_id=UUID(node_id),
            adapter=adapter,
            poller=client.app.state.session_poller,
            persist=True,
        )
        inspect_primary_session_screen_state(
            client.app.state.db_session_factory,
            logical_node_id=UUID(node_id),
            adapter=adapter,
            poller=client.app.state.session_poller,
            persist=True,
        )
        nudge_response = nudge_primary_session(
            client.app.state.db_session_factory,
            logical_node_id=UUID(node_id),
            adapter=adapter,
            poller=client.app.state.session_poller,
            max_nudge_count=2,
            idle_nudge_text=resource_catalog.load_text("prompt_pack_default", "recovery/idle_nudge.md").content,
            repeated_nudge_text=resource_catalog.load_text("prompt_pack_default", "recovery/repeated_missed_step.md").content,
        )
        events_response = client.get(f"/api/sessions/{session_id}/events", headers={"Authorization": "Bearer change-me"})

    assert nudge_response.status == "summary_registered"
    assert events_response is not None
    assert events_response.status_code == 200
    events = events_response.json()["events"]
    event_types = [item["event_type"] for item in events]
    assert "nudged" not in event_types
    assert any(
        item["event_type"] == "nudge_skipped"
        and item["payload_json"].get("reason") == "summary_already_registered"
        for item in events
    )


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
