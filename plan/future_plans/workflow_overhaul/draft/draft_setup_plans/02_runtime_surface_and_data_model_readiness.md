# Setup 02: Runtime Surface And Data Model Readiness

## Goal

Freeze the runtime surfaces, persistence posture, and inspection boundaries needed before implementing workflow-profile and checklist-mode behavior.

## Main Work

- freeze startup/create/materialize/profile inspection routes
- freeze compile-context and brief payload posture
- freeze checklist persistence and inspection posture
- identify additive migration direction

## Main Outputs

- route readiness map
- persistence split decisions
- read/write surface boundaries

## Implementation Subtasks

- freeze the route posture for startup, creation, materialization, workflow brief, profile inspection, and checklist inspection
- decide the additive persistence model for selected profiles, compiled profile context, checklist instances, checklist items, and blockers
- define which data belongs in relational columns versus compile-frozen or instance-frozen JSON payloads
- map the read/write responsibility split between daemon routes, CLI handlers, and website reads before any code migration starts

## Main Dependencies

- Setup 00
- Setup 01

## Flows Touched

- `01_create_top_level_node_flow`
- `02_compile_or_recompile_workflow_flow`
- `05_admit_and_execute_node_run_flow`
- `06_inspect_state_and_blockers_flow`

## Relevant Current Code

- `src/aicoding/db/models.py`
- `src/aicoding/daemon/app.py`
- `src/aicoding/daemon/workflow_start.py`
- `src/aicoding/daemon/workflows.py`
- `src/aicoding/daemon/materialization.py`
- `src/aicoding/cli/parser.py`
- `src/aicoding/cli/handlers.py`
- `frontend/src/lib/api/types.js`
- `frontend/src/lib/api/workflows.js`

## Current Gaps

- current persistence has no selected-workflow-profile or checklist-instance state
- current daemon and CLI surfaces do not expose `node profiles`, rich `node types`, `workflow brief`, or any checklist routes
