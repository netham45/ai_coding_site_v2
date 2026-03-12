# Task: E2E Pool 02 Parent Decomposition And Runtime-Created Descendants

## Goal

Fix the parent-node runtime so real epic/phase runs create and expose runtime-owned descendants instead of stalling or falling into leaf execution.

## Rationale

- This is the blocker behind the real `phase -> plan -> task` creation gap the user is seeing.
- It affects the biggest orchestration narratives and the most important “AI creates children” claims.
- Rationale: The repo still does not consistently prove live parent-driven child creation, which is the core missing E2E behavior.
- Reason for existence: This plan exists to give one agent ownership of the decomposition and child-materialization runtime path.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/14_F10_ai_facing_cli_command_loop.md`
- `plan/features/20_F15_child_node_spawning.md`
- `plan/features/23_F18_child_merge_and_reconcile_pipeline.md`
- `plan/features/71_F11_live_git_merge_and_finalize_execution.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/checklists/16_e2e_real_runtime_gap_closure.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`
- `notes/contracts/parent_child/child_session_mergeback_contract.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`

## Scope

- Database: verify runtime-created descendants and their lineage become durably visible to operator inspection commands.
- CLI: keep `tree show`, `node children --versions`, and related operator surfaces as the proof boundary.
- Daemon: repair parent decomposition, layout registration, and descendant creation for epic/phase/plan nodes.
- YAML: fix the builtin task-selection and layout contract that currently routes parent nodes into leaf execution.
- Prompts: ensure parent prompts and descendant prompts align with decomposition rather than leaf implementation.
- Tests: rerun only the owned descendant-creation narratives until runtime-created children appear for real.
- Performance: keep child-creation reruns targeted before using the longest full-tree suites.
- Notes: record any parent/decomposition contract changes in the gap checklist and related logs.

## Owned Files

- `tests/e2e/test_e2e_full_epic_tree_runtime_real.py`
- `tests/e2e/test_flow_08_handle_failure_and_escalate_real.py`
- `tests/e2e/test_flow_10_regenerate_and_rectify_real.py`
- `tests/e2e/test_e2e_regeneration_and_upstream_rectification_real.py`
- `tests/e2e/test_flow_22_dependency_blocked_sibling_wait_real.py`
- descendant-creation branches of `tests/e2e/test_e2e_incremental_parent_merge_real.py`

## Runtime Focus

- parent-node available-task routing
- decomposition task selection for `epic`, `phase`, and `plan`
- child layout registration/materialization visibility
- runtime-created descendant persistence and inspection surfaces
- sibling/dependency-aware child creation

## Primary Failure Signatures

- parent node enters `execute_node.run_leaf_prompt`
- epic/phase never creates children
- `tree show --full` and `node children --versions` stay empty
- descendant git hierarchy never appears

## Plan

1. Fix the builtin workflow/task contract so parent nodes are not routed into the leaf-only `execute_node` path.
2. Verify child layout registration, review, and materialization events become operator-visible through the E2E surfaces.
3. Rerun the smallest direct child-creation checks first:
   - `tests/e2e/test_flow_08_handle_failure_and_escalate_real.py`
   - `tests/e2e/test_flow_22_dependency_blocked_sibling_wait_real.py`
4. Rerun the regeneration/rectification narratives:
   - `tests/e2e/test_e2e_regeneration_and_upstream_rectification_real.py`
   - `tests/e2e/test_flow_10_regenerate_and_rectify_real.py`
5. Rerun the large descendant-chain suites:
   - `tests/e2e/test_e2e_full_epic_tree_runtime_real.py`
   - descendant-creation branches in `tests/e2e/test_e2e_incremental_parent_merge_real.py`

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/e2e/test_flow_08_handle_failure_and_escalate_real.py -q
PYTHONPATH=src python3 -m pytest tests/e2e/test_flow_22_dependency_blocked_sibling_wait_real.py -q
PYTHONPATH=src python3 -m pytest tests/e2e/test_e2e_regeneration_and_upstream_rectification_real.py -q -k dependency_invalidated_fresh_restart_is_childless_and_remapped
PYTHONPATH=src python3 -m pytest tests/e2e/test_flow_10_regenerate_and_rectify_real.py -q -k dependency_invalidated_fresh_restart_is_childless_and_remapped_into_parent_candidate
PYTHONPATH=src python3 -m pytest tests/e2e/test_e2e_full_epic_tree_runtime_real.py -q
PYTHONPATH=src python3 -m pytest tests/e2e/test_e2e_incremental_parent_merge_real.py -q -k "grouped_cutover_rematerializes_authoritative_child or manual_restart_requires_explicit_reconcile or manual_restart_clears_after_fresh_manual_child_create"
```

## Exit Criteria

- owned files show real runtime-created descendants where their narrative requires them
- parent nodes no longer fall into the leaf-task execution path when the runtime should decompose children
- any remaining failures are downstream of actual created descendants, not child-creation absence
