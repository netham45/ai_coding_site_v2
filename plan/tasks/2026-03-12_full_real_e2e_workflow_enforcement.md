# Task: Full Real E2E Workflow Enforcement

## Goal

Make every claimed E2E test in `tests/e2e/` prove the full real workflow it names, with no mocked runtime, no operator/test-side advancement standing in for the AI/runtime, and no canonical command or note claiming real end-to-end coverage until the exact real workflow passes.

## Absolute Doctrine

There is zero acceptable deviation from this rule for any test that is claimed as E2E:

- test every component as if it is being used in a live run
- the test must use the same runtime boundaries the real feature uses
- the test must wait for the real system to do the work it claims to do
- the test must verify the real durable and operator-visible consequences of that work

If a test does anything else, it is not E2E for repository-claim purposes.

That means:

- no partial substitutions
- no “close enough” harness shortcuts
- no simulated middle sections inside an otherwise real harness
- no operator/test rescue steps where the live runtime is supposed to act
- no counting a bounded, integration, or bring-up proof as full E2E

A test is either a full live-run-equivalent E2E or it is not an E2E checkpoint.

## No-Shortcut Repair Rule

This task is specifically to fix the E2E tests so they become true E2E tests.

That means the required path is:

- keep the affected tests in `tests/e2e/`
- remove the synthetic workflow steps
- fix the runtime and/or rewrite the test so the workflow becomes live-run-equivalent
- keep iterating until the E2E itself is truly end to end

The following do not count as progress toward completing this task:

- moving an E2E file out of `tests/e2e/`
- downgrading an E2E to integration or bounded coverage as a substitute for repairing it
- relabeling a broken E2E as a non-E2E artifact without also creating the real E2E replacement
- treating quarantine, demotion, relocation, or command-list removal as completion of the task
- using policy, marker, or documentation cleanup as a substitute for repairing the live workflow

Quarantine and honest status labeling may still be used to prevent false claims while repair is underway, but they are not the task goal and must never replace in-place E2E repair.

## Rationale

- Rationale: The repository currently still contains E2E narratives that use operator-driven progression, explicit API completion shortcuts, or manual materialization in places where the claimed behavior is supposed to come from the live runtime itself.
- Reason for existence: This task exists to close the gap between the user requirement and the current proving surface so that “E2E” means the whole real workflow, not a partially real harness around simulated progression.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/14_F10_ai_facing_cli_command_loop.md`
- `plan/features/15_F11_operator_cli_and_introspection.md`
- `plan/features/16_F12_session_binding_and_resume.md`
- `plan/features/20_F15_child_node_spawning.md`
- `plan/features/23_F18_child_merge_and_reconcile_pipeline.md`
- `plan/features/39_F12_tmux_session_manager.md`
- `plan/features/50_F12_session_attach_resume_and_control_commands.md`
- `plan/features/71_F11_live_git_merge_and_finalize_execution.md`
- `plan/e2e_tests/03_e2e_session_recovery_and_child_runtime.md`
- `plan/e2e_tests/06_e2e_feature_matrix.md`
- `plan/checklists/16_e2e_real_runtime_gap_closure.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/runtime/tmux_session_lifecycle_spec_v1.md`
- `notes/contracts/parent_child/child_session_mergeback_contract.md`
- `notes/planning/implementation/real_e2e_flow_contract_phase1_decisions.md`

## Non-Negotiable E2E Rule

For this task, a test may count as real E2E only if all of the following are true:

- real daemon subprocess
- real CLI and API boundaries
- real PostgreSQL persistence
- real tmux session lifecycle where session orchestration is part of the feature
- real AI/provider execution where AI/runtime work is part of the feature
- real prompt rendering and delivery
- real workflow progression driven by the runtime or the actual operator surface being tested
- real child creation, scheduling, and merge/reconcile behavior where claimed
- real workspace/git side effects where claimed
- real website/browser interaction where the claimed workflow includes the website UI
- no direct DB mutation to force state
- no `/api/subtasks/complete` or equivalent synthetic completion injection
- no test-side `subtask start`, `subtask complete`, `subtask fail`, `summary register`, `session pop`, or `workflow advance` as a substitute for live runtime behavior
- no manual `node lifecycle transition` calls as a substitute for real runtime progression
- no manual `node materialize-children` calls in a test whose claim is that parent AI/runtime created descendants itself
- no test-only hidden helpers that perform the workflow step off-screen and then expose the result as if the live system had done it
- no using a lower-layer proof to stand in for a full-run proof of a higher-layer workflow
- no “the harness is real so the workflow counts as E2E” reasoning when any claimed workflow step is still synthetic

The standard is not “mostly real.”

The standard is:

- every workflow step that exists in a live run must also happen in the E2E
- every component involved in that live run must be exercised through its real runtime boundary
- every claimed outcome must come from that real execution path

If any claimed workflow step is skipped, injected, forced, mocked, manually advanced, or completed through a lower-layer shortcut, the test fails this doctrine and must not be treated as E2E.

If a feature cannot satisfy that rule yet, the test must either:

- move to integration/bounded coverage, or
- stay in `tests/e2e/` only as an explicitly partial bring-up target that is excluded from canonical “passing real E2E” claims

There is no third category where a partially simulated workflow is still allowed to count as E2E.

For this task specifically, the required outcome is not “move to integration/bounded coverage.”

For this task specifically, the required outcome is:

- repair the E2E in place until it becomes a true E2E

## Scope

- Database: prove durable runtime state only through the real daemon/runtime path, not by injected records or test-only forcing.
- CLI: keep CLI subprocess execution as the primary operator proof surface for E2E narratives.
- Daemon: fix runtime gaps that prevent full workflows from progressing naturally, especially child-session bootstrap, parent-created descendants, and leaf-task completion/reporting.
- YAML: ensure parent decomposition and child-spawn behavior come from real compiled workflow and layout contracts rather than test-side materialization when the claim is AI-created descendants.
- Prompts: fix prompt rendering/delivery defects that cause live sessions to stall, mis-execute, or receive unresolved placeholders.
- Website UI: not a primary focus in this batch except that any UI E2E claiming runtime-backed creation must obey the same no-simulation rule.
- Tests: rewrite or demote any E2E that currently simulates progression; separate true passing checkpoints from bring-up files that still expose runtime defects.
- Performance: keep the canonical passing checkpoint set narrow enough to stay runnable while still requiring that every claimed workflow be proven end to end through real runtime resources.
- Notes: correct overclaiming notes, checklists, and command catalogs so they do not describe partial or helper-driven flows as fully real E2E.

## Plan

### Phase 1: Quarantine false E2E claims

1. Inventory every file in `tests/e2e/` and classify it as:
   - passing full-real E2E
   - real harness but simulated progression
   - real harness but runtime currently broken
   - bounded/integration proof misplaced in E2E
2. Remove any test with simulated progression from canonical “real E2E” command lists immediately.
3. Mark any still-broken full-real narratives as bring-up targets, not verified checkpoints.
4. Treat every file with even one synthetic workflow step as invalid for canonical E2E status until rewritten or moved.

Phase 1 is a truthfulness gate only.

It is not allowed to become the end state for this task.

The output of Phase 1 must feed direct repair of the affected E2E files.

### Phase 2: Eliminate simulated progression from E2E files

1. Remove every use of:
   - `/api/subtasks/complete`
   - test-side `subtask start`
   - test-side `subtask complete`
   - test-side `subtask fail`
   - test-side `summary register`
   - test-side `workflow advance`
   - `node lifecycle transition` used to stand in for runtime work
2. Replace those files with one of:
   - a true runtime-driven E2E narrative in the same `tests/e2e/` file or an immediately adjacent replacement E2E file in `tests/e2e/`
3. Keep the feature-to-E2E matrix current as tests move or change status.
4. Do not preserve any partially simulated E2E just because it is convenient, fast, historically present, or already referenced by a checklist.

For this task, Phase 2 must repair the E2E surface itself.

It must not satisfy the work by downgrading the workflow to a lower layer and stopping there.

### Phase 3: Fix runtime blockers preventing full workflows

1. Fix child-session bootstrap so delegated child sessions receive a usable rendered prompt and produce durable merge-back results.
2. Fix parent decomposition/runtime behavior so AI-created `phase -> plan -> task` descendants are proven through the live runtime, not explicit test-side materialization, in the tests that claim that behavior.
3. Fix leaf-session progression/reporting so a live tmux/provider session can move from implementation through validation/review/testing/final summary without hidden operator rescue.
4. Fix any daemon/product defects exposed by those reruns before restoring the affected tests to canonical status.

Phase 3 is mandatory whenever the reason a test is not truly E2E is that the real runtime cannot yet perform the workflow.

### Phase 4: Rebuild the canonical E2E command set from truth

1. Define one canonical command set for passing full-real E2E checkpoints only.
2. Define a separate bring-up command set for long-running or currently failing real-runtime narratives.
3. Do not let a bring-up target appear in a passing checkpoint list until it actually passes in the real workflow it claims.

### Phase 5: Re-prove every affected workflow honestly

1. Run the non-gated full-real E2E checkpoint set.
2. Run the tmux-gated checkpoint set.
3. Run the provider-gated child/runtime/full-tree checkpoint set.
4. Record the exact pass/fail outcome for each workflow and update the checklist, matrix, and logs from those actual reruns.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_feature_plan_docs.py tests/unit/test_feature_checklist_docs.py tests/unit/test_verification_command_docs.py -q
PYTHONPATH=src python3 -m pytest tests/e2e/test_flow_21_child_session_round_trip_and_mergeback_real.py -q
PYTHONPATH=src python3 -m pytest tests/e2e/test_e2e_automated_full_tree_cat_runtime_real.py -q
PYTHONPATH=src python3 -m pytest tests/e2e/test_e2e_full_epic_tree_runtime_real.py -q
PYTHONPATH=src python3 -m pytest tests/e2e/test_e2e_incremental_parent_merge_real.py -q
rg -n "/api/subtasks/complete|subtask\", \"(start|complete|fail)|summary\", \"register|workflow\", \"advance|node\", \"lifecycle\", \"transition" tests/e2e
```

## Exit Criteria

- no canonical real-E2E command claims a test that still simulates progression
- no test in the passing real-E2E checkpoint set uses synthetic completion or artificial advancement
- no passing canonical E2E relies on any step that would not happen exactly that way in a live run
- the child-session mergeback flow passes through real tmux/provider execution
- at least one canonical full-real E2E proves AI-driven `phase -> plan -> task` descendant creation and leaf completion without manual descendant materialization
- every workflow claimed in the canonical real-E2E command set has been rerun successfully through the exact real workflow it names
- notes, checklists, feature-to-E2E mappings, and command catalogs are updated to match the actual rerun results

Additional task-specific exit criteria:

- no affected E2E is considered “fixed” merely because it was moved, renamed, relabeled, or excluded from canonical commands
- any E2E that was broken at task start remains in `tests/e2e/` and has a direct repair path tracked until it becomes live-run-equivalent
- this task is not complete until the work is expressed as repaired E2E workflows, not just cleaner documentation about broken ones
