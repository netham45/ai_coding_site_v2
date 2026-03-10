from __future__ import annotations

from argparse import Namespace
import json
import pytest

from aicoding.cli.context import build_cli_context
from aicoding.cli.handlers import (
    handle_node_children,
    handle_node_respond_to_child_failure,
    handle_subtask_retry,
    handle_subtask_list,
    handle_task_current,
    handle_task_list,
    handle_workflow_hook_policy,
    handle_workflow_override_resolution,
    handle_workflow_rendering,
    handle_workflow_schema_validation,
    handle_workflow_source_discovery,
    handle_yaml_sources,
)
from aicoding.cli.parser import build_parser
from aicoding.errors import CommandExecutionError
from aicoding.cli.app import run


def test_doctor_command_prints_bootstrap_status(capsys) -> None:
    exit_code = run(["admin", "doctor"])
    output = capsys.readouterr().out

    payload = json.loads(output)
    assert exit_code == 0
    assert payload["missing_directories"] == []


def test_print_settings_omits_auth_token(capsys, monkeypatch) -> None:
    monkeypatch.setenv("AICODING_AUTH_TOKEN", "secret-value")

    exit_code = run(["admin", "print-settings"])
    output = capsys.readouterr().out

    payload = json.loads(output)
    assert exit_code == 0
    assert "auth_token" not in payload


def test_auth_token_command_reports_source_without_exposing_token(capsys) -> None:
    exit_code = run(["admin", "auth-token"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["auth_token_source"] in {"settings", "file"}
    assert "auth_token" not in payload


def test_resources_command_reports_group_paths(capsys) -> None:
    exit_code = run(["admin", "resources"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert "prompt_layouts" in payload
    assert payload["prompt_layouts"].endswith("/src/aicoding/resources/prompts/layouts")


def test_cli_formats_application_errors_to_stderr_json(capsys, monkeypatch) -> None:
    def boom(*args, **kwargs):
        raise CommandExecutionError(message="broken command", code="broken_command", exit_code=7)

    monkeypatch.setattr("aicoding.cli.app.build_cli_context", boom)

    exit_code = run(["admin", "auth-token"])
    payload = json.loads(capsys.readouterr().err)

    assert exit_code == 7
    assert payload == {"error": "broken_command", "message": "broken command"}


def test_cli_help_lists_expected_command_groups(capsys) -> None:
    parser = build_parser()

    with pytest.raises(SystemExit):
        parser.parse_args(["--help"])

    output = capsys.readouterr().out
    for command_name in ("node", "workflow", "tree", "rebuild", "git", "task", "subtask", "summary", "environment", "session", "yaml", "prompts", "docs", "rationale", "entity", "admin", "debug"):
        assert command_name in output


def test_node_show_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["node", "show", "--node", "node-123"])

    assert args.command == "node"
    assert args.node_command == "show"
    assert args.node == "node-123"
    assert args.handler


def test_node_child_create_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(
        ["node", "child", "create", "--parent", "node-123", "--kind", "phase", "--title", "Child", "--prompt", "manual"]
    )

    assert args.command == "node"
    assert args.node_command == "child"
    assert args.node_child_command == "create"
    assert args.parent == "node-123"
    assert args.kind == "phase"
    assert args.handler


def test_node_create_compile_flags_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(
        ["node", "create", "--kind", "epic", "--title", "Top", "--prompt", "boot", "--compile", "--start-run"]
    )

    assert args.command == "node"
    assert args.node_command == "create"
    assert args.compile is True
    assert args.start_run is True
    assert args.handler


def test_node_audit_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["node", "audit", "--node", "node-123"])

    assert args.command == "node"
    assert args.node_command == "audit"
    assert args.node == "node-123"
    assert args.handler


def test_tree_show_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["tree", "show", "--node", "node-123"])

    assert args.command == "tree"
    assert args.tree_command == "show"
    assert args.node == "node-123"
    assert args.handler


def test_docs_build_node_view_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["docs", "build-node-view", "--node", "node-123"])

    assert args.command == "docs"
    assert args.docs_command == "build-node-view"
    assert args.node == "node-123"
    assert args.handler


def test_workflow_compile_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["workflow", "compile", "--node", "node-123"])

    assert args.command == "workflow"
    assert args.workflow_command == "compile"
    assert args.node == "node-123"
    assert args.handler


def test_workflow_start_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["workflow", "start", "--kind", "epic", "--prompt", "boot", "--no-run"])

    assert args.command == "workflow"
    assert args.workflow_command == "start"
    assert args.kind == "epic"
    assert args.no_run is True
    assert args.handler


def test_workflow_advance_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["workflow", "advance", "--node", "node-123"])

    assert args.command == "workflow"
    assert args.workflow_command == "advance"
    assert args.node == "node-123"
    assert args.handler


def test_node_run_audit_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["node", "run", "audit", "--run", "run-123"])

    assert args.command == "node"
    assert args.node_command == "run"
    assert args.node_run_command == "audit"
    assert args.run == "run-123"
    assert args.handler


def test_subtask_environment_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["subtask", "environment", "--node", "node-123"])

    assert args.command == "subtask"
    assert args.subtask_command == "environment"
    assert args.node == "node-123"
    assert args.handler


def test_environment_show_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["environment", "show", "--attempt", "attempt-123"])

    assert args.command == "environment"
    assert args.environment_command == "show"
    assert args.attempt == "attempt-123"
    assert args.handler


def test_workflow_pause_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["workflow", "pause", "--node", "node-123"])

    assert args.command == "workflow"
    assert args.workflow_command == "pause"
    assert args.node == "node-123"
    assert args.handler


def test_workflow_cancel_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["workflow", "cancel", "--node", "node-123"])

    assert args.command == "workflow"
    assert args.workflow_command == "cancel"
    assert args.node == "node-123"
    assert args.handler


def test_workflow_hooks_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["workflow", "hooks", "--workflow", "workflow-123"])

    assert args.command == "workflow"
    assert args.workflow_command == "hooks"
    assert args.workflow == "workflow-123"
    assert args.handler


def test_yaml_policy_impact_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["yaml", "policy-impact", "--kind", "epic"])

    assert args.command == "yaml"
    assert args.yaml_command == "policy-impact"
    assert args.kind == "epic"
    assert args.handler


def test_yaml_override_chain_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["yaml", "override-chain", "--node", "node-123"])

    assert args.command == "yaml"
    assert args.yaml_command == "override-chain"
    assert args.node == "node-123"
    assert args.handler


def test_session_recover_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["session", "recover", "--node", "node-123"])

    assert args.command == "session"
    assert args.session_command == "recover"
    assert args.node == "node-123"
    assert args.handler


def test_node_recovery_status_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["node", "recovery-status", "--node", "node-123"])

    assert args.command == "node"
    assert args.node_command == "recovery-status"
    assert args.node == "node-123"
    assert args.handler


def test_session_nudge_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["session", "nudge", "--node", "node-123"])

    assert args.command == "session"
    assert args.session_command == "nudge"
    assert args.node == "node-123"
    assert args.handler


def test_session_push_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["session", "push", "--node", "node-123", "--reason", "research_context"])

    assert args.command == "session"
    assert args.session_command == "push"
    assert args.node == "node-123"
    assert args.reason == "research_context"
    assert args.handler


def test_session_pop_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["session", "pop", "--session", "session-123", "--file", "child.json"])

    assert args.command == "session"
    assert args.session_command == "pop"
    assert args.session == "session-123"
    assert args.file == "child.json"
    assert args.handler


def test_yaml_resolved_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["yaml", "resolved", "--workflow", "workflow-123", "--family", "task_definition", "--id", "review_node"])

    assert args.command == "yaml"
    assert args.yaml_command == "resolved"
    assert args.workflow == "workflow-123"
    assert args.family == "task_definition"
    assert args.id == "review_node"
    assert args.handler


def test_node_dependency_status_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["node", "dependency-status", "--node", "node-123"])

    assert args.command == "node"
    assert args.node_command == "dependency-status"
    assert args.node == "node-123"
    assert args.handler


def test_node_child_materialization_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["node", "child-materialization", "--node", "node-123"])

    assert args.command == "node"
    assert args.node_command == "child-materialization"
    assert args.node == "node-123"
    assert args.handler


def test_node_child_results_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["node", "child-results", "--node", "node-123"])

    assert args.command == "node"
    assert args.node_command == "child-results"
    assert args.node == "node-123"
    assert args.handler


def test_node_child_failures_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["node", "child-failures", "--node", "node-123"])

    assert args.command == "node"
    assert args.node_command == "child-failures"
    assert args.node == "node-123"
    assert args.handler


def test_node_decision_history_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["node", "decision-history", "--node", "node-123"])

    assert args.command == "node"
    assert args.node_command == "decision-history"
    assert args.node == "node-123"
    assert args.handler


def test_node_respond_to_child_failure_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(
        ["node", "respond-to-child-failure", "--node", "node-123", "--child", "child-456", "--action", "retry_child"]
    )

    assert args.command == "node"
    assert args.node_command == "respond-to-child-failure"
    assert args.node == "node-123"
    assert args.child == "child-456"
    assert args.action == "retry_child"
    assert args.handler


def test_node_respond_to_child_failure_handler_posts_expected_payload(monkeypatch) -> None:
    calls: list[tuple[str, str, dict[str, object] | None]] = []

    class StubClient:
        def request(self, method: str, path: str, json_payload: dict[str, object] | None = None) -> dict[str, object]:
            calls.append((method, path, json_payload))
            return {"status": "ok"}

    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: StubClient())

    payload = handle_node_respond_to_child_failure(
        Namespace(node="node-123", child="child-456", action="retry_child"),
        build_cli_context(),
    )

    assert payload == {"status": "ok"}
    assert calls == [
        (
            "POST",
            "/api/nodes/respond-to-child-failure",
            {"node_id": "node-123", "child_node_id": "child-456", "requested_action": "retry_child"},
        )
    ]


def test_node_reconcile_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["node", "reconcile", "--node", "node-123"])

    assert args.command == "node"
    assert args.node_command == "reconcile"
    assert args.node == "node-123"
    assert args.handler


def test_node_validate_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["node", "validate", "--node", "node-123"])

    assert args.command == "node"
    assert args.node_command == "validate"
    assert args.node == "node-123"
    assert args.handler


def test_validation_results_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["validation", "results", "--node", "node-123"])

    assert args.command == "validation"
    assert args.validation_command == "results"
    assert args.node == "node-123"
    assert args.handler


def test_node_review_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["node", "review", "--node", "node-123", "--status", "revise", "--summary", "needs work"])

    assert args.command == "node"
    assert args.node_command == "review"
    assert args.node == "node-123"
    assert args.status == "revise"
    assert args.handler


def test_review_results_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["review", "results", "--node", "node-123"])

    assert args.command == "review"
    assert args.review_command == "results"
    assert args.node == "node-123"
    assert args.handler


def test_node_test_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["node", "test", "--node", "node-123"])

    assert args.command == "node"
    assert args.node_command == "test"
    assert args.node == "node-123"
    assert args.handler


def test_testing_show_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["testing", "show", "--run", "run-123"])

    assert args.command == "testing"
    assert args.testing_command == "show"
    assert args.run == "run-123"
    assert args.handler


def test_testing_results_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["testing", "results", "--node", "node-123"])

    assert args.command == "testing"
    assert args.testing_command == "results"
    assert args.node == "node-123"
    assert args.handler


def test_node_materialize_children_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["node", "materialize-children", "--node", "node-123"])

    assert args.command == "node"
    assert args.node_command == "materialize-children"
    assert args.node == "node-123"
    assert args.handler


def test_node_pause_state_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["node", "pause-state", "--node", "node-123"])

    assert args.command == "node"
    assert args.node_command == "pause-state"
    assert args.node == "node-123"
    assert args.handler


def test_node_cancel_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["node", "cancel", "--node", "node-123"])

    assert args.command == "node"
    assert args.node_command == "cancel"
    assert args.node == "node-123"
    assert args.handler


def test_node_approve_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["node", "approve", "--node", "node-123", "--pause-flag", "user_guidance_required", "--summary", "ok"])

    assert args.command == "node"
    assert args.node_command == "approve"
    assert args.node == "node-123"
    assert args.pause_flag == "user_guidance_required"
    assert args.summary == "ok"
    assert args.handler


def test_workflow_approve_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["workflow", "approve", "--node", "node-123"])

    assert args.command == "workflow"
    assert args.workflow_command == "approve"
    assert args.node == "node-123"
    assert args.handler


def test_subtask_fail_argument_parsing_accepts_summary_file() -> None:
    parser = build_parser()
    args = parser.parse_args(
        ["subtask", "fail", "--node", "node-123", "--compiled-subtask", "subtask-123", "--summary-file", "failure.md"]
    )

    assert args.command == "subtask"
    assert args.subtask_command == "fail"
    assert args.node == "node-123"
    assert args.compiled_subtask == "subtask-123"
    assert args.summary is None
    assert args.summary_file == "failure.md"
    assert args.handler


def test_node_dependency_add_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["node", "dependency-add", "--node", "node-123", "--depends-on", "node-456"])

    assert args.command == "node"
    assert args.node_command == "dependency-add"
    assert args.node == "node-123"
    assert args.depends_on == "node-456"
    assert args.handler


def test_git_branch_show_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["git", "branch", "show", "--node", "node-123"])

    assert args.command == "git"
    assert args.git_command == "branch"
    assert args.node == "node-123"
    assert args.handler


def test_rebuild_show_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["rebuild", "show", "--node", "node-123"])

    assert args.command == "rebuild"
    assert args.rebuild_command == "show"
    assert args.node == "node-123"
    assert args.handler


def test_subtask_retry_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["subtask", "retry", "--attempt", "attempt-123"])

    assert args.command == "subtask"
    assert args.subtask_command == "retry"
    assert args.attempt == "attempt-123"
    assert args.handler


def test_git_merge_conflicts_record_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "git",
            "merge-conflicts",
            "record",
            "--parent-version",
            "version-1",
            "--child-version",
            "version-2",
            "--child-final-commit",
            "abc1234",
            "--parent-before",
            "seed123",
            "--parent-after",
            "merge123",
            "--merge-order",
            "1",
            "--file",
            "src/conflicted.py",
        ]
    )

    assert args.command == "git"
    assert args.git_command == "merge-conflicts"
    assert args.git_merge_conflicts_command == "record"
    assert args.parent_version == "version-1"
    assert args.files == ["src/conflicted.py"]
    assert args.handler


def test_git_merge_conflicts_resolve_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["git", "merge-conflicts", "resolve", "--conflict", "conflict-1", "--summary", "resolved"])

    assert args.command == "git"
    assert args.git_command == "merge-conflicts"
    assert args.git_merge_conflicts_command == "resolve"
    assert args.conflict == "conflict-1"
    assert args.status == "resolved"
    assert args.handler


def test_subtask_retry_handler_posts_expected_path(monkeypatch) -> None:
    calls: list[tuple[str, str, dict[str, object] | None]] = []

    class StubClient:
        def request(self, method: str, path: str, json_payload: dict[str, object] | None = None) -> dict[str, object]:
            calls.append((method, path, json_payload))
            return {"status": "ok"}

    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: StubClient())

    payload = handle_subtask_retry(Namespace(node=None, attempt="attempt-123"), build_cli_context())

    assert payload == {"status": "ok"}
    assert calls == [("POST", "/api/subtask-attempts/attempt-123/retry", {})]


def test_task_list_and_current_handlers_project_current_workflow(monkeypatch) -> None:
    class StubClient:
        def request(self, method: str, path: str, json_payload: dict[str, object] | None = None) -> dict[str, object]:
            assert method == "GET"
            assert json_payload is None
            if path == "/api/nodes/node-123/workflow/current":
                return {
                    "id": "workflow-1",
                    "tasks": [
                        {"id": "task-1", "task_key": "research_context", "ordinal": 1, "subtasks": [{"id": "sub-1"}]},
                        {"id": "task-2", "task_key": "execute_node", "ordinal": 2, "subtasks": [{"id": "sub-2"}, {"id": "sub-3"}]},
                    ],
                }
            if path == "/api/nodes/node-123/lifecycle":
                return {
                    "lifecycle_state": "RUNNING",
                    "run_status": "RUNNING",
                    "current_task_id": "task-2",
                    "current_subtask_id": "sub-2",
                }
            raise AssertionError(path)

    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: StubClient())

    listed = handle_task_list(Namespace(node="node-123"), build_cli_context())
    current = handle_task_current(Namespace(node="node-123"), build_cli_context())

    assert listed["compiled_workflow_id"] == "workflow-1"
    assert listed["current_task_id"] == "task-2"
    assert [item["subtask_count"] for item in listed["tasks"]] == [1, 2]
    assert [item["is_current"] for item in listed["tasks"]] == [False, True]
    assert current["current_task"]["id"] == "task-2"
    assert current["current_subtask_id"] == "sub-2"


def test_subtask_list_handler_flattens_current_workflow(monkeypatch) -> None:
    class StubClient:
        def request(self, method: str, path: str, json_payload: dict[str, object] | None = None) -> dict[str, object]:
            assert method == "GET"
            assert json_payload is None
            if path == "/api/nodes/node-123/workflow/current":
                return {
                    "id": "workflow-1",
                    "tasks": [
                        {"id": "task-1", "task_key": "research_context", "ordinal": 1, "subtasks": [{"id": "sub-1", "ordinal": 1}]},
                        {"id": "task-2", "task_key": "execute_node", "ordinal": 2, "subtasks": [{"id": "sub-2", "ordinal": 1}]},
                    ],
                }
            if path == "/api/nodes/node-123/lifecycle":
                return {
                    "lifecycle_state": "RUNNING",
                    "run_status": "RUNNING",
                    "current_task_id": "task-2",
                    "current_subtask_id": "sub-2",
                }
            raise AssertionError(path)

    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: StubClient())

    payload = handle_subtask_list(Namespace(node="node-123"), build_cli_context())

    assert payload["compiled_workflow_id"] == "workflow-1"
    assert payload["current_subtask_id"] == "sub-2"
    assert [item["task_key"] for item in payload["subtasks"]] == ["research_context", "execute_node"]
    assert [item["is_current"] for item in payload["subtasks"]] == [False, True]


def test_node_children_versions_handler_loads_operator_summaries(monkeypatch) -> None:
    calls: list[str] = []

    class StubClient:
        def request(self, method: str, path: str, json_payload: dict[str, object] | None = None) -> dict[str, object] | list[dict[str, object]]:
            assert method == "GET"
            assert json_payload is None
            calls.append(path)
            if path == "/api/nodes/node-123/children":
                return [{"node_id": "child-1"}, {"node_id": "child-2"}]
            if path == "/api/nodes/child-1/summary":
                return {"node_id": "child-1", "authoritative_node_version_id": "v1"}
            if path == "/api/nodes/child-2/summary":
                return {"node_id": "child-2", "authoritative_node_version_id": "v2"}
            raise AssertionError(path)

    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: StubClient())

    payload = handle_node_children(Namespace(node="node-123", versions=True), build_cli_context())

    assert payload["include_versions"] is True
    assert [item["authoritative_node_version_id"] for item in payload["children"]] == ["v1", "v2"]
    assert calls == ["/api/nodes/node-123/children", "/api/nodes/child-1/summary", "/api/nodes/child-2/summary"]


def test_yaml_sources_handler_uses_daemon_backed_node_sources(monkeypatch) -> None:
    calls: list[tuple[str, str, dict[str, object] | None]] = []

    class StubClient:
        def request(self, method: str, path: str, json_payload: dict[str, object] | None = None) -> dict[str, object]:
            calls.append((method, path, json_payload))
            return {"node_version_id": "version-1", "source_documents": []}

    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: StubClient())

    payload = handle_yaml_sources(Namespace(node="node-123", workflow=None, scope="builtin"), build_cli_context())

    assert payload["node_version_id"] == "version-1"
    assert calls == [("GET", "/api/nodes/node-123/sources", None)]


def test_workflow_source_discovery_handler_uses_daemon_backed_workflow_stage(monkeypatch) -> None:
    calls: list[tuple[str, str, dict[str, object] | None]] = []

    class StubClient:
        def request(self, method: str, path: str, json_payload: dict[str, object] | None = None) -> dict[str, object]:
            calls.append((method, path, json_payload))
            return {"compiled_workflow_id": "workflow-1", "discovery_order": []}

    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: StubClient())

    payload = handle_workflow_source_discovery(Namespace(node="node-123", workflow=None), build_cli_context())

    assert payload["compiled_workflow_id"] == "workflow-1"
    assert calls == [("GET", "/api/nodes/node-123/workflow/source-discovery", None)]


def test_workflow_schema_validation_handler_uses_daemon_backed_workflow_stage(monkeypatch) -> None:
    calls: list[tuple[str, str, dict[str, object] | None]] = []

    class StubClient:
        def request(self, method: str, path: str, json_payload: dict[str, object] | None = None) -> dict[str, object]:
            calls.append((method, path, json_payload))
            return {"compiled_workflow_id": "workflow-1", "validated_document_count": 3}

    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: StubClient())

    payload = handle_workflow_schema_validation(Namespace(node="node-123", workflow=None), build_cli_context())

    assert payload["compiled_workflow_id"] == "workflow-1"
    assert payload["validated_document_count"] == 3
    assert calls == [("GET", "/api/nodes/node-123/workflow/schema-validation", None)]


def test_workflow_override_resolution_handler_uses_daemon_backed_workflow_stage(monkeypatch) -> None:
    calls: list[tuple[str, str, dict[str, object] | None]] = []

    class StubClient:
        def request(self, method: str, path: str, json_payload: dict[str, object] | None = None) -> dict[str, object]:
            calls.append((method, path, json_payload))
            return {"compiled_workflow_id": "workflow-1", "applied_override_count": 1}

    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: StubClient())

    payload = handle_workflow_override_resolution(Namespace(node="node-123", workflow=None), build_cli_context())

    assert payload["compiled_workflow_id"] == "workflow-1"
    assert payload["applied_override_count"] == 1
    assert calls == [("GET", "/api/nodes/node-123/workflow/override-resolution", None)]


def test_workflow_hook_policy_handler_uses_daemon_backed_workflow_stage(monkeypatch) -> None:
    calls: list[tuple[str, str, dict[str, object] | None]] = []

    class StubClient:
        def request(self, method: str, path: str, json_payload: dict[str, object] | None = None) -> dict[str, object]:
            calls.append((method, path, json_payload))
            return {"compiled_workflow_id": "workflow-1", "selected_hooks": [], "effective_policy": {}}

    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: StubClient())

    payload = handle_workflow_hook_policy(Namespace(node="node-123", workflow=None), build_cli_context())

    assert payload["compiled_workflow_id"] == "workflow-1"
    assert calls == [("GET", "/api/nodes/node-123/workflow/hook-policy", None)]


def test_workflow_rendering_handler_uses_daemon_backed_workflow_stage(monkeypatch) -> None:
    calls: list[tuple[str, str, dict[str, object] | None]] = []

    class StubClient:
        def request(self, method: str, path: str, json_payload: dict[str, object] | None = None) -> dict[str, object]:
            calls.append((method, path, json_payload))
            return {"compiled_workflow_id": "workflow-1", "compiled_subtask_count": 2}

    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: StubClient())

    payload = handle_workflow_rendering(Namespace(node="node-123", workflow=None), build_cli_context())

    assert payload["compiled_workflow_id"] == "workflow-1"
    assert payload["compiled_subtask_count"] == 2
    assert calls == [("GET", "/api/nodes/node-123/workflow/rendering", None)]


def test_git_merge_events_show_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["git", "merge-events", "show", "--node", "node-123"])

    assert args.command == "git"
    assert args.git_command == "merge-events"
    assert args.git_merge_events_command == "show"
    assert args.node == "node-123"
    assert args.handler


def test_git_merge_children_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["git", "merge-children", "--node", "node-123"])

    assert args.command == "git"
    assert args.git_command == "merge-children"
    assert args.node == "node-123"
    assert args.handler


def test_subtask_current_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["subtask", "current", "--node", "node-123"])

    assert args.command == "subtask"
    assert args.subtask_command == "current"
    assert args.node == "node-123"
    assert args.handler


def test_task_list_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["task", "list", "--node", "node-123"])

    assert args.command == "task"
    assert args.task_command == "list"
    assert args.node == "node-123"
    assert args.handler


def test_task_current_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["task", "current", "--node", "node-123"])

    assert args.command == "task"
    assert args.task_command == "current"
    assert args.node == "node-123"
    assert args.handler


def test_subtask_list_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["subtask", "list", "--node", "node-123"])

    assert args.command == "subtask"
    assert args.subtask_command == "list"
    assert args.node == "node-123"
    assert args.handler


def test_node_children_versions_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["node", "children", "--node", "node-123", "--versions"])

    assert args.command == "node"
    assert args.node_command == "children"
    assert args.versions is True
    assert args.handler


def test_node_ancestors_to_root_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["node", "ancestors", "--node", "node-123", "--to-root"])

    assert args.command == "node"
    assert args.node_command == "ancestors"
    assert args.to_root is True
    assert args.handler


def test_tree_show_full_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["tree", "show", "--node", "node-123", "--full"])

    assert args.command == "tree"
    assert args.tree_command == "show"
    assert args.full is True
    assert args.handler


def test_yaml_sources_argument_parsing_supports_node_target() -> None:
    parser = build_parser()
    args = parser.parse_args(["yaml", "sources", "--node", "node-123"])

    assert args.command == "yaml"
    assert args.yaml_command == "sources"
    assert args.node == "node-123"
    assert args.handler


def test_workflow_source_discovery_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["workflow", "source-discovery", "--node", "node-123"])

    assert args.command == "workflow"
    assert args.workflow_command == "source-discovery"
    assert args.node == "node-123"
    assert args.handler


def test_workflow_schema_validation_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["workflow", "schema-validation", "--node", "node-123"])

    assert args.command == "workflow"
    assert args.workflow_command == "schema-validation"
    assert args.node == "node-123"
    assert args.handler


def test_workflow_override_resolution_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["workflow", "override-resolution", "--node", "node-123"])

    assert args.command == "workflow"
    assert args.workflow_command == "override-resolution"
    assert args.node == "node-123"
    assert args.handler


def test_workflow_hook_policy_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["workflow", "hook-policy", "--node", "node-123"])

    assert args.command == "workflow"
    assert args.workflow_command == "hook-policy"
    assert args.node == "node-123"
    assert args.handler


def test_workflow_rendering_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["workflow", "rendering", "--node", "node-123"])

    assert args.command == "workflow"
    assert args.workflow_command == "rendering"
    assert args.node == "node-123"
    assert args.handler


def test_subtask_prompt_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["subtask", "prompt", "--node", "node-123"])

    assert args.command == "subtask"
    assert args.subtask_command == "prompt"
    assert args.node == "node-123"
    assert args.handler


def test_session_show_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["session", "show", "--node", "node-123"])

    assert args.command == "session"
    assert args.session_command == "show"
    assert args.node == "node-123"
    assert args.handler


def test_session_events_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["session", "events", "--session", "session-123"])

    assert args.command == "session"
    assert args.session_command == "events"
    assert args.session == "session-123"
    assert args.handler


def test_summary_register_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["summary", "register", "--node", "node-123", "--file", "summary.md", "--type", "subtask"])

    assert args.command == "summary"
    assert args.summary_command == "register"
    assert args.node == "node-123"
    assert args.file == "summary.md"
    assert args.type == "subtask"
    assert args.handler


def test_summary_history_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["summary", "history", "--node", "node-123"])

    assert args.command == "summary"
    assert args.summary_command == "history"
    assert args.node == "node-123"
    assert args.handler


def test_summary_show_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["summary", "show", "--summary", "summary-123"])

    assert args.command == "summary"
    assert args.summary_command == "show"
    assert args.summary == "summary-123"
    assert args.handler


def test_prompts_history_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["prompts", "history", "--node", "node-123"])

    assert args.command == "prompts"
    assert args.prompts_command == "history"
    assert args.node == "node-123"
    assert args.handler


def test_prompts_delivered_show_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["prompts", "delivered-show", "--prompt", "prompt-123"])

    assert args.command == "prompts"
    assert args.prompts_command == "delivered-show"
    assert args.prompt == "prompt-123"
    assert args.handler


def test_node_provenance_refresh_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["node", "provenance-refresh", "--node", "node-123"])

    assert args.command == "node"
    assert args.node_command == "provenance-refresh"
    assert args.node == "node-123"
    assert args.handler


def test_rationale_show_argument_parsing_sets_handler() -> None:
    parser = build_parser()
    args = parser.parse_args(["rationale", "show", "--node", "node-123"])

    assert args.command == "rationale"
    assert args.rationale_command == "show"
    assert args.node == "node-123"
    assert args.handler


def test_entity_commands_argument_parsing_sets_handlers() -> None:
    parser = build_parser()

    show_args = parser.parse_args(["entity", "show", "--name", "src.aicoding.daemon.app.create_app"])
    history_args = parser.parse_args(["entity", "history", "--name", "src.aicoding.daemon.app.create_app"])
    relations_args = parser.parse_args(["entity", "relations", "--name", "src.aicoding.daemon.app.create_app"])
    changed_by_args = parser.parse_args(["entity", "changed-by", "--name", "src.aicoding.daemon.app.create_app"])

    assert show_args.entity_command == "show"
    assert history_args.entity_command == "history"
    assert relations_args.entity_command == "relations"
    assert changed_by_args.entity_command == "changed-by"
    assert show_args.name == "src.aicoding.daemon.app.create_app"
    assert history_args.handler
    assert relations_args.handler
    assert changed_by_args.handler


def test_missing_auth_token_returns_structured_error(capsys, monkeypatch) -> None:
    monkeypatch.setenv("AICODING_AUTH_TOKEN", "   ")
    monkeypatch.setenv("AICODING_AUTH_TOKEN_FILE", "missing-token-file")

    exit_code = run(["admin", "auth-token"])
    payload = json.loads(capsys.readouterr().err)

    assert exit_code == 2
    assert payload["error"] == "auth_token_missing"
