# Phase F13-S2: Expanded Human Intervention Matrix

## Goal

Expand human intervention beyond pause approval so reconcile, rebuild, merge, and escalation decisions share one explicit intervention model.

## Rationale

- Rationale: The runtime already supports pause-state inspection, approval, and resumed execution, but Flow 13 still covers only one intervention family instead of a broader human-decision matrix.
- Reason for existence: This phase exists to make human intervention a consistent orchestration surface instead of a pause-only special case.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/29_F24_user_gating_and_pause_flags.md`: F24 established the current pause and approval model.
- `plan/features/30_F25_failure_escalation_and_parent_decision_logic.md`: F25 may route failures into human decisions.
- `plan/features/23_F18_child_merge_and_reconcile_pipeline.md`: F18 can require human reconciliation input.
- `plan/features/71_F11_live_git_merge_and_finalize_execution.md`: F11-S1 will need human intervention for some merge/finalize paths.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/specs/database/database_schema_spec_v2.md`
- `notes/contracts/persistence/pause_workflow_event_persistence.md`
- `notes/contracts/parent_child/manual_vs_auto_tree_interaction.md`
- `notes/planning/implementation/per_flow_gap_remediation_plan.md`

## Scope

- Database: persist a broader intervention record model that covers more than pause approval alone.
- CLI: expose reads and mutations for intervention state across reconcile, rebuild, merge, and escalation decisions.
- Daemon: route more runtime branches through an explicit human-intervention decision framework rather than ad hoc pause-only logic.
- YAML: keep intervention authority code-owned while allowing YAML to declare where intervention can be requested.
- Prompts: add or refine intervention prompts for reconcile, rebuild, merge, and escalation decisions.
- Tests: exhaustively cover intervention-required pauses, approvals, rejections, deferred actions, resumed flows, and audit reconstruction.
- Performance: benchmark intervention-state reads and event-history inspection under repeated decision points.
- Notes: update pause, intervention, reconcile, and merge notes to reflect the unified intervention model.
