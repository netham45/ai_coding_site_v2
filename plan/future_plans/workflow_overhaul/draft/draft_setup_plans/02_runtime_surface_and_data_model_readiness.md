# Setup 02: Runtime Surface And Data Model Readiness

## Goal

Freeze the runtime surfaces, persistence posture, and inspection boundaries needed before implementing workflow-profile and templated-task-generation behavior.

## Main Work

- freeze startup/create/materialize/profile inspection routes
- freeze compile-context and brief payload posture
- freeze template provenance, generated-task materialization, and inspection posture
- freeze the corrective-expansion runtime posture for verification-driven remediation and reverification
- identify additive migration direction

## Main Outputs

- route readiness map
- persistence split decisions
- read/write surface boundaries
- corrective-expansion persistence and legality map

## Implementation Subtasks

- freeze the route posture for startup, creation, materialization, workflow brief, profile inspection, and generated-task provenance inspection
- decide the additive persistence model for selected profiles, compiled profile context, template references, generated-task materialization records, and template provenance
- define which data belongs in relational columns versus compile-frozen or instance-frozen JSON payloads
- map the read/write responsibility split between daemon routes, CLI handlers, and website reads before any code migration starts
- define the additive persistence and route posture for corrective expansion, including append-only leaf subtask extension, plan/phase corrective child materialization, remediation-turn caps, and corrective-loop inspection surfaces

## Main Dependencies

- Setup 00
- Setup 01

## Flows Touched

- `01_create_top_level_node_flow`
- `02_compile_or_recompile_workflow_flow`
- `05_admit_and_execute_node_run_flow`
- `06_inspect_state_and_blockers_flow`
- `09_run_quality_gates_flow`

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

- current persistence has no selected-workflow-profile, template-reference, or generated-task lineage state
- current daemon and CLI surfaces do not expose `node profiles`, rich `node types`, `workflow brief`, or any template-provenance routes
- current runtime state assumes one frozen compiled subtask chain per workflow compile and only supports rewind-style correction; there is no additive persistence model for verification-triggered corrective expansion, remediation-turn counters, or follow-up reverification routing
