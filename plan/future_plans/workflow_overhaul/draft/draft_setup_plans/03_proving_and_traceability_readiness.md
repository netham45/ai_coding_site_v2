# Setup 03: Proving And Traceability Readiness

## Goal

Prepare the verification, checklist, E2E, and flow-traceability surfaces required to land workflow-overhaul features honestly, including template-driven generated-task narratives.

## Main Work

- freeze canonical bounded and E2E proving expectations
- map route plans and future flows into traceability updates
- define which feature/checklist/template families must be updated together

## Main Outputs

- proving readiness map
- flow update triggers
- feature-to-E2E planning posture

## Implementation Subtasks

- define the bounded-test and real-E2E proving standard for workflow-profile and templated-task-generation work
- map which canonical flows and future flows must be updated when each feature slice lands
- define the checklist, verification-command, and traceability artifacts that must move in lockstep with each slice
- align the route-plan assets with the future authoritative E2E narratives so proof scope stays explicit

## Main Dependencies

- Setup 00
- Setup 01
- Setup 02

## Flows Touched

- all workflow-overhaul-affected flows
- future template-generation flows

## Relevant Current Code

- `tests/unit/test_workflows.py`
- `tests/unit/test_workflow_start.py`
- `tests/unit/test_materialization.py`
- `tests/integration/test_workflow_compile_flow.py`
- `tests/integration/test_workflow_start_flow.py`
- `tests/e2e/test_flow_01_create_top_level_node_real.py`
- `tests/e2e/test_flow_03_materialize_and_schedule_children_real.py`
- `tests/e2e/test_flow_06_inspect_state_and_blockers_real.py`
- `tests/unit/test_flow_e2e_alignment_docs.py`

## Current Gaps

- there are no profile-aware or template-generation-aware real E2E suites yet
- the current traceability and flow surfaces cover existing runtime flows, not the future workflow-profile and template-generation routes drafted in this bundle
