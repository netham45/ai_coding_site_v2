from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

import pytest

from tests.helpers.e2e import RealDaemonHarness


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


def _compile_ready_and_start_node(harness: RealDaemonHarness, *, node_id: str) -> None:
    compile_result = harness.cli("workflow", "compile", "--node", node_id)
    ready_result = harness.cli("node", "lifecycle", "transition", "--node", node_id, "--state", "READY")
    start_result = harness.cli("node", "run", "start", "--node", node_id)
    assert compile_result.exit_code == 0, compile_result.stderr
    assert ready_result.exit_code == 0, ready_result.stderr
    assert start_result.exit_code == 0, start_result.stderr


def _complete_one_current_subtask(harness: RealDaemonHarness, *, node_id: str) -> None:
    current_result = harness.cli("subtask", "current", "--node", node_id)
    assert current_result.exit_code == 0, current_result.stderr
    current_payload = current_result.json()
    compiled_subtask_id = current_payload["state"]["current_compiled_subtask_id"]
    current_subtask = current_payload["current_subtask"]
    assert compiled_subtask_id is not None
    assert current_subtask is not None

    start_result = harness.cli("subtask", "start", "--node", node_id, "--compiled-subtask", compiled_subtask_id)
    assert start_result.exit_code == 0, start_result.stderr

    subtask_type = current_subtask["subtask_type"]
    if subtask_type == "validate":
        payload = {"exit_code": 0}
        summary = "validated"
    elif subtask_type == "review":
        payload = {
            "status": "pass",
            "findings": [{"message": "ok"}],
            "criteria_results": [{"criterion": "ok", "status": "passed"}],
        }
        summary = "reviewed"
    elif subtask_type == "run_tests":
        payload = {
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
            ]
        }
        summary = "tested"
    else:
        payload = {"status": "ok", "subtask_type": subtask_type}
        summary = f"completed {subtask_type}"

    response = harness.request(
        "POST",
        "/api/subtasks/complete",
        json_payload={
            "node_id": node_id,
            "compiled_subtask_id": compiled_subtask_id,
            "output_json": payload,
            "summary": summary,
        },
    )
    assert response.status_code == 200, response.text

    advance_result = harness.cli("workflow", "advance", "--node", node_id)
    assert advance_result.exit_code == 0, advance_result.stderr


def _complete_node_run(harness: RealDaemonHarness, *, node_id: str, timeout_seconds: float = 45.0) -> None:
    deadline = time.time() + timeout_seconds
    last_run_payload: dict[str, object] | None = None
    while time.time() < deadline:
        run_show = harness.cli("node", "run", "show", "--node", node_id)
        if run_show.exit_code == 0:
            last_run_payload = run_show.json()
            if last_run_payload["run"]["run_status"] == "COMPLETE":
                return
        else:
            lifecycle_show = harness.cli("node", "lifecycle", "show", "--node", node_id)
            assert lifecycle_show.exit_code == 0, lifecycle_show.stderr
            lifecycle_payload = lifecycle_show.json()
            if lifecycle_payload["lifecycle_state"] == "COMPLETE":
                return
            raise AssertionError(run_show.stderr)
        _complete_one_current_subtask(harness, node_id=node_id)
    raise AssertionError(f"Timed out waiting for node {node_id} to complete.\nlast_run_payload={last_run_payload}")


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
    compile_child_b = harness.cli("workflow", "compile", "--node", child_b_id)
    ready_child_b = harness.cli("node", "lifecycle", "transition", "--node", child_b_id, "--state", "READY")
    assert compile_child_b.exit_code == 0, compile_child_b.stderr
    assert ready_child_b.exit_code == 0, ready_child_b.stderr

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


@pytest.mark.e2e_real
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

    observed_blocker_kinds: set[str] = set()

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
        observed_blocker_kinds.update(item["blocker_kind"] for item in _dependency_blockers(blockers_payload))
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
    assert "blocked_on_incremental_merge" in observed_blocker_kinds or "blocked_on_parent_refresh" in observed_blocker_kinds
    assert ready_state["child_b_status"]["seed_commit_sha"] == merged_parent_head
    assert (child_b_repo / "shared.txt").read_text(encoding="utf-8") == "seed\nfrom-a\n"


@pytest.mark.e2e_real
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
