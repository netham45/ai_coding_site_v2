# Full E2E: Incremental Parent Merge For Sibling Dependencies

## Goal

Define the full real end-to-end proving plan for merge-backed sibling dependency execution, including happy path, refresh path, conflict path, restart path, and final parent reconcile behavior.

## Rationale

- Rationale: This feature changes real runtime behavior across child completion, daemon background orchestration, git state, dependency readiness, prompt context, and final parent reconcile semantics, so bounded tests alone are not enough.
- Reason for existence: This draft exists to spell out the real-runtime proof needed before any future implementation slice could honestly claim the flow is working end to end.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/11_F08_dependency_graph_and_admission_control.md`: the E2E plan must prove readiness now depends on merge-backed dependency truth.
- `plan/features/13_F09_node_run_orchestration.md`: the E2E flow begins at real child run completion and daemon-owned progression.
- `plan/features/23_F18_child_merge_and_reconcile_pipeline.md`: the E2E plan must prove incremental child-to-parent merge and later final parent reconcile do not conflict.
- `plan/features/71_F11_live_git_merge_and_finalize_execution.md`: the E2E plan must use real git-backed execution rather than metadata-only simulation.
- `plan/features/69_F21_F22_F23_F29_turnkey_quality_gate_finalize_chain.md`: the final parent flow still has to complete after incremental merges are applied.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/catalogs/checklists/e2e_execution_policy.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/git/git_rectification_spec_v2.md`
- `notes/specs/prompts/prompt_library_plan.md`
- `notes/contracts/parent_child/child_materialization_and_scheduling.md`
- `plan/features/74_F08_F18_incremental_parent_merge_overview.md`

## Scope

- Database: prove durable merge-lane state, blocker transitions, conflict persistence, and restart-safe replay through the real persistence layer.
- CLI: prove operator- and AI-facing commands can inspect blocked reasons, merge progress, conflicts, actual applied merge order, and final parent readiness through real command surfaces.
- Daemon: prove background merge processing, dependency unblock, child refresh, and conflict handoff through real daemon process boundaries.
- YAML: prove the runtime still respects the shipped child/task/policy structure while introducing merge-backed behavior; no fake bypass of compiled workflow or child layout structure.
- Prompts: prove the parent and child prompt/context surfaces expose the new merge-backed state in real runtime flows where applicable.
- Tests: add real E2E narratives for happy path, stale-bootstrap refresh, conflict handoff, restart recovery, and final parent reconcile.
- Performance: keep the real E2E narratives bounded enough to be runnable while still exercising true git and daemon behavior.
- Notes: document exact E2E claims and keep the feature status below `flow_complete` until the real-runtime narratives pass. Pause/cancel and supersession narratives may remain follow-on hardening if the first implementation slice does not claim them yet.

## E2E Narratives

### E2E 1: Basic merge-backed sibling unblock

Purpose:

- prove the core bug is actually fixed in real runtime behavior

Narrative:

1. create a parent with child `A -> B`
2. start `A`
3. complete `A` through real runtime
4. assert `B` does not unblock immediately on `A = COMPLETE`
5. wait for daemon incremental merge of `A`
6. assert `B` becomes ready only after merge success
7. start `B`
8. prove `B` sees parent state that includes `A`

Required observations:

- durable merge-lane state exists
- dependency blockers transition through the merge-backed path
- existing CLI/operator reads expose merge progress without needing a brand new command family
- child `B` startup context or actual repo content reflects `A`'s merged work

### E2E 2: Stale bootstrap refresh path

Purpose:

- prove a dependent child cannot continue from stale parent ancestry

Narrative:

1. create parent with `A -> B`
2. materialize both children early so `B` has an old bootstrap state
3. complete `A`
4. daemon incrementally merges `A`
5. assert `B` is marked refresh-required or equivalent before admission
6. daemon refreshes/reboots `B` against the updated parent state
7. start `B`
8. prove `B` runs from updated parent ancestry, not the old seed

Required observations:

- stale-bootstrap truth is durable and inspectable
- `B` is not admitted until refresh is complete

### E2E 3: Incremental merge conflict handoff

Purpose:

- prove parent AI involvement stays exceptional and conflict-scoped

Narrative:

1. create parent with child `A -> B`
2. arrange a real git conflict when `A` merges upward
3. complete `A`
4. daemon attempts incremental merge and conflicts
5. assert merge lane becomes conflicted/paused
6. assert `B` remains blocked
7. inspect parent conflict context through real CLI/daemon surfaces
8. resolve conflict through the real parent AI/session path
9. resume merge lane
10. prove `B` unblocks only after durable resolution

Required observations:

- parent AI prompt/context contains conflict metadata
- dependents do not unblock early

### E2E 4: Restart and recovery

Purpose:

- prove the merge lane is restart-safe

Narrative:

1. create parent with `A -> B`
2. complete `A`
3. stop the daemon after child completion and before, during, or just after incremental merge processing
4. restart the daemon
5. assert the parent merge lane resumes from durable state
6. assert no duplicate merge occurs
7. assert `B` becomes ready exactly once when the merge is durably satisfied

Required observations:

- durable completed-unmerged child state and parent lane state survive process restart
- replay is idempotent

### E2E 5: Final parent reconcile after incremental merges

Purpose:

- prove the final parent flow still works after child work has already been merged upward

Narrative:

1. create parent with at least `A -> B` and optionally another independent child
2. let child merges happen incrementally through the daemon
3. finish all required children
4. assert parent enters final reconcile-ready state
5. run final parent reconcile / quality / finalize path
6. assert no duplicate child merge occurs
7. assert final parent state includes all child work and completes successfully

Required observations:

- merged-upward child history is visible
- the recorded applied incremental merge order is visible through existing inspection surfaces
- final reconcile acts as post-merge synthesis rather than first merge point

## Suggested Real E2E File Layout

The exact filenames can change, but the bundle should likely end with a small family of explicit tests such as:

- `tests/e2e/test_e2e_incremental_parent_merge_basic_real.py`
- `tests/e2e/test_e2e_incremental_parent_merge_refresh_real.py`
- `tests/e2e/test_e2e_incremental_parent_merge_conflict_real.py`
- `tests/e2e/test_e2e_incremental_parent_merge_recovery_real.py`
- `tests/e2e/test_e2e_incremental_parent_merge_final_reconcile_real.py`

Grouping some of these into fewer files is acceptable if the narrative boundaries remain explicit.

## Canonical Future Verification Commands

These are draft commands for the eventual implementation slice.

```bash
python3 -m pytest tests/e2e/test_e2e_incremental_parent_merge_basic_real.py -q
python3 -m pytest tests/e2e/test_e2e_incremental_parent_merge_refresh_real.py -q
python3 -m pytest tests/e2e/test_e2e_incremental_parent_merge_conflict_real.py -q
python3 -m pytest tests/e2e/test_e2e_incremental_parent_merge_recovery_real.py -q
python3 -m pytest tests/e2e/test_e2e_incremental_parent_merge_final_reconcile_real.py -q
```

Combined future proving command:

```bash
python3 -m pytest \
  tests/e2e/test_e2e_incremental_parent_merge_basic_real.py \
  tests/e2e/test_e2e_incremental_parent_merge_refresh_real.py \
  tests/e2e/test_e2e_incremental_parent_merge_conflict_real.py \
  tests/e2e/test_e2e_incremental_parent_merge_recovery_real.py \
  tests/e2e/test_e2e_incremental_parent_merge_final_reconcile_real.py -q
```

## Exit Criteria

- the bundle has explicit real-runtime narratives for every major risk surface
- the minimum real E2E for the core bug is named separately from later hardening flows
- restart, conflict, and final-parent behavior are not silently deferred
- this phase is an authoritative feature plan and not an implementation claim by itself
