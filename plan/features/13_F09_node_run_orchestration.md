# Phase F09: Node Run Orchestration

## Goal

Implement the authoritative run loop for compiled nodes.

## Rationale

- Rationale: Compiled workflows do nothing on their own; the daemon still needs a controlled run loop that advances work, records outcomes, and enforces stage order.
- Reason for existence: This phase exists to define the actual execution semantics for nodes rather than leaving each task family to invent its own runtime behavior.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/07_F03_immutable_workflow_compilation.md`: F03 provides the compiled workflow the run loop executes.
- `plan/features/04_F07_durable_node_lifecycle_state.md`: F07 supplies the runtime states and legal transitions the loop must honor.
- `plan/features/11_F08_dependency_graph_and_admission_control.md`: F08 decides when a node may be admitted or must wait.
- `plan/features/14_F10_ai_facing_cli_command_loop.md`: F10 is the primary interface active AI sessions use to interact with the run loop.
- `plan/features/25_F21_validation_framework.md`: F21 injects validation gates into run progression.
- `plan/features/26_F22_review_framework.md`: F22 adds review-gate behavior to the same loop.
- `plan/features/28_F23_testing_framework_integration.md`: F23 adds testing gates and retry behavior.
- `plan/features/29_F24_user_gating_and_pause_flags.md`: F24 pauses and approvals alter progression in the loop.
- `plan/features/30_F25_failure_escalation_and_parent_decision_logic.md`: F25 governs failure outcomes when execution cannot proceed normally.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/catalogs/inventory/major_feature_inventory.md`
- `notes/catalogs/traceability/spec_traceability_matrix.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/database/database_schema_spec_v2.md`
- `notes/specs/prompts/prompt_library_plan.md`
- `notes/pseudocode/modules/run_node_loop.md`
- `notes/pseudocode/modules/execute_compiled_subtask.md`

## Scope

- Database: node runs, run state, cursor, attempts, run history.
- CLI: current task/subtask, attempt state, workflow advancement.
- Daemon: admit-or-load, loop ownership, cursor advancement, acceptance of stage completion.
- YAML: executable task/subtask ordering and acceptance contracts.
- Prompts: compiled execution prompts tied to real stage behavior.
- Tests: exhaustive happy, pause, failure, retry, and cursor-integrity coverage.
- Performance: benchmark hot loop operations.
- Notes: update runtime loop notes if ownership shifts during coding.
