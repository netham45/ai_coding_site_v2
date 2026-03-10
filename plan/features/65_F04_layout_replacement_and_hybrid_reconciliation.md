# Phase F04-S1: Layout Replacement And Hybrid Reconciliation

## Goal

Implement explicit layout replacement and reconciliation behavior for hybrid manual/layout-driven trees.

## Rationale

- Rationale: Manual child creation already works, but the runtime still lacks a first-class way to replace a generated layout, record reconciliation choices, and safely manage hybrid authority.
- Reason for existence: This phase exists to close the most important gap in manual tree management so Flow 04 can become a full runtime path rather than only a manual-child subset.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/20_F15_child_node_spawning.md`: F15 owns layout-driven child materialization that hybrid reconciliation must integrate with.
- `plan/features/21_F16_manual_tree_construction.md`: F16 added manual child creation and current manual-authority behavior.
- `plan/features/23_F18_child_merge_and_reconcile_pipeline.md`: F18 consumes child authority and reconcile state downstream.
- `plan/features/29_F24_user_gating_and_pause_flags.md`: F24 may be needed when reconciliation requires explicit approval.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/contracts/parent_child/manual_vs_auto_tree_interaction.md`
- `notes/contracts/parent_child/child_materialization_and_scheduling.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/specs/database/database_schema_spec_v2.md`
- `notes/planning/implementation/per_flow_gap_remediation_plan.md`

## Scope

- Database: persist layout replacement intent, hybrid reconciliation choices, and any authority-state transitions needed beyond current parent-child authority records.
- CLI: add explicit layout replacement and reconciliation-choice commands instead of relying only on manual child creation.
- Daemon: implement hybrid-authority reconciliation rules, conflict checks, and safe subtree state transitions.
- YAML: allow layout selection and replacement references where needed, while keeping authority and reconcile decisions daemon-owned.
- Prompts: add reconciliation and layout-replacement guidance prompts where operator or AI sessions must choose how to proceed.
- Tests: exhaustively cover replacing layout-managed structures, hybrid transitions, reconcile choices, and protection against silent overwrite.
- Performance: benchmark hybrid-tree inspection and reconciliation readiness reads for larger subtrees.
- Notes: update manual-vs-auto tree, child-materialization, and runtime notes with the final authority model.
