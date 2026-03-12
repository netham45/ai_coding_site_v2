# Task: E2E Parallel Repair Pool Coordination

## Goal

Split the remaining real E2E failures into parallelizable work pools so multiple agents can repair the runtime and the affected `tests/e2e/` files simultaneously without overlapping ownership or redoing the same investigation.

## Rationale

- The remaining E2E failures are no longer primarily test-side simulation problems.
- They now cluster into a small number of runtime blocker classes.
- Multiple agents can work in parallel if each pool owns a distinct blocker family, file set, and verification surface.
- Rationale: The repo needs explicit pool ownership so agents can repair the remaining real E2E blockers in parallel without colliding.
- Reason for existence: This plan exists to turn the current flat failure inventory into concurrent workstreams with clear boundaries.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/14_F10_ai_facing_cli_command_loop.md`
- `plan/features/15_F11_operator_cli_and_introspection.md`
- `plan/features/16_F12_session_binding_and_resume.md`
- `plan/features/20_F15_child_node_spawning.md`
- `plan/features/23_F18_child_merge_and_reconcile_pipeline.md`
- `plan/features/39_F12_tmux_session_manager.md`
- `plan/features/71_F11_live_git_merge_and_finalize_execution.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/tasks/2026-03-12_full_real_e2e_workflow_enforcement.md`
- `plan/checklists/16_e2e_real_runtime_gap_closure.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`
- `notes/catalogs/checklists/verification_command_catalog.md`

## Scope

- Database: keep pool boundaries aligned with the durable runtime rows each blocker family depends on.
- CLI: assign operator-surface failures to one owning pool so command-contract fixes are not duplicated.
- Daemon: split the remaining daemon/runtime defects by blocker family rather than by arbitrary test file order.
- YAML: route parent-decomposition/YAML contract work to the descendant-creation pool.
- Prompts: route prompt bootstrap, ordering, and child-session rendering issues to the tmux/session pool.
- Tests: map every remaining failing real E2E file to a specific pool with explicit ownership.
- Performance: keep pool plans narrow enough that agents can iterate and rerun targeted commands quickly.
- Notes: make the pool split durable in repository plans instead of leaving it implicit in chat.

## Pool Map

### Pool 1: Run Bind And Durable Session Visibility

- Plan: `plan/tasks/2026-03-12_e2e_pool_01_run_bind_and_durable_session_visibility.md`
- Core blocker:
  - `node run start` succeeds but `session bind --node <id>` returns `active durable run not found`
- Primary files:
  - `tests/e2e/test_flow_11_finalize_and_merge_real.py`
  - `tests/e2e/test_e2e_live_git_merge_and_finalize_real.py`
  - `tests/e2e/test_e2e_rebuild_cutover_coordination_real.py`
  - `tests/e2e/test_e2e_incremental_parent_merge_real.py`
  - `tests/e2e/test_flow_14_project_bootstrap_and_yaml_onboarding_real.py`
  - `tests/e2e/test_flow_15_to_18_default_blueprints_real.py`
  - `tests/e2e/test_flow_19_hook_expansion_compile_stage_real.py`
  - `tests/e2e/test_flow_20_compile_failure_and_reattempt_real.py`
  - `tests/e2e/test_e2e_compile_variants_and_diagnostics.py`

### Pool 2: Parent Decomposition And Runtime-Created Descendants

- Plan: `plan/tasks/2026-03-12_e2e_pool_02_parent_decomposition_and_runtime_children.md`
- Core blocker:
  - parent nodes route into leaf execution or stall instead of creating `phase -> plan -> task` descendants
- Primary files:
  - `tests/e2e/test_e2e_full_epic_tree_runtime_real.py`
  - `tests/e2e/test_flow_08_handle_failure_and_escalate_real.py`
  - `tests/e2e/test_flow_10_regenerate_and_rectify_real.py`
  - `tests/e2e/test_e2e_regeneration_and_upstream_rectification_real.py`
  - `tests/e2e/test_flow_22_dependency_blocked_sibling_wait_real.py`
  - `tests/e2e/test_e2e_incremental_parent_merge_real.py`

### Pool 3: Tmux Prompt, Idle, Recovery, And Child Session Bootstrap

- Plan: `plan/tasks/2026-03-12_e2e_pool_03_tmux_prompt_idle_recovery_and_child_sessions.md`
- Core blockers:
  - child-session prompt bootstrap defects
  - prompt ordering / prompt-surface mismatches
  - run loss before prompt delivery
  - tmux supervision restart mismatch
- Primary files:
  - `tests/e2e/test_tmux_codex_idle_nudge_real.py`
  - `tests/e2e/test_flow_07_pause_resume_and_recover_real.py`
  - `tests/e2e/test_flow_13_human_gate_and_intervention_real.py`
  - `tests/e2e/test_flow_21_child_session_round_trip_and_mergeback_real.py`
  - `tests/e2e/test_e2e_prompt_and_summary_history_real.py`
  - `tests/e2e/test_flow_05_admit_and_execute_node_run_real.py`

### Pool 4: Compile, Quality-Gate, And Inspection Contract Gaps

- Plan: `plan/tasks/2026-03-12_e2e_pool_04_compile_quality_gate_and_inspection_contracts.md`
- Core blockers:
  - compile during active run conflict
  - failed-compile inspection gap
  - quality-gate runtime entry gap
  - rebuild-cutover blocker-surface mismatch once bind works
- Primary files:
  - `tests/e2e/test_flow_02_compile_or_recompile_workflow_real.py`
  - `tests/e2e/test_flow_09_run_quality_gates_real.py`
  - `tests/e2e/test_flow_20_compile_failure_and_reattempt_real.py`
  - `tests/e2e/test_e2e_rebuild_cutover_coordination_real.py`

## Coordination Rules

1. Each pool owns its listed E2E files and the directly related runtime code paths.
2. If a runtime fix overlaps another pool's owned files, the first agent must document the overlap in its development log and link the affected pool plan.
3. Pool 2 and Pool 1 may both touch `test_e2e_incremental_parent_merge_real.py`, but ownership is split:
   - Pool 1 owns run/session bind failures.
   - Pool 2 owns descendant-creation / parent-decomposition failures.
4. Pool 4 may consume Pool 1 fixes once `session bind` starts working, but should not block on that for compile/inspection-specific work.
5. No pool is allowed to reintroduce synthetic progression into any E2E file.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- every remaining failing real E2E file is assigned to exactly one active blocker pool, except where a shared file has explicitly split ownership
- each pool has:
  - a goal
  - owned files
  - owned runtime focus
  - canonical commands
  - completion criteria
- the pool split is documented in repository plans rather than left implicit in chat
