from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest


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


@pytest.mark.e2e_real
@pytest.mark.requires_git
def test_flow_11_finalize_and_merge_runs_against_real_daemon_real_cli_and_real_git(real_daemon_harness, tmp_path) -> None:
    parent_create = real_daemon_harness.cli(
        "node",
        "create",
        "--kind",
        "epic",
        "--title",
        "Real E2E Flow 11 Parent",
        "--prompt",
        "Create the merge parent node.",
    )
    assert parent_create.exit_code == 0, parent_create.stderr
    parent_id = str(parent_create.json()["node_id"])

    child_create = real_daemon_harness.cli(
        "node",
        "child",
        "create",
        "--parent",
        parent_id,
        "--kind",
        "phase",
        "--title",
        "Real E2E Flow 11 Child",
        "--prompt",
        "Create the merge child node.",
    )
    assert child_create.exit_code == 0, child_create.stderr
    child_id = str(child_create.json()["node_id"])

    parent_versions = real_daemon_harness.cli("node", "versions", "--node", parent_id)
    child_versions = real_daemon_harness.cli("node", "versions", "--node", child_id)
    assert parent_versions.exit_code == 0, parent_versions.stderr
    assert child_versions.exit_code == 0, child_versions.stderr
    parent_version_id = str(parent_versions.json()["versions"][0]["id"])
    child_version_id = str(child_versions.json()["versions"][0]["id"])

    parent_files = tmp_path / "parent-bootstrap.json"
    parent_files.write_text(json.dumps({"shared.txt": "base\n"}), encoding="utf-8")

    parent_bootstrap = real_daemon_harness.cli(
        "git",
        "bootstrap-node",
        "--version",
        parent_version_id,
        "--files-file",
        str(parent_files),
        "--replace-existing",
    )
    child_bootstrap = real_daemon_harness.cli(
        "git",
        "bootstrap-node",
        "--version",
        child_version_id,
        "--base-version",
        parent_version_id,
        "--replace-existing",
    )
    assert parent_bootstrap.exit_code == 0, parent_bootstrap.stderr
    assert child_bootstrap.exit_code == 0, child_bootstrap.stderr

    parent_status = real_daemon_harness.cli("git", "status", "show", "--version", parent_version_id)
    child_status = real_daemon_harness.cli("git", "status", "show", "--version", child_version_id)
    assert parent_status.exit_code == 0, parent_status.stderr
    assert child_status.exit_code == 0, child_status.stderr
    parent_repo = Path(parent_status.json()["repo_path"])
    child_repo = Path(child_status.json()["repo_path"])

    shared_file = child_repo / "shared.txt"
    shared_file.write_text("base\nchild change\n", encoding="utf-8")
    _git(child_repo, "add", ".")
    _git(child_repo, "commit", "-m", "Child final change")

    child_finalize = real_daemon_harness.cli("git", "finalize-node", "--node", child_id)
    assert child_finalize.exit_code == 0, child_finalize.stderr
    child_final_payload = child_finalize.json()

    child_show = real_daemon_harness.cli("node", "show", "--node", child_id)
    child_results = real_daemon_harness.cli("node", "child-results", "--node", parent_id)
    reconcile = real_daemon_harness.cli("node", "reconcile", "--node", parent_id)
    merge_children = real_daemon_harness.cli("git", "merge-children", "--node", parent_id)
    finalize_parent = real_daemon_harness.cli("git", "finalize-node", "--node", parent_id)
    merge_events = real_daemon_harness.cli("git", "merge-events", "show", "--node", parent_id)
    final_show = real_daemon_harness.cli("git", "final", "show", "--node", parent_id)
    final_status = real_daemon_harness.cli("git", "status", "show", "--version", parent_version_id)

    assert child_show.exit_code == 0, child_show.stderr
    assert child_results.exit_code == 0, child_results.stderr
    assert reconcile.exit_code == 0, reconcile.stderr
    assert merge_children.exit_code == 0, merge_children.stderr
    assert finalize_parent.exit_code == 0, finalize_parent.stderr
    assert merge_events.exit_code == 0, merge_events.stderr
    assert final_show.exit_code == 0, final_show.stderr
    assert final_status.exit_code == 0, final_status.stderr

    child_show_payload = child_show.json()
    child_results_payload = child_results.json()
    reconcile_payload = reconcile.json()
    merge_payload = merge_children.json()
    finalize_parent_payload = finalize_parent.json()
    merge_events_payload = merge_events.json()
    final_show_payload = final_show.json()
    final_status_payload = final_status.json()

    assert child_show_payload["final_commit_sha"] == child_final_payload["final_commit_sha"]
    assert child_show_payload["seed_commit_sha"]
    assert child_results_payload["children"]
    assert child_results_payload["children"][0]["child_node_id"] == child_id
    assert child_results_payload["children"][0]["final_commit_sha"] == child_final_payload["final_commit_sha"]
    assert reconcile_payload["status"] == "ready_for_reconcile"
    assert merge_payload["status"] == "merged"
    assert merge_payload["merge_events"]
    assert merge_payload["merge_events"][0]["child_final_commit_sha"] == child_final_payload["final_commit_sha"]
    assert finalize_parent_payload["status"] == "finalized"
    assert final_show_payload["final_commit_sha"] == finalize_parent_payload["final_commit_sha"]
    assert final_status_payload["working_tree_state"] == "finalized_clean"
    assert merge_events_payload["events"]
