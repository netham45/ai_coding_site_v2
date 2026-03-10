# Task: Full Epic Tree Git Lifecycle E2E Expansion Planning

## Goal

Produce the implementation plan for extending the authoritative full-tree real E2E to verify hierarchy-wide git merges, rollbacks, redos, and conflicts through real runtime behavior.

## Rationale

- Rationale: The current full-tree E2E proves real decomposition and live task execution, but it does not yet prove that git state is merged, rebuilt, replayed, or conflicted correctly through plan, phase, and epic boundaries.
- Reason for existence: This task exists to convert the remaining git lifecycle gap into an explicit implementation plan grounded in the repo’s current real E2E coverage.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/23_F18_child_merge_and_reconcile_pipeline.md`
- `plan/features/24_F19_regeneration_and_upstream_rectification.md`
- `plan/features/70_F19_live_rebuild_cutover_coordination.md`
- `plan/features/71_F11_live_git_merge_and_finalize_execution.md`
- `plan/features/72_F20_live_merge_conflict_resolution.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/specs/git/git_rectification_spec_v2.md`
- `notes/specs/runtime/tmux_session_lifecycle_spec_v1.md`
- `notes/contracts/parent_child/child_session_mergeback_contract.md`
- `notes/contracts/runtime/cutover_policy_note.md`
- `notes/catalogs/audit/flow_coverage_checklist.md`
- `notes/catalogs/checklists/verification_command_catalog.md`

## Scope

- Database: identify the durable merge, rebuild, conflict, and authoritative-version assertions the future E2E must make.
- CLI: inventory the real commands the future E2E must drive and inspect.
- Daemon: align the plan with the real runtime’s merge, finalize, rectify, and conflict authority boundaries.
- YAML: account for the compiled workflow and hierarchy behavior that must remain in the real path.
- Prompts: account for live prompt surfaces where decomposition, task execution, or recovery guidance affects the runtime outcome.
- Notes: create the reconciliation plan and the adjacent development log for the planning task.
- Tests: anchor the plan in existing real E2E coverage instead of inventing a mocked or synthetic path.
- Performance: keep the future repo fixtures tiny and deterministic.

## Verification

- `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py -q`

## Exit Criteria

- The repo contains a durable reconciliation plan for full-tree git lifecycle E2E expansion.
- The plan references the current real git and full-tree E2E files that should be reused.
- The plan explicitly states the no-mock, real-runtime constraint.
- The task plan and development log pass the repository’s current document checks.
