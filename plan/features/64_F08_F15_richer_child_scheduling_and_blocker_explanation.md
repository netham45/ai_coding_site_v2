# Phase F08/F15-S1: Richer Child Scheduling And Blocker Explanation

## Goal

Make child scheduling and blocker reporting explain ready versus blocked descendants in a richer, operator-facing way.

## Rationale

- Rationale: Current materialization and inspection flows work for the shipped built-in layouts, but they do not yet expose a deep scheduling contract for blocked descendants, dependency-derived waits, and mixed pause states.
- Reason for existence: This phase exists to turn child scheduling from a basic materialization outcome into a clearly inspectable coordination model with actionable blocker explanations.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/20_F15_child_node_spawning.md`: F15 creates children and initial scheduling classifications.
- `plan/features/11_F08_dependency_graph_and_admission_control.md`: F08 defines dependency blockers and admission gating.
- `plan/features/15_F11_operator_cli_and_introspection.md`: F11 currently exposes the main read-side operator surfaces that need richer blocker detail.
- `plan/features/29_F24_user_gating_and_pause_flags.md`: F24 introduces pause-state blockers that should surface in scheduling views.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/contracts/parent_child/child_materialization_and_scheduling.md`
- `notes/contracts/runtime/invalid_dependency_graph_handling.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/specs/database/database_schema_spec_v2.md`
- `notes/planning/implementation/per_flow_gap_remediation_plan.md`

## Scope

- Database: add any derived blocker/scheduling views or durable explanation records needed for richer descendant readiness inspection.
- CLI: expand child-materialization, blockers, tree, and related operator commands to explain blocked descendants and why they are blocked.
- Daemon: classify scheduling and blocker states more precisely across dependency, pause, user-gate, and recovery conditions.
- YAML: preserve the code/YAML boundary; YAML may declare dependencies or policies, but blocker explanation remains daemon-owned.
- Prompts: update operator or recovery prompts only where richer blocker explanations alter the expected guidance.
- Tests: exhaustively cover blocked descendants, dependency waits, pause-derived blockers, and mixed subtree scheduling cases.
- Performance: benchmark tree/blocker inspection on larger child sets and mixed dependency graphs.
- Notes: update scheduling, blocker, and operator-read notes to match the richer explanation model.
