# Phase F11-S1: Live Git Merge And Finalize Execution

## Goal

Implement the real working-tree merge and finalize execution path that turns the current durable merge staging model into a true end-to-end runtime flow.

## Rationale

- Rationale: The current system persists merge events, merge conflicts, child results, and final-commit metadata, but Flow 11 still stops at durable staging instead of executing a real live git merge/finalize path.
- Reason for existence: This phase exists to close the largest remaining orchestration gap and make finalize-and-merge a real runtime capability instead of a simulated or deferred one.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/22_F20_conflict_detection_and_resolution.md`: F20 provides durable conflict persistence that live merge execution must use.
- `plan/features/23_F18_child_merge_and_reconcile_pipeline.md`: F18 already computes staged child merge order and reconcile context.
- `plan/features/24_F19_regeneration_and_upstream_rectification.md`: F19 interacts with merge state during rebuild and cutover.
- `plan/features/12_F17_deterministic_branch_model.md`: F17 provides branch and seed/final metadata that live merge/finalize execution must preserve.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/specs/git/git_rectification_spec_v2.md`
- `notes/contracts/runtime/cutover_policy_note.md`
- `notes/contracts/parent_child/child_session_mergeback_contract.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/specs/database/database_schema_spec_v2.md`
- `notes/planning/implementation/per_flow_gap_remediation_plan.md`

## Scope

- Database: extend merge/finalize persistence only where the current durable merge records are insufficient for real execution, rollback, and recovery.
- CLI: expose explicit operator surfaces for live merge execution, finalize execution, and safe recovery from live git failures.
- Daemon: execute real working-tree merge and finalize steps with safety rails, conflict handling, rollback behavior, and durable event recording.
- YAML: keep merge/finalize authority in code; YAML may supply guidance hooks or policies, but not live git execution semantics.
- Prompts: ensure reconcile, conflict, and finalize prompts match the real live git path and operator intervention model.
- Tests: exhaustively cover clean merge, conflicted merge, abandoned merge, successful finalize, failed finalize, rollback, and resumed execution.
- Performance: benchmark merge-event inspection plus the runtime overhead of real merge/finalize orchestration under repeated child merges.
- Notes: update git, runtime, recovery, and audit notes to replace staged-only language with the real execution contract.
