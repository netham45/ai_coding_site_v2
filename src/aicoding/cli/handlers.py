from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path

from aicoding.auth import load_auth_token
from aicoding.bootstrap import bootstrap_status
from aicoding.cli.context import CliContext
from aicoding.cli.daemon_client import build_daemon_client, build_daemon_base_url
from aicoding.db.bootstrap import database_status
from aicoding.db.migrations import (
    expected_database_revision,
    migration_history,
    migration_status,
    upgrade_database,
    downgrade_database,
)
from aicoding.db.session import create_engine_from_settings, current_alembic_revision, probe_database
from aicoding.errors import CommandExecutionError
from aicoding.operational_library import inspect_builtin_operational_library
from aicoding.quality_library import inspect_builtin_quality_library
from aicoding.structural_library import inspect_builtin_structural_library


def handle_doctor(args: Namespace, context: CliContext) -> dict[str, object]:
    return bootstrap_status()


def handle_print_settings(args: Namespace, context: CliContext) -> dict[str, object]:
    settings = context.settings
    return {
        "env": settings.env,
        "database_url": settings.database_url,
        "database_pool_size": settings.database_pool_size,
        "database_max_overflow": settings.database_max_overflow,
        "database_pool_timeout": settings.database_pool_timeout,
        "log_level": settings.normalized_log_level,
        "daemon_app_name": settings.daemon_app_name,
        "daemon_host": settings.daemon_host,
        "daemon_port": settings.daemon_port,
        "daemon_request_timeout_seconds": settings.daemon_request_timeout_seconds,
        "auth_token_file": str(settings.auth_token_file),
    }


def handle_auth_token(args: Namespace, context: CliContext) -> dict[str, object]:
    token = load_auth_token(settings=context.settings)
    source = "file" if context.settings.auth_token_file.exists() else "settings"
    return {
        "auth_token_source": source,
        "auth_token_length": len(token),
        "auth_token_file": str(context.settings.auth_token_file),
    }


def handle_resources(args: Namespace, context: CliContext) -> dict[str, object]:
    return {name: str(path) for name, path in context.resources.group_paths().items()}


def handle_db_upgrade(args: Namespace, context: CliContext, *, alembic_config_factory) -> dict[str, object]:
    upgrade_database(args.revision, config=alembic_config_factory())
    return {"status": "ok", "revision": args.revision}


def handle_db_downgrade(args: Namespace, context: CliContext, *, alembic_config_factory) -> dict[str, object]:
    downgrade_database(args.revision, config=alembic_config_factory())
    return {"status": "ok", "revision": args.revision}


def handle_db_ping(args: Namespace, context: CliContext) -> dict[str, object]:
    engine = create_engine_from_settings()
    try:
        return probe_database(engine)
    finally:
        engine.dispose()


def handle_db_status(args: Namespace, context: CliContext) -> dict[str, object]:
    engine = create_engine_from_settings()
    try:
        return database_status(engine)
    finally:
        engine.dispose()


def handle_db_current_revision(args: Namespace, context: CliContext) -> dict[str, object]:
    engine = create_engine_from_settings()
    try:
        return {"alembic_revision": current_alembic_revision(engine)}
    finally:
        engine.dispose()


def handle_db_heads(args: Namespace, context: CliContext, *, alembic_config_factory) -> dict[str, object]:
    expected_revision = expected_database_revision(alembic_config_factory())
    return {"heads": [] if expected_revision is None else [expected_revision]}


def handle_db_history(args: Namespace, context: CliContext, *, alembic_config_factory) -> dict[str, object]:
    return {"revisions": migration_history(alembic_config_factory())}


def handle_db_check_schema(args: Namespace, context: CliContext, *, alembic_config_factory) -> dict[str, object]:
    engine = create_engine_from_settings()
    try:
        return migration_status(engine, alembic_config_factory())
    finally:
        engine.dispose()


def handle_group_placeholder(args: Namespace, context: CliContext) -> dict[str, object]:
    return {
        "command_group": args.command,
        "available_subcommands": getattr(args, "available_subcommands", []),
    }


def handle_static_placeholder(args: Namespace, context: CliContext) -> dict[str, object]:
    return {
        "status": "not_implemented",
        "command_path": getattr(args, "command_path", []),
        "message": getattr(args, "placeholder_message", "CLI command skeleton placeholder."),
    }


def handle_node_run_show(args: Namespace, context: CliContext) -> dict[str, object]:
    if getattr(args, "node", None):
        client = build_daemon_client(context.settings)
        return client.request("GET", f"/api/node-runs/{args.node}")
    return {
        "status": "not_implemented",
        "command_path": ["node", "run", "show"],
        "message": "Lookup by run id is not implemented yet in this slice.",
    }


def handle_node_audit(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", f"/api/nodes/{args.node}/audit")


def handle_node_run_audit(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    if getattr(args, "run", None):
        return client.request("GET", f"/api/node-runs/{args.run}/audit")
    if getattr(args, "node", None):
        return client.request("GET", f"/api/nodes/{args.node}/runs/latest-audit")
    raise CommandExecutionError(
        message="Select --node or --run to inspect a durable run reconstruction bundle.",
        code="missing_run_selector",
        details={"command_path": ["node", "run", "audit"]},
        exit_code=2,
    )


def handle_node_runs(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", f"/api/nodes/{args.node}/runs")


def handle_node_create(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    if getattr(args, "compile", False) or getattr(args, "start_run", False):
        if getattr(args, "parent", None):
            raise CommandExecutionError(
                message="Top-level workflow start flags are only valid for parentless node creation.",
                code="invalid_top_level_start_selector",
                details={"command_path": ["node", "create"]},
                exit_code=2,
            )
        return client.request(
            "POST",
            "/api/workflows/start",
            json_payload={
                "kind": args.kind,
                "title": args.title,
                "prompt": args.prompt,
                "start_run": bool(getattr(args, "start_run", False)),
            },
        )
    payload = {
        "kind": args.kind,
        "title": args.title,
        "prompt": args.prompt,
        "parent_node_id": getattr(args, "parent", None),
    }
    return client.request("POST", "/api/nodes/create", json_payload=payload)


def handle_node_child_create(args: Namespace, context: CliContext) -> dict[str, object]:
    return handle_node_create(args, context)


def handle_node_show(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", f"/api/nodes/{args.node}/summary")


def handle_node_lineage(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", f"/api/nodes/{args.node}/lineage")


def handle_node_versions(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", f"/api/nodes/{args.node}/versions")


def handle_node_sources(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", f"/api/nodes/{args.node}/sources")


def handle_node_dependencies(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", f"/api/nodes/{args.node}/dependencies")


def handle_node_dependency_add(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request(
        "POST",
        "/api/nodes/dependencies/add",
        json_payload={
            "node_id": args.node,
            "depends_on_node_id": args.depends_on,
            "required_state": args.required_state,
        },
    )


def handle_node_dependency_status(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", f"/api/nodes/{args.node}/dependency-status")


def handle_node_dependency_validate(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", f"/api/nodes/{args.node}/dependency-validate")


def handle_node_blockers(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", f"/api/nodes/{args.node}/blockers")


def handle_node_supersede(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    payload: dict[str, object] = {}
    if getattr(args, "title", None) is not None:
        payload["title"] = args.title
    if getattr(args, "prompt", None) is not None:
        payload["prompt"] = args.prompt
    return client.request("POST", f"/api/nodes/{args.node}/supersede", json_payload=payload)


def handle_node_regenerate(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("POST", f"/api/nodes/{args.node}/regenerate", json_payload={})


def handle_node_rectify_upstream(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("POST", f"/api/nodes/{args.node}/rectify-upstream", json_payload={})


def handle_node_rebuild_history(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", f"/api/nodes/{args.node}/rebuild-history")


def handle_node_rebuild_coordination(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", f"/api/nodes/{args.node}/rebuild-coordination?scope={args.scope}")


def handle_node_validate(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("POST", f"/api/nodes/{args.node}/validation/run", json_payload={})


def handle_validation_show(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    if getattr(args, "node", None):
        return client.request("GET", f"/api/nodes/{args.node}/validation")
    return client.request("GET", f"/api/node-runs/{args.run}/validation")


def handle_validation_results(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", f"/api/nodes/{args.node}/validation/results")


def handle_node_review(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    payload = {
        "node_id": args.node,
        "status": args.status,
        "summary": args.summary,
        "findings_json": _load_optional_json_file(args.findings_file, expected="list"),
        "criteria_json": _load_optional_json_file(args.criteria_file, expected="any"),
    }
    return client.request("POST", f"/api/nodes/{args.node}/review/run", json_payload=payload)


def handle_review_show(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    if getattr(args, "node", None):
        return client.request("GET", f"/api/nodes/{args.node}/review")
    return client.request("GET", f"/api/node-runs/{args.run}/review")


def handle_review_results(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", f"/api/nodes/{args.node}/review/results")


def handle_node_test(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("POST", f"/api/nodes/{args.node}/testing/run", json_payload={})


def handle_node_quality_chain(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("POST", f"/api/nodes/{args.node}/quality-chain/run", json_payload={})


def handle_testing_show(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    if getattr(args, "node", None):
        return client.request("GET", f"/api/nodes/{args.node}/testing")
    return client.request("GET", f"/api/node-runs/{args.run}/testing")


def handle_testing_results(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", f"/api/nodes/{args.node}/testing/results")


def _load_optional_json_file(path: str | None, *, expected: str) -> object:
    if path is None:
        return [] if expected == "list" else None
    try:
        content = Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        raise CommandExecutionError(
            message="Unable to read JSON payload file.",
            code="json_payload_unreadable",
            details={"path": path, "reason": str(exc)},
        ) from exc
    try:
        payload = json.loads(content)
    except json.JSONDecodeError as exc:
        raise CommandExecutionError(
            message="JSON payload file is not valid JSON.",
            code="json_payload_invalid",
            details={"path": path, "reason": str(exc)},
        ) from exc
    if expected == "list" and not isinstance(payload, list):
        raise CommandExecutionError(
            message="Expected a JSON list payload.",
            code="json_payload_wrong_shape",
            details={"path": path, "expected": "list"},
        )
    return payload


def handle_node_version_show(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", f"/api/node-versions/{args.version}")


def handle_node_version_sources(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", f"/api/node-versions/{args.version}/sources")


def handle_node_version_cutover(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("POST", f"/api/node-versions/{args.version}/cutover", json_payload={})


def handle_node_version_cutover_readiness(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", f"/api/node-versions/{args.version}/cutover-readiness")


def handle_node_children(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    children = client.request("GET", f"/api/nodes/{args.node}/children")
    if not getattr(args, "versions", False):
        return {"children": children}
    summaries = [client.request("GET", f"/api/nodes/{item['node_id']}/summary") for item in children]
    return {"children": summaries, "include_versions": True}


def handle_node_materialization(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", f"/api/nodes/{args.node}/children/materialization")


def handle_node_register_layout(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    resolved_file = str(Path(args.file).expanduser().resolve())
    return client.request(
        "POST",
        f"/api/nodes/{args.node}/children/register-layout",
        json_payload={"file_path": resolved_file},
    )


def handle_node_child_reconciliation(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", f"/api/nodes/{args.node}/children/reconciliation")


def handle_node_reconcile_children(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request(
        "POST",
        f"/api/nodes/{args.node}/children/reconcile",
        json_payload={"decision": args.decision},
    )


def handle_node_child_results(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", f"/api/nodes/{args.node}/child-results")


def handle_node_reconcile(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", f"/api/nodes/{args.node}/reconcile")


def handle_node_materialize_children(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("POST", f"/api/nodes/{args.node}/children/materialize", json_payload={})


def handle_node_ancestors(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return {"ancestors": client.request("GET", f"/api/nodes/{args.node}/ancestors"), "to_root": bool(getattr(args, "to_root", False))}


def handle_node_siblings(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return {"siblings": client.request("GET", f"/api/nodes/{args.node}/siblings")}


def handle_node_kinds(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", "/api/node-kinds")


def handle_node_lifecycle_show(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", f"/api/nodes/{args.node}/lifecycle")


def handle_node_pause_state(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", f"/api/nodes/{args.node}/pause-state")


def handle_node_interventions(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", f"/api/nodes/{args.node}/interventions")


def handle_node_intervention_apply(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    payload: dict[str, object] = {
        "node_id": args.node,
        "intervention_kind": args.kind,
        "action": args.action,
    }
    if getattr(args, "summary", None):
        payload["summary"] = args.summary
    if getattr(args, "conflict_id", None):
        payload["conflict_id"] = args.conflict_id
    if getattr(args, "pause_flag", None):
        payload["pause_flag_name"] = args.pause_flag
    return client.request("POST", "/api/nodes/interventions/apply", json_payload=payload)


def handle_node_approve(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    payload = {"node_id": args.node}
    if getattr(args, "pause_flag", None):
        payload["pause_flag_name"] = args.pause_flag
    if getattr(args, "summary", None):
        payload["approval_summary"] = args.summary
    return client.request("POST", "/api/nodes/pause/approve", json_payload=payload)


def handle_node_recovery_status(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", f"/api/nodes/{args.node}/recovery-status")


def handle_node_provider_recovery_status(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", f"/api/nodes/{args.node}/recovery-provider-status")


def handle_node_events(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", f"/api/nodes/{args.node}/events")


def handle_node_child_failures(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", f"/api/nodes/{args.node}/child-failures")


def handle_node_decision_history(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", f"/api/nodes/{args.node}/decision-history")


def handle_node_respond_to_child_failure(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    payload = {"node_id": args.node, "child_node_id": args.child}
    if getattr(args, "action", None) is not None:
        payload["requested_action"] = args.action
    return client.request("POST", "/api/nodes/respond-to-child-failure", json_payload=payload)


def handle_node_lifecycle_transition(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    payload = {"node_id": args.node, "target_state": args.state}
    if getattr(args, "pause_flag", None) is not None:
        payload["pause_flag_name"] = args.pause_flag
    return client.request("POST", "/api/nodes/lifecycle/transition", json_payload=payload)


def handle_node_cursor_update(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    payload = {"node_id": args.node}
    for field_name in (
        "task",
        "subtask",
        "attempt",
        "last_completed_subtask",
        "failure_count_from_children",
        "failure_count_consecutive",
        "defer_to_user_threshold",
        "working_tree_state",
        "pause_flag",
    ):
        value = getattr(args, field_name, None)
        if value is None:
            continue
        mapped = {
            "task": "current_task_id",
            "subtask": "current_subtask_id",
            "attempt": "current_subtask_attempt",
            "last_completed_subtask": "last_completed_subtask_id",
            "pause_flag": "pause_flag_name",
        }.get(field_name, field_name)
        payload[mapped] = value
    if getattr(args, "resumable", None) is not None:
        payload["is_resumable"] = args.resumable == "true"
    if getattr(args, "cursor_json", None):
        import json

        payload["execution_cursor_json"] = json.loads(args.cursor_json)
    return client.request("POST", "/api/nodes/cursor/update", json_payload=payload)


def handle_workflow_advance(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("POST", f"/api/nodes/{args.node}/workflow/advance", json_payload={})


def handle_task_list(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    workflow = client.request("GET", f"/api/nodes/{args.node}/workflow/current")
    lifecycle = client.request("GET", f"/api/nodes/{args.node}/lifecycle")
    current_task_id = lifecycle.get("current_task_id")
    tasks = [
        {
            **task,
            "subtask_count": len(task["subtasks"]),
            "is_current": task["id"] == current_task_id,
        }
        for task in workflow["tasks"]
    ]
    return {
        "node_id": args.node,
        "compiled_workflow_id": workflow["id"],
        "lifecycle_state": lifecycle["lifecycle_state"],
        "run_status": lifecycle["run_status"],
        "current_task_id": current_task_id,
        "current_subtask_id": lifecycle.get("current_subtask_id"),
        "tasks": tasks,
    }


def handle_task_current(args: Namespace, context: CliContext) -> dict[str, object]:
    payload = handle_task_list(args, context)
    current_task_id = payload["current_task_id"]
    current_task = next((item for item in payload["tasks"] if item["id"] == current_task_id), None)
    return {
        **payload,
        "current_task": current_task,
    }


def handle_subtask_list(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    workflow = client.request("GET", f"/api/nodes/{args.node}/workflow/current")
    lifecycle = client.request("GET", f"/api/nodes/{args.node}/lifecycle")
    current_subtask_id = lifecycle.get("current_subtask_id")
    subtasks: list[dict[str, object]] = []
    for task in workflow["tasks"]:
        for subtask in task["subtasks"]:
            subtasks.append(
                {
                    **subtask,
                    "task_id": task["id"],
                    "task_key": task["task_key"],
                    "task_ordinal": task["ordinal"],
                    "is_current": subtask["id"] == current_subtask_id,
                }
            )
    return {
        "node_id": args.node,
        "compiled_workflow_id": workflow["id"],
        "lifecycle_state": lifecycle["lifecycle_state"],
        "run_status": lifecycle["run_status"],
        "current_task_id": lifecycle.get("current_task_id"),
        "current_subtask_id": current_subtask_id,
        "subtasks": subtasks,
    }


def handle_subtask_current(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", f"/api/nodes/{args.node}/subtasks/current")


def handle_subtask_attempts(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", f"/api/nodes/{args.node}/subtask-attempts")


def handle_subtask_attempt_show(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", f"/api/subtask-attempts/{args.attempt}")


def handle_subtask_prompt(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", f"/api/nodes/{args.node}/subtasks/current/prompt")


def handle_subtask_context(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", f"/api/nodes/{args.node}/subtasks/current/context")


def handle_subtask_environment(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", f"/api/nodes/{args.node}/subtasks/current/environment")


def handle_subtask_progress(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    payload = {
        "node_id": args.node,
        "compiled_subtask_id": args.compiled_subtask,
    }
    if getattr(args, "summary", None) is not None:
        payload["summary"] = args.summary
    elif getattr(args, "summary_file", None) is not None:
        try:
            payload["summary"] = Path(args.summary_file).read_text(encoding="utf-8")
        except OSError as exc:
            raise CommandExecutionError(
                message="Unable to read summary file.",
                code="summary_file_unreadable",
                details={"summary_path": args.summary_file, "reason": str(exc)},
            ) from exc
    if getattr(args, "result_file", None) is not None:
        try:
            payload["execution_result_json"] = json.loads(Path(args.result_file).read_text(encoding="utf-8"))
        except OSError as exc:
            raise CommandExecutionError(
                message="Unable to read result file.",
                code="result_file_unreadable",
                details={"result_path": args.result_file, "reason": str(exc)},
            ) from exc
        except json.JSONDecodeError as exc:
            raise CommandExecutionError(
                message="Result file must contain valid JSON.",
                code="result_file_invalid_json",
                details={"result_path": args.result_file, "reason": str(exc)},
            ) from exc
    return client.request("POST", args.daemon_path, json_payload=payload)


def handle_subtask_succeed(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    try:
        content = Path(args.summary_file).read_text(encoding="utf-8")
    except OSError as exc:
        raise CommandExecutionError(
            message="Unable to read summary file.",
            code="summary_file_unreadable",
            details={"summary_path": args.summary_file, "reason": str(exc)},
        ) from exc
    return client.request(
        "POST",
        "/api/subtasks/succeed",
        json_payload={
            "node_id": args.node,
            "compiled_subtask_id": args.compiled_subtask,
            "summary_path": args.summary_file,
            "content": content,
        },
    )


def handle_subtask_report_command(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    try:
        result_json = json.loads(Path(args.result_file).read_text(encoding="utf-8"))
    except OSError as exc:
        raise CommandExecutionError(
            message="Unable to read result file.",
            code="result_file_unreadable",
            details={"result_path": args.result_file, "reason": str(exc)},
        ) from exc
    except json.JSONDecodeError as exc:
        raise CommandExecutionError(
            message="Result file must contain valid JSON.",
            code="result_file_invalid_json",
            details={"result_path": args.result_file, "reason": str(exc)},
        ) from exc
    failure_summary = None
    if getattr(args, "failure_summary_file", None):
        try:
            failure_summary = Path(args.failure_summary_file).read_text(encoding="utf-8")
        except OSError as exc:
            raise CommandExecutionError(
                message="Unable to read failure summary file.",
                code="failure_summary_file_unreadable",
                details={"summary_path": args.failure_summary_file, "reason": str(exc)},
            ) from exc
    return client.request(
        "POST",
        "/api/subtasks/report-command",
        json_payload={
            "node_id": args.node,
            "compiled_subtask_id": args.compiled_subtask,
            "execution_result_json": result_json,
            "failure_summary": failure_summary,
        },
    )


def handle_subtask_retry(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    if getattr(args, "node", None):
        return client.request("POST", f"/api/nodes/{args.node}/subtasks/retry", json_payload={})
    return client.request("POST", f"/api/subtask-attempts/{args.attempt}/retry", json_payload={})


def handle_summary_register(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    try:
        content = Path(args.file).read_text(encoding="utf-8")
    except OSError as exc:
        raise CommandExecutionError(
            message="Unable to read summary file.",
            code="summary_file_unreadable",
            details={"summary_path": args.file, "reason": str(exc)},
        ) from exc
    return client.request(
        "POST",
        "/api/summaries/register",
        json_payload={
            "node_id": args.node,
            "summary_type": args.type,
            "summary_path": args.file,
            "content": content,
        },
    )


def handle_prompt_history(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", f"/api/nodes/{args.node}/prompt-history")


def handle_prompt_record_show(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", f"/api/prompts/{args.prompt}")


def handle_summary_history(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", f"/api/nodes/{args.node}/summary-history")


def handle_summary_show(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", f"/api/summaries/{args.summary}")


def handle_environment_policies(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", "/api/policies/environments")


def handle_attempt_environment(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", f"/api/subtask-attempts/{args.attempt}/environment")


def handle_node_provenance_refresh(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("POST", f"/api/nodes/{args.node}/provenance/refresh", json_payload={})


def handle_rationale_show(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", f"/api/nodes/{args.node}/rationale")


def handle_entity_show(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", f"/api/entities/by-name/{args.name}")


def handle_entity_history(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", f"/api/entities/by-name/{args.name}/history")


def handle_entity_relations(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", f"/api/entities/by-name/{args.name}/relations")


def handle_entity_changed_by(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", f"/api/entities/by-name/{args.name}/changed-by")


def handle_git_branch_show(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    if getattr(args, "node", None):
        return client.request("GET", f"/api/nodes/{args.node}/git/branch")
    return client.request("GET", f"/api/node-versions/{args.version}/git/branch")


def handle_git_seed_show(args: Namespace, context: CliContext) -> dict[str, object]:
    payload = handle_git_branch_show(args, context)
    return {
        "node_version_id": payload["node_version_id"],
        "logical_node_id": payload["logical_node_id"],
        "active_branch_name": payload["active_branch_name"],
        "seed_commit_sha": payload["seed_commit_sha"],
        "branch_status": payload["branch_status"],
        "violations": payload["violations"],
    }


def handle_git_final_show(args: Namespace, context: CliContext) -> dict[str, object]:
    payload = handle_git_branch_show(args, context)
    return {
        "node_version_id": payload["node_version_id"],
        "logical_node_id": payload["logical_node_id"],
        "active_branch_name": payload["active_branch_name"],
        "final_commit_sha": payload["final_commit_sha"],
        "branch_status": payload["branch_status"],
        "violations": payload["violations"],
    }


def handle_git_merge_events_show(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", f"/api/nodes/{args.node}/git/merge-events")


def handle_git_bootstrap_node(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    files_json = _load_optional_json_file(args.files_file, expected="any")
    if files_json is None:
        files_json = {}
    if not isinstance(files_json, dict) or not all(isinstance(key, str) and isinstance(value, str) for key, value in files_json.items()):
        raise CommandExecutionError(
            message="Git bootstrap files payload must be a JSON object of string file paths to string contents.",
            code="git_bootstrap_files_invalid",
            details={"path": args.files_file},
        )
    return client.request(
        "POST",
        f"/api/node-versions/{args.version}/git/bootstrap",
        json_payload={
            "version_id": args.version,
            "base_version_id": args.base_version,
            "replace_existing": args.replace_existing,
            "files_json": files_json,
        },
    )


def handle_git_merge_children(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("POST", f"/api/nodes/{args.node}/git/merge-children", json_payload={})


def handle_git_abort_merge(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("POST", f"/api/nodes/{args.node}/git/abort-merge", json_payload={})


def handle_git_finalize_node(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("POST", f"/api/nodes/{args.node}/git/finalize", json_payload={})


def handle_git_status_show(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", f"/api/node-versions/{args.version}/git/status")


def handle_git_merge_conflicts_show(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    if getattr(args, "node", None):
        return client.request("GET", f"/api/nodes/{args.node}/git/merge-conflicts")
    return client.request("GET", f"/api/node-versions/{args.version}/git/merge-conflicts")


def handle_git_merge_conflicts_record(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request(
        "POST",
        "/api/git/merge-conflicts/record",
        json_payload={
            "parent_node_version_id": args.parent_version,
            "child_node_version_id": args.child_version,
            "child_final_commit_sha": args.child_final_commit,
            "parent_commit_before": args.parent_before,
            "parent_commit_after": args.parent_after,
            "merge_order": args.merge_order,
            "files_json": args.files,
            "merge_base_sha": args.merge_base,
        },
    )


def handle_git_merge_conflicts_resolve(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request(
        "POST",
        f"/api/git/merge-conflicts/{args.conflict}/resolve",
        json_payload={
            "resolution_summary": args.summary,
            "resolution_status": args.status,
        },
    )


def handle_yaml_validate(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request(
        "POST",
        "/api/yaml/validate",
        json_payload={"source_group": args.group, "relative_path": args.path},
    )


def handle_yaml_schema_families(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", "/api/yaml/schema-families")


def handle_yaml_sources(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    if getattr(args, "node", None):
        return client.request("GET", f"/api/nodes/{args.node}/sources")
    if getattr(args, "workflow", None):
        return client.request("GET", f"/api/workflows/{args.workflow}/sources")
    return {
        "source_type": "yaml",
        "scope": args.scope,
        "resources": {name: str(path) for name, path in context.resources.group_paths().items() if name.startswith("yaml_")},
    }


def handle_yaml_structural_library(args: Namespace, context: CliContext) -> dict[str, object]:
    return inspect_builtin_structural_library(context.resources).to_payload()


def handle_yaml_quality_library(args: Namespace, context: CliContext) -> dict[str, object]:
    return inspect_builtin_quality_library(context.resources).to_payload()


def handle_yaml_operational_library(args: Namespace, context: CliContext) -> dict[str, object]:
    return inspect_builtin_operational_library(context.resources).to_payload()


def handle_yaml_project_policy(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", "/api/policies/project")


def handle_yaml_effective_policy(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", "/api/policies/effective")


def handle_yaml_policy_impact(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", f"/api/policies/impact/{args.kind}")


def handle_yaml_override_chain(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    if getattr(args, "node", None):
        return client.request("GET", f"/api/nodes/{args.node}/yaml/override-chain")
    if getattr(args, "workflow", None):
        return client.request("GET", f"/api/workflows/{args.workflow}/yaml/override-chain")
    return {
        "status": "not_implemented",
        "command_path": ["yaml", "override-chain"],
        "message": "Select --node or --workflow.",
    }


def handle_yaml_resolved(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    query = []
    if getattr(args, "family", None):
        query.append(f"family={args.family}")
    if getattr(args, "id", None):
        query.append(f"document_id={args.id}")
    suffix = "" if not query else f"?{'&'.join(query)}"
    if getattr(args, "node", None):
        return client.request("GET", f"/api/nodes/{args.node}/yaml/resolved{suffix}")
    if getattr(args, "workflow", None):
        return client.request("GET", f"/api/workflows/{args.workflow}/yaml/resolved{suffix}")
    return {
        "status": "not_implemented",
        "command_path": ["yaml", "resolved"],
        "message": "Select --node or --workflow.",
    }


def handle_workflow_sources(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    if getattr(args, "node", None):
        return client.request("GET", f"/api/nodes/{args.node}/workflow/sources")
    if getattr(args, "version", None):
        return client.request("GET", f"/api/node-versions/{args.version}/workflow/sources")
    if getattr(args, "workflow", None):
        return client.request("GET", f"/api/workflows/{args.workflow}/sources")
    return {
        "status": "not_implemented",
        "command_path": ["workflow", "sources"],
        "message": "Select --node or --workflow to inspect compiled workflow source lineage.",
    }


def handle_workflow_source_discovery(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    if getattr(args, "node", None):
        return client.request("GET", f"/api/nodes/{args.node}/workflow/source-discovery")
    if getattr(args, "version", None):
        return client.request("GET", f"/api/node-versions/{args.version}/workflow/source-discovery")
    if getattr(args, "workflow", None):
        return client.request("GET", f"/api/workflows/{args.workflow}/source-discovery")
    return {
        "status": "not_implemented",
        "command_path": ["workflow", "source-discovery"],
        "message": "Select --node or --workflow to inspect deterministic source discovery inputs.",
    }


def handle_workflow_schema_validation(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    if getattr(args, "node", None):
        return client.request("GET", f"/api/nodes/{args.node}/workflow/schema-validation")
    if getattr(args, "version", None):
        return client.request("GET", f"/api/node-versions/{args.version}/workflow/schema-validation")
    if getattr(args, "workflow", None):
        return client.request("GET", f"/api/workflows/{args.workflow}/schema-validation")
    return {
        "status": "not_implemented",
        "command_path": ["workflow", "schema-validation"],
        "message": "Select --node or --workflow to inspect compile-stage schema validation inputs.",
    }


def handle_workflow_override_resolution(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    if getattr(args, "node", None):
        return client.request("GET", f"/api/nodes/{args.node}/workflow/override-resolution")
    if getattr(args, "version", None):
        return client.request("GET", f"/api/node-versions/{args.version}/workflow/override-resolution")
    if getattr(args, "workflow", None):
        return client.request("GET", f"/api/workflows/{args.workflow}/override-resolution")
    return {
        "status": "not_implemented",
        "command_path": ["workflow", "override-resolution"],
        "message": "Select --node or --workflow to inspect compile-stage override resolution.",
    }


def handle_workflow_hook_policy(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    if getattr(args, "node", None):
        return client.request("GET", f"/api/nodes/{args.node}/workflow/hook-policy")
    if getattr(args, "version", None):
        return client.request("GET", f"/api/node-versions/{args.version}/workflow/hook-policy")
    if getattr(args, "workflow", None):
        return client.request("GET", f"/api/workflows/{args.workflow}/hook-policy")
    return {
        "status": "not_implemented",
        "command_path": ["workflow", "hook-policy"],
        "message": "Select --node or --workflow to inspect compile-stage policy folding and hook expansion.",
    }


def handle_workflow_hooks(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    if getattr(args, "node", None):
        return client.request("GET", f"/api/nodes/{args.node}/workflow/hooks")
    if getattr(args, "version", None):
        return client.request("GET", f"/api/node-versions/{args.version}/workflow/hooks")
    if getattr(args, "workflow", None):
        return client.request("GET", f"/api/workflows/{args.workflow}/hooks")
    return {
        "status": "not_implemented",
        "command_path": ["workflow", "hooks"],
        "message": "Select --node or --workflow to inspect hook expansion.",
    }


def handle_workflow_rendering(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    if getattr(args, "node", None):
        return client.request("GET", f"/api/nodes/{args.node}/workflow/rendering")
    if getattr(args, "version", None):
        return client.request("GET", f"/api/node-versions/{args.version}/workflow/rendering")
    if getattr(args, "workflow", None):
        return client.request("GET", f"/api/workflows/{args.workflow}/rendering")
    return {
        "status": "not_implemented",
        "command_path": ["workflow", "rendering"],
        "message": "Select --node or --workflow to inspect compile-stage rendering and frozen payloads.",
    }


def handle_workflow_show(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    if getattr(args, "node", None):
        return client.request("GET", f"/api/nodes/{args.node}/workflow/current")
    if getattr(args, "version", None):
        return client.request("GET", f"/api/node-versions/{args.version}/workflow/current")
    if getattr(args, "workflow", None):
        return client.request("GET", f"/api/workflows/{args.workflow}")
    return {
        "status": "not_implemented",
        "command_path": ["workflow", "show"],
        "message": "Select --node or --workflow.",
    }


def handle_workflow_chain(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    if getattr(args, "node", None):
        return client.request("GET", f"/api/nodes/{args.node}/workflow/chain")
    if getattr(args, "version", None):
        return client.request("GET", f"/api/node-versions/{args.version}/workflow/chain")
    if getattr(args, "workflow", None):
        return client.request("GET", f"/api/workflows/{args.workflow}/chain")
    return {
        "status": "not_implemented",
        "command_path": ["workflow", "chain"],
        "message": "Select --node or --workflow.",
    }


def handle_tree_show(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    payload = client.request("GET", f"/api/nodes/{args.node}/tree")
    if getattr(args, "full", False):
        payload["full_view"] = True
    return payload


def handle_workflow_current(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", f"/api/nodes/{args.node}/workflow/current")


def handle_workflow_compile(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    if getattr(args, "node", None):
        return client.request("POST", f"/api/nodes/{args.node}/workflow/compile", json_payload={})
    if getattr(args, "version", None):
        return client.request("POST", f"/api/node-versions/{args.version}/workflow/compile", json_payload={})
    return {
        "status": "not_implemented",
        "command_path": ["workflow", "compile"],
        "message": "Select --node or --version to compile a workflow target.",
    }


def handle_workflow_start(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    if getattr(args, "project", None):
        return client.request(
            "POST",
            f"/api/projects/{args.project}/top-level-nodes",
            json_payload={
                "kind": args.kind,
                "title": getattr(args, "title", None),
                "prompt": args.prompt,
                "start_run": not getattr(args, "no_run", False),
            },
        )
    return client.request(
        "POST",
        "/api/workflows/start",
        json_payload={
            "kind": args.kind,
            "title": getattr(args, "title", None),
            "prompt": args.prompt,
            "start_run": not getattr(args, "no_run", False),
        },
    )


def handle_workflow_compile_failures(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    if getattr(args, "node", None):
        return client.request("GET", f"/api/nodes/{args.node}/workflow/compile-failures")
    if getattr(args, "version", None):
        return client.request("GET", f"/api/node-versions/{args.version}/workflow/compile-failures")
    if getattr(args, "workflow", None):
        return client.request("GET", f"/api/workflows/{args.workflow}/compile-failures")
    return {
        "status": "not_implemented",
        "command_path": ["workflow", "compile-failures"],
        "message": "Select --node or --workflow.",
    }


def handle_prompt_show(args: Namespace, context: CliContext) -> dict[str, object]:
    return {
        "source_type": "prompts",
        "scope": args.scope,
        "resources": {name: str(path) for name, path in context.resources.group_paths().items() if name.startswith("prompt_")},
    }


def handle_docs_show(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", f"/api/nodes/{args.node}/docs/{args.scope}")


def handle_docs_list(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", f"/api/nodes/{args.node}/docs")


def handle_docs_build_node_view(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("POST", f"/api/nodes/{args.node}/docs/build-node-view")


def handle_docs_build_tree(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("POST", f"/api/nodes/{args.node}/docs/build-tree")


def handle_daemon_boundary(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return {
        "transport": "daemon_api",
        "daemon_base_url": client.base_url,
        "auth_token_source": "file" if context.settings.auth_token_file.exists() else "settings",
        "command_path": getattr(args, "command_path", []),
    }


def handle_mutating_daemon_command(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    payload = getattr(args, "daemon_payload", None)
    if payload is None:
        payload = {"node_id": getattr(args, "node")}
    return client.request("POST", getattr(args, "daemon_path"), json_payload=payload)


def _node_run_start_is_nonfatal_conflict(payload: dict[str, object]) -> bool:
    if payload.get("status") != "blocked":
        return False
    blockers = payload.get("blockers")
    if not isinstance(blockers, list) or not blockers:
        return False
    blocker_kinds = {
        str(item.get("blocker_kind"))
        for item in blockers
        if isinstance(item, dict) and item.get("blocker_kind") is not None
    }
    return blocker_kinds == {"already_running"}


def handle_node_run_start(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    payload = client.request("POST", "/api/node-runs/start", json_payload={"node_id": getattr(args, "node")})
    if payload.get("status") == "blocked" and not _node_run_start_is_nonfatal_conflict(payload):
        raise CommandExecutionError(
            message="The daemon rejected the node run start because the node is not ready to run.",
            code="daemon_conflict",
            exit_code=4,
            details={
                "base_url": build_daemon_base_url(context.settings),
                "path": "/api/node-runs/start",
                "status_code": 200,
                "response": payload,
            },
        )
    return payload


def handle_debug_daemon_ping(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", "/healthz")


def handle_debug_daemon_boundary(args: Namespace, context: CliContext) -> dict[str, object]:
    return {
        "daemon_base_url": build_daemon_base_url(context.settings),
        "auth_token_source": "file" if context.settings.auth_token_file.exists() else "settings",
        "boundary": "mutating_cli_commands_must_use_daemon",
    }


def handle_session_daemon_command(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    if getattr(args, "session_http_method", "POST") == "GET":
        return client.request("GET", getattr(args, "daemon_path"))
    return client.request("POST", getattr(args, "daemon_path"), json_payload={"node_id": getattr(args, "node")})


def handle_session_show(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    if getattr(args, "node", None):
        return client.request("GET", f"/api/nodes/{args.node}/sessions/current")
    return client.request("GET", f"/api/sessions/{args.session}")


def handle_session_list(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", f"/api/nodes/{args.node}/sessions")


def handle_session_events(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", f"/api/sessions/{args.session}/events")


def handle_session_recover(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("POST", "/api/sessions/resume", json_payload={"node_id": getattr(args, "node")})


def handle_session_provider_recover(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("POST", "/api/sessions/provider-resume", json_payload={"node_id": getattr(args, "node")})


def handle_session_nudge(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("POST", "/api/sessions/nudge", json_payload={"node_id": getattr(args, "node")})


def handle_session_push(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("POST", "/api/sessions/push", json_payload={"node_id": args.node, "reason": args.reason})


def handle_session_pop(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    try:
        import json

        payload = json.loads(Path(args.file).read_text(encoding="utf-8"))
    except OSError as exc:
        raise CommandExecutionError(
            message="Unable to read child session result file.",
            code="child_session_result_unreadable",
            details={"result_path": args.file, "reason": str(exc)},
        ) from exc
    except ValueError as exc:
        raise CommandExecutionError(
            message="Child session result file must be valid JSON.",
            code="child_session_result_invalid_json",
            details={"result_path": args.file, "reason": str(exc)},
        ) from exc
    payload["session_id"] = args.session
    return client.request("POST", "/api/sessions/pop", json_payload=payload)


def handle_session_result_show(args: Namespace, context: CliContext) -> dict[str, object]:
    client = build_daemon_client(context.settings)
    return client.request("GET", f"/api/sessions/{args.session}/result")
