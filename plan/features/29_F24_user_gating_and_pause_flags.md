# Phase F24: User Gating And Pause Flags

## Goal

Support explicit pause points, approval gates, and safe resume behavior.

## Rationale

- Rationale: Human approvals and pause points are core orchestration states, not side conversations outside the system.
- Reason for existence: This phase exists to make user-gated stops durable and resumable so the daemon never silently skips required approval.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/13_F09_node_run_orchestration.md`: F09 must stop and resume correctly around pause points.
- `plan/features/14_F10_ai_facing_cli_command_loop.md`: F10 provides the commands used to pause, approve, and resume.
- `plan/features/25_F21_validation_framework.md`: F21 may trigger pause-worthy validation failures.
- `plan/features/26_F22_review_framework.md`: F22 may produce approval-gated review outcomes.
- `plan/features/30_F25_failure_escalation_and_parent_decision_logic.md`: F25 may escalate into user-gated pauses.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/catalogs/inventory/major_feature_inventory.md`
- `notes/catalogs/traceability/spec_traceability_matrix.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/contracts/persistence/pause_workflow_event_persistence.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/specs/prompts/prompt_library_plan.md`
- `notes/pseudocode/state_machines/workflow_events.md`

## Scope

- Database: pause flags, pause summaries, pause-event history.
- CLI: pause-state, approval, and resume flows.
- Daemon: enforce pause transitions and prevent silent skip on resume.
- YAML: gate declarations and gate policies.
- Prompts: pause-for-user and approval-handoff prompts.
- Tests: exhaustive pause entry, pause clearing, approval-required, and illegal-resume coverage.
- Performance: benchmark pause-state query paths.
- Notes: update pause-event notes if event granularity changes.
