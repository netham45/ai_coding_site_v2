# Task: Git E2E Merge, Rollback, And Conflict Verification Planning

## Goal

Review the current real E2E git coverage and produce an implementation plan for end-to-end tests that verify actual repository contents after clean merges, rebuild-triggered rollback/rerun, and merge-conflict resolution.

## Rationale

- Rationale: The current git-oriented E2E tests prove command execution, durable metadata, and status transitions, but they do not prove that the working tree and final commits contain the expected files after merge, rollback, or conflict resolution.
- Reason for existence: This task exists to close the gap between "git/runtime bookkeeping succeeded" and "the repository contents are correct and reconstructible after the runtime claims success."

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/12_F17_deterministic_branch_model.md`
- `plan/features/22_F20_conflict_detection_and_resolution.md`
- `plan/features/23_F18_child_merge_and_reconcile_pipeline.md`
- `plan/features/24_F19_regeneration_and_upstream_rectification.md`
- `plan/features/70_F19_live_rebuild_cutover_coordination.md`
- `plan/features/71_F11_live_git_merge_and_finalize_execution.md`
- `plan/e2e_tests/05_e2e_git_rectification_and_cutover.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/specs/git/git_rectification_spec_v2.md`
- `notes/contracts/runtime/cutover_policy_note.md`
- `notes/contracts/parent_child/child_session_mergeback_contract.md`
- `notes/catalogs/checklists/feature_checklist_backfill.md`
- `notes/catalogs/audit/flow_coverage_checklist.md`
- `notes/catalogs/checklists/verification_command_catalog.md`

## Scope

- Database: verify durable merge events, conflict records, rebuild events, and cutover-readiness state against the git state that actually exists on disk.
- CLI: drive bootstrap, merge, finalize, rectify, conflict-inspection, and conflict-resolution commands through the real CLI path.
- Daemon: exercise real repo bootstrap, merge, finalize, conflict pause/resume, rollback/reset, rerun, and cutover behavior without bypassing live git operations.
- YAML: keep git authority in code, but ensure any merge/reconcile hooks required for the tested narrative are triggered through real compiled workflows where applicable.
- Prompts: validate any conflict or rectify prompt/recovery surfaces only when the runtime actually enters those stages.
- Notes: document the current proof gap and the canonical commands for the new git-content E2E targets.
- Tests: add real E2E cases that assert repository contents, commit ancestry, and rollback/reset effects instead of only daemon payloads.
- Performance: keep fixtures small by using tiny repos with deterministic file layouts while still asserting real filesystem outcomes.

## Review Findings

- Current Flow 11 coverage is real git, but it only asserts metadata and status payloads. The shipped test stops at `merge_payload["status"] == "merged"`, `final_commit_sha` equality, and `working_tree_state == "finalized_clean"` without reading the parent repo contents or verifying the merge commit tree. See `tests/e2e/test_flow_11_finalize_and_merge_real.py`.
- Current Flow 10 coverage proves regeneration and rectify command surfaces, rebuild history, and cutover-readiness payloads, but it does not bootstrap repos, re-merge child finals, or inspect rollback/reset effects in the rebuilt working trees. See `tests/e2e/test_flow_10_regenerate_and_rectify_real.py`.
- Current Flow 21 coverage proves child-session result attachment, not git mergeback semantics. It never checks a parent repo, merge commit, or file content after child work returns. See `tests/e2e/test_flow_21_child_session_round_trip_and_mergeback_real.py`.
- The existing E2E git phase already says these areas need real working-tree proof, so the doctrinal direction is already present; what is missing is test implementation at the repo-content layer. See `plan/e2e_tests/05_e2e_git_rectification_and_cutover.md`.

## Proposed Test Additions

### 1. Clean Merge Content Verification

Target file:

- `tests/e2e/test_e2e_live_git_merge_and_finalize_real.py`

Narrative:

1. Create parent plus two children.
2. Bootstrap parent with a small deterministic file tree.
3. Bootstrap each child from the parent seed.
4. Change disjoint files in each child and finalize each child.
5. Run real `git merge-children` and `git finalize-node` through the CLI.
6. Inspect the parent repo on disk and assert:
   - merged file contents match both children’s changes
   - untouched files remain at seed values
   - `git rev-parse HEAD` matches the daemon-reported final commit SHA
   - `git show --name-only --format=` on the final commit includes the expected files
   - `git status --short` is empty
7. Inspect durable merge events and verify each event’s child final SHA matches the commit actually merged.

Why this matters:

- This closes the current gap where a merge can be reported as successful without proving the resulting tree contents.

### 2. Rectification Rollback And Rerun Verification

Target file:

- `tests/e2e/test_e2e_regeneration_and_upstream_rectification_real.py`

Narrative:

1. Create parent with two children and bootstrap all repos from a shared seed.
2. Finalize both children and merge/finalize the parent once, capturing:
   - parent seed commit
   - parent first final commit
   - parent repo contents after initial merge
3. Regenerate one child into a superseding version and change its output.
4. Trigger real `node rectify-upstream` for that child.
5. Assert on disk that the rebuilt parent repo:
   - no longer contains stale pre-rectification merged content from the replaced child version
   - still contains current-final content from unaffected siblings
   - has replayed the expected merged file set after reset-to-seed and re-merge
6. Assert ancestry and rollback evidence with git commands:
   - rebuilt parent HEAD differs from the old final commit
   - rebuilt parent tree matches a deterministic expected filesystem snapshot
   - the old authoritative lineage remains authoritative until cutover if the runtime still stages candidates conservatively
7. Assert durable records:
   - rebuild history contains subtree plus upstream events
   - merge events for the rebuilt parent correspond to current child finals, not superseded finals

Why this matters:

- The git spec requires ancestor rebuild from seed plus replay of current child finals. The current E2E slice does not prove that reset/replay actually happened in git.

### 3. Conflict Resolution Content Verification

Target file:

- `tests/e2e/test_e2e_merge_conflict_and_resolution_real.py`

Narrative:

1. Create parent plus two children from the same seed file.
2. Make both children modify the same line so the second merge conflicts deterministically.
3. Run real `git merge-children` and assert:
   - CLI reports conflict/pause state
   - parent repo contains conflict markers in the expected file before resolution
   - durable merge-conflict records list the file path and unresolved status
4. Resolve the conflict through the intended runtime/operator surface.
   - If the repo exposes a conflict-resolution CLI, use it directly.
   - If it only exposes pause approval plus repo edit today, the test should edit the conflicted file in the parent repo, stage/commit through the supported runtime path, then mark the conflict resolved through the CLI.
5. Resume/finalize the parent and assert:
   - conflict markers are gone
   - resolved file content equals the expected canonical resolution
   - final commit SHA equals `git rev-parse HEAD`
   - merge-conflict record moved to `resolved`
   - cutover/finalize remains blocked while unresolved and unblocks only after resolution

Why this matters:

- The current bounded conflict tests prove durable records, but there is no real E2E proof that a conflicted repo becomes correct on disk after runtime resolution.

## Harness And Fixture Requirements

- Add helper utilities for E2E git assertions:
  - read file contents from a repo path
  - capture `git rev-parse HEAD`
  - capture `git show --name-only`
  - capture `git status --short`
  - optionally snapshot the full repo tree for tiny deterministic fixtures
- Prefer tiny fixture trees such as:
  - `shared.txt`
  - `docs/notes.md`
  - `src/module.py`
- Use disjoint-file merges for clean-merge assertions and single-line same-file edits for deterministic conflict assertions.
- Keep rollback proof at the parent repo boundary; do not rely only on DB history to infer that reset-to-seed happened.

## Notes And Checklist Follow-Up

- Update `notes/catalogs/audit/flow_coverage_checklist.md` so Flow 11 explicitly distinguishes "merge/finalize commands executed" from "merged tree contents verified."
- Update `notes/catalogs/checklists/feature_checklist_backfill.md` once the new suites exist so FC-08 can move from planned git E2E targets toward implemented or verified status.
- Update `notes/catalogs/checklists/verification_command_catalog.md` with the new canonical git-content E2E commands when the tests land.
- If implementation reveals missing runtime surfaces for conflict resolution or rollback inspection, update `notes/specs/git/git_rectification_spec_v2.md` and `notes/contracts/runtime/cutover_policy_note.md` in the same change.

## Verification

- Review current git E2E coverage: `python3 -m pytest tests/e2e/test_flow_10_regenerate_and_rectify_real.py tests/e2e/test_flow_11_finalize_and_merge_real.py tests/e2e/test_flow_21_child_session_round_trip_and_mergeback_real.py -q`
- Document-schema targeted suite: `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py -q`

## Exit Criteria

- The repo has a durable plan for real E2E tests that verify git tree contents after clean merges, rectification rollback/rerun, and conflict resolution.
- The plan names the missing assertions in the current E2E suite and ties them to concrete new test files.
- The task plan itself passes the repository document-schema checks.
