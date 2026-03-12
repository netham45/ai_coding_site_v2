from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text

from tests.helpers.e2e import RealDaemonHarness

pytestmark = [pytest.mark.e2e_bringup, pytest.mark.requires_tmux, pytest.mark.requires_ai_provider]


def _git(repo_path: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_path,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(result.stderr or result.stdout)
    return result.stdout.strip()


def _write_json(path: Path, payload: dict[str, str]) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


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


def _compile_ready_and_start_node(harness: RealDaemonHarness, *, node_id: str) -> None:
    compile_result = harness.cli("workflow", "compile", "--node", node_id)
    start_result = harness.cli("node", "run", "start", "--node", node_id)
    assert compile_result.exit_code == 0, compile_result.stderr
    assert start_result.exit_code == 0, start_result.stderr


def _complete_node_run(harness: RealDaemonHarness, *, node_id: str, timeout_seconds: float = 180.0) -> None:
    bind_result = harness.cli("session", "bind", "--node", node_id)
    assert bind_result.exit_code == 0, bind_result.stderr
    session_name = str(bind_result.json()["session_name"])
    deadline = time.time() + timeout_seconds
    last_run_payload: dict[str, object] | None = None
    last_session_payload: dict[str, object] | None = None
    last_pane_text = ""
    try:
        while time.time() < deadline:
            session_show = harness.cli("session", "show", "--node", node_id)
            if session_show.exit_code == 0:
                last_session_payload = session_show.json()
                session_name = str(last_session_payload["session_name"])
                recovery_classification = str(last_session_payload["recovery_classification"])
                if recovery_classification in {"stale_but_recoverable", "detached"}:
                    resume_result = harness.cli("session", "resume", "--node", node_id)
                    assert resume_result.exit_code == 0, resume_result.stderr
                    resume_payload = resume_result.json()
                    resumed_session = resume_payload.get("session")
                    if isinstance(resumed_session, dict) and resumed_session.get("session_name"):
                        session_name = str(resumed_session["session_name"])

            run_show = harness.cli("node", "run", "show", "--node", node_id)
            if run_show.exit_code == 0:
                last_run_payload = run_show.json()
                run_status = str(last_run_payload["run"]["run_status"])
                if run_status in {"COMPLETE", "COMPLETED"}:
                    return
                if run_status in {"FAILED", "PAUSED"}:
                    raise AssertionError(
                        f"Real node session stopped before completion for node {node_id}.\n"
                        f"run_status={run_status}\n"
                        f"pane_text=\n{last_pane_text}\n"
                        f"last_run_payload={last_run_payload}"
                    )
            else:
                lifecycle_show = harness.cli("node", "lifecycle", "show", "--node", node_id)
                assert lifecycle_show.exit_code == 0, lifecycle_show.stderr
                lifecycle_payload = lifecycle_show.json()
                if lifecycle_payload["lifecycle_state"] == "COMPLETE":
                    return
                raise AssertionError(
                    f"{run_show.stderr}\n"
                    f"lifecycle_payload={lifecycle_payload}\n"
                    f"last_session_payload={last_session_payload}"
                )
            last_pane_text = _tmux_capture(session_name)
            time.sleep(2.0)
    finally:
        _tmux_kill(session_name)
    raise AssertionError(
        f"Timed out waiting for node {node_id} to complete through the real tmux/provider session.\n"
        f"session_name={session_name}\n"
        f"pane_text=\n{last_pane_text}\n"
        f"last_run_payload={last_run_payload}\n"
        f"last_session_payload={last_session_payload}"
    )


def _wait_for_runtime_child(
    harness: RealDaemonHarness,
    *,
    parent_node_id: str,
    expected_kind: str,
    timeout_seconds: float = 180.0,
) -> dict[str, object]:
    bind_result = harness.cli("session", "bind", "--node", parent_node_id)
    assert bind_result.exit_code == 0, bind_result.stderr
    session_name = str(bind_result.json()["session_name"])
    deadline = time.time() + timeout_seconds
    last_children_payload: dict[str, object] | None = None
    last_pane_text = ""
    try:
        while time.time() < deadline:
            children_result = harness.cli("node", "children", "--node", parent_node_id, "--versions")
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


def _wait_for(predicate, *, timeout_seconds: float = 30.0, sleep_seconds: float = 0.5, failure_message: str):
    deadline = time.time() + timeout_seconds
    last_value = None
    while time.time() < deadline:
        last_value = predicate()
        if last_value:
            return last_value
        time.sleep(sleep_seconds)
    raise AssertionError(f"{failure_message}\nlast_value={last_value}")


def _dependency_is_ready(payload: dict[str, object]) -> bool:
    if "ready" in payload:
        return bool(payload["ready"])
    return payload.get("status") == "ready"


def _dependency_blockers(payload: object) -> list[dict[str, object]]:
    if isinstance(payload, dict):
        if "dependency_blockers" in payload:
            return list(payload["dependency_blockers"])
        if "blockers" in payload and isinstance(payload["blockers"], list):
            return list(payload["blockers"])
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    return []


def _has_blocker_kind(payload: object, blocker_kind: str) -> bool:
    return any(item.get("blocker_kind") == blocker_kind for item in _dependency_blockers(payload))


def _setup_parent_and_children(harness: RealDaemonHarness, tmp_path: Path) -> dict[str, object]:
    parent_create = harness.cli(
        "node",
        "create",
        "--kind",
        "epic",
        "--title",
        "Incremental Merge Parent",
        "--prompt",
        "Create a parent whose sibling children need merge-backed visibility.",
    )
    assert parent_create.exit_code == 0, parent_create.stderr
    parent_id = str(parent_create.json()["node_id"])

    child_a_create = harness.cli(
        "node",
        "child",
        "create",
        "--parent",
        parent_id,
        "--kind",
        "phase",
        "--title",
        "Discovery Child",
        "--prompt",
        "Do the prerequisite sibling work.",
    )
    child_b_create = harness.cli(
        "node",
        "child",
        "create",
        "--parent",
        parent_id,
        "--kind",
        "phase",
        "--title",
        "Implementation Child",
        "--prompt",
        "Consume the prerequisite sibling work after it is merged upward.",
    )
    assert child_a_create.exit_code == 0, child_a_create.stderr
    assert child_b_create.exit_code == 0, child_b_create.stderr
    child_a_id = str(child_a_create.json()["node_id"])
    child_b_id = str(child_b_create.json()["node_id"])

    dependency_add = harness.cli("node", "dependency-add", "--node", child_b_id, "--depends-on", child_a_id)
    assert dependency_add.exit_code == 0, dependency_add.stderr

    parent_version_id = str(harness.cli("node", "versions", "--node", parent_id).json()["versions"][0]["id"])
    child_a_version_id = str(harness.cli("node", "versions", "--node", child_a_id).json()["versions"][0]["id"])
    child_b_version_id = str(harness.cli("node", "versions", "--node", child_b_id).json()["versions"][0]["id"])

    parent_files = tmp_path / "parent-bootstrap.json"
    _write_json(parent_files, {"shared.txt": "seed\n"})
    parent_bootstrap = harness.cli(
        "git",
        "bootstrap-node",
        "--version",
        parent_version_id,
        "--files-file",
        str(parent_files),
        "--replace-existing",
    )
    child_a_bootstrap = harness.cli(
        "git",
        "bootstrap-node",
        "--version",
        child_a_version_id,
        "--base-version",
        parent_version_id,
        "--replace-existing",
    )
    child_b_bootstrap = harness.cli(
        "git",
        "bootstrap-node",
        "--version",
        child_b_version_id,
        "--base-version",
        parent_version_id,
        "--replace-existing",
    )
    assert parent_bootstrap.exit_code == 0, parent_bootstrap.stderr
    assert child_a_bootstrap.exit_code == 0, child_a_bootstrap.stderr
    assert child_b_bootstrap.exit_code == 0, child_b_bootstrap.stderr

    parent_status = harness.cli("git", "status", "show", "--version", parent_version_id)
    child_a_status = harness.cli("git", "status", "show", "--version", child_a_version_id)
    child_b_status = harness.cli("git", "status", "show", "--version", child_b_version_id)
    assert parent_status.exit_code == 0, parent_status.stderr
    assert child_a_status.exit_code == 0, child_a_status.stderr
    assert child_b_status.exit_code == 0, child_b_status.stderr

    _compile_ready_and_start_node(harness, node_id=parent_id)
    _compile_ready_and_start_node(harness, node_id=child_a_id)
    _compile_ready_and_start_node(harness, node_id=child_b_id)

    return {
        "parent_id": parent_id,
        "child_a_id": child_a_id,
        "child_b_id": child_b_id,
        "parent_version_id": parent_version_id,
        "child_a_version_id": child_a_version_id,
        "child_b_version_id": child_b_version_id,
        "parent_repo": Path(parent_status.json()["repo_path"]),
        "child_a_repo": Path(child_a_status.json()["repo_path"]),
        "child_b_repo": Path(child_b_status.json()["repo_path"]),
    }


@pytest.mark.requires_git
def test_e2e_incremental_parent_merge_dependency_invalidated_grouped_cutover_rematerializes_authoritative_child(
    real_daemon_harness_factory,
    tmp_path: Path,
) -> None:
    harness = real_daemon_harness_factory(extra_env={"AICODING_SESSION_POLL_INTERVAL_SECONDS": "0.1"})

    parent_create = harness.cli(
        "node",
        "create",
        "--kind",
        "epic",
        "--title",
        "Dependency Invalidated Cutover Parent",
        "--prompt",
        "Create a parent whose dependent sibling must rematerialize after grouped cutover and real merge progression.",
    )
    assert parent_create.exit_code == 0, parent_create.stderr
    parent_id = str(parent_create.json()["node_id"])

    left_create = harness.cli(
        "node",
        "child",
        "create",
        "--parent",
        parent_id,
        "--kind",
        "phase",
        "--title",
        "Dependency Prerequisite Phase",
        "--prompt",
        "Complete and merge first.",
    )
    right_create = harness.cli(
        "node",
        "child",
        "create",
        "--parent",
        parent_id,
        "--kind",
        "phase",
        "--title",
        "Dependency Blocked Phase",
        "--prompt",
        "Restart fresh after the prerequisite is regenerated and merged.",
    )
    assert left_create.exit_code == 0, left_create.stderr
    assert right_create.exit_code == 0, right_create.stderr
    left_id = str(left_create.json()["node_id"])
    right_id = str(right_create.json()["node_id"])

    _compile_ready_and_start_node(harness, node_id=right_id)
    runtime_child = _wait_for_runtime_child(harness, parent_node_id=right_id, expected_kind="plan")
    dependency_add = harness.cli("node", "dependency-add", "--node", right_id, "--depends-on", left_id)
    assert dependency_add.exit_code == 0, dependency_add.stderr

    original_child_ids = {str(runtime_child["node_id"])}
    assert original_child_ids

    parent_version_id = str(harness.cli("node", "versions", "--node", parent_id).json()["versions"][0]["id"])
    left_version_id = str(harness.cli("node", "versions", "--node", left_id).json()["versions"][0]["id"])
    right_version_id = str(harness.cli("node", "versions", "--node", right_id).json()["versions"][0]["id"])

    parent_files = tmp_path / "dependency-invalidated-parent-bootstrap.json"
    _write_json(parent_files, {"shared.txt": "seed\n"})
    for args in [
        ("git", "bootstrap-node", "--version", parent_version_id, "--files-file", str(parent_files), "--replace-existing"),
        ("git", "bootstrap-node", "--version", left_version_id, "--base-version", parent_version_id, "--replace-existing"),
        ("git", "bootstrap-node", "--version", right_version_id, "--base-version", parent_version_id, "--replace-existing"),
    ]:
        result = harness.cli(*args)
        assert result.exit_code == 0, result.stderr

    rectify_result = harness.cli("node", "rectify-upstream", "--node", left_id)
    assert rectify_result.exit_code == 0, rectify_result.stderr

    parent_versions_payload = harness.cli("node", "versions", "--node", parent_id).json()
    left_versions_payload = harness.cli("node", "versions", "--node", left_id).json()
    right_versions_payload = harness.cli("node", "versions", "--node", right_id).json()
    parent_candidate_id = str(parent_versions_payload["versions"][-1]["id"])
    left_candidate_id = str(left_versions_payload["versions"][-1]["id"])
    right_candidate_id = str(right_versions_payload["versions"][-1]["id"])

    for args in [
        ("git", "bootstrap-node", "--version", parent_candidate_id, "--base-version", parent_version_id, "--replace-existing"),
        ("git", "bootstrap-node", "--version", left_candidate_id, "--base-version", parent_candidate_id, "--replace-existing"),
        ("git", "bootstrap-node", "--version", right_candidate_id, "--base-version", parent_candidate_id, "--replace-existing"),
    ]:
        result = harness.cli(*args)
        assert result.exit_code == 0, result.stderr

    parent_readiness = harness.cli("node", "version", "cutover-readiness", "--version", parent_candidate_id)
    right_readiness = harness.cli("node", "version", "cutover-readiness", "--version", right_candidate_id)
    cutover_result = harness.cli("node", "version", "cutover", "--version", parent_candidate_id)
    assert parent_readiness.exit_code == 0, parent_readiness.stderr
    assert right_readiness.exit_code == 0, right_readiness.stderr
    assert cutover_result.exit_code == 0, cutover_result.stderr
    assert parent_readiness.json()["status"] == "ready_with_follow_on_replay"
    assert right_readiness.json()["status"] == "blocked"

    _compile_ready_and_start_node(harness, node_id=left_id)
    left_candidate_repo = Path(harness.cli("git", "status", "show", "--version", left_candidate_id).json()["repo_path"])
    (left_candidate_repo / "shared.txt").write_text("seed\nfrom-rectified-left\n", encoding="utf-8")
    _git(left_candidate_repo, "add", ".")
    _git(left_candidate_repo, "commit", "-m", "Dependency prerequisite final change after grouped cutover")
    finalize_left = harness.cli("git", "finalize-node", "--node", left_id)
    assert finalize_left.exit_code == 0, finalize_left.stderr
    _complete_node_run(harness, node_id=left_id)

    def _rematerialized_state():
        dependency = harness.cli("node", "dependency-status", "--node", right_id)
        children = harness.cli("node", "children", "--node", right_id, "--versions")
        lifecycle = harness.cli("node", "lifecycle", "show", "--node", right_id)
        show = harness.cli("node", "show", "--node", right_id)
        versions = harness.cli("node", "versions", "--node", right_id)
        merge_events = harness.cli("git", "merge-events", "show", "--node", parent_id)
        status = harness.cli("git", "status", "show", "--version", right_candidate_id)
        assert dependency.exit_code == 0, dependency.stderr
        assert children.exit_code == 0, children.stderr
        assert lifecycle.exit_code == 0, lifecycle.stderr
        assert show.exit_code == 0, show.stderr
        assert versions.exit_code == 0, versions.stderr
        assert merge_events.exit_code == 0, merge_events.stderr
        assert status.exit_code == 0, status.stderr

        dependency_payload = dependency.json()
        children_payload = children.json()
        lifecycle_payload = lifecycle.json()
        show_payload = show.json()
        versions_payload = versions.json()
        merge_events_payload = merge_events.json()
        status_payload = status.json()
        current_child_ids = {str(child["node_id"]) for child in children_payload["children"]}

        if (
            current_child_ids
            and current_child_ids.isdisjoint(original_child_ids)
            and lifecycle_payload["lifecycle_state"] != "WAITING_ON_SIBLING_DEPENDENCY"
            and (_dependency_is_ready(dependency_payload) or _has_blocker_kind(dependency_payload, "already_running"))
            and merge_events_payload["events"]
        ):
            return {
                "dependency": dependency_payload,
                "children": children_payload,
                "lifecycle": lifecycle_payload,
                "show": show_payload,
                "versions": versions_payload,
                "merge_events": merge_events_payload,
                "status": status_payload,
            }
        return None

    ready_state = _wait_for(
        _rematerialized_state,
        timeout_seconds=60.0,
        failure_message="Timed out waiting for grouped-cutover dependency-invalidated child to refresh and rematerialize after real merge progression",
    )

    merge_head = ready_state["merge_events"]["events"][-1]["parent_commit_after"]
    assert ready_state["show"]["authoritative_node_version_id"] == right_candidate_id
    assert ready_state["versions"]["versions"][-1]["status"] == "authoritative"
    assert {str(child["node_id"]) for child in ready_state["children"]["children"]}.isdisjoint(original_child_ids)
    assert ready_state["status"]["seed_commit_sha"] == merge_head
    assert ready_state["lifecycle"]["lifecycle_state"] != "WAITING_ON_SIBLING_DEPENDENCY"


@pytest.mark.requires_git
def test_e2e_incremental_parent_merge_dependency_invalidated_manual_restart_requires_explicit_reconcile(
    real_daemon_harness_factory,
    tmp_path: Path,
) -> None:
    harness = real_daemon_harness_factory(extra_env={"AICODING_SESSION_POLL_INTERVAL_SECONDS": "0.1"})

    parent_create = harness.cli(
        "node",
        "create",
        "--kind",
        "epic",
        "--title",
        "Dependency Invalidated Manual Cutover Parent",
        "--prompt",
        "Create a parent whose dependent sibling must stay blocked until manual child-tree reconciliation is applied on the fresh version.",
    )
    assert parent_create.exit_code == 0, parent_create.stderr
    parent_id = str(parent_create.json()["node_id"])

    left_create = harness.cli(
        "node",
        "child",
        "create",
        "--parent",
        parent_id,
        "--kind",
        "phase",
        "--title",
        "Manual Dependency Prerequisite Phase",
        "--prompt",
        "Complete and merge first.",
    )
    right_create = harness.cli(
        "node",
        "child",
        "create",
        "--parent",
        parent_id,
        "--kind",
        "phase",
        "--title",
        "Manual Dependency Blocked Phase",
        "--prompt",
        "Restart fresh after the prerequisite is regenerated and merged, then require explicit manual reconciliation.",
    )
    assert left_create.exit_code == 0, left_create.stderr
    assert right_create.exit_code == 0, right_create.stderr
    left_id = str(left_create.json()["node_id"])
    right_id = str(right_create.json()["node_id"])

    _compile_ready_and_start_node(harness, node_id=right_id)
    runtime_child = _wait_for_runtime_child(harness, parent_node_id=right_id, expected_kind="plan")
    dependency_add = harness.cli("node", "dependency-add", "--node", right_id, "--depends-on", left_id)
    manual_child_right = harness.cli(
        "node",
        "child",
        "create",
        "--parent",
        right_id,
        "--kind",
        "plan",
        "--title",
        "Manual Preserved Plan",
        "--prompt",
        "Preserve this child through manual reconciliation before dependency invalidation.",
    )
    reconcile_old_right = harness.cli("node", "reconcile-children", "--node", right_id, "--decision", "preserve_manual")
    assert dependency_add.exit_code == 0, dependency_add.stderr
    assert manual_child_right.exit_code == 0, manual_child_right.stderr
    assert reconcile_old_right.exit_code == 0, reconcile_old_right.stderr
    assert reconcile_old_right.json()["authority_mode"] == "manual"
    assert reconcile_old_right.json()["materialization_status"] == "manual"
    original_child_ids = {str(child["node_id"]) for child in reconcile_old_right.json()["children"]}
    assert original_child_ids
    assert str(runtime_child["node_id"]) in original_child_ids

    parent_version_id = str(harness.cli("node", "versions", "--node", parent_id).json()["versions"][0]["id"])
    left_version_id = str(harness.cli("node", "versions", "--node", left_id).json()["versions"][0]["id"])
    right_version_id = str(harness.cli("node", "versions", "--node", right_id).json()["versions"][0]["id"])

    parent_files = tmp_path / "dependency-invalidated-manual-parent-bootstrap.json"
    _write_json(parent_files, {"shared.txt": "seed\n"})
    for args in [
        ("git", "bootstrap-node", "--version", parent_version_id, "--files-file", str(parent_files), "--replace-existing"),
        ("git", "bootstrap-node", "--version", left_version_id, "--base-version", parent_version_id, "--replace-existing"),
        ("git", "bootstrap-node", "--version", right_version_id, "--base-version", parent_version_id, "--replace-existing"),
    ]:
        result = harness.cli(*args)
        assert result.exit_code == 0, result.stderr

    rectify_result = harness.cli("node", "rectify-upstream", "--node", left_id)
    assert rectify_result.exit_code == 0, rectify_result.stderr

    parent_versions_payload = harness.cli("node", "versions", "--node", parent_id).json()
    left_versions_payload = harness.cli("node", "versions", "--node", left_id).json()
    right_versions_payload = harness.cli("node", "versions", "--node", right_id).json()
    parent_candidate_id = str(parent_versions_payload["versions"][-1]["id"])
    left_candidate_id = str(left_versions_payload["versions"][-1]["id"])
    right_candidate_id = str(right_versions_payload["versions"][-1]["id"])

    for args in [
        ("git", "bootstrap-node", "--version", parent_candidate_id, "--base-version", parent_version_id, "--replace-existing"),
        ("git", "bootstrap-node", "--version", left_candidate_id, "--base-version", parent_candidate_id, "--replace-existing"),
        ("git", "bootstrap-node", "--version", right_candidate_id, "--base-version", parent_candidate_id, "--replace-existing"),
    ]:
        result = harness.cli(*args)
        assert result.exit_code == 0, result.stderr

    cutover_result = harness.cli("node", "version", "cutover", "--version", parent_candidate_id)
    assert cutover_result.exit_code == 0, cutover_result.stderr

    _compile_ready_and_start_node(harness, node_id=left_id)
    left_candidate_repo = Path(harness.cli("git", "status", "show", "--version", left_candidate_id).json()["repo_path"])
    (left_candidate_repo / "shared.txt").write_text("seed\nfrom-rectified-left\n", encoding="utf-8")
    _git(left_candidate_repo, "add", ".")
    _git(left_candidate_repo, "commit", "-m", "Manual dependency prerequisite final change after grouped cutover")
    finalize_left = harness.cli("git", "finalize-node", "--node", left_id)
    assert finalize_left.exit_code == 0, finalize_left.stderr
    _complete_node_run(harness, node_id=left_id)

    def _blocked_manual_rebuild_state():
        dependency = harness.cli("node", "dependency-status", "--node", right_id)
        children = harness.cli("node", "children", "--node", right_id, "--versions")
        lifecycle = harness.cli("node", "lifecycle", "show", "--node", right_id)
        show = harness.cli("node", "show", "--node", right_id)
        reconciliation = harness.cli("node", "child-reconciliation", "--node", right_id)
        materialization = harness.cli("node", "child-materialization", "--node", right_id)
        assert dependency.exit_code == 0, dependency.stderr
        assert children.exit_code == 0, children.stderr
        assert lifecycle.exit_code == 0, lifecycle.stderr
        assert show.exit_code == 0, show.stderr
        assert reconciliation.exit_code == 0, reconciliation.stderr
        assert materialization.exit_code == 0, materialization.stderr

        dependency_payload = dependency.json()
        children_payload = children.json()
        lifecycle_payload = lifecycle.json()
        show_payload = show.json()
        reconciliation_payload = reconciliation.json()
        materialization_payload = materialization.json()
        current_child_ids = {str(child["node_id"]) for child in children_payload["children"]}

        if (
            show_payload["authoritative_node_version_id"] == right_candidate_id
            and not current_child_ids
            and current_child_ids.isdisjoint(original_child_ids)
            and lifecycle_payload["lifecycle_state"] == "WAITING_ON_SIBLING_DEPENDENCY"
            and _has_blocker_kind(dependency_payload, "child_tree_rebuild_required")
            and reconciliation_payload["available_decisions"] == ["preserve_manual"]
        ):
            return {
                "dependency": dependency_payload,
                "children": children_payload,
                "lifecycle": lifecycle_payload,
                "show": show_payload,
                "reconciliation": reconciliation_payload,
                "materialization": materialization_payload,
            }
        return None

    blocked_state = _wait_for(
        _blocked_manual_rebuild_state,
        timeout_seconds=60.0,
        failure_message="Timed out waiting for grouped-cutover dependency-invalidated manual child to block on explicit rebuild after real merge progression",
    )

    assert blocked_state["reconciliation"]["authority_mode"] == "manual"
    assert blocked_state["children"]["children"] == []
    assert blocked_state["reconciliation"]["materialization_status"] in {"reconciliation_required", "manual"}
    assert blocked_state["materialization"]["status"] in {"not_materialized", "manual"}

    reconcile_fresh = harness.cli("node", "reconcile-children", "--node", right_id, "--decision", "preserve_manual")
    assert reconcile_fresh.exit_code == 0, reconcile_fresh.stderr

    def _manual_rebuild_gate_cleared():
        dependency = harness.cli("node", "dependency-status", "--node", right_id)
        reconciliation = harness.cli("node", "child-reconciliation", "--node", right_id)
        materialization = harness.cli("node", "child-materialization", "--node", right_id)
        assert dependency.exit_code == 0, dependency.stderr
        assert reconciliation.exit_code == 0, reconciliation.stderr
        assert materialization.exit_code == 0, materialization.stderr
        dependency_payload = dependency.json()
        reconciliation_payload = reconciliation.json()
        materialization_payload = materialization.json()
        blocker_kinds = [item["blocker_kind"] for item in dependency_payload["blockers"]]
        if (
            "child_tree_rebuild_required" not in blocker_kinds
            and reconciliation_payload["materialization_status"] == "manual"
            and reconciliation_payload["authority_mode"] == "manual"
            and materialization_payload["status"] == "manual"
            and materialization_payload["child_count"] == 0
        ):
            return {
                "dependency": dependency_payload,
                "reconciliation": reconciliation_payload,
                "materialization": materialization_payload,
            }
        return None

    cleared_state = _wait_for(
        _manual_rebuild_gate_cleared,
        timeout_seconds=30.0,
        failure_message="Timed out waiting for explicit manual reconciliation to clear child_tree_rebuild_required on the fresh dependency-invalidated version",
    )

    assert "child_tree_rebuild_required" not in [item["blocker_kind"] for item in cleared_state["dependency"]["blockers"]]
    assert cleared_state["reconciliation"]["available_decisions"] == ["preserve_manual"]


@pytest.mark.requires_git
def test_e2e_incremental_parent_merge_dependency_invalidated_manual_restart_clears_after_fresh_manual_child_create(
    real_daemon_harness_factory,
    tmp_path: Path,
) -> None:
    harness = real_daemon_harness_factory(extra_env={"AICODING_SESSION_POLL_INTERVAL_SECONDS": "0.1"})

    parent_create = harness.cli(
        "node",
        "create",
        "--kind",
        "epic",
        "--title",
        "Dependency Invalidated Manual Create Parent",
        "--prompt",
        "Create a parent whose dependent sibling must stay blocked until a fresh manual child is created on the new authoritative version.",
    )
    assert parent_create.exit_code == 0, parent_create.stderr
    parent_id = str(parent_create.json()["node_id"])

    left_create = harness.cli(
        "node",
        "child",
        "create",
        "--parent",
        parent_id,
        "--kind",
        "phase",
        "--title",
        "Manual Create Prerequisite Phase",
        "--prompt",
        "Complete and merge first.",
    )
    right_create = harness.cli(
        "node",
        "child",
        "create",
        "--parent",
        parent_id,
        "--kind",
        "phase",
        "--title",
        "Manual Create Blocked Phase",
        "--prompt",
        "Restart fresh after the prerequisite is regenerated and merged, then require fresh manual child creation.",
    )
    assert left_create.exit_code == 0, left_create.stderr
    assert right_create.exit_code == 0, right_create.stderr
    left_id = str(left_create.json()["node_id"])
    right_id = str(right_create.json()["node_id"])

    _compile_ready_and_start_node(harness, node_id=right_id)
    runtime_child = _wait_for_runtime_child(harness, parent_node_id=right_id, expected_kind="plan")
    dependency_add = harness.cli("node", "dependency-add", "--node", right_id, "--depends-on", left_id)
    manual_child_right = harness.cli(
        "node",
        "child",
        "create",
        "--parent",
        right_id,
        "--kind",
        "plan",
        "--title",
        "Manual Preserved Plan",
        "--prompt",
        "Preserve this child through manual reconciliation before dependency invalidation.",
    )
    reconcile_old_right = harness.cli("node", "reconcile-children", "--node", right_id, "--decision", "preserve_manual")
    assert dependency_add.exit_code == 0, dependency_add.stderr
    assert manual_child_right.exit_code == 0, manual_child_right.stderr
    assert reconcile_old_right.exit_code == 0, reconcile_old_right.stderr
    original_child_ids = {str(child["node_id"]) for child in reconcile_old_right.json()["children"]}
    assert original_child_ids
    assert str(runtime_child["node_id"]) in original_child_ids

    parent_version_id = str(harness.cli("node", "versions", "--node", parent_id).json()["versions"][0]["id"])
    left_version_id = str(harness.cli("node", "versions", "--node", left_id).json()["versions"][0]["id"])
    right_version_id = str(harness.cli("node", "versions", "--node", right_id).json()["versions"][0]["id"])

    parent_files = tmp_path / "dependency-invalidated-manual-create-parent-bootstrap.json"
    _write_json(parent_files, {"shared.txt": "seed\n"})
    for args in [
        ("git", "bootstrap-node", "--version", parent_version_id, "--files-file", str(parent_files), "--replace-existing"),
        ("git", "bootstrap-node", "--version", left_version_id, "--base-version", parent_version_id, "--replace-existing"),
        ("git", "bootstrap-node", "--version", right_version_id, "--base-version", parent_version_id, "--replace-existing"),
    ]:
        result = harness.cli(*args)
        assert result.exit_code == 0, result.stderr

    rectify_result = harness.cli("node", "rectify-upstream", "--node", left_id)
    assert rectify_result.exit_code == 0, rectify_result.stderr

    parent_versions_payload = harness.cli("node", "versions", "--node", parent_id).json()
    left_versions_payload = harness.cli("node", "versions", "--node", left_id).json()
    right_versions_payload = harness.cli("node", "versions", "--node", right_id).json()
    parent_candidate_id = str(parent_versions_payload["versions"][-1]["id"])
    left_candidate_id = str(left_versions_payload["versions"][-1]["id"])
    right_candidate_id = str(right_versions_payload["versions"][-1]["id"])

    for args in [
        ("git", "bootstrap-node", "--version", parent_candidate_id, "--base-version", parent_version_id, "--replace-existing"),
        ("git", "bootstrap-node", "--version", left_candidate_id, "--base-version", parent_candidate_id, "--replace-existing"),
        ("git", "bootstrap-node", "--version", right_candidate_id, "--base-version", parent_candidate_id, "--replace-existing"),
    ]:
        result = harness.cli(*args)
        assert result.exit_code == 0, result.stderr

    cutover_result = harness.cli("node", "version", "cutover", "--version", parent_candidate_id)
    assert cutover_result.exit_code == 0, cutover_result.stderr

    _compile_ready_and_start_node(harness, node_id=left_id)
    left_candidate_repo = Path(harness.cli("git", "status", "show", "--version", left_candidate_id).json()["repo_path"])
    (left_candidate_repo / "shared.txt").write_text("seed\nfrom-rectified-left\n", encoding="utf-8")
    _git(left_candidate_repo, "add", ".")
    _git(left_candidate_repo, "commit", "-m", "Manual create prerequisite final change after grouped cutover")
    finalize_left = harness.cli("git", "finalize-node", "--node", left_id)
    assert finalize_left.exit_code == 0, finalize_left.stderr
    _complete_node_run(harness, node_id=left_id)

    def _blocked_manual_rebuild_state():
        dependency = harness.cli("node", "dependency-status", "--node", right_id)
        children = harness.cli("node", "children", "--node", right_id, "--versions")
        lifecycle = harness.cli("node", "lifecycle", "show", "--node", right_id)
        show = harness.cli("node", "show", "--node", right_id)
        reconciliation = harness.cli("node", "child-reconciliation", "--node", right_id)
        assert dependency.exit_code == 0, dependency.stderr
        assert children.exit_code == 0, children.stderr
        assert lifecycle.exit_code == 0, lifecycle.stderr
        assert show.exit_code == 0, show.stderr
        assert reconciliation.exit_code == 0, reconciliation.stderr

        dependency_payload = dependency.json()
        children_payload = children.json()
        lifecycle_payload = lifecycle.json()
        show_payload = show.json()
        reconciliation_payload = reconciliation.json()
        current_child_ids = {str(child["node_id"]) for child in children_payload["children"]}

        if (
            show_payload["authoritative_node_version_id"] == right_candidate_id
            and not current_child_ids
            and current_child_ids.isdisjoint(original_child_ids)
            and lifecycle_payload["lifecycle_state"] == "WAITING_ON_SIBLING_DEPENDENCY"
            and _has_blocker_kind(dependency_payload, "child_tree_rebuild_required")
            and reconciliation_payload["available_decisions"] == ["preserve_manual"]
        ):
            return {
                "dependency": dependency_payload,
                "children": children_payload,
                "lifecycle": lifecycle_payload,
            }
        return None

    blocked_state = _wait_for(
        _blocked_manual_rebuild_state,
        timeout_seconds=60.0,
        failure_message="Timed out waiting for grouped-cutover dependency-invalidated manual child to block before fresh manual child creation",
    )

    assert blocked_state["children"]["children"] == []

    fresh_manual_child = harness.cli(
        "node",
        "child",
        "create",
        "--parent",
        right_id,
        "--kind",
        "plan",
        "--title",
        "Fresh Manual Replacement Plan",
        "--prompt",
        "Create a fresh child tree on the new authoritative version.",
    )
    assert fresh_manual_child.exit_code == 0, fresh_manual_child.stderr
    fresh_manual_child_id = str(fresh_manual_child.json()["node_id"])

    def _manual_create_gate_cleared():
        dependency = harness.cli("node", "dependency-status", "--node", right_id)
        reconciliation = harness.cli("node", "child-reconciliation", "--node", right_id)
        materialization = harness.cli("node", "child-materialization", "--node", right_id)
        children = harness.cli("node", "children", "--node", right_id, "--versions")
        assert dependency.exit_code == 0, dependency.stderr
        assert reconciliation.exit_code == 0, reconciliation.stderr
        assert materialization.exit_code == 0, materialization.stderr
        assert children.exit_code == 0, children.stderr
        dependency_payload = dependency.json()
        reconciliation_payload = reconciliation.json()
        materialization_payload = materialization.json()
        children_payload = children.json()
        blocker_kinds = [item["blocker_kind"] for item in dependency_payload["blockers"]]
        current_child_ids = {str(child["node_id"]) for child in children_payload["children"]}
        if (
            "child_tree_rebuild_required" not in blocker_kinds
            and fresh_manual_child_id in current_child_ids
            and current_child_ids.isdisjoint(original_child_ids)
            and reconciliation_payload["authority_mode"] == "manual"
            and materialization_payload["status"] == "manual"
            and materialization_payload["child_count"] >= 1
        ):
            return {
                "dependency": dependency_payload,
                "reconciliation": reconciliation_payload,
                "materialization": materialization_payload,
                "children": children_payload,
            }
        return None

    cleared_state = _wait_for(
        _manual_create_gate_cleared,
        timeout_seconds=30.0,
        failure_message="Timed out waiting for fresh manual child creation to clear child_tree_rebuild_required on the dependency-invalidated version",
    )

    assert "child_tree_rebuild_required" not in [item["blocker_kind"] for item in cleared_state["dependency"]["blockers"]]
    assert fresh_manual_child_id in {str(child["node_id"]) for child in cleared_state["children"]["children"]}


def _setup_parent_with_conflict_chain(harness: RealDaemonHarness, tmp_path: Path) -> dict[str, object]:
    parent_create = harness.cli(
        "node",
        "create",
        "--kind",
        "epic",
        "--title",
        "Incremental Merge Conflict Parent",
        "--prompt",
        "Create a parent whose second child will conflict during incremental merge.",
    )
    assert parent_create.exit_code == 0, parent_create.stderr
    parent_id = str(parent_create.json()["node_id"])

    child_a_create = harness.cli(
        "node",
        "child",
        "create",
        "--parent",
        parent_id,
        "--kind",
        "phase",
        "--title",
        "Independent Child A",
        "--prompt",
        "Merge first and advance the parent head.",
    )
    child_b_create = harness.cli(
        "node",
        "child",
        "create",
        "--parent",
        parent_id,
        "--kind",
        "phase",
        "--title",
        "Independent Child B",
        "--prompt",
        "Conflict against the advanced parent head.",
    )
    child_c_create = harness.cli(
        "node",
        "child",
        "create",
        "--parent",
        parent_id,
        "--kind",
        "phase",
        "--title",
        "Dependent Child C",
        "--prompt",
        "Wait until child B is durably merged into the parent.",
    )
    assert child_a_create.exit_code == 0, child_a_create.stderr
    assert child_b_create.exit_code == 0, child_b_create.stderr
    assert child_c_create.exit_code == 0, child_c_create.stderr
    child_a_id = str(child_a_create.json()["node_id"])
    child_b_id = str(child_b_create.json()["node_id"])
    child_c_id = str(child_c_create.json()["node_id"])

    dependency_add = harness.cli("node", "dependency-add", "--node", child_c_id, "--depends-on", child_b_id)
    assert dependency_add.exit_code == 0, dependency_add.stderr

    parent_version_id = str(harness.cli("node", "versions", "--node", parent_id).json()["versions"][0]["id"])
    child_a_version_id = str(harness.cli("node", "versions", "--node", child_a_id).json()["versions"][0]["id"])
    child_b_version_id = str(harness.cli("node", "versions", "--node", child_b_id).json()["versions"][0]["id"])
    child_c_version_id = str(harness.cli("node", "versions", "--node", child_c_id).json()["versions"][0]["id"])

    parent_files = tmp_path / "conflict-parent-bootstrap.json"
    _write_json(parent_files, {"shared.txt": "seed\nsame line\n"})
    for args in [
        ("git", "bootstrap-node", "--version", parent_version_id, "--files-file", str(parent_files), "--replace-existing"),
        ("git", "bootstrap-node", "--version", child_a_version_id, "--base-version", parent_version_id, "--replace-existing"),
        ("git", "bootstrap-node", "--version", child_b_version_id, "--base-version", parent_version_id, "--replace-existing"),
        ("git", "bootstrap-node", "--version", child_c_version_id, "--base-version", parent_version_id, "--replace-existing"),
    ]:
        result = harness.cli(*args)
        assert result.exit_code == 0, result.stderr

    parent_status = harness.cli("git", "status", "show", "--version", parent_version_id)
    child_a_status = harness.cli("git", "status", "show", "--version", child_a_version_id)
    child_b_status = harness.cli("git", "status", "show", "--version", child_b_version_id)
    child_c_status = harness.cli("git", "status", "show", "--version", child_c_version_id)
    assert parent_status.exit_code == 0, parent_status.stderr
    assert child_a_status.exit_code == 0, child_a_status.stderr
    assert child_b_status.exit_code == 0, child_b_status.stderr
    assert child_c_status.exit_code == 0, child_c_status.stderr

    _compile_ready_and_start_node(harness, node_id=parent_id)
    _compile_ready_and_start_node(harness, node_id=child_a_id)
    _compile_ready_and_start_node(harness, node_id=child_b_id)
    _compile_ready_and_start_node(harness, node_id=child_c_id)

    return {
        "parent_id": parent_id,
        "child_a_id": child_a_id,
        "child_b_id": child_b_id,
        "child_c_id": child_c_id,
        "parent_version_id": parent_version_id,
        "child_a_version_id": child_a_version_id,
        "child_b_version_id": child_b_version_id,
        "child_c_version_id": child_c_version_id,
        "parent_repo": Path(parent_status.json()["repo_path"]),
        "child_a_repo": Path(child_a_status.json()["repo_path"]),
        "child_b_repo": Path(child_b_status.json()["repo_path"]),
        "child_c_repo": Path(child_c_status.json()["repo_path"]),
    }


@pytest.mark.requires_git
def test_e2e_incremental_parent_merge_unblocks_dependent_child_only_after_merge_and_refresh(
    real_daemon_harness,
    tmp_path: Path,
) -> None:
    state = _setup_parent_and_children(real_daemon_harness, tmp_path)
    child_a_repo = state["child_a_repo"]
    child_b_repo = state["child_b_repo"]
    child_a_id = state["child_a_id"]
    child_b_id = state["child_b_id"]
    child_a_version_id = state["child_a_version_id"]
    child_b_version_id = state["child_b_version_id"]
    parent_id = state["parent_id"]

    (child_a_repo / "shared.txt").write_text("seed\nfrom-a\n", encoding="utf-8")
    _git(child_a_repo, "add", ".")
    _git(child_a_repo, "commit", "-m", "Child A final change")

    child_a_finalize = real_daemon_harness.cli("git", "finalize-node", "--node", child_a_id)
    assert child_a_finalize.exit_code == 0, child_a_finalize.stderr

    before_payload = real_daemon_harness.cli("node", "dependency-status", "--node", child_b_id).json()
    before_blockers = real_daemon_harness.cli("node", "blockers", "--node", child_b_id).json()
    before_merge_events = real_daemon_harness.cli("git", "merge-events", "show", "--node", parent_id).json()

    assert _dependency_is_ready(before_payload) is False
    assert _dependency_blockers(before_blockers)
    assert before_merge_events["events"] == []

    _complete_node_run(real_daemon_harness, node_id=child_a_id)

    immediate_after = real_daemon_harness.cli("node", "dependency-status", "--node", child_b_id).json()
    assert _dependency_is_ready(immediate_after) is False

    def _child_b_state():
        dependency_status = real_daemon_harness.cli("node", "dependency-status", "--node", child_b_id)
        blockers = real_daemon_harness.cli("node", "blockers", "--node", child_b_id)
        merge_events = real_daemon_harness.cli("git", "merge-events", "show", "--node", parent_id)
        child_b_status = real_daemon_harness.cli("git", "status", "show", "--version", child_b_version_id)
        assert dependency_status.exit_code == 0, dependency_status.stderr
        assert blockers.exit_code == 0, blockers.stderr
        assert merge_events.exit_code == 0, merge_events.stderr
        assert child_b_status.exit_code == 0, child_b_status.stderr
        dependency_payload = dependency_status.json()
        blockers_payload = blockers.json()
        merge_events_payload = merge_events.json()
        child_b_status_payload = child_b_status.json()
        return {
            "dependency": dependency_payload,
            "blockers": blockers_payload,
            "merge_events": merge_events_payload,
            "child_b_status": child_b_status_payload,
        }

    ready_state = None
    last_state = None
    deadline = time.time() + 45.0
    while time.time() < deadline:
        last_state = _child_b_state()
        if _dependency_is_ready(last_state["dependency"]) or _has_blocker_kind(last_state["dependency"], "already_running"):
            assert last_state["merge_events"]["events"], "dependent child advanced before any merge event existed"
            ready_state = last_state
            break
        time.sleep(0.5)
    assert ready_state is not None, f"Timed out waiting for dependent child to become ready after incremental merge\nlast_state={last_state}"

    merged_parent_head = ready_state["merge_events"]["events"][0]["parent_commit_after"]
    assert _dependency_is_ready(ready_state["dependency"]) or _has_blocker_kind(ready_state["dependency"], "already_running")
    assert ready_state["child_b_status"]["seed_commit_sha"] == merged_parent_head
    assert (child_b_repo / "shared.txt").read_text(encoding="utf-8") == "seed\nfrom-a\n"


@pytest.mark.requires_git
def test_e2e_incremental_parent_merge_reconcile_surface_reads_applied_history_real(
    real_daemon_harness,
    tmp_path: Path,
) -> None:
    state = _setup_parent_and_children(real_daemon_harness, tmp_path)
    parent_id = state["parent_id"]
    child_a_id = state["child_a_id"]
    child_b_id = state["child_b_id"]
    child_a_repo = state["child_a_repo"]
    child_b_repo = state["child_b_repo"]

    (child_a_repo / "shared.txt").write_text("seed\nfrom-a\n", encoding="utf-8")
    _git(child_a_repo, "add", ".")
    _git(child_a_repo, "commit", "-m", "Child A final change")
    assert real_daemon_harness.cli("git", "finalize-node", "--node", child_a_id).exit_code == 0
    _complete_node_run(real_daemon_harness, node_id=child_a_id)

    def _child_b_progressed():
        payload = real_daemon_harness.cli("node", "dependency-status", "--node", child_b_id).json()
        return payload if (_dependency_is_ready(payload) or _has_blocker_kind(payload, "already_running")) else None

    child_b_dependency = _wait_for(
        _child_b_progressed,
        timeout_seconds=45.0,
        failure_message="Timed out waiting for child B to unblock or auto-start after child A merge",
    )

    (child_b_repo / "shared.txt").write_text("seed\nfrom-a\nfrom-b\n", encoding="utf-8")
    _git(child_b_repo, "add", ".")
    _git(child_b_repo, "commit", "-m", "Child B final change")
    assert real_daemon_harness.cli("git", "finalize-node", "--node", child_b_id).exit_code == 0
    if _dependency_is_ready(child_b_dependency):
        assert real_daemon_harness.cli("node", "run", "start", "--node", child_b_id).exit_code == 0
    _complete_node_run(real_daemon_harness, node_id=child_b_id)

    def _reconcile_ready():
        child_results = real_daemon_harness.cli("node", "child-results", "--node", parent_id)
        reconcile = real_daemon_harness.cli("node", "reconcile", "--node", parent_id)
        merge_events = real_daemon_harness.cli("git", "merge-events", "show", "--node", parent_id)
        assert child_results.exit_code == 0, child_results.stderr
        assert reconcile.exit_code == 0, reconcile.stderr
        assert merge_events.exit_code == 0, merge_events.stderr
        child_results_payload = child_results.json()
        reconcile_payload = reconcile.json()
        merge_events_payload = merge_events.json()
        if child_results_payload["status"] == "ready_for_reconcile" and reconcile_payload["status"] == "ready_for_reconcile":
            return {
                "child_results": child_results_payload,
                "reconcile": reconcile_payload,
                "merge_events": merge_events_payload,
            }
        return None

    ready_state = _wait_for(
        _reconcile_ready,
        timeout_seconds=45.0,
        failure_message="Timed out waiting for parent reconcile surface to become ready after incremental merges",
    )

    child_results_payload = ready_state["child_results"]
    reconcile_payload = ready_state["reconcile"]
    merge_events_payload = ready_state["merge_events"]

    assert [item["merge_order"] for item in child_results_payload["children"]] == [1, 2]
    assert [item["reconcile_status"] for item in child_results_payload["children"]] == [
        "ready_for_reconcile",
        "ready_for_reconcile",
    ]
    assert [event["merge_order"] for event in merge_events_payload["events"]] == [1, 2]
    assert len(reconcile_payload["merge_events"]) == 2
    assert reconcile_payload["context_json"]["status"] == "ready_for_reconcile"
    assert reconcile_payload["prompt_relative_path"] == "execution/reconcile_parent_after_merge.md"


@pytest.mark.requires_git
def test_e2e_incremental_parent_merge_conflict_resolution_unblocks_dependent_child_real(
    real_daemon_harness,
    tmp_path: Path,
) -> None:
    state = _setup_parent_with_conflict_chain(real_daemon_harness, tmp_path)
    parent_id = state["parent_id"]
    parent_repo = state["parent_repo"]
    child_a_id = state["child_a_id"]
    child_b_id = state["child_b_id"]
    child_c_id = state["child_c_id"]
    child_a_repo = state["child_a_repo"]
    child_b_repo = state["child_b_repo"]
    child_c_repo = state["child_c_repo"]
    child_c_version_id = state["child_c_version_id"]

    (child_a_repo / "shared.txt").write_text("seed\nchild a line\n", encoding="utf-8")
    _git(child_a_repo, "add", ".")
    _git(child_a_repo, "commit", "-m", "Child A conflict precursor")
    finalize_a = real_daemon_harness.cli("git", "finalize-node", "--node", child_a_id)
    assert finalize_a.exit_code == 0, finalize_a.stderr
    _complete_node_run(real_daemon_harness, node_id=child_a_id)

    def _child_a_merged():
        merge_events = real_daemon_harness.cli("git", "merge-events", "show", "--node", parent_id)
        assert merge_events.exit_code == 0, merge_events.stderr
        payload = merge_events.json()
        return payload if len(payload["events"]) >= 1 else None

    _wait_for(
        _child_a_merged,
        timeout_seconds=45.0,
        failure_message="Timed out waiting for child A to merge upward before creating the conflict",
    )

    (child_b_repo / "shared.txt").write_text("seed\nchild b line\n", encoding="utf-8")
    _git(child_b_repo, "add", ".")
    _git(child_b_repo, "commit", "-m", "Child B conflicting change")
    finalize_b = real_daemon_harness.cli("git", "finalize-node", "--node", child_b_id)
    assert finalize_b.exit_code == 0, finalize_b.stderr
    _complete_node_run(real_daemon_harness, node_id=child_b_id)

    def _conflict_state():
        conflicts = real_daemon_harness.cli("git", "merge-conflicts", "show", "--node", parent_id)
        interventions = real_daemon_harness.cli("node", "interventions", "--node", parent_id)
        blockers = real_daemon_harness.cli("node", "blockers", "--node", child_c_id)
        dependency = real_daemon_harness.cli("node", "dependency-status", "--node", child_c_id)
        subtask_context = real_daemon_harness.cli("subtask", "context", "--node", parent_id)
        parent_status = real_daemon_harness.cli("git", "status", "show", "--version", state["parent_version_id"])
        assert conflicts.exit_code == 0, conflicts.stderr
        assert interventions.exit_code == 0, interventions.stderr
        assert blockers.exit_code == 0, blockers.stderr
        assert dependency.exit_code == 0, dependency.stderr
        assert subtask_context.exit_code == 0, subtask_context.stderr
        assert parent_status.exit_code == 0, parent_status.stderr
        conflicts_payload = conflicts.json()
        if not conflicts_payload["conflicts"]:
            return None
        return {
            "conflicts": conflicts_payload,
            "interventions": interventions.json(),
            "blockers": blockers.json(),
            "dependency": dependency.json(),
            "subtask_context": subtask_context.json(),
            "parent_status": parent_status.json(),
        }

    conflict_state = _wait_for(
        _conflict_state,
        timeout_seconds=45.0,
        failure_message="Timed out waiting for the incremental merge conflict to surface",
    )

    conflict_payload = conflict_state["conflicts"]["conflicts"][0]
    conflict_id = str(conflict_payload["id"])
    assert conflict_payload["resolution_status"] == "unresolved"
    assert "shared.txt" in conflict_payload["files_json"]
    assert any(item["kind"] == "merge_conflict" for item in conflict_state["interventions"]["interventions"])
    assert _has_blocker_kind(conflict_state["dependency"], "blocked_on_merge_conflict")
    assert conflict_state["parent_status"]["working_tree_state"] == "merge_conflict"
    parent_reconcile_context = conflict_state["subtask_context"]["input_context_json"]["parent_reconcile_context"]
    assert parent_reconcile_context["context_kind"] == "incremental_merge_conflict"
    assert parent_reconcile_context["incremental_merge_conflict"]["conflict_id"] == conflict_id
    assert parent_reconcile_context["incremental_merge_conflict"]["resolution_status"] == "unresolved"

    (parent_repo / "shared.txt").write_text("seed\nchild a line\nchild b line\n", encoding="utf-8")
    _git(parent_repo, "add", "shared.txt")
    _git(parent_repo, "commit", "-m", "Resolve incremental merge conflict for child B")
    resolved_head = _git(parent_repo, "rev-parse", "HEAD")

    resolve_result = real_daemon_harness.cli(
        "node",
        "intervention-apply",
        "--node",
        parent_id,
        "--kind",
        "merge_conflict",
        "--action",
        "resolve_conflict",
        "--conflict-id",
        conflict_id,
        "--summary",
        "Resolved in parent repo and committed.",
    )
    assert resolve_result.exit_code == 0, resolve_result.stderr

    def _child_c_progressed():
        dependency = real_daemon_harness.cli("node", "dependency-status", "--node", child_c_id)
        blockers = real_daemon_harness.cli("node", "blockers", "--node", child_c_id)
        conflicts = real_daemon_harness.cli("git", "merge-conflicts", "show", "--node", parent_id)
        merge_events = real_daemon_harness.cli("git", "merge-events", "show", "--node", parent_id)
        child_c_status = real_daemon_harness.cli("git", "status", "show", "--version", child_c_version_id)
        subtask_context = real_daemon_harness.cli("subtask", "context", "--node", parent_id)
        assert dependency.exit_code == 0, dependency.stderr
        assert blockers.exit_code == 0, blockers.stderr
        assert conflicts.exit_code == 0, conflicts.stderr
        assert merge_events.exit_code == 0, merge_events.stderr
        assert child_c_status.exit_code == 0, child_c_status.stderr
        assert subtask_context.exit_code == 0, subtask_context.stderr
        dependency_payload = dependency.json()
        blockers_payload = blockers.json()
        conflicts_payload = conflicts.json()
        merge_events_payload = merge_events.json()
        child_c_status_payload = child_c_status.json()
        subtask_context_payload = subtask_context.json()
        if _dependency_is_ready(dependency_payload) or _has_blocker_kind(dependency_payload, "already_running"):
            return {
                "dependency": dependency_payload,
                "blockers": blockers_payload,
                "conflicts": conflicts_payload,
                "merge_events": merge_events_payload,
                "child_c_status": child_c_status_payload,
                "subtask_context": subtask_context_payload,
            }
        return None

    resolved_state = _wait_for(
        _child_c_progressed,
        timeout_seconds=45.0,
        failure_message="Timed out waiting for child C to unblock after resolving child B's incremental merge conflict",
    )

    latest_conflict_payload = resolved_state["conflicts"]["conflicts"][0]
    assert latest_conflict_payload["resolution_status"] == "resolved"
    assert _dependency_is_ready(resolved_state["dependency"]) or _has_blocker_kind(resolved_state["dependency"], "already_running")
    assert resolved_state["child_c_status"]["seed_commit_sha"] == resolved_head
    assert (child_c_repo / "shared.txt").read_text(encoding="utf-8") == "seed\nchild a line\nchild b line\n"
    assert resolved_state["merge_events"]["events"][-1]["had_conflict"] is True
    assert resolved_state["merge_events"]["events"][-1]["parent_commit_after"] == resolved_head
    resolved_context = resolved_state["subtask_context"]["input_context_json"]["parent_reconcile_context"]
    assert resolved_context["status"] == "conflict_resolution_recorded"
    assert resolved_context["incremental_merge_conflict"]["resolution_status"] == "resolved"


@pytest.mark.requires_git
def test_e2e_incremental_parent_merge_resumes_after_daemon_restart_real(real_daemon_harness_factory, tmp_path: Path) -> None:
    harness = real_daemon_harness_factory(extra_env={"AICODING_SESSION_POLL_INTERVAL_SECONDS": "10.0"})
    state = _setup_parent_and_children(harness, tmp_path)
    child_a_repo = state["child_a_repo"]
    child_b_repo = state["child_b_repo"]
    child_a_id = state["child_a_id"]
    child_b_id = state["child_b_id"]
    child_a_version_id = state["child_a_version_id"]
    child_b_version_id = state["child_b_version_id"]
    parent_id = state["parent_id"]
    parent_version_id = state["parent_version_id"]

    (child_a_repo / "shared.txt").write_text("seed\nfrom-a\n", encoding="utf-8")
    _git(child_a_repo, "add", ".")
    _git(child_a_repo, "commit", "-m", "Child A final change before daemon restart")

    child_a_finalize = harness.cli("git", "finalize-node", "--node", child_a_id)
    assert child_a_finalize.exit_code == 0, child_a_finalize.stderr

    _complete_node_run(harness, node_id=child_a_id)
    harness.terminate()

    engine = create_engine(harness.database_url)
    try:
        with engine.connect() as connection:
            merge_row = connection.execute(
                text(
                    """
                    select status
                    from incremental_child_merge_state
                    where parent_node_version_id = :parent_version_id
                      and child_node_version_id = :child_version_id
                    """
                ),
                {
                    "parent_version_id": parent_version_id,
                    "child_version_id": child_a_version_id,
                },
            ).mappings().one()
            merge_event_count = connection.execute(
                text("select count(*) from merge_events where parent_node_version_id = :parent_version_id"),
                {"parent_version_id": parent_version_id},
            ).scalar_one()
    finally:
        engine.dispose()

    assert merge_row["status"] == "completed_unmerged"
    assert merge_event_count == 0

    harness.restart(extra_env={"AICODING_SESSION_POLL_INTERVAL_SECONDS": "0.1"})

    def _post_restart_state():
        dependency = harness.cli("node", "dependency-status", "--node", child_b_id)
        blockers = harness.cli("node", "blockers", "--node", child_b_id)
        merge_events = harness.cli("git", "merge-events", "show", "--node", parent_id)
        child_b_status = harness.cli("git", "status", "show", "--version", child_b_version_id)
        assert dependency.exit_code == 0, dependency.stderr
        assert blockers.exit_code == 0, blockers.stderr
        assert merge_events.exit_code == 0, merge_events.stderr
        assert child_b_status.exit_code == 0, child_b_status.stderr
        dependency_payload = dependency.json()
        blockers_payload = blockers.json()
        merge_events_payload = merge_events.json()
        child_b_status_payload = child_b_status.json()
        if _dependency_is_ready(dependency_payload) or _has_blocker_kind(dependency_payload, "already_running"):
            return {
                "dependency": dependency_payload,
                "blockers": blockers_payload,
                "merge_events": merge_events_payload,
                "child_b_status": child_b_status_payload,
            }
        return None

    restarted_state = _wait_for(
        _post_restart_state,
        timeout_seconds=45.0,
        failure_message="Timed out waiting for the restarted daemon to resume the incremental merge lane and unblock child B",
    )

    merge_events_payload = restarted_state["merge_events"]
    assert len(merge_events_payload["events"]) == 1
    merged_parent_head = merge_events_payload["events"][0]["parent_commit_after"]
    assert restarted_state["child_b_status"]["seed_commit_sha"] == merged_parent_head
    assert _dependency_is_ready(restarted_state["dependency"]) or _has_blocker_kind(restarted_state["dependency"], "already_running")
    assert (child_b_repo / "shared.txt").read_text(encoding="utf-8") == "seed\nfrom-a\n"
