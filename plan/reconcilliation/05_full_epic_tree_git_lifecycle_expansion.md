# Full Epic Tree Git Lifecycle Expansion Plan

## Goal

Expand the authoritative full-tree real E2E narrative so it proves the real git lifecycle across the hierarchy, not just live task execution.

The expanded narrative must verify, through real runtime behavior and real repositories on disk:

- clean child-to-parent merges
- rollback or reset-to-seed behavior during rebuild or replay
- redo or replay of current authoritative child finals after regeneration
- deterministic merge-conflict handling and resolution
- final file contents and commit ancestry at task, plan, phase, and epic depth

## Rationale

- Rationale: The current full-tree real E2E proves real epic-to-task descent and live leaf-task execution, but it still stops short of proving that git state is merged, rebuilt, replayed, or conflicted correctly through the hierarchy.
- Reason for existence: This plan exists to turn the orchestration claim into a full runtime proof that the hierarchy and the repos stay correct together.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/02_F01_configurable_node_hierarchy.md`
- `plan/features/13_F09_node_run_orchestration.md`
- `plan/features/20_F15_child_node_spawning.md`
- `plan/features/23_F18_child_merge_and_reconcile_pipeline.md`
- `plan/features/24_F19_regeneration_and_upstream_rectification.md`
- `plan/features/70_F19_live_rebuild_cutover_coordination.md`
- `plan/features/71_F11_live_git_merge_and_finalize_execution.md`
- `plan/features/72_F20_live_merge_conflict_resolution.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/specs/runtime/tmux_session_lifecycle_spec_v1.md`
- `notes/specs/git/git_rectification_spec_v2.md`
- `notes/contracts/parent_child/child_session_mergeback_contract.md`
- `notes/contracts/runtime/cutover_policy_note.md`
- `notes/catalogs/audit/flow_coverage_checklist.md`
- `notes/catalogs/checklists/feature_checklist_backfill.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`

## Current Baseline

- `tests/e2e/test_e2e_full_epic_tree_runtime_real.py` proves real epic-to-task descent and live leaf-task execution through the daemon, CLI, tmux, Codex, PostgreSQL, YAML compilation, and prompt surfaces.
- `tests/e2e/test_e2e_live_git_merge_and_finalize_real.py` proves real git bootstrap, child finalization, merge, finalize, and some rerun-reset behavior at a smaller parent-child scope.
- `tests/e2e/test_flow_11_finalize_and_merge_real.py` proves real finalize-and-merge command execution and durable records at a small scope.
- `tests/e2e/test_flow_10_regenerate_and_rectify_real.py` proves regenerate and upstream-rectify command surfaces and rebuild history, but not full repo replay correctness.
- `tests/e2e/test_flow_21_child_session_round_trip_and_mergeback_real.py` proves real tmux child-session round-trip and durable mergeback context, but not hierarchy-wide git result propagation.

## Gap Statement

The current full-tree runtime proof does not yet demonstrate:

- task repo changes merging into the authoritative plan repo
- plan repo changes merging into the authoritative phase repo
- phase repo changes merging into the authoritative epic repo
- parent repos resetting or rebuilding correctly before replay
- superseded child finals being excluded after rectification
- deterministic merge conflicts pausing the runtime with correct repo state
- conflict resolution producing the expected final tree and durable records

## Scope

- Database: verify durable merge events, final commits, rebuild history, cutover-readiness, conflict state, and authoritative-version reads against the git state that actually exists on disk.
- CLI: drive bootstrap, inspect, finalize, merge, rectify, regenerate, resolve-conflict, rollback, and audit actions through real subprocess CLI commands.
- Daemon: require the real daemon subprocess to own merge admission, rebuild ordering, replay sequencing, conflict pause or unblock, and finalize transitions.
- YAML: exercise the shipped hierarchy and workflow YAML that causes child creation, execution, waiting, reconciliation, and git-affecting runtime progression.
- Prompts: verify the real prompts used for decomposition, leaf implementation, conflict or recovery guidance, and rebuild or redo behavior where prompts materially affect the path.
- Notes: update flow coverage, verification commands, runtime notes, and git notes whenever the real runtime exposes a missing contract or a narrower behavior.
- Tests: extend the authoritative full-tree E2E or add tightly-coupled companion E2Es without weakening the “one real narrative” coverage claim.
- Performance: keep repo fixtures tiny and deterministic while still proving real git lifecycle behavior.

## Required Real Runtime Interactions

The expanded narrative should exercise and inspect all of these surfaces through real code:

### CLI interactions

- `workflow start`
- `node show`
- `node children`
- `tree show`
- `workflow current`
- `workflow chain`
- `subtask current`
- `subtask prompt`
- `subtask context`
- `session bind`
- `git bootstrap-node`
- `git status show`
- `git finalize-node`
- `git merge-children`
- `git merge-events show`
- `git final show`
- `node child-results`
- `node reconcile`
- `node regenerate`
- `node rectify-upstream`
- `node rebuild-history`
- `node version cutover-readiness`
- `node rebuild-coordination`
- any real conflict-inspection or conflict-resolution CLI surface the runtime already exposes

### Database interactions

- authoritative node and version reads
- compiled workflow reads
- run and workflow-event reads
- merge-event reads
- final-commit and git-state reads
- rebuild-history reads
- conflict record reads
- prompt and summary history reads where task execution or recovery depends on them

### Filesystem and git interactions

- inspect repo paths returned by the CLI
- read merged files on disk at task, plan, phase, and epic levels
- `git rev-parse HEAD`
- `git status --short`
- `git show --name-only --format=`
- `git diff --name-only`
- `git rev-list --parents -n 1`
- conflict-marker presence before resolution and absence after resolution

### Tmux and session interactions

- bind a real tmux or Codex session where the runtime requires it
- inspect tmux pane output when diagnosis is needed
- verify child-session round-trip if the mergeback narrative depends on live delegated work

## Proposed Expansion Strategy

### Phase 1: Clean hierarchy-wide merge proof

Extend the full-tree narrative so one task produces a real repo change, then prove:

1. task repo finalizes cleanly
2. task output merges into the authoritative plan repo
3. plan repo content and final commit are correct on disk
4. plan output merges into the authoritative phase repo
5. phase repo content and final commit are correct on disk
6. phase output merges into the authoritative epic repo
7. epic repo content and final commit are correct on disk

Required assertions:

- expected files changed at each level
- untouched seed files remain unchanged
- final CLI-reported commit SHAs equal `git rev-parse HEAD`
- merge-event child SHAs equal the actual finalized child SHAs
- working trees are clean after finalize

### Phase 2: Rebuild rollback and redo proof

After an initial successful hierarchy merge:

1. modify a previously merged phase through the supported regeneration surface
2. trigger real downward regeneration from that phase
3. rerun the regenerated descendant work through the live runtime path
4. rebuild upward and re-merge

Required assertions:

- parent repos no longer expose stale superseded child content
- unaffected sibling contributions remain present
- rebuilt parent HEADs differ from the old finalized commits
- rebuilt parent trees match deterministic expected snapshots
- merge-event history after rebuild references current child finals, not superseded finals
- rebuild history and cutover-readiness surfaces explain the change coherently

### Phase 3: Real conflict proof

Create a deterministic conflict inside the hierarchy by causing overlapping changes in descendants that converge at a common parent.

Required assertions:

- merge runtime pauses or blocks instead of silently choosing an outcome
- the parent repo contains conflict markers before resolution if that is the current runtime behavior
- durable conflict records identify the conflicted path and unresolved status
- resolution must go through the supported operator or runtime surface
- final resolved content matches the expected canonical result
- finalize or cutover stays blocked while unresolved and unblocks only after resolution

## Test Shape

Primary authoritative target:

- `tests/e2e/test_e2e_full_epic_tree_runtime_real.py`

Acceptable companion suites if the primary file becomes too large:

- `tests/e2e/test_e2e_full_epic_tree_git_merge_real.py`
- `tests/e2e/test_e2e_full_epic_tree_git_rectification_real.py`
- `tests/e2e/test_e2e_full_epic_tree_git_conflict_real.py`

Constraint:

- if companion suites are added, `tests/e2e/test_e2e_full_epic_tree_runtime_real.py` must remain the authoritative narrative entry point and the feature-to-E2E mapping must remain explicit

## Existing Tests To Reuse As References

- `tests/e2e/test_e2e_live_git_merge_and_finalize_real.py`
- `tests/e2e/test_flow_11_finalize_and_merge_real.py`
- `tests/e2e/test_flow_10_regenerate_and_rectify_real.py`
- `tests/e2e/test_flow_21_child_session_round_trip_and_mergeback_real.py`

These should be treated as source material for assertions, fixtures, and runtime surfaces, not as substitutes for the hierarchy-wide proof.

## Prohibited Shortcuts

- no fake session backend
- no in-process daemon bridge as the only proof
- no direct DB mutation to create git state, merge state, conflict state, or rebuild completion
- no synthetic mergeback payload in place of real merge runtime
- no synthetic conflict record without a real repo conflict
- no mock git repo or fake commit history
- no file-presence-only proof where durable CLI or DB inspection is part of the claim

## Notes And Checklist Follow-Up

When implementation starts, update:

- `notes/catalogs/audit/flow_coverage_checklist.md`
- `notes/catalogs/checklists/feature_checklist_backfill.md`
- `notes/catalogs/checklists/verification_command_catalog.md`

If runtime gaps are discovered, also update the relevant git or runtime notes in the same change set.

## Canonical Verification Command Targets

Planning and document checks:

- `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py -q`

Reference real E2E coverage during implementation:

- `python3 -m pytest tests/e2e/test_e2e_live_git_merge_and_finalize_real.py tests/e2e/test_flow_10_regenerate_and_rectify_real.py tests/e2e/test_flow_11_finalize_and_merge_real.py tests/e2e/test_flow_21_child_session_round_trip_and_mergeback_real.py tests/e2e/test_e2e_full_epic_tree_runtime_real.py -q`

## Exit Criteria

- The repository has a durable implementation plan for full-tree real git lifecycle testing.
- The plan explicitly covers merge, rollback, redo, and conflict behavior through real runtime boundaries.
- The plan ties the existing full-tree E2E to the existing real git E2E references without weakening the no-mock requirement.
- The associated task plan and development log are current and the relevant document-schema tests pass.
