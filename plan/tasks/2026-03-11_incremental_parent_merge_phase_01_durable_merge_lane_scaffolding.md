# Task: Incremental Parent Merge Phase 01 Durable Merge Lane Scaffolding

## Goal

Implement the first incremental parent-merge slice by adding durable completed-unmerged child merge state and parent merge-lane state, then recording that state when child runs complete successfully.

## Rationale

- Rationale: Merge-backed sibling dependency execution cannot be restart-safe or inspectable unless completed child merge work is represented durably in the database instead of existing only as transient daemon knowledge.
- Reason for existence: This task exists as a separate slice so the repository can prove the durable-state substrate and child-completion recording path before changing dependency truth, child refresh behavior, or the full background merge worker.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/74_F08_F18_incremental_parent_merge_overview.md`
- `plan/features/75_F08_F18_incremental_parent_merge_phase_01_durable_merge_lane_scaffolding.md`
- `plan/features/11_F08_dependency_graph_and_admission_control.md`
- `plan/features/13_F09_node_run_orchestration.md`
- `plan/features/23_F18_child_merge_and_reconcile_pipeline.md`
- `plan/features/71_F11_live_git_merge_and_finalize_execution.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/specs/database/database_schema_spec_v2.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/contracts/parent_child/child_materialization_and_scheduling.md`
- `notes/contracts/runtime/cutover_policy_note.md`
- `notes/planning/implementation/child_merge_and_reconcile_pipeline_decisions.md`
- `notes/planning/implementation/dependency_graph_and_admission_control_decisions.md`
- `notes/planning/implementation/live_git_merge_and_finalize_execution_decisions.md`

## Scope

- Database: add durable incremental child merge state and parent merge-lane state with Alembic coverage.
- CLI: no new command family in this slice, but existing reads must remain compatible with the new durable state.
- Daemon: when a child run completes successfully, record completed-unmerged merge state for its authoritative parent lineage if eligible.
- YAML: not affected in this slice.
- Prompts: not affected in this slice.
- Tests: add bounded DB/daemon tests proving state creation, idempotent re-recording, and no duplicate rows on repeated completion handling.
- Performance: state recording on child completion must stay cheap and avoid broad rescans.
- Notes: fold the accepted incremental-merge runtime doctrine into the relevant implementation and runtime notes as part of this change.

## Plan

### Phase 1A: Authoritative planning and doctrine alignment

1. Promote the incremental parent-merge plan set into `plan/features/` and wire the new feature docs into the checklist backfill surface.
2. Update the applicable implementation/runtime notes so they reflect the accepted daemon-owned scan-and-lock model, completion-driven applied merge order, and durable-state expectations.
3. Add this authoritative task plan and a development log entry before code changes land.

Exit criteria:

- authoritative feature/task/log artifacts exist and the affected doctrinal notes mention the accepted runtime model

### Phase 1B: Durable state schema and model scaffolding

1. Add database models for per-child incremental merge state and per-parent merge-lane state.
2. Add an Alembic migration for the new tables and any required indexes or constraints.
3. Add daemon-side helpers to read/write the new state without yet starting incremental merge execution.

Exit criteria:

- the schema and ORM layer can persist completed-unmerged child merge state and parent lane state

### Phase 1C: Child-completion recording path and bounded proof

1. Hook successful child run completion into the durable incremental-merge state recording path.
2. Ensure repeated completion handling stays idempotent for the same authoritative parent/child/version state.
3. Add bounded tests and run the affected document/code verification commands.

Exit criteria:

- successful child completion records durable incremental-merge state exactly once for the current authoritative parent lineage

## Verification

- `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_feature_plan_docs.py tests/unit/test_feature_checklist_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_verification_command_docs.py -q`
- `python3 -m pytest tests/unit/test_incremental_parent_merge.py tests/unit/test_run_orchestration.py -q`
- `git diff --check`

## Exit Criteria

- authoritative feature/task/log artifacts are in place for incremental parent merge phase 1
- the repository has durable incremental child merge state and parent merge-lane state in the ORM and migration layer
- successful child completion records completed-unmerged merge state restart-safely
- bounded proof exists for state creation and idempotent re-recording
- no merge-backed dependency unblocking or child refresh behavior is claimed yet
