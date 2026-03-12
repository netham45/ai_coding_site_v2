# Feature 07: Profile E2E And Traceability

## Goal

Land the workflow-profile proving layer, route coverage, and traceability updates for the profile-aware runtime.

## Main Work

- adopt route-level E2E plans
- map profile-aware features into E2E/checklist/flow traceability
- add real-runtime profile ladder and enforcement suites

## Implementation Subtasks

- convert the route-plan assets into implementation-backed E2E task plans and future test skeletons
- update feature/checklist/traceability surfaces so workflow-profile slices map to explicit proof targets
- implement the parentless-start, ladder, enforcement, recovery, and inspection E2E narratives for profile-aware runtime
- update flow and relevant-flow inventory artifacts once the new profile-aware flows become real runtime behavior

## Main Dependencies

- Setup 03
- Features 01 through 06

## Flows Touched

- `01_create_top_level_node_flow`
- `02_compile_or_recompile_workflow_flow`
- `03_materialize_and_schedule_children_flow`
- `05_admit_and_execute_node_run_flow`
- `06_inspect_state_and_blockers_flow`
- `07_pause_resume_and_recover_flow`
- `10_regenerate_and_rectify_flow`
- `13_human_gate_and_intervention_flow`

## Relevant Current Code

- `tests/e2e/test_flow_01_create_top_level_node_real.py`
- `tests/e2e/test_flow_02_compile_or_recompile_workflow_real.py`
- `tests/e2e/test_flow_03_materialize_and_schedule_children_real.py`
- `tests/e2e/test_flow_06_inspect_state_and_blockers_real.py`
- `tests/e2e/test_flow_07_pause_resume_and_recover_real.py`
- `tests/e2e/test_flow_10_regenerate_and_rectify_real.py`
- `tests/e2e/test_flow_13_human_gate_and_intervention_real.py`
- `tests/unit/test_flow_e2e_alignment_docs.py`

## Current Gaps

- no real E2E tests exist for profile-aware startup, profile-aware materialization, rigid non-leaf enforcement, or workflow brief inspection
- the draft route plans have no implementation-backed test files yet
