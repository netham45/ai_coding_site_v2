from __future__ import annotations

import subprocess
import time
from pathlib import Path
from uuid import UUID

import pytest
from sqlalchemy import create_engine, text


def _tmux_capture(session_name: str) -> str:
    result = subprocess.run(
        ["tmux", "capture-pane", "-p", "-t", session_name],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return f"[tmux capture failed] {result.stderr.strip()}"
    return result.stdout


def _tmux_kill(session_name: str) -> None:
    subprocess.run(
        ["tmux", "kill-session", "-t", session_name],
        text=True,
        capture_output=True,
        check=False,
    )


def _write_scoped_parent_overrides(workspace_root: Path, *, node_kinds: tuple[str, ...]) -> None:
    overrides_root = workspace_root / "resources" / "yaml" / "overrides" / "nodes"
    overrides_root.mkdir(parents=True, exist_ok=True)
    for node_kind in node_kinds:
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
            )
            + "\n",
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
            )
            + "\n",
            encoding="utf-8",
        )


def _compile_ready_and_start_node(real_daemon_harness, *, node_id: str) -> None:
    compile_result = real_daemon_harness.cli("workflow", "compile", "--node", node_id)
    start_result = real_daemon_harness.cli("node", "run", "start", "--node", node_id)
    assert compile_result.exit_code == 0, compile_result.stderr
    assert start_result.exit_code == 0, start_result.stderr


def _wait_for_runtime_child(real_daemon_harness, *, parent_node_id: str, expected_kind: str, timeout_seconds: float = 180.0) -> dict[str, object]:
    bind_result = real_daemon_harness.cli("session", "bind", "--node", parent_node_id)
    assert bind_result.exit_code == 0, bind_result.stderr
    session_name = str(bind_result.json()["session_name"])
    deadline = time.time() + timeout_seconds
    last_children_payload: dict[str, object] | None = None
    last_pane_text = ""
    try:
        while time.time() < deadline:
            children_result = real_daemon_harness.cli("node", "children", "--node", parent_node_id, "--versions")
            assert children_result.exit_code == 0, children_result.stderr
            last_children_payload = children_result.json()
            for child in last_children_payload["children"]:
                if child["kind"] == expected_kind:
                    return child
            last_pane_text = _tmux_capture(session_name)
            time.sleep(2.0)
    finally:
        _tmux_kill(session_name)
    raise AssertionError(
        f"Timed out waiting for node {parent_node_id} to create a {expected_kind} child through the real tmux/provider session.\n"
        f"session_name={session_name}\n"
        f"pane_text=\n{last_pane_text}\n"
        f"last_children_payload={last_children_payload}"
    )


def _wait_for_runtime_children(
    real_daemon_harness,
    *,
    parent_node_id: str,
    expected_kind: str,
    minimum_count: int,
    timeout_seconds: float = 180.0,
) -> list[dict[str, object]]:
    bind_result = real_daemon_harness.cli("session", "bind", "--node", parent_node_id)
    assert bind_result.exit_code == 0, bind_result.stderr
    session_name = str(bind_result.json()["session_name"])
    deadline = time.time() + timeout_seconds
    last_children_payload: dict[str, object] | None = None
    last_pane_text = ""
    try:
        while time.time() < deadline:
            children_result = real_daemon_harness.cli("node", "children", "--node", parent_node_id, "--versions")
            assert children_result.exit_code == 0, children_result.stderr
            last_children_payload = children_result.json()
            matching_children = [child for child in last_children_payload["children"] if child["kind"] == expected_kind]
            if len(matching_children) >= minimum_count:
                return matching_children
            last_pane_text = _tmux_capture(session_name)
            time.sleep(2.0)
    finally:
        _tmux_kill(session_name)
    raise AssertionError(
        f"Timed out waiting for node {parent_node_id} to create at least {minimum_count} {expected_kind} children through the real tmux/provider session.\n"
        f"session_name={session_name}\n"
        f"pane_text=\n{last_pane_text}\n"
        f"last_children_payload={last_children_payload}"
    )


@pytest.mark.e2e_real
def test_e2e_regeneration_and_upstream_rectification_round_trip_against_real_daemon_and_cli(
    real_daemon_harness,
) -> None:
    root_create_result = real_daemon_harness.cli(
        "node",
        "create",
        "--kind",
        "epic",
        "--title",
        "Real Rectification Root",
        "--prompt",
        "Create the root node for a dedicated real regenerate-and-rectify cycle.",
    )
    assert root_create_result.exit_code == 0, root_create_result.stderr
    root_id = str(root_create_result.json()["node_id"])

    child_create_result = real_daemon_harness.cli(
        "node",
        "create",
        "--kind",
        "phase",
        "--title",
        "Real Rectification Child",
        "--prompt",
        "Create the child node that will be rectified upstream through the dedicated real suite.",
        "--parent",
        root_id,
    )
    assert child_create_result.exit_code == 0, child_create_result.stderr
    child_id = str(child_create_result.json()["node_id"])

    regenerate_result = real_daemon_harness.cli("node", "regenerate", "--node", root_id)
    rectify_result = real_daemon_harness.cli("node", "rectify-upstream", "--node", child_id)
    history_result = real_daemon_harness.cli("node", "rebuild-history", "--node", child_id)
    versions_result = real_daemon_harness.cli("node", "versions", "--node", child_id)
    cutover_readiness_result = real_daemon_harness.cli(
        "node",
        "version",
        "cutover-readiness",
        "--version",
        str(real_daemon_harness.cli("node", "versions", "--node", child_id).json()["versions"][-1]["id"]),
    )
    coordination_result = real_daemon_harness.cli(
        "node",
        "rebuild-coordination",
        "--node",
        child_id,
        "--scope",
        "upstream",
    )

    assert regenerate_result.exit_code == 0, regenerate_result.stderr
    assert rectify_result.exit_code == 0, rectify_result.stderr
    assert history_result.exit_code == 0, history_result.stderr
    assert versions_result.exit_code == 0, versions_result.stderr
    assert cutover_readiness_result.exit_code == 0, cutover_readiness_result.stderr
    assert coordination_result.exit_code == 0, coordination_result.stderr

    regenerate_payload = regenerate_result.json()
    rectify_payload = rectify_result.json()
    history_payload = history_result.json()
    versions_payload = versions_result.json()
    cutover_readiness_payload = cutover_readiness_result.json()
    coordination_payload = coordination_result.json()

    candidate_version_id = str(versions_payload["versions"][-1]["id"])

    assert regenerate_payload["scope"] == "subtree"
    assert rectify_payload["scope"] == "upstream"
    assert {event["scope"] for event in history_payload["events"]} >= {"subtree", "upstream"}
    assert len(versions_payload["versions"]) >= 2
    assert cutover_readiness_payload["node_version_id"] == candidate_version_id
    assert cutover_readiness_payload["status"] in {"ready", "blocked"}
    assert coordination_payload["scope"] == "upstream"
    assert coordination_payload["status"] in {"clear", "blocked"}


@pytest.mark.e2e_real
@pytest.mark.requires_tmux
@pytest.mark.requires_ai_provider
def test_e2e_regeneration_and_upstream_rectification_dependency_invalidated_fresh_restart_is_childless_and_remapped(
    real_daemon_harness,
) -> None:
    _write_scoped_parent_overrides(real_daemon_harness.workspace_root, node_kinds=("epic", "phase"))
    parent_create = real_daemon_harness.cli(
        "workflow",
        "start",
        "--kind",
        "epic",
        "--title",
        "Real Rectification Dependency Parent",
        "--prompt",
        "Create a parent with sibling dependency invalidation during the dedicated real rectify/upstream suite.",
    )
    assert parent_create.exit_code == 0, parent_create.stderr
    parent_id = str(parent_create.json()["node"]["node_id"])
    phase_children = _wait_for_runtime_children(
        real_daemon_harness,
        parent_node_id=parent_id,
        expected_kind="phase",
        minimum_count=2,
    )
    left_id = str(phase_children[0]["node_id"])
    right_id = str(phase_children[1]["node_id"])

    _compile_ready_and_start_node(real_daemon_harness, node_id=right_id)
    runtime_child = _wait_for_runtime_child(real_daemon_harness, parent_node_id=right_id, expected_kind="plan")
    add_dependency = real_daemon_harness.cli("node", "dependency-add", "--node", right_id, "--depends-on", left_id)
    rectify_result = real_daemon_harness.cli("node", "rectify-upstream", "--node", left_id)
    history_result = real_daemon_harness.cli("node", "rebuild-history", "--node", left_id)
    parent_versions_result = real_daemon_harness.cli("node", "versions", "--node", parent_id)
    left_versions_result = real_daemon_harness.cli("node", "versions", "--node", left_id)
    right_versions_result = real_daemon_harness.cli("node", "versions", "--node", right_id)

    assert add_dependency.exit_code == 0, add_dependency.stderr
    assert rectify_result.exit_code == 0, rectify_result.stderr
    assert history_result.exit_code == 0, history_result.stderr
    assert parent_versions_result.exit_code == 0, parent_versions_result.stderr
    assert left_versions_result.exit_code == 0, left_versions_result.stderr
    assert right_versions_result.exit_code == 0, right_versions_result.stderr

    history_payload = history_result.json()
    parent_versions_payload = parent_versions_result.json()
    left_versions_payload = left_versions_result.json()
    right_versions_payload = right_versions_result.json()

    parent_candidate_id = str(parent_versions_payload["versions"][-1]["id"])
    left_candidate_id = str(left_versions_payload["versions"][-1]["id"])
    right_candidate_id = str(right_versions_payload["versions"][-1]["id"])

    assert runtime_child["kind"] == "plan"
    assert parent_versions_payload["versions"][-1]["status"] == "candidate"
    assert left_versions_payload["versions"][-1]["status"] == "candidate"
    assert right_versions_payload["versions"][-1]["status"] == "candidate"
    assert any(
        event["event_kind"] == "candidate_created"
        and event["target_node_version_id"] == right_candidate_id
        and event["details_json"].get("candidate_role") == "dependency_invalidated_fresh_restart"
        for event in history_payload["events"]
    )

    engine = create_engine(real_daemon_harness.database_url, future=True)
    try:
        with engine.connect() as connection:
            right_candidate_child_count = connection.execute(
                text("select count(*) from node_children where parent_node_version_id = :version_id"),
                {"version_id": right_candidate_id},
            ).scalar_one()
            right_candidate_parent_version_id = connection.execute(
                text("select parent_node_version_id from node_versions where id = :version_id"),
                {"version_id": right_candidate_id},
            ).scalar_one()
            parent_candidate_child_ids = {
                row[0]
                for row in connection.execute(
                    text(
                        "select child_node_version_id from node_children where parent_node_version_id = :version_id order by ordinal, created_at"
                    ),
                    {"version_id": parent_candidate_id},
                )
            }
        assert right_candidate_child_count == 0
        assert str(right_candidate_parent_version_id) == parent_candidate_id
        assert parent_candidate_child_ids == {UUID(left_candidate_id), UUID(right_candidate_id)}
    finally:
        engine.dispose()
