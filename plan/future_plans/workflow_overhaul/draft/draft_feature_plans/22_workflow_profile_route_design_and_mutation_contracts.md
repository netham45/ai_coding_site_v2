# Feature 22: Workflow-Profile Route Design And Mutation Contracts

## Goal

Turn the route-design draft into explicit implementation work for daemon endpoints, CLI commands, and blocked mutation behavior.

## Main Work

- define the runtime route family for profile-aware create, inspect, compile, and legality-check surfaces
- make blocked workflow-profile mutations explicit and inspectable
- align CLI command families and browser actions with daemon-owned legality rules

## Implementation Subtasks

- define or update daemon endpoints for profile-aware create, inspect, compile, and blocked-action readback
- map CLI commands and browser actions to the daemon route family instead of inventing separate semantics
- document and enforce blocked mutation payloads for children-required, step-skip, and invalid-profile transitions
- align route-level observability with operator inspection expectations and audit surfaces

## Main Dependencies

- Setup 02
- Feature 02
- Feature 05
- Feature 19
- Feature 20
- Feature 21

## Flows Touched

- `01_create_top_level_node_flow`
- `02_compile_or_recompile_workflow_flow`
- `05_admit_and_execute_node_run_flow`
- `06_inspect_state_and_blockers_flow`
- `11_finalize_and_merge_flow`

## Relevant Current Code

- `src/aicoding/daemon/app.py`
- `src/aicoding/cli/parser.py`
- `src/aicoding/cli/handlers.py`
- `frontend/src/lib/api/workflows.js`
- `frontend/src/lib/api/nodes.js`

## Current Gaps

- the future-plan route-design note existed, but there was no standalone plan to implement those route and mutation contracts
- current runtime command and route surfaces do not yet expose the blocked workflow-profile legality model described by the notes
