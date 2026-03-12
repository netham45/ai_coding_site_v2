# Task: Incremental Parent Merge Restart Recovery Real E2E

## Goal

Prove the incremental parent-merge lane survives daemon restart by resuming from durable completed-unmerged state and unblocking the dependent child exactly once after restart.

## Rationale

- Rationale: The incremental parent-merge feature now has real happy-path and conflict-resolution proof, but it still lacks real process-restart evidence for the durable merge lane.
- Reason for existence: This task exists to convert the restart-safety claim from a bounded inference into real daemon/CLI/git proof using the same persisted database and workspace across daemon processes.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/74_F08_F18_incremental_parent_merge_overview.md`
- `plan/features/75_F08_F18_incremental_parent_merge_phase_01_durable_merge_lane_scaffolding.md`
- `plan/features/79_F09_incremental_parent_merge_phase_05_background_orchestration_and_autostart.md`
- `plan/features/82_F08_F18_incremental_parent_merge_full_e2e.md`
- `plan/features/17_F34_provider_agnostic_session_recovery.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/git/git_rectification_spec_v2.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/catalogs/checklists/feature_checklist_backfill.md`
- `plan/e2e_tests/06_e2e_feature_matrix.md`
- `plan/features/82_F08_F18_incremental_parent_merge_full_e2e.md`

## Scope

- Database: prove completed-unmerged child state and parent merge-lane state survive daemon process restart without duplicate merge events.
- CLI: keep using existing inspection surfaces such as `node dependency-status`, `node blockers`, `git merge-events show`, and `git status show`.
- Daemon: add only the minimal real-harness support needed to restart the daemon against the same DB/workspace, then prove the existing background loop resumes the incremental merge lane.
- YAML: not affected directly in this slice.
- Prompts: not the primary target in this slice beyond keeping parent/dependent context coherent after restart.
- Tests: add one real E2E narrative for “child completed, daemon stopped before merge, daemon restarted, lane resumes and dependent unblocks once.”
- Performance: keep the restart window deterministic by explicitly slowing the initial poll loop and speeding the restarted daemon back up.
- Notes: update the incremental parent-merge E2E plan, feature checklist, command catalog, and matrix so restart recovery is tracked as real proof rather than deferred.

## Plan

### Phase RR-A: Harness support

1. Add the authoritative task plan and development log.
2. Extend the shared real-daemon harness with an in-place restart path that reuses the same database, workspace, and token file while launching a new daemon process.
3. Keep the harness change narrow enough that existing real E2E suites are unaffected.

Exit criteria:

- real E2E tests can stop and restart the daemon against the same durable runtime state

### Phase RR-B: Real restart narrative

1. Add a real incremental parent-merge E2E that uses a slow initial daemon poll interval, completes the prerequisite child, confirms the dependent remains blocked and no merge event exists yet, then stops the daemon.
2. Restart the daemon against the same DB/workspace with a fast poll interval.
3. Prove the completed-unmerged child is merged exactly once after restart and the dependent child refreshes/unblocks only after that resumed merge.

Exit criteria:

- the merge lane is proven restart-safe through the real daemon process boundary

### Phase RR-C: Note alignment and verification

1. Update the incremental parent-merge E2E feature plan, feature matrix, verification catalog, and checklist surfaces.
2. Run the real E2E checkpoint plus the affected document-family verification commands.

Exit criteria:

- restart recovery is documented as a real checkpoint, not a deferred claim

## Verification

- `PYTHONPATH=src python3 -m pytest tests/e2e/test_e2e_incremental_parent_merge_real.py -q`
- `PYTHONPATH=src python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_feature_checklist_docs.py tests/unit/test_feature_plan_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_verification_command_docs.py -q`
- `git diff --check`

## Exit Criteria

- a real daemon restart against the same DB/workspace resumes the incremental merge lane from durable state
- restart does not create duplicate merge events
- the dependent child unblocks only after the resumed post-restart merge
- broader hierarchy-wide restart stories remain explicitly deferred if not proven here
