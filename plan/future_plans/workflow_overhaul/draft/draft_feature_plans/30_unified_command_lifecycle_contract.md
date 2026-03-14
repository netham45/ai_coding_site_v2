# Feature 30: Unified Command Lifecycle Contract

## Goal

Replace the current split command semantics with one daemon-owned lifecycle contract that governs executable subtask commands and adjacent action surfaces consistently.

## Main Work

- define the standard command lifecycle interface
- define structured legality and action-result payloads
- inventory and plan the migration of every built-in subtask command kind and adjacent action surfaces
- define the corrective-expansion contract for verification-discovered remediation and reverification

## Implementation Subtasks

- define the shared lifecycle foundation layer before command-specific handler work begins
- define the shared command state vocabulary and legality/result payloads
- define the code-owned handler contract for executable command kinds
- align YAML schema expectations with the new command contract boundary
- map the built-in subtask command library and adjacent action surfaces to explicit migration slices
- ensure the contract covers blocked reasons, completion checks, retry posture, and daemon-owned bounded actions without creating two command systems
- define `needs_remediation` as a first-class lifecycle outcome that deterministically creates exactly one remediation step and one follow-up verification step for leaf chains, with a hard remediation-turn cap before escalation
- define the parallel non-leaf corrective-expansion contract so plan- and phase-level verification/remediation can materialize additional task or plan descendants inside the current authority boundary and then schedule follow-up reverification
- define how corrective-loop lineage, loop budgets, finding linkage, and duplicate-loop prevention surface through daemon payloads, CLI results, and operator inspection views

## Main Dependencies

- Setup 01
- Setup 02
- Setup 03
- Feature 10
- Feature 11
- Feature 12
- Feature 13
- Feature 20
- Feature 21
- Feature 22

## Flows Touched

- `05_admit_and_execute_node_run_flow`
- `06_inspect_state_and_blockers_flow`
- `07_pause_resume_and_recover_flow`
- `08_handle_failure_and_escalate_flow`
- `09_run_quality_gates_flow`
- `10_regenerate_and_rectify_flow`
- `13_human_gate_and_intervention_flow`

## Relevant Current Code

- `src/aicoding/yaml_schemas.py`
- `src/aicoding/daemon/workflows.py`
- `src/aicoding/daemon/run_orchestration.py`
- `src/aicoding/daemon/interventions.py`
- `src/aicoding/resources/yaml/builtin/system-yaml/tasks/`
- `src/aicoding/resources/yaml/builtin/system-yaml/subtasks/`

## Current Gaps

- executable command lifecycle behavior is currently split across YAML, compiled subtask metadata, daemon runtime paths, and intervention/action surfaces
- there is no single draft feature slice governing a full-system migration to one command lifecycle contract
- the command-specific draft plans need shared foundation plans for the interface, shared state models, registry/dispatch, and operator projection contract
- the current runtime still assumes one frozen compiled chain plus cursor rewinds, so there is no unified contract yet for append-only corrective expansion, remediation-turn caps, or tier-aware reverification routing
