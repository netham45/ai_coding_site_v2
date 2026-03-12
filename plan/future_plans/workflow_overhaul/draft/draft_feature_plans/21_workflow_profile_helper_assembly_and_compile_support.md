# Feature 21: Workflow-Profile Helper Assembly And Compile Support

## Goal

Land the helper-assembly work needed to make workflow-profile compile behavior reusable, testable, and consistent across daemon surfaces.

## Main Work

- extract helper assembly for profile selection, effective layout resolution, child-role enforcement, and brief assembly
- stop embedding workflow-profile logic only inside large daemon route bodies
- make compile and inspect behavior share one assembly path

## Implementation Subtasks

- define helper entry points for selected-profile resolution and effective-layout projection
- define helper assembly for child-role expectation calculation and blocked-action metadata
- define helper assembly for `workflow_brief` payload construction and retrieval
- align compile, inspect, and startup paths to reuse the helper family instead of drifting independently

## Main Dependencies

- Setup 01
- Setup 02
- Feature 03
- Feature 04
- Feature 19
- Feature 20

## Flows Touched

- `01_create_top_level_node_flow`
- `02_compile_or_recompile_workflow_flow`
- `03_materialize_and_schedule_children_flow`
- `06_inspect_state_and_blockers_flow`

## Relevant Current Code

- `src/aicoding/daemon/workflows.py`
- `src/aicoding/daemon/materialization.py`
- `src/aicoding/daemon/workflow_start.py`
- `src/aicoding/structural_library.py`

## Current Gaps

- helper-assembly expectations were documented in a support note, but the draft queue had no explicit execution slice for that work
- current compile and materialization logic is still concentrated in monolithic runtime modules with limited reusable profile-aware helper surfaces
