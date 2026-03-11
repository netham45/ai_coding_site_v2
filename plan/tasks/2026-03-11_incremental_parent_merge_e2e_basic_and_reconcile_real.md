# Task: Incremental Parent Merge Real E2E Basic Unblock And Reconcile

## Goal

Add the first real end-to-end incremental parent-merge checkpoint that proves a sibling dependency stays blocked until the prerequisite child is actually merged upward, then proves the parent reconcile surface reads that applied merge history.

## Rationale

- Rationale: The incremental parent-merge feature is now implemented across durable state, daemon orchestration, git, dependency truth, refresh, conflict handoff, and reconcile context, but bounded tests are not enough to claim the runtime flow works.
- Reason for existence: This task exists to land the first real-runtime proof for the core sibling-unblock bug fix and the post-merge reconcile inspection surface before tackling conflict and restart hardening.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/74_F08_F18_incremental_parent_merge_overview.md`
- `plan/features/77_F08_incremental_parent_merge_phase_03_merge_backed_dependency_truth.md`
- `plan/features/78_F15_incremental_parent_merge_phase_04_dependent_child_parent_refresh.md`
- `plan/features/79_F09_incremental_parent_merge_phase_05_background_orchestration_and_autostart.md`
- `plan/features/81_F18_incremental_parent_merge_phase_07_final_parent_reconcile_redefinition.md`
- `plan/features/82_F08_F18_incremental_parent_merge_full_e2e.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/catalogs/checklists/feature_checklist_backfill.md`
- `plan/e2e_tests/06_e2e_feature_matrix.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/git/git_rectification_spec_v2.md`
- `notes/contracts/parent_child/child_materialization_and_scheduling.md`
- `plan/features/74_F08_F18_incremental_parent_merge_overview.md`

## Scope

- Database: prove durable merge events, dependency blockers, and reconcile-ready state through the real persistence layer created per E2E test.
- CLI: prove the existing `node dependency-status`, `node blockers`, `node child-results`, `node reconcile`, `git status show`, and `git merge-events show` surfaces expose the runtime truth needed for the feature.
- Daemon: prove real daemon background progression from child completion to incremental merge to dependent-child refresh/unblock.
- YAML: not directly mutated in this slice; use shipped node/workflow behavior.
- Prompts: not the primary proving target in this slice beyond verifying the parent reconcile prompt/context surface remains coherent after incremental merges.
- Tests: add one real git-backed sibling unblock narrative and one real post-merge reconcile-surface narrative.
- Performance: keep the real runtime narrative narrow enough to run repeatedly while still using real subprocess, daemon, CLI, database, and git boundaries.
- Notes: update the E2E inventory and checklist surfaces so the new checkpoint is traceable and does not over-claim unresolved conflict/restart coverage.

## Plan

### Phase E2E-A: Runtime-path selection and scaffolding

1. Add the authoritative task plan and E2E development log.
2. Reuse the existing real daemon harness and live git helpers rather than inventing a separate incremental-merge harness.
3. Confirm the minimal real-runtime path for child completion that still triggers the incremental merge hook.

Exit criteria:

- the task/log artifacts exist and the first real-runtime narrative is scoped tightly enough to run today

### Phase E2E-B: Real sibling unblock checkpoint

1. Add a real git-backed E2E that creates a parent with sibling dependency `A -> B`, pre-bootstraps child repos, finalizes `A`, drives `A` to terminal run completion, and proves `B` remains blocked until the daemon durably merges `A` upward.
2. Prove the daemon refreshes `B` against the merged parent state before `B` becomes ready.
3. Verify `B`'s repo content or base state includes `A`'s merged change before admission.

Exit criteria:

- the core sibling-unblock bug is proven fixed through real daemon/CLI/git boundaries

### Phase E2E-C: Real reconcile-surface checkpoint

1. Add a real follow-on assertion that once all required children are merged upward, `node child-results` and `node reconcile` expose applied merge order and post-merge reconcile readiness.
2. Update the authoritative E2E matrix, checklist, command catalog, and development log.
3. Run the new real-E2E checkpoint plus the affected document consistency tests.

Exit criteria:

- the new real checkpoint is documented, runnable, and honestly scoped as a happy-path proof rather than a conflict/restart completion claim

## Verification

- `PYTHONPATH=src python3 -m pytest tests/e2e/test_e2e_incremental_parent_merge_real.py -q`
- `PYTHONPATH=src python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_feature_checklist_docs.py tests/unit/test_feature_plan_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_verification_command_docs.py -q`
- `git diff --check`

## Exit Criteria

- a real daemon/CLI/git E2E proves merge-backed sibling unblock and stale-child refresh on the happy path
- a real daemon/CLI/git E2E proves the parent reconcile inspection surface reads already-applied merge history
- authoritative E2E inventory and checklist surfaces are updated to include the new checkpoint
- conflict, restart, and broader hierarchy narratives remain explicitly deferred rather than implied
