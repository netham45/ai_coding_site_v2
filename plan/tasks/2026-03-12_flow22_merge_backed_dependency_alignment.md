# Task: Flow 22 Merge-Backed Dependency Alignment

## Goal

Align Flow 22's YAML contract and bounded/real test expectations with the current merge-backed sibling-dependency runtime doctrine so the flow no longer expects immediate unblock on prerequisite lifecycle `COMPLETE` alone.

## Rationale

- Rationale: The current runtime now treats same-parent sibling dependency satisfaction as merge-backed truth, but Flow 22's YAML/test layer still expects the dependent sibling to become ready immediately after the prerequisite sibling reaches `COMPLETE`.
- Reason for existence: This task exists to remove stale flow-contract drift, keep Flow 22 aligned with the implemented incremental-merge model, and restore the broader flow-YAML verification command if the bounded suite can be updated to prove the current contract correctly.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/74_F08_F18_incremental_parent_merge_overview.md`
- `plan/features/76_F18_incremental_parent_merge_phase_02_one_child_incremental_merge_execution.md`
- `plan/features/77_F08_incremental_parent_merge_phase_03_merge_backed_dependency_truth.md`
- `plan/features/82_F08_F18_incremental_parent_merge_full_e2e.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `flows/22_dependency_blocked_sibling_wait_flow.yaml`
- `notes/planning/implementation/dependency_graph_and_admission_control_decisions.md`
- `notes/catalogs/audit/flow_coverage_checklist.md`
- `notes/planning/implementation/missing_simulation_flow_yaml_and_test_plan.md`

## Scope

- Database: not directly changed, but the bounded proof must respect durable incremental-merge state expectations.
- CLI: the real E2E contract should still read as a CLI-observed unblock flow rather than an in-memory shortcut.
- Daemon: no runtime behavior change is planned unless the investigation finds a real runtime bug rather than stale test expectations.
- Website: not affected in this slice.
- YAML: update the Flow 22 YAML asset so its documented task flow matches merge-backed dependency truth.
- Prompts: not affected in this slice.
- Tests: revise bounded and possibly real Flow 22 tests to prove the current merge-backed sibling unblock contract accurately.
- Performance: keep the bounded test fixture minimal even if it needs explicit live-git/bootstrap setup for the merge lane.
- Notes: update adjacent audit/planning notes if Flow 22's current gap wording still describes the old pre-merge expectation.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/integration/test_flow_yaml_contract_suite.py -q
PYTHONPATH=src python3 -m pytest tests/unit/test_flow_assets.py tests/unit/test_flow_e2e_alignment_docs.py tests/unit/test_notes_quickstart_docs.py tests/unit/test_task_plan_docs.py -q
```

## Exit Criteria

- Flow 22's YAML asset no longer claims raw lifecycle `COMPLETE` alone unblocks the dependent sibling
- the bounded Flow 22 proof passes against the current merge-backed runtime contract
- any touched notes or audit docs describe the current gap honestly
- task plan and development log entries record the actual proving results
