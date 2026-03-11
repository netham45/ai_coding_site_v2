from __future__ import annotations

import argparse

from alembic.config import Config

from aicoding.cli.handlers import (
    handle_auth_token,
    handle_daemon_boundary,
    handle_git_abort_merge,
    handle_git_bootstrap_node,
    handle_git_branch_show,
    handle_git_finalize_node,
    handle_git_merge_children,
    handle_git_final_show,
    handle_git_merge_conflicts_record,
    handle_git_merge_conflicts_resolve,
    handle_git_merge_conflicts_show,
    handle_git_merge_events_show,
    handle_git_seed_show,
    handle_git_status_show,
    handle_node_approve,
    handle_node_ancestors,
    handle_node_audit,
    handle_node_child_create,
    handle_node_child_reconciliation,
    handle_node_child_results,
    handle_node_child_failures,
    handle_node_children,
    handle_node_decision_history,
    handle_node_materialization,
    handle_node_materialize_children,
    handle_node_events,
    handle_node_intervention_apply,
    handle_node_interventions,
    handle_node_dependencies,
    handle_node_dependency_add,
    handle_node_dependency_status,
    handle_node_dependency_validate,
    handle_node_create,
    handle_node_kinds,
    handle_node_cursor_update,
    handle_node_lineage,
    handle_node_lifecycle_show,
    handle_node_lifecycle_transition,
    handle_node_pause_state,
    handle_node_provenance_refresh,
    handle_node_quality_chain,
    handle_node_rebuild_coordination,
    handle_node_rebuild_history,
    handle_node_reconcile,
    handle_node_rectify_upstream,
    handle_node_reconcile_children,
    handle_node_register_layout,
    handle_node_recovery_status,
    handle_node_provider_recovery_status,
    handle_node_respond_to_child_failure,
    handle_node_regenerate,
    handle_node_test,
    handle_node_validate,
    handle_node_blockers,
    handle_node_run_show,
    handle_node_run_audit,
    handle_node_runs,
    handle_node_show,
    handle_node_siblings,
    handle_node_sources,
    handle_node_supersede,
    handle_node_version_cutover,
    handle_node_version_cutover_readiness,
    handle_node_version_show,
    handle_node_version_sources,
    handle_node_versions,
    handle_yaml_schema_families,
    handle_db_check_schema,
    handle_db_current_revision,
    handle_db_downgrade,
    handle_db_heads,
    handle_db_history,
    handle_db_ping,
    handle_db_status,
    handle_db_upgrade,
    handle_debug_daemon_boundary,
    handle_debug_daemon_ping,
    handle_doctor,
    handle_docs_build_node_view,
    handle_docs_build_tree,
    handle_docs_list,
    handle_docs_show,
    handle_environment_policies,
    handle_group_placeholder,
    handle_mutating_daemon_command,
    handle_print_settings,
    handle_prompt_history,
    handle_prompt_record_show,
    handle_prompt_show,
    handle_rationale_show,
    handle_review_results,
    handle_review_show,
    handle_resources,
    handle_session_events,
    handle_session_daemon_command,
    handle_session_nudge,
    handle_session_pop,
    handle_session_push,
    handle_session_provider_recover,
    handle_session_recover,
    handle_session_result_show,
    handle_session_list,
    handle_session_show,
    handle_static_placeholder,
    handle_subtask_attempt_show,
    handle_subtask_attempts,
    handle_subtask_list,
    handle_subtask_current,
    handle_subtask_context,
    handle_subtask_environment,
    handle_subtask_prompt,
    handle_subtask_progress,
    handle_subtask_report_command,
    handle_subtask_retry,
    handle_subtask_succeed,
    handle_summary_history,
    handle_summary_register,
    handle_summary_show,
    handle_task_current,
    handle_task_list,
    handle_attempt_environment,
    handle_entity_changed_by,
    handle_entity_history,
    handle_entity_relations,
    handle_entity_show,
    handle_testing_results,
    handle_testing_show,
    handle_tree_show,
    handle_node_review,
    handle_validation_results,
    handle_validation_show,
    handle_workflow_advance,
    handle_workflow_hook_policy,
    handle_workflow_override_resolution,
    handle_workflow_rendering,
    handle_workflow_schema_validation,
    handle_workflow_source_discovery,
    handle_workflow_sources,
    handle_workflow_show,
    handle_workflow_chain,
    handle_workflow_current,
    handle_workflow_start,
    handle_workflow_compile,
    handle_workflow_compile_failures,
    handle_workflow_hooks,
    handle_yaml_effective_policy,
    handle_yaml_override_chain,
    handle_yaml_operational_library,
    handle_yaml_policy_impact,
    handle_yaml_quality_library,
    handle_yaml_project_policy,
    handle_yaml_resolved,
    handle_yaml_structural_library,
    handle_yaml_validate,
    handle_yaml_sources,
)


def alembic_config() -> Config:
    return Config("alembic.ini")


def add_common_output_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--json", action="store_true", help="Emit machine-readable output.")


def add_node_group(subparsers) -> None:
    node_parser = subparsers.add_parser("node", help="Node inspection and control commands.")
    node_subparsers = node_parser.add_subparsers(dest="node_command", required=True)

    create_parser = node_subparsers.add_parser("create", help="Create a node via the daemon.")
    create_parser.add_argument("--kind", required=True)
    create_parser.add_argument("--title", required=True)
    create_parser.add_argument("--prompt", required=True)
    create_parser.add_argument("--parent")
    create_parser.add_argument("--compile", action="store_true")
    create_parser.add_argument("--start-run", action="store_true")
    create_parser.set_defaults(handler=handle_node_create, command_path=["node", "create"])

    child_parser = node_subparsers.add_parser("child", help="Manual child-node construction commands.")
    child_subparsers = child_parser.add_subparsers(dest="node_child_command", required=True)

    child_create_parser = child_subparsers.add_parser("create", help="Create a child node manually under an existing parent.")
    child_create_parser.add_argument("--parent", required=True)
    child_create_parser.add_argument("--kind", required=True)
    child_create_parser.add_argument("--title", required=True)
    child_create_parser.add_argument("--prompt", required=True)
    child_create_parser.set_defaults(handler=handle_node_child_create, command_path=["node", "child", "create"])

    show_parser = node_subparsers.add_parser("show", help="Show node details.")
    show_parser.add_argument("--node", required=True)
    show_parser.set_defaults(handler=handle_node_show, command_path=["node", "show"])

    audit_parser = node_subparsers.add_parser("audit", help="Show the durable reconstruction bundle for a node.")
    audit_parser.add_argument("--node", required=True)
    audit_parser.set_defaults(handler=handle_node_audit, command_path=["node", "audit"])

    ancestors_parser = node_subparsers.add_parser("ancestors", help="Show node ancestors.")
    ancestors_parser.add_argument("--node", required=True)
    ancestors_parser.add_argument("--to-root", action="store_true")
    ancestors_parser.set_defaults(handler=handle_node_ancestors, command_path=["node", "ancestors"])

    children_parser = node_subparsers.add_parser("children", help="Show node children.")
    children_parser.add_argument("--node", required=True)
    children_parser.add_argument("--versions", action="store_true")
    children_parser.set_defaults(handler=handle_node_children, command_path=["node", "children"])

    materialization_parser = node_subparsers.add_parser("child-materialization", help="Show layout-driven child materialization and scheduling state.")
    materialization_parser.add_argument("--node", required=True)
    materialization_parser.set_defaults(handler=handle_node_materialization, command_path=["node", "child-materialization"])

    register_layout_parser = node_subparsers.add_parser("register-layout", help="Register a generated child layout file by filename for later materialization.")
    register_layout_parser.add_argument("--node", required=True)
    register_layout_parser.add_argument("--file", required=True)
    register_layout_parser.set_defaults(handler=handle_node_register_layout, command_path=["node", "register-layout"])

    materialize_children_parser = node_subparsers.add_parser("materialize-children", help="Materialize child nodes from the node's default layout.")
    materialize_children_parser.add_argument("--node", required=True)
    materialize_children_parser.set_defaults(handler=handle_node_materialize_children, command_path=["node", "materialize-children"])

    reconciliation_parser = node_subparsers.add_parser("child-reconciliation", help="Show available reconciliation decisions for a manual/layout hybrid child tree.")
    reconciliation_parser.add_argument("--node", required=True)
    reconciliation_parser.set_defaults(handler=handle_node_child_reconciliation, command_path=["node", "child-reconciliation"])

    reconcile_children_parser = node_subparsers.add_parser("reconcile-children", help="Apply an explicit reconciliation decision to a manual/layout child tree.")
    reconcile_children_parser.add_argument("--node", required=True)
    reconcile_children_parser.add_argument("--decision", required=True, choices=["preserve_manual"])
    reconcile_children_parser.set_defaults(handler=handle_node_reconcile_children, command_path=["node", "reconcile-children"])

    child_results_parser = node_subparsers.add_parser("child-results", help="Show authoritative child finals and reconcile readiness for a parent node.")
    child_results_parser.add_argument("--node", required=True)
    child_results_parser.set_defaults(handler=handle_node_child_results, command_path=["node", "child-results"])

    reconcile_parser = node_subparsers.add_parser("reconcile", help="Inspect the parent-local reconcile prompt and current merge context.")
    reconcile_parser.add_argument("--node", required=True)
    reconcile_parser.set_defaults(handler=handle_node_reconcile, command_path=["node", "reconcile"])

    siblings_parser = node_subparsers.add_parser("siblings", help="Show node siblings.")
    siblings_parser.add_argument("--node", required=True)
    siblings_parser.set_defaults(handler=handle_node_siblings, command_path=["node", "siblings"])

    kinds_parser = node_subparsers.add_parser("kinds", help="List configured node kinds.")
    kinds_parser.set_defaults(handler=handle_node_kinds, command_path=["node", "kinds"])

    lifecycle_parser = node_subparsers.add_parser("lifecycle", help="Inspect or transition durable node lifecycle state.")
    lifecycle_subparsers = lifecycle_parser.add_subparsers(dest="node_lifecycle_command", required=True)

    lifecycle_show_parser = lifecycle_subparsers.add_parser("show", help="Show the durable lifecycle and cursor state for a node.")
    lifecycle_show_parser.add_argument("--node", required=True)
    lifecycle_show_parser.set_defaults(handler=handle_node_lifecycle_show, command_path=["node", "lifecycle", "show"])

    lifecycle_transition_parser = lifecycle_subparsers.add_parser("transition", help="Apply a durable lifecycle transition via the daemon.")
    lifecycle_transition_parser.add_argument("--node", required=True)
    lifecycle_transition_parser.add_argument("--state", required=True)
    lifecycle_transition_parser.add_argument("--pause-flag")
    lifecycle_transition_parser.set_defaults(handler=handle_node_lifecycle_transition, command_path=["node", "lifecycle", "transition"])

    cursor_parser = node_subparsers.add_parser("cursor", help="Inspect or update the durable execution cursor for a node.")
    cursor_subparsers = cursor_parser.add_subparsers(dest="node_cursor_command", required=True)

    cursor_show_parser = cursor_subparsers.add_parser("show", help="Show the durable cursor state for a node.")
    cursor_show_parser.add_argument("--node", required=True)
    cursor_show_parser.set_defaults(handler=handle_node_lifecycle_show, command_path=["node", "cursor", "show"])

    cursor_update_parser = cursor_subparsers.add_parser("update", help="Update the durable cursor state for a node.")
    cursor_update_parser.add_argument("--node", required=True)
    cursor_update_parser.add_argument("--task")
    cursor_update_parser.add_argument("--subtask")
    cursor_update_parser.add_argument("--attempt", type=int)
    cursor_update_parser.add_argument("--last-completed-subtask")
    cursor_update_parser.add_argument("--cursor-json")
    cursor_update_parser.add_argument("--failure-count-from-children", type=int)
    cursor_update_parser.add_argument("--failure-count-consecutive", type=int)
    cursor_update_parser.add_argument("--defer-to-user-threshold", type=int)
    cursor_update_parser.add_argument("--resumable", choices=["true", "false"])
    cursor_update_parser.add_argument("--pause-flag")
    cursor_update_parser.add_argument("--working-tree-state")
    cursor_update_parser.set_defaults(handler=handle_node_cursor_update, command_path=["node", "cursor", "update"])

    lineage_parser = node_subparsers.add_parser("lineage", help="Show node version lineage.")
    lineage_parser.add_argument("--node", required=True)
    lineage_parser.set_defaults(handler=handle_node_lineage, command_path=["node", "lineage"])

    versions_parser = node_subparsers.add_parser("versions", help="List durable versions for a logical node.")
    versions_parser.add_argument("--node", required=True)
    versions_parser.set_defaults(handler=handle_node_versions, command_path=["node", "versions"])

    sources_parser = node_subparsers.add_parser("sources", help="Show captured source lineage for the authoritative node version.")
    sources_parser.add_argument("--node", required=True)
    sources_parser.set_defaults(handler=handle_node_sources, command_path=["node", "sources"])

    dependencies_parser = node_subparsers.add_parser("dependencies", help="Show authoritative node dependency edges.")
    dependencies_parser.add_argument("--node", required=True)
    dependencies_parser.set_defaults(handler=handle_node_dependencies, command_path=["node", "dependencies"])

    dependency_add_parser = node_subparsers.add_parser("dependency-add", help="Add a dependency edge between authoritative nodes.")
    dependency_add_parser.add_argument("--node", required=True)
    dependency_add_parser.add_argument("--depends-on", required=True)
    dependency_add_parser.add_argument("--required-state", default="COMPLETE")
    dependency_add_parser.set_defaults(handler=handle_node_dependency_add, command_path=["node", "dependency-add"])

    dependency_status_parser = node_subparsers.add_parser("dependency-status", help="Show dependency readiness for a node.")
    dependency_status_parser.add_argument("--node", required=True)
    dependency_status_parser.set_defaults(handler=handle_node_dependency_status, command_path=["node", "dependency-status"])

    dependency_validate_parser = node_subparsers.add_parser("dependency-validate", help="Validate the current node dependency graph.")
    dependency_validate_parser.add_argument("--node", required=True)
    dependency_validate_parser.set_defaults(handler=handle_node_dependency_validate, command_path=["node", "dependency-validate"])

    blockers_parser = node_subparsers.add_parser("blockers", help="Show persisted dependency blockers for a node.")
    blockers_parser.add_argument("--node", required=True)
    blockers_parser.set_defaults(handler=handle_node_blockers, command_path=["node", "blockers"])

    provenance_refresh_parser = node_subparsers.add_parser("provenance-refresh", help="Refresh durable code provenance and rationale mappings for the authoritative node version.")
    provenance_refresh_parser.add_argument("--node", required=True)
    provenance_refresh_parser.set_defaults(handler=handle_node_provenance_refresh, command_path=["node", "provenance-refresh"])

    supersede_parser = node_subparsers.add_parser("supersede", help="Create a non-destructive candidate version for a node.")
    supersede_parser.add_argument("--node", required=True)
    supersede_parser.add_argument("--title")
    supersede_parser.add_argument("--prompt")
    supersede_parser.set_defaults(handler=handle_node_supersede, command_path=["node", "supersede"])

    regenerate_parser = node_subparsers.add_parser("regenerate", help="Create and compile a candidate subtree rebuild for a node and its descendants.")
    regenerate_parser.add_argument("--node", required=True)
    regenerate_parser.set_defaults(handler=handle_node_regenerate, command_path=["node", "regenerate"])

    rectify_parser = node_subparsers.add_parser("rectify-upstream", help="Regenerate a node subtree and rebuild ancestor candidates up to the top node.")
    rectify_parser.add_argument("--node", required=True)
    rectify_parser.set_defaults(handler=handle_node_rectify_upstream, command_path=["node", "rectify-upstream"])

    rebuild_history_parser = node_subparsers.add_parser("rebuild-history", help="Show durable rebuild and rectification history for a node lineage.")
    rebuild_history_parser.add_argument("--node", required=True)
    rebuild_history_parser.set_defaults(handler=handle_node_rebuild_history, command_path=["node", "rebuild-history"])

    rebuild_coordination_parser = node_subparsers.add_parser("rebuild-coordination", help="Show live runtime blockers for subtree or upstream rebuild coordination.")
    rebuild_coordination_parser.add_argument("--node", required=True)
    rebuild_coordination_parser.add_argument("--scope", choices=["subtree", "upstream"], default="subtree")
    rebuild_coordination_parser.set_defaults(handler=handle_node_rebuild_coordination, command_path=["node", "rebuild-coordination"])

    validate_parser = node_subparsers.add_parser("validate", help="Run the current validation gate for a node's active workflow.")
    validate_parser.add_argument("--node", required=True)
    validate_parser.set_defaults(handler=handle_node_validate, command_path=["node", "validate"])

    review_parser = node_subparsers.add_parser("review", help="Record and route the current review gate for a node's active workflow.")
    review_parser.add_argument("--node", required=True)
    review_parser.add_argument("--status", required=True, choices=["pass", "revise", "fail", "passed", "failed"])
    review_parser.add_argument("--summary")
    review_parser.add_argument("--findings-file")
    review_parser.add_argument("--criteria-file")
    review_parser.set_defaults(handler=handle_node_review, command_path=["node", "review"])

    test_parser = node_subparsers.add_parser("test", help="Run the current testing gate for a node's active workflow.")
    test_parser.add_argument("--node", required=True)
    test_parser.set_defaults(handler=handle_node_test, command_path=["node", "test"])

    quality_chain_parser = node_subparsers.add_parser("quality-chain", help="Run the built-in validation, review, testing, provenance, docs, and finalize chain for the active node run.")
    quality_chain_parser.add_argument("--node", required=True)
    quality_chain_parser.set_defaults(handler=handle_node_quality_chain, command_path=["node", "quality-chain"])

    runs_parser = node_subparsers.add_parser("runs", help="List node runs.")
    runs_parser.add_argument("--node", required=True)
    runs_parser.set_defaults(handler=handle_node_runs, command_path=["node", "runs"])

    run_parser = node_subparsers.add_parser("run", help="Run-specific node commands.")
    run_subparsers = run_parser.add_subparsers(dest="node_run_command", required=True)

    run_show_parser = run_subparsers.add_parser("show", help="Show a node run.")
    run_show_parser.add_argument("--node")
    run_show_parser.add_argument("--run")
    run_show_parser.set_defaults(handler=handle_node_run_show, command_path=["node", "run", "show"])

    run_audit_parser = run_subparsers.add_parser("audit", help="Show the durable reconstruction bundle for a node run.")
    run_audit_parser.add_argument("--node")
    run_audit_parser.add_argument("--run")
    run_audit_parser.set_defaults(handler=handle_node_run_audit, command_path=["node", "run", "audit"])

    run_start_parser = run_subparsers.add_parser("start", help="Start a node run via the daemon.")
    run_start_parser.add_argument("--node", required=True)
    run_start_parser.set_defaults(
        handler=handle_mutating_daemon_command,
        command_path=["node", "run", "start"],
        daemon_path="/api/node-runs/start",
        daemon_payload=None,
    )

    pause_parser = node_subparsers.add_parser("pause", help="Pause a node via the daemon.")
    pause_parser.add_argument("--node", required=True)
    pause_parser.set_defaults(
        handler=handle_mutating_daemon_command,
        command_path=["node", "pause"],
        daemon_path="/api/nodes/pause",
        daemon_payload=None,
    )

    resume_parser = node_subparsers.add_parser("resume", help="Resume a node via the daemon.")
    resume_parser.add_argument("--node", required=True)
    resume_parser.set_defaults(
        handler=handle_mutating_daemon_command,
        command_path=["node", "resume"],
        daemon_path="/api/nodes/resume",
        daemon_payload=None,
    )

    cancel_parser = node_subparsers.add_parser("cancel", help="Cancel the active node run via the daemon.")
    cancel_parser.add_argument("--node", required=True)
    cancel_parser.set_defaults(
        handler=handle_mutating_daemon_command,
        command_path=["node", "cancel"],
        daemon_path="/api/nodes/cancel",
        daemon_payload=None,
    )

    pause_state_parser = node_subparsers.add_parser("pause-state", help="Show current pause-related state for a node.")
    pause_state_parser.add_argument("--node", required=True)
    pause_state_parser.set_defaults(handler=handle_node_pause_state, command_path=["node", "pause-state"])

    interventions_parser = node_subparsers.add_parser("interventions", help="Show pending human intervention items for a node.")
    interventions_parser.add_argument("--node", required=True)
    interventions_parser.set_defaults(handler=handle_node_interventions, command_path=["node", "interventions"])

    intervention_apply_parser = node_subparsers.add_parser("intervention-apply", help="Apply a pending human intervention action for a node.")
    intervention_apply_parser.add_argument("--node", required=True)
    intervention_apply_parser.add_argument("--kind", required=True)
    intervention_apply_parser.add_argument("--action", required=True)
    intervention_apply_parser.add_argument("--summary")
    intervention_apply_parser.add_argument("--conflict-id")
    intervention_apply_parser.add_argument("--pause-flag")
    intervention_apply_parser.set_defaults(handler=handle_node_intervention_apply, command_path=["node", "intervention-apply"])

    approve_parser = node_subparsers.add_parser("approve", help="Approve the current user-gated pause for a node without resuming it yet.")
    approve_parser.add_argument("--node", required=True)
    approve_parser.add_argument("--pause-flag")
    approve_parser.add_argument("--summary")
    approve_parser.set_defaults(handler=handle_node_approve, command_path=["node", "approve"])

    recovery_status_parser = node_subparsers.add_parser("recovery-status", help="Show provider-agnostic recovery classification for the active node run.")
    recovery_status_parser.add_argument("--node", required=True)
    recovery_status_parser.set_defaults(handler=handle_node_recovery_status, command_path=["node", "recovery-status"])

    provider_recovery_status_parser = node_subparsers.add_parser("recovery-provider-status", help="Show provider-aware recovery classification for the active node run.")
    provider_recovery_status_parser.add_argument("--node", required=True)
    provider_recovery_status_parser.set_defaults(handler=handle_node_provider_recovery_status, command_path=["node", "recovery-provider-status"])

    events_parser = node_subparsers.add_parser("events", help="Show daemon-owned node event history.")
    events_parser.add_argument("--node", required=True)
    events_parser.set_defaults(handler=handle_node_events, command_path=["node", "events"])

    child_failures_parser = node_subparsers.add_parser("child-failures", help="Show durable child-failure counters for a parent node.")
    child_failures_parser.add_argument("--node", required=True)
    child_failures_parser.set_defaults(handler=handle_node_child_failures, command_path=["node", "child-failures"])

    decision_history_parser = node_subparsers.add_parser("decision-history", help="Show durable parent-decision history for a node.")
    decision_history_parser.add_argument("--node", required=True)
    decision_history_parser.set_defaults(handler=handle_node_decision_history, command_path=["node", "decision-history"])

    respond_failure_parser = node_subparsers.add_parser("respond-to-child-failure", help="Apply parent decision logic to a failed child node.")
    respond_failure_parser.add_argument("--node", required=True)
    respond_failure_parser.add_argument("--child", required=True)
    respond_failure_parser.add_argument("--action", choices=["retry_child", "regenerate_child", "replan_parent", "pause_for_user"])
    respond_failure_parser.set_defaults(handler=handle_node_respond_to_child_failure, command_path=["node", "respond-to-child-failure"])

    version_parser = node_subparsers.add_parser("version", help="Version-specific node commands.")
    version_subparsers = version_parser.add_subparsers(dest="node_version_command", required=True)

    version_show_parser = version_subparsers.add_parser("show", help="Show one durable node version.")
    version_show_parser.add_argument("--version", required=True)
    version_show_parser.set_defaults(handler=handle_node_version_show, command_path=["node", "version", "show"])

    version_sources_parser = version_subparsers.add_parser("sources", help="Show captured source lineage for one node version.")
    version_sources_parser.add_argument("--version", required=True)
    version_sources_parser.set_defaults(handler=handle_node_version_sources, command_path=["node", "version", "sources"])

    version_cutover_parser = version_subparsers.add_parser("cutover", help="Promote a candidate version to authoritative.")
    version_cutover_parser.add_argument("--version", required=True)
    version_cutover_parser.set_defaults(handler=handle_node_version_cutover, command_path=["node", "version", "cutover"])

    version_cutover_readiness_parser = version_subparsers.add_parser("cutover-readiness", help="Show detailed cutover readiness and blockers for a candidate version.")
    version_cutover_readiness_parser.add_argument("--version", required=True)
    version_cutover_readiness_parser.set_defaults(handler=handle_node_version_cutover_readiness, command_path=["node", "version", "cutover-readiness"])


def add_workflow_group(subparsers) -> None:
    workflow_parser = subparsers.add_parser("workflow", help="Workflow inspection commands.")
    workflow_subparsers = workflow_parser.add_subparsers(dest="workflow_command", required=True)

    show_parser = workflow_subparsers.add_parser("show", help="Show one compiled workflow.")
    show_parser.add_argument("--node")
    show_parser.add_argument("--version")
    show_parser.add_argument("--workflow")
    show_parser.add_argument("--run")
    show_parser.set_defaults(handler=handle_workflow_show, command_path=["workflow", "show"])

    chain_parser = workflow_subparsers.add_parser("chain", help="Show the compiled subtask chain.")
    chain_parser.add_argument("--node")
    chain_parser.add_argument("--version")
    chain_parser.add_argument("--workflow")
    chain_parser.add_argument("--run")
    chain_parser.set_defaults(handler=handle_workflow_chain, command_path=["workflow", "chain"])

    current_parser = workflow_subparsers.add_parser("current", help="Show the current compiled workflow binding for a node.")
    current_parser.add_argument("--node", required=True)
    current_parser.set_defaults(handler=handle_workflow_current, command_path=["workflow", "current"])

    sources_parser = workflow_subparsers.add_parser("sources", help="Show source lineage for a compiled workflow.")
    sources_parser.add_argument("--node")
    sources_parser.add_argument("--version")
    sources_parser.add_argument("--workflow")
    sources_parser.add_argument("--run")
    sources_parser.set_defaults(handler=handle_workflow_sources, command_path=["workflow", "sources"])

    source_discovery_parser = workflow_subparsers.add_parser("source-discovery", help="Show deterministic compile input discovery for a workflow.")
    source_discovery_parser.add_argument("--node")
    source_discovery_parser.add_argument("--version")
    source_discovery_parser.add_argument("--workflow")
    source_discovery_parser.set_defaults(handler=handle_workflow_source_discovery, command_path=["workflow", "source-discovery"])

    schema_validation_parser = workflow_subparsers.add_parser("schema-validation", help="Show compile-stage schema validation inventory for a workflow.")
    schema_validation_parser.add_argument("--node")
    schema_validation_parser.add_argument("--version")
    schema_validation_parser.add_argument("--workflow")
    schema_validation_parser.set_defaults(handler=handle_workflow_schema_validation, command_path=["workflow", "schema-validation"])

    override_resolution_parser = workflow_subparsers.add_parser("override-resolution", help="Show compile-stage override resolution for a workflow.")
    override_resolution_parser.add_argument("--node")
    override_resolution_parser.add_argument("--version")
    override_resolution_parser.add_argument("--workflow")
    override_resolution_parser.set_defaults(handler=handle_workflow_override_resolution, command_path=["workflow", "override-resolution"])

    hook_policy_parser = workflow_subparsers.add_parser("hook-policy", help="Show compile-stage policy folding and hook expansion for a workflow.")
    hook_policy_parser.add_argument("--node")
    hook_policy_parser.add_argument("--version")
    hook_policy_parser.add_argument("--workflow")
    hook_policy_parser.set_defaults(handler=handle_workflow_hook_policy, command_path=["workflow", "hook-policy"])

    hooks_parser = workflow_subparsers.add_parser("hooks", help="Show the hook selection and expansion plan for a compiled workflow.")
    hooks_parser.add_argument("--node")
    hooks_parser.add_argument("--version")
    hooks_parser.add_argument("--workflow")
    hooks_parser.add_argument("--run")
    hooks_parser.set_defaults(handler=handle_workflow_hooks, command_path=["workflow", "hooks"])

    rendering_parser = workflow_subparsers.add_parser("rendering", help="Show compile-stage rendering diagnostics and frozen payloads for a workflow.")
    rendering_parser.add_argument("--node")
    rendering_parser.add_argument("--version")
    rendering_parser.add_argument("--workflow")
    rendering_parser.set_defaults(handler=handle_workflow_rendering, command_path=["workflow", "rendering"])

    compile_parser = workflow_subparsers.add_parser("compile", help="Compile the workflow for an authoritative node or an explicit node version.")
    compile_parser.add_argument("--node")
    compile_parser.add_argument("--version")
    compile_parser.set_defaults(handler=handle_workflow_compile, command_path=["workflow", "compile"])

    start_parser = workflow_subparsers.add_parser("start", help="Create a top-level node from a prompt, compile it, and optionally start the first run.")
    start_parser.add_argument("--kind", required=True)
    start_parser.add_argument("--prompt", required=True)
    start_parser.add_argument("--title")
    start_parser.add_argument("--no-run", action="store_true")
    start_parser.set_defaults(handler=handle_workflow_start, command_path=["workflow", "start"])

    advance_parser = workflow_subparsers.add_parser("advance", help="Advance the active workflow after successful subtask completion.")
    advance_parser.add_argument("--node", required=True)
    advance_parser.set_defaults(handler=handle_workflow_advance, command_path=["workflow", "advance"])

    pause_parser = workflow_subparsers.add_parser("pause", help="Pause the active workflow for a node.")
    pause_parser.add_argument("--node", required=True)
    pause_parser.set_defaults(
        handler=handle_mutating_daemon_command,
        command_path=["workflow", "pause"],
        daemon_path="/api/nodes/pause",
        daemon_payload=None,
    )

    resume_parser = workflow_subparsers.add_parser("resume", help="Resume the active workflow for a node.")
    resume_parser.add_argument("--node", required=True)
    resume_parser.set_defaults(
        handler=handle_mutating_daemon_command,
        command_path=["workflow", "resume"],
        daemon_path="/api/nodes/resume",
        daemon_payload=None,
    )

    cancel_parser = workflow_subparsers.add_parser("cancel", help="Cancel the active workflow for a node.")
    cancel_parser.add_argument("--node", required=True)
    cancel_parser.set_defaults(
        handler=handle_mutating_daemon_command,
        command_path=["workflow", "cancel"],
        daemon_path="/api/nodes/cancel",
        daemon_payload=None,
    )

    approve_parser = workflow_subparsers.add_parser("approve", help="Approve the current workflow pause gate for a node without resuming it yet.")
    approve_parser.add_argument("--node", required=True)
    approve_parser.add_argument("--pause-flag")
    approve_parser.add_argument("--summary")
    approve_parser.set_defaults(handler=handle_node_approve, command_path=["workflow", "approve"])

    failures_parser = workflow_subparsers.add_parser("compile-failures", help="Show durable compile failures.")
    failures_parser.add_argument("--node")
    failures_parser.add_argument("--version")
    failures_parser.add_argument("--workflow")
    failures_parser.add_argument("--run")
    failures_parser.set_defaults(handler=handle_workflow_compile_failures, command_path=["workflow", "compile-failures"])


def add_tree_group(subparsers) -> None:
    tree_parser = subparsers.add_parser("tree", help="Tree and subtree inspection commands.")
    tree_subparsers = tree_parser.add_subparsers(dest="tree_command", required=True)

    show_parser = tree_subparsers.add_parser("show", help="Show a node subtree with live state.")
    show_parser.add_argument("--node", required=True)
    show_parser.add_argument("--full", action="store_true")
    show_parser.set_defaults(handler=handle_tree_show, command_path=["tree", "show"])


def add_task_group(subparsers) -> None:
    task_parser = subparsers.add_parser("task", help="Compiled task inspection commands.")
    task_subparsers = task_parser.add_subparsers(dest="task_command", required=True)

    list_parser = task_subparsers.add_parser("list", help="List compiled tasks for the current workflow.")
    list_parser.add_argument("--node", required=True)
    list_parser.set_defaults(handler=handle_task_list, command_path=["task", "list"])

    current_parser = task_subparsers.add_parser("current", help="Show the current compiled task for a node.")
    current_parser.add_argument("--node", required=True)
    current_parser.set_defaults(handler=handle_task_current, command_path=["task", "current"])


def add_git_group(subparsers) -> None:
    git_parser = subparsers.add_parser("git", help="Git and branch metadata inspection commands.")
    git_subparsers = git_parser.add_subparsers(dest="git_command", required=True)

    branch_parser = git_subparsers.add_parser("branch", help="Inspect canonical branch metadata.")
    branch_subparsers = branch_parser.add_subparsers(dest="git_branch_command", required=True)
    branch_show_parser = branch_subparsers.add_parser("show", help="Show branch identity for a node or version.")
    branch_show_target = branch_show_parser.add_mutually_exclusive_group(required=True)
    branch_show_target.add_argument("--node")
    branch_show_target.add_argument("--version")
    branch_show_parser.set_defaults(handler=handle_git_branch_show, command_path=["git", "branch", "show"])

    seed_parser = git_subparsers.add_parser("seed", help="Inspect seed commit metadata.")
    seed_subparsers = seed_parser.add_subparsers(dest="git_seed_command", required=True)
    seed_show_parser = seed_subparsers.add_parser("show", help="Show the recorded seed commit.")
    seed_show_target = seed_show_parser.add_mutually_exclusive_group(required=True)
    seed_show_target.add_argument("--node")
    seed_show_target.add_argument("--version")
    seed_show_parser.set_defaults(handler=handle_git_seed_show, command_path=["git", "seed", "show"])

    final_parser = git_subparsers.add_parser("final", help="Inspect final commit metadata.")
    final_subparsers = final_parser.add_subparsers(dest="git_final_command", required=True)
    final_show_parser = final_subparsers.add_parser("show", help="Show the recorded final commit.")
    final_show_target = final_show_parser.add_mutually_exclusive_group(required=True)
    final_show_target.add_argument("--node")
    final_show_target.add_argument("--version")
    final_show_parser.set_defaults(handler=handle_git_final_show, command_path=["git", "final", "show"])

    merge_events_parser = git_subparsers.add_parser("merge-events", help="Inspect durable merge event history.")
    merge_events_subparsers = merge_events_parser.add_subparsers(dest="git_merge_events_command", required=True)
    merge_events_show_parser = merge_events_subparsers.add_parser("show", help="Show merge events for a node.")
    merge_events_show_parser.add_argument("--node", required=True)
    merge_events_show_parser.set_defaults(handler=handle_git_merge_events_show, command_path=["git", "merge-events", "show"])

    bootstrap_node_parser = git_subparsers.add_parser("bootstrap-node", help="Bootstrap a real live git repo for a node version.")
    bootstrap_node_parser.add_argument("--version", required=True)
    bootstrap_node_parser.add_argument("--base-version")
    bootstrap_node_parser.add_argument("--files-file")
    bootstrap_node_parser.add_argument("--replace-existing", action="store_true")
    bootstrap_node_parser.set_defaults(handler=handle_git_bootstrap_node, command_path=["git", "bootstrap-node"])

    merge_children_parser = git_subparsers.add_parser("merge-children", help="Run the live deterministic child-merge pipeline for a parent node.")
    merge_children_parser.add_argument("--node", required=True)
    merge_children_parser.set_defaults(handler=handle_git_merge_children, command_path=["git", "merge-children"])

    abort_merge_parser = git_subparsers.add_parser("abort-merge", help="Abort a conflicted live merge and reset the parent repo back to seed.")
    abort_merge_parser.add_argument("--node", required=True)
    abort_merge_parser.set_defaults(handler=handle_git_abort_merge, command_path=["git", "abort-merge"])

    finalize_node_parser = git_subparsers.add_parser("finalize-node", help="Create a real finalize commit for the authoritative node version.")
    finalize_node_parser.add_argument("--node", required=True)
    finalize_node_parser.set_defaults(handler=handle_git_finalize_node, command_path=["git", "finalize-node"])

    status_parser = git_subparsers.add_parser("status", help="Show live git status for a node version repo.")
    status_subparsers = status_parser.add_subparsers(dest="git_status_command", required=True)
    status_show_parser = status_subparsers.add_parser("show", help="Show live git status for a node version.")
    status_show_parser.add_argument("--version", required=True)
    status_show_parser.set_defaults(handler=handle_git_status_show, command_path=["git", "status", "show"])

    merge_conflicts_parser = git_subparsers.add_parser("merge-conflicts", help="Inspect and resolve durable merge conflicts.")
    merge_conflicts_subparsers = merge_conflicts_parser.add_subparsers(dest="git_merge_conflicts_command", required=True)

    merge_conflicts_show_parser = merge_conflicts_subparsers.add_parser("show", help="Show merge conflicts for a node or version.")
    merge_conflicts_show_target = merge_conflicts_show_parser.add_mutually_exclusive_group(required=True)
    merge_conflicts_show_target.add_argument("--node")
    merge_conflicts_show_target.add_argument("--version")
    merge_conflicts_show_parser.set_defaults(handler=handle_git_merge_conflicts_show, command_path=["git", "merge-conflicts", "show"])

    merge_conflicts_record_parser = merge_conflicts_subparsers.add_parser("record", help="Record a merge conflict for a parent candidate version.")
    merge_conflicts_record_parser.add_argument("--parent-version", required=True)
    merge_conflicts_record_parser.add_argument("--child-version", required=True)
    merge_conflicts_record_parser.add_argument("--child-final-commit", required=True)
    merge_conflicts_record_parser.add_argument("--parent-before", required=True)
    merge_conflicts_record_parser.add_argument("--parent-after", required=True)
    merge_conflicts_record_parser.add_argument("--merge-order", type=int, required=True)
    merge_conflicts_record_parser.add_argument("--file", dest="files", action="append", required=True)
    merge_conflicts_record_parser.add_argument("--merge-base")
    merge_conflicts_record_parser.set_defaults(handler=handle_git_merge_conflicts_record, command_path=["git", "merge-conflicts", "record"])

    merge_conflicts_resolve_parser = merge_conflicts_subparsers.add_parser("resolve", help="Resolve a recorded merge conflict.")
    merge_conflicts_resolve_parser.add_argument("--conflict", required=True)
    merge_conflicts_resolve_parser.add_argument("--summary", required=True)
    merge_conflicts_resolve_parser.add_argument("--status", choices=["resolved", "abandoned"], default="resolved")
    merge_conflicts_resolve_parser.set_defaults(handler=handle_git_merge_conflicts_resolve, command_path=["git", "merge-conflicts", "resolve"])


def add_subtask_group(subparsers) -> None:
    subtask_parser = subparsers.add_parser("subtask", help="Compiled subtask inspection commands.")
    subtask_subparsers = subtask_parser.add_subparsers(dest="subtask_command", required=True)

    list_parser = subtask_subparsers.add_parser("list", help="List compiled subtasks for the current workflow.")
    list_parser.add_argument("--node", required=True)
    list_parser.set_defaults(handler=handle_subtask_list, command_path=["subtask", "list"])

    show_parser = subtask_subparsers.add_parser("show", help="Show compiled subtask details.")
    show_parser.add_argument("--subtask", required=True)
    show_parser.set_defaults(handler=handle_static_placeholder, command_path=["subtask", "show"])

    current_parser = subtask_subparsers.add_parser("current", help="Show current run and compiled subtask state for a node.")
    current_parser.add_argument("--node", required=True)
    current_parser.set_defaults(handler=handle_subtask_current, command_path=["subtask", "current"])

    attempts_parser = subtask_subparsers.add_parser("attempts", help="List durable subtask attempts for the active node run.")
    attempts_parser.add_argument("--node", required=True)
    attempts_parser.set_defaults(handler=handle_subtask_attempts, command_path=["subtask", "attempts"])

    attempt_show_parser = subtask_subparsers.add_parser("attempt-show", help="Show one durable subtask attempt.")
    attempt_show_parser.add_argument("--attempt", required=True)
    attempt_show_parser.set_defaults(handler=handle_subtask_attempt_show, command_path=["subtask", "attempt-show"])

    prompt_parser = subtask_subparsers.add_parser("prompt", help="Show the current compiled subtask prompt payload.")
    prompt_parser.add_argument("--node", required=True)
    prompt_parser.set_defaults(handler=handle_subtask_prompt, command_path=["subtask", "prompt"])

    context_parser = subtask_subparsers.add_parser("context", help="Show the current compiled subtask context payload.")
    context_parser.add_argument("--node", required=True)
    context_parser.set_defaults(handler=handle_subtask_context, command_path=["subtask", "context"])

    environment_parser = subtask_subparsers.add_parser("environment", help="Show the current compiled subtask environment request.")
    environment_parser.add_argument("--node", required=True)
    environment_parser.set_defaults(handler=handle_subtask_environment, command_path=["subtask", "environment"])

    start_parser = subtask_subparsers.add_parser("start", help="Mark the current compiled subtask attempt as started.")
    start_parser.add_argument("--node", required=True)
    start_parser.add_argument("--compiled-subtask", required=True)
    start_parser.set_defaults(handler=handle_subtask_progress, command_path=["subtask", "start"], daemon_path="/api/subtasks/start")

    heartbeat_parser = subtask_subparsers.add_parser("heartbeat", help="Record a durable heartbeat for the current running attempt.")
    heartbeat_parser.add_argument("--node", required=True)
    heartbeat_parser.add_argument("--compiled-subtask", required=True)
    heartbeat_parser.set_defaults(handler=handle_subtask_progress, command_path=["subtask", "heartbeat"], daemon_path="/api/subtasks/heartbeat")

    complete_parser = subtask_subparsers.add_parser("complete", help="Mark the current compiled subtask attempt as complete.")
    complete_parser.add_argument("--node", required=True)
    complete_parser.add_argument("--compiled-subtask", required=True)
    complete_parser.add_argument("--summary")
    complete_parser.add_argument("--result-file")
    complete_parser.set_defaults(handler=handle_subtask_progress, command_path=["subtask", "complete"], daemon_path="/api/subtasks/complete")

    succeed_parser = subtask_subparsers.add_parser(
        "succeed",
        help="Record a durable summary, complete the current ordinary execution subtask, and route the workflow.",
    )
    succeed_parser.add_argument("--node", required=True)
    succeed_parser.add_argument("--compiled-subtask", required=True)
    succeed_parser.add_argument("--summary-file", required=True)
    succeed_parser.set_defaults(handler=handle_subtask_succeed, command_path=["subtask", "succeed"])

    report_command_parser = subtask_subparsers.add_parser(
        "report-command",
        help="Record a structured command result and let the daemon route the current command subtask.",
    )
    report_command_parser.add_argument("--node", required=True)
    report_command_parser.add_argument("--compiled-subtask", required=True)
    report_command_parser.add_argument("--result-file", required=True)
    report_command_parser.add_argument("--failure-summary-file")
    report_command_parser.set_defaults(handler=handle_subtask_report_command, command_path=["subtask", "report-command"])

    fail_parser = subtask_subparsers.add_parser("fail", help="Mark the current compiled subtask attempt as failed.")
    fail_parser.add_argument("--node", required=True)
    fail_parser.add_argument("--compiled-subtask", required=True)
    fail_parser.add_argument("--result-file")
    fail_summary = fail_parser.add_mutually_exclusive_group(required=True)
    fail_summary.add_argument("--summary")
    fail_summary.add_argument("--summary-file")
    fail_parser.set_defaults(handler=handle_subtask_progress, command_path=["subtask", "fail"], daemon_path="/api/subtasks/fail")

    retry_parser = subtask_subparsers.add_parser("retry", help="Retry the current compiled subtask.")
    retry_target = retry_parser.add_mutually_exclusive_group(required=True)
    retry_target.add_argument("--node")
    retry_target.add_argument("--attempt")
    retry_parser.set_defaults(handler=handle_subtask_retry, command_path=["subtask", "retry"])


def add_rebuild_group(subparsers) -> None:
    rebuild_parser = subparsers.add_parser("rebuild", help="Rebuild and rectification history commands.")
    rebuild_subparsers = rebuild_parser.add_subparsers(dest="rebuild_command", required=True)

    show_parser = rebuild_subparsers.add_parser("show", help="Show durable rebuild history for a node.")
    show_parser.add_argument("--node", required=True)
    show_parser.set_defaults(handler=handle_node_rebuild_history, command_path=["rebuild", "show"])


def add_summary_group(subparsers) -> None:
    summary_parser = subparsers.add_parser("summary", help="Summary registration commands.")
    summary_subparsers = summary_parser.add_subparsers(dest="summary_command", required=True)

    register_parser = summary_subparsers.add_parser("register", help="Register a summary file against the current running subtask attempt.")
    register_parser.add_argument("--node", required=True)
    register_parser.add_argument("--file", required=True)
    register_parser.add_argument("--type", required=True)
    register_parser.set_defaults(handler=handle_summary_register, command_path=["summary", "register"])

    history_parser = summary_subparsers.add_parser("history", help="List durable summary history for a node.")
    history_parser.add_argument("--node", required=True)
    history_parser.set_defaults(handler=handle_summary_history, command_path=["summary", "history"])

    show_parser = summary_subparsers.add_parser("show", help="Show one durable summary history record.")
    show_parser.add_argument("--summary", required=True)
    show_parser.set_defaults(handler=handle_summary_show, command_path=["summary", "show"])


def add_environment_group(subparsers) -> None:
    environment_parser = subparsers.add_parser("environment", help="Environment policy and execution inspection commands.")
    environment_subparsers = environment_parser.add_subparsers(dest="environment_command", required=True)

    policies_parser = environment_subparsers.add_parser("policies", help="List declared runtime environment policies.")
    policies_parser.set_defaults(handler=handle_environment_policies, command_path=["environment", "policies"])

    show_parser = environment_subparsers.add_parser("show", help="Show the resolved execution environment for a subtask attempt.")
    show_parser.add_argument("--attempt", required=True)
    show_parser.set_defaults(handler=handle_attempt_environment, command_path=["environment", "show"])


def add_validation_group(subparsers) -> None:
    validation_parser = subparsers.add_parser("validation", help="Validation result inspection commands.")
    validation_subparsers = validation_parser.add_subparsers(dest="validation_command", required=True)

    show_parser = validation_subparsers.add_parser("show", help="Show the latest validation summary for a node or run.")
    show_target = show_parser.add_mutually_exclusive_group(required=True)
    show_target.add_argument("--node")
    show_target.add_argument("--run")
    show_parser.set_defaults(handler=handle_validation_show, command_path=["validation", "show"])

    results_parser = validation_subparsers.add_parser("results", help="List durable validation result history for a node.")
    results_parser.add_argument("--node", required=True)
    results_parser.set_defaults(handler=handle_validation_results, command_path=["validation", "results"])


def add_review_group(subparsers) -> None:
    review_parser = subparsers.add_parser("review", help="Review result inspection and execution commands.")
    review_subparsers = review_parser.add_subparsers(dest="review_command", required=True)

    show_parser = review_subparsers.add_parser("show", help="Show the latest review summary for a node or run.")
    show_parser.add_argument("--node")
    show_parser.add_argument("--run")
    show_parser.set_defaults(handler=handle_review_show, command_path=["review", "show"])

    results_parser = review_subparsers.add_parser("results", help="List durable review result history for a node.")
    results_parser.add_argument("--node", required=True)
    results_parser.set_defaults(handler=handle_review_results, command_path=["review", "results"])

    run_parser = review_subparsers.add_parser("run", help="Record and route the current review gate for a node.")
    run_parser.add_argument("--node", required=True)
    run_parser.add_argument("--status", required=True, choices=["pass", "revise", "fail", "passed", "failed"])
    run_parser.add_argument("--summary")
    run_parser.add_argument("--findings-file")
    run_parser.add_argument("--criteria-file")
    run_parser.set_defaults(handler=handle_node_review, command_path=["review", "run"])


def add_testing_group(subparsers) -> None:
    testing_parser = subparsers.add_parser("testing", help="Testing result inspection and execution commands.")
    testing_subparsers = testing_parser.add_subparsers(dest="testing_command", required=True)

    show_parser = testing_subparsers.add_parser("show", help="Show the latest testing summary for a node or run.")
    show_target = show_parser.add_mutually_exclusive_group(required=True)
    show_target.add_argument("--node")
    show_target.add_argument("--run")
    show_parser.set_defaults(handler=handle_testing_show, command_path=["testing", "show"])

    results_parser = testing_subparsers.add_parser("results", help="List durable test result history for a node.")
    results_parser.add_argument("--node", required=True)
    results_parser.set_defaults(handler=handle_testing_results, command_path=["testing", "results"])

    run_parser = testing_subparsers.add_parser("run", help="Evaluate the current testing gate for a node.")
    run_parser.add_argument("--node", required=True)
    run_parser.set_defaults(handler=handle_node_test, command_path=["testing", "run"])


def add_session_group(subparsers) -> None:
    session_parser = subparsers.add_parser("session", help="Session inspection commands.")
    session_subparsers = session_parser.add_subparsers(dest="session_command", required=True)

    show_parser = session_subparsers.add_parser("show", help="Show session details.")
    show_target = show_parser.add_mutually_exclusive_group(required=True)
    show_target.add_argument("--session")
    show_target.add_argument("--node")
    show_parser.set_defaults(handler=handle_session_show, command_path=["session", "show"])

    list_parser = session_subparsers.add_parser("list", help="List sessions.")
    list_parser.add_argument("--node", required=True)
    list_parser.set_defaults(handler=handle_session_list, command_path=["session", "list"])

    current_parser = session_subparsers.add_parser("show-current", help="Show the current active session harness state.")
    current_parser.set_defaults(handler=handle_session_daemon_command, daemon_path="/api/sessions/show-current", session_http_method="GET")

    bind_parser = session_subparsers.add_parser("bind", help="Bind a session to a node via the daemon harness.")
    bind_parser.add_argument("--node", required=True)
    bind_parser.set_defaults(handler=handle_session_daemon_command, daemon_path="/api/sessions/bind")

    attach_parser = session_subparsers.add_parser("attach", help="Attach to a node session via the daemon harness.")
    attach_parser.add_argument("--node", required=True)
    attach_parser.set_defaults(handler=handle_session_daemon_command, daemon_path="/api/sessions/attach")

    resume_parser = session_subparsers.add_parser("resume", help="Resume a node session via the daemon harness.")
    resume_parser.add_argument("--node", required=True)
    resume_parser.set_defaults(handler=handle_session_recover, command_path=["session", "resume"])

    recover_parser = session_subparsers.add_parser("recover", help="Run provider-agnostic recovery for the active node session.")
    recover_parser.add_argument("--node", required=True)
    recover_parser.set_defaults(handler=handle_session_recover, command_path=["session", "recover"])

    provider_resume_parser = session_subparsers.add_parser("provider-resume", help="Run provider-aware recovery for the active node session when provider identity is restorable.")
    provider_resume_parser.add_argument("--node", required=True)
    provider_resume_parser.set_defaults(handler=handle_session_provider_recover, command_path=["session", "provider-resume"])

    nudge_parser = session_subparsers.add_parser("nudge", help="Nudge an idle primary session and escalate safely if needed.")
    nudge_parser.add_argument("--node", required=True)
    nudge_parser.set_defaults(handler=handle_session_nudge, command_path=["session", "nudge"])

    push_parser = session_subparsers.add_parser("push", help="Launch a bounded delegated child session without transferring node ownership.")
    push_parser.add_argument("--node", required=True)
    push_parser.add_argument("--reason", required=True)
    push_parser.set_defaults(handler=handle_session_push, command_path=["session", "push"])

    pop_parser = session_subparsers.add_parser("pop", help="Persist and merge back a delegated child session result.")
    pop_parser.add_argument("--session", required=True)
    pop_parser.add_argument("--file", required=True)
    pop_parser.set_defaults(handler=handle_session_pop, command_path=["session", "pop"])

    result_parser = session_subparsers.add_parser("result", help="Inspect delegated child-session merge-back artifacts.")
    result_subparsers = result_parser.add_subparsers(dest="session_result_command", required=True)

    result_show_parser = result_subparsers.add_parser("show", help="Show the latest bounded child-session result.")
    result_show_parser.add_argument("--session", required=True)
    result_show_parser.set_defaults(handler=handle_session_result_show, command_path=["session", "result", "show"])

    events_parser = session_subparsers.add_parser("events", help="Show durable session event history.")
    events_parser.add_argument("--session", required=True)
    events_parser.set_defaults(handler=handle_session_events, command_path=["session", "events"])


def add_yaml_group(subparsers) -> None:
    yaml_parser = subparsers.add_parser("yaml", help="YAML source and resolved-definition commands.")
    yaml_subparsers = yaml_parser.add_subparsers(dest="yaml_command", required=True)

    source_parser = yaml_subparsers.add_parser("sources", help="Inspect source YAML locations or daemon-backed source artifacts.")
    source_target = source_parser.add_mutually_exclusive_group()
    source_target.add_argument("--node")
    source_target.add_argument("--workflow")
    source_target.add_argument("--scope", choices=["builtin", "project", "overrides", "schemas"], default="builtin")
    source_parser.set_defaults(handler=handle_yaml_sources)

    structural_parser = yaml_subparsers.add_parser(
        "structural-library",
        help="Inspect the built-in structural YAML library manifest and integrity.",
    )
    structural_parser.set_defaults(handler=handle_yaml_structural_library)

    quality_parser = yaml_subparsers.add_parser(
        "quality-library",
        help="Inspect the built-in validation, review, testing, and docs library manifest and integrity.",
    )
    quality_parser.set_defaults(handler=handle_yaml_quality_library)

    operational_parser = yaml_subparsers.add_parser(
        "operational-library",
        help="Inspect the built-in runtime, hook, policy, environment, and prompt library manifest and integrity.",
    )
    operational_parser.set_defaults(handler=handle_yaml_operational_library)

    validate_parser = yaml_subparsers.add_parser("validate", help="Validate one YAML document through the daemon schema layer.")
    validate_parser.add_argument("--group", default="yaml_builtin_system")
    validate_parser.add_argument("--path", required=True)
    validate_parser.set_defaults(handler=handle_yaml_validate)

    schema_parser = yaml_subparsers.add_parser("schema-families", help="List configured YAML schema families.")
    schema_parser.set_defaults(handler=handle_yaml_schema_families)

    project_policy_parser = yaml_subparsers.add_parser("project-policy", help="Show project policy documents.")
    project_policy_parser.set_defaults(handler=handle_yaml_project_policy)

    effective_policy_parser = yaml_subparsers.add_parser("effective-policy", help="Show the effective merged project policy.")
    effective_policy_parser.set_defaults(handler=handle_yaml_effective_policy)

    policy_impact_parser = yaml_subparsers.add_parser("policy-impact", help="Show policy impact for one node kind.")
    policy_impact_parser.add_argument("--kind", required=True)
    policy_impact_parser.set_defaults(handler=handle_yaml_policy_impact)

    override_chain_parser = yaml_subparsers.add_parser("override-chain", help="Show the applied override chain for a node or workflow.")
    override_chain_parser.add_argument("--node")
    override_chain_parser.add_argument("--workflow")
    override_chain_parser.set_defaults(handler=handle_yaml_override_chain)

    resolved_parser = yaml_subparsers.add_parser("resolved", help="Inspect resolved YAML documents from a compiled workflow.")
    resolved_parser.add_argument("--node")
    resolved_parser.add_argument("--workflow")
    resolved_parser.add_argument("--family")
    resolved_parser.add_argument("--id")
    resolved_parser.set_defaults(handler=handle_yaml_resolved)


def add_prompts_group(subparsers) -> None:
    prompts_parser = subparsers.add_parser("prompts", help="Prompt asset inspection commands.")
    prompts_subparsers = prompts_parser.add_subparsers(dest="prompts_command", required=True)

    show_parser = prompts_subparsers.add_parser("show", help="Inspect packaged prompt locations.")
    show_parser.add_argument("--scope", choices=["layouts", "execution", "recovery", "quality"], default="layouts")
    show_parser.set_defaults(handler=handle_prompt_show)

    history_parser = prompts_subparsers.add_parser("history", help="List durable delivered-prompt history for a node.")
    history_parser.add_argument("--node", required=True)
    history_parser.set_defaults(handler=handle_prompt_history, command_path=["prompts", "history"])

    delivered_show_parser = prompts_subparsers.add_parser("delivered-show", help="Show one durable delivered prompt record.")
    delivered_show_parser.add_argument("--prompt", required=True)
    delivered_show_parser.set_defaults(handler=handle_prompt_record_show, command_path=["prompts", "delivered-show"])


def add_docs_group(subparsers) -> None:
    docs_parser = subparsers.add_parser("docs", help="Documentation generation and inspection commands.")
    docs_subparsers = docs_parser.add_subparsers(dest="docs_command", required=True)

    build_node_parser = docs_subparsers.add_parser("build-node-view", help="Build local node documentation views.")
    build_node_parser.add_argument("--node", required=True)
    build_node_parser.set_defaults(handler=handle_docs_build_node_view)

    build_tree_parser = docs_subparsers.add_parser("build-tree", help="Build merged tree documentation views.")
    build_tree_parser.add_argument("--node", required=True)
    build_tree_parser.set_defaults(handler=handle_docs_build_tree)

    list_parser = docs_subparsers.add_parser("list", help="List durable documentation outputs for a node.")
    list_parser.add_argument("--node", required=True)
    list_parser.set_defaults(handler=handle_docs_list)

    show_parser = docs_subparsers.add_parser("show", help="Show the latest durable documentation output for a scope.")
    show_parser.add_argument("--node", required=True)
    show_parser.add_argument("--scope", required=True, choices=["local", "merged", "entity_history", "rationale_view", "custom"])
    show_parser.set_defaults(handler=handle_docs_show)


def add_rationale_group(subparsers) -> None:
    rationale_parser = subparsers.add_parser("rationale", help="Rationale inspection commands.")
    rationale_subparsers = rationale_parser.add_subparsers(dest="rationale_command", required=True)

    show_parser = rationale_subparsers.add_parser("show", help="Show node rationale and linked entity changes.")
    show_parser.add_argument("--node", required=True)
    show_parser.set_defaults(handler=handle_rationale_show, command_path=["rationale", "show"])


def add_entity_group(subparsers) -> None:
    entity_parser = subparsers.add_parser("entity", help="Code provenance inspection commands.")
    entity_subparsers = entity_parser.add_subparsers(dest="entity_command", required=True)

    show_parser = entity_subparsers.add_parser("show", help="Show durable entity anchors by canonical name.")
    show_parser.add_argument("--name", required=True)
    show_parser.set_defaults(handler=handle_entity_show, command_path=["entity", "show"])

    history_parser = entity_subparsers.add_parser("history", help="Show full entity history by canonical name.")
    history_parser.add_argument("--name", required=True)
    history_parser.set_defaults(handler=handle_entity_history, command_path=["entity", "history"])

    relations_parser = entity_subparsers.add_parser("relations", help="Show entity relations by canonical name.")
    relations_parser.add_argument("--name", required=True)
    relations_parser.set_defaults(handler=handle_entity_relations, command_path=["entity", "relations"])

    changed_by_parser = entity_subparsers.add_parser("changed-by", help="Show non-unchanged node-version changes for an entity.")
    changed_by_parser.add_argument("--name", required=True)
    changed_by_parser.set_defaults(handler=handle_entity_changed_by, command_path=["entity", "changed-by"])


def add_admin_group(subparsers) -> None:
    admin_parser = subparsers.add_parser("admin", help="Admin and bootstrap commands.")
    admin_subparsers = admin_parser.add_subparsers(dest="admin_command", required=True)

    doctor_parser = admin_subparsers.add_parser("doctor", help="Inspect bootstrap health.")
    doctor_parser.set_defaults(handler=handle_doctor)

    settings_parser = admin_subparsers.add_parser("print-settings", help="Print runtime settings.")
    settings_parser.set_defaults(handler=handle_print_settings)

    auth_parser = admin_subparsers.add_parser("auth-token", help="Resolve the daemon auth token source.")
    auth_parser.set_defaults(handler=handle_auth_token)

    resources_parser = admin_subparsers.add_parser("resources", help="Inspect packaged resource directories.")
    resources_parser.set_defaults(handler=handle_resources)

    boundary_parser = admin_subparsers.add_parser("daemon-boundary", help="Show daemon boundary configuration.")
    boundary_parser.set_defaults(handler=handle_daemon_boundary, command_path=["admin", "daemon-boundary"])

    db_parser = admin_subparsers.add_parser("db", help="Database bootstrap utilities.")
    db_subparsers = db_parser.add_subparsers(dest="db_command", required=True)

    ping_parser = db_subparsers.add_parser("ping", help="Verify the database connection.")
    ping_parser.set_defaults(handler=handle_db_ping)

    status_parser = db_subparsers.add_parser("status", help="Inspect the current database bootstrap state.")
    status_parser.set_defaults(handler=handle_db_status)

    upgrade_parser = db_subparsers.add_parser("upgrade", help="Apply Alembic migrations.")
    upgrade_parser.add_argument("--revision", default="head")
    upgrade_parser.set_defaults(handler=handle_db_upgrade, alembic_config_factory=alembic_config)

    downgrade_parser = db_subparsers.add_parser("downgrade", help="Revert Alembic migrations.")
    downgrade_parser.add_argument("--revision", default="base")
    downgrade_parser.set_defaults(handler=handle_db_downgrade, alembic_config_factory=alembic_config)

    revision_parser = db_subparsers.add_parser("current-revision", help="Show the current Alembic revision.")
    revision_parser.set_defaults(handler=handle_db_current_revision)

    heads_parser = db_subparsers.add_parser("heads", help="Show expected Alembic head revisions.")
    heads_parser.set_defaults(handler=handle_db_heads, alembic_config_factory=alembic_config)

    history_parser = db_subparsers.add_parser("history", help="Show Alembic revision history.")
    history_parser.set_defaults(handler=handle_db_history, alembic_config_factory=alembic_config)

    check_parser = db_subparsers.add_parser("check-schema", help="Compare database revision to the expected Alembic head.")
    check_parser.set_defaults(handler=handle_db_check_schema, alembic_config_factory=alembic_config)


def add_debug_group(subparsers) -> None:
    debug_parser = subparsers.add_parser("debug", help="Debug and daemon-connectivity commands.")
    debug_subparsers = debug_parser.add_subparsers(dest="debug_command", required=True)

    daemon_parser = debug_subparsers.add_parser("daemon", help="Inspect daemon connectivity.")
    daemon_subparsers = daemon_parser.add_subparsers(dest="daemon_command", required=True)

    ping_parser = daemon_subparsers.add_parser("ping", help="Ping the daemon health endpoint.")
    ping_parser.set_defaults(handler=handle_debug_daemon_ping)

    boundary_parser = daemon_subparsers.add_parser("boundary", help="Show daemon client boundary settings.")
    boundary_parser.set_defaults(handler=handle_debug_daemon_boundary)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="aicoding", description="Project CLI skeleton.")
    add_common_output_options(parser)
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_node_group(subparsers)
    add_workflow_group(subparsers)
    add_tree_group(subparsers)
    add_rebuild_group(subparsers)
    add_git_group(subparsers)
    add_task_group(subparsers)
    add_subtask_group(subparsers)
    add_summary_group(subparsers)
    add_environment_group(subparsers)
    add_validation_group(subparsers)
    add_review_group(subparsers)
    add_testing_group(subparsers)
    add_session_group(subparsers)
    add_yaml_group(subparsers)
    add_prompts_group(subparsers)
    add_docs_group(subparsers)
    add_rationale_group(subparsers)
    add_entity_group(subparsers)
    add_admin_group(subparsers)
    add_debug_group(subparsers)
    return parser
