from __future__ import annotations

import subprocess
import time
import pytest
from sqlalchemy import create_engine, text
from uuid import UUID


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


def _compile_ready_and_start_node(real_daemon_harness, *, node_id: str) -> None:
    compile_result = real_daemon_harness.cli("workflow", "compile", "--node", node_id)
    ready_result = real_daemon_harness.cli("node", "lifecycle", "transition", "--node", node_id, "--state", "READY")
    start_result = real_daemon_harness.cli("node", "run", "start", "--node", node_id)
    assert compile_result.exit_code == 0, compile_result.stderr
    assert ready_result.exit_code == 0, ready_result.stderr
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
def test_flow_10_regenerate_and_rectify_runs_against_real_daemon_and_real_cli(real_daemon_harness) -> None:
    root_create_result = real_daemon_harness.cli(
        "node",
        "create",
        "--kind",
        "epic",
        "--title",
        "Real E2E Flow 10 Root",
        "--prompt",
        "Create the root node for a real regenerate-and-rectify cycle.",
    )
    assert root_create_result.exit_code == 0, root_create_result.stderr
    root_id = str(root_create_result.json()["node_id"])

    child_create_result = real_daemon_harness.cli(
        "node",
        "create",
        "--kind",
        "phase",
        "--title",
        "Real E2E Flow 10 Child",
        "--prompt",
        "Create the child node that will be rectified upstream.",
        "--parent",
        root_id,
    )
    assert child_create_result.exit_code == 0, child_create_result.stderr
    child_id = str(child_create_result.json()["node_id"])

    regenerate_result = real_daemon_harness.cli("node", "regenerate", "--node", root_id)
    rectify_result = real_daemon_harness.cli("node", "rectify-upstream", "--node", child_id)
    history_result = real_daemon_harness.cli("node", "rebuild-history", "--node", child_id)
    versions_result = real_daemon_harness.cli("node", "versions", "--node", child_id)

    assert regenerate_result.exit_code == 0, regenerate_result.stderr
    assert rectify_result.exit_code == 0, rectify_result.stderr
    assert history_result.exit_code == 0, history_result.stderr
    assert versions_result.exit_code == 0, versions_result.stderr

    regenerate_payload = regenerate_result.json()
    rectify_payload = rectify_result.json()
    history_payload = history_result.json()
    versions_payload = versions_result.json()

    candidate_version_id = str(versions_payload["versions"][-1]["id"])

    cutover_readiness_result = real_daemon_harness.cli(
        "node",
        "version",
        "cutover-readiness",
        "--version",
        candidate_version_id,
    )
    coordination_result = real_daemon_harness.cli(
        "node",
        "rebuild-coordination",
        "--node",
        child_id,
        "--scope",
        "upstream",
    )

    assert cutover_readiness_result.exit_code == 0, cutover_readiness_result.stderr
    assert coordination_result.exit_code == 0, coordination_result.stderr

    cutover_readiness_payload = cutover_readiness_result.json()
    coordination_payload = coordination_result.json()

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
def test_flow_10_supersede_cutover_does_not_reuse_old_primary_session_after_authority_moves(
    real_daemon_harness_factory,
) -> None:
    harness = real_daemon_harness_factory(session_backend="tmux")
    session_names_to_cleanup: set[str] = set()
    try:
        start_result = harness.cli(
            "workflow",
            "start",
            "--kind",
            "epic",
            "--title",
            "Real E2E Flow 10 Version Authority",
            "--prompt",
            "Create a node, bind a primary session, supersede it, cut over to the new version, and prove the old session is not treated as current work afterward.",
        )
        assert start_result.exit_code == 0, start_result.stderr
        node_id = str(start_result.json()["node"]["node_id"])
        old_version_id = str(start_result.json()["node_version_id"])

        bind_result = harness.cli("session", "bind", "--node", node_id)
        assert bind_result.exit_code == 0, bind_result.stderr
        bind_payload = bind_result.json()
        old_session_id = str(bind_payload["session_id"])
        old_session_name = str(bind_payload["session_name"])
        session_names_to_cleanup.add(old_session_name)

        cancel_result = harness.cli("node", "cancel", "--node", node_id)
        supersede_result = harness.cli(
            "node",
            "supersede",
            "--node",
            node_id,
            "--title",
            "Real E2E Flow 10 Version Authority v2",
        )
        assert cancel_result.exit_code == 0, cancel_result.stderr
        assert supersede_result.exit_code == 0, supersede_result.stderr
        candidate_version_id = str(supersede_result.json()["id"])

        cutover_result = harness.cli("node", "version", "cutover", "--version", candidate_version_id)
        current_after_cutover = harness.cli("session", "show-current")
        list_after_cutover = harness.cli("session", "list", "--node", node_id)

        assert cutover_result.exit_code == 0, cutover_result.stderr
        assert current_after_cutover.exit_code == 0, current_after_cutover.stderr
        assert list_after_cutover.exit_code == 0, list_after_cutover.stderr

        current_after_cutover_payload = current_after_cutover.json()
        list_after_cutover_payload = list_after_cutover.json()

        assert current_after_cutover_payload["status"] == "none"
        assert list_after_cutover_payload["sessions"] == []

        new_run_start = harness.cli("node", "run", "start", "--node", node_id)
        current_after_restart = harness.cli("session", "show-current")
        node_show_result = harness.cli("node", "show", "--node", node_id)
        lifecycle_result = harness.cli("node", "lifecycle", "show", "--node", node_id)

        assert new_run_start.exit_code == 0, new_run_start.stderr
        assert current_after_restart.exit_code == 0, current_after_restart.stderr
        assert node_show_result.exit_code == 0, node_show_result.stderr
        assert lifecycle_result.exit_code == 0, lifecycle_result.stderr

        current_after_restart_payload = current_after_restart.json()
        node_show_payload = node_show_result.json()
        lifecycle_payload = lifecycle_result.json()

        assert old_version_id != candidate_version_id
        assert old_session_id
        assert old_session_name
        assert current_after_restart_payload["status"] == "none"
        assert str(node_show_payload["authoritative_node_version_id"]) == candidate_version_id
        assert str(lifecycle_payload["node_version_id"]) == candidate_version_id
    finally:
        for session_name in session_names_to_cleanup:
            import subprocess

            subprocess.run(["tmux", "kill-session", "-t", session_name], check=False, capture_output=True, text=True)


@pytest.mark.e2e_real
@pytest.mark.requires_tmux
@pytest.mark.requires_ai_provider
def test_flow_10_dependency_invalidated_fresh_restart_is_childless_and_remapped_into_parent_candidate(
    real_daemon_harness,
) -> None:
    parent_create = real_daemon_harness.cli(
        "workflow",
        "start",
        "--kind",
        "epic",
        "--title",
        "Real E2E Flow 10 Dependency Parent",
        "--prompt",
        "Create a parent with sibling dependency invalidation during regenerate/rectify.",
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


@pytest.mark.e2e_real
def test_flow_10_grouped_lineage_cutover_moves_rebuilt_child_scope_with_parent_candidate(
    real_daemon_harness,
) -> None:
    root_create_result = real_daemon_harness.cli(
        "node",
        "create",
        "--kind",
        "epic",
        "--title",
        "Real E2E Flow 10 Grouped Cutover Root",
        "--prompt",
        "Create the root node for grouped rebuild-backed cutover.",
    )
    assert root_create_result.exit_code == 0, root_create_result.stderr
    root_id = str(root_create_result.json()["node_id"])

    child_create_result = real_daemon_harness.cli(
        "node",
        "create",
        "--kind",
        "phase",
        "--title",
        "Real E2E Flow 10 Grouped Cutover Child",
        "--prompt",
        "Create the child node that should cut over with the rebuilt parent scope.",
        "--parent",
        root_id,
    )
    assert child_create_result.exit_code == 0, child_create_result.stderr
    child_id = str(child_create_result.json()["node_id"])

    regenerate_result = real_daemon_harness.cli("node", "regenerate", "--node", root_id)
    root_versions_result = real_daemon_harness.cli("node", "versions", "--node", root_id)
    child_versions_result = real_daemon_harness.cli("node", "versions", "--node", child_id)

    assert regenerate_result.exit_code == 0, regenerate_result.stderr
    assert root_versions_result.exit_code == 0, root_versions_result.stderr
    assert child_versions_result.exit_code == 0, child_versions_result.stderr

    root_versions_payload = root_versions_result.json()
    child_versions_payload = child_versions_result.json()
    root_candidate_id = str(root_versions_payload["versions"][-1]["id"])
    child_candidate_id = str(child_versions_payload["versions"][-1]["id"])

    cutover_readiness_result = real_daemon_harness.cli(
        "node",
        "version",
        "cutover-readiness",
        "--version",
        root_candidate_id,
    )
    cutover_result = real_daemon_harness.cli("node", "version", "cutover", "--version", root_candidate_id)
    root_show_result = real_daemon_harness.cli("node", "show", "--node", root_id)
    child_show_result = real_daemon_harness.cli("node", "show", "--node", child_id)
    root_versions_after_result = real_daemon_harness.cli("node", "versions", "--node", root_id)
    child_versions_after_result = real_daemon_harness.cli("node", "versions", "--node", child_id)

    assert cutover_readiness_result.exit_code == 0, cutover_readiness_result.stderr
    assert cutover_result.exit_code == 0, cutover_result.stderr
    assert root_show_result.exit_code == 0, root_show_result.stderr
    assert child_show_result.exit_code == 0, child_show_result.stderr
    assert root_versions_after_result.exit_code == 0, root_versions_after_result.stderr
    assert child_versions_after_result.exit_code == 0, child_versions_after_result.stderr

    cutover_readiness_payload = cutover_readiness_result.json()
    root_show_payload = root_show_result.json()
    child_show_payload = child_show_result.json()
    root_versions_after_payload = root_versions_after_result.json()
    child_versions_after_payload = child_versions_after_result.json()

    assert cutover_readiness_payload["status"] == "ready"
    assert root_show_payload["authoritative_node_version_id"] == root_candidate_id
    assert child_show_payload["authoritative_node_version_id"] == child_candidate_id
    assert root_versions_after_payload["versions"][-1]["status"] == "authoritative"
    assert child_versions_after_payload["versions"][-1]["status"] == "authoritative"
    assert root_versions_after_payload["versions"][0]["status"] == "superseded"
    assert child_versions_after_payload["versions"][0]["status"] == "superseded"
