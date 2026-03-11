# Phase 03 Draft: Merge-Backed Dependency Truth

## Goal

Require prerequisite siblings to be incrementally merged upward before dependent children become ready.

## Rationale

- Rationale: The current broken behavior exists because dependency satisfaction collapses too early to sibling lifecycle completion.
- Reason for existence: This phase exists to move readiness truth from "sibling is COMPLETE" to "sibling is merged into current parent state," which is the actual contract dependent children need.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/11_F08_dependency_graph_and_admission_control.md`: this phase is the direct extension point for merge-backed readiness truth.
- `plan/features/04_F07_durable_node_lifecycle_state.md`: lifecycle and blocker state must remain coherent when blocker semantics expand.
- `plan/features/20_F15_child_node_spawning.md`: materialized child dependency edges are the structural input this phase reinterprets.
- `plan/features/64_F08_F15_richer_child_scheduling_and_blocker_explanation.md`: richer blocker explanations should eventually include the new merge-backed waiting reasons.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/contracts/parent_child/child_materialization_and_scheduling.md`
- `notes/contracts/runtime/invalid_dependency_graph_handling.md`
- `notes/pseudocode/modules/check_node_dependency_readiness.md`
- `notes/pseudocode/state_machines/node_lifecycle.md`
- `plan/future_plans/sibling_dependency_incremental_parent_merge/2026-03-11_overview.md`

## Scope

- Database: extend blocker truth and any supporting read models so merge-backed dependency status is durable and inspectable.
- CLI: expose richer blocker reasons so operators can distinguish unmet sibling completion from unmet sibling merge.
- Daemon: change dependency satisfaction logic so prerequisite sibling merges, not sibling lifecycle alone, drive readiness.
- YAML: keep dependency structure declarative but leave merge-backed satisfaction logic code-owned.
- Prompts: later startup and conflict prompts will consume this truth, but prompt-surface changes are not the main focus in this phase.
- Tests: bounded blocker transitions and integration proof that sibling completion alone no longer unblocks dependents.
- Performance: blocker recomputation must remain efficient enough to run after every incremental merge.
- Notes: revise dependency doctrine so merge-backed readiness is explicit rather than implied.

## Verification

- Bounded proof:
  - blocked after sibling completion but before sibling merge
  - ready only after sibling merge success
  - richer blocker kinds persist correctly
- Real proof:
  - real daemon path proves dependent child cannot start until prerequisite sibling merge is durable

## Exit Criteria

- readiness truth depends on incremental merge state rather than child lifecycle alone
- operator/CLI-facing blocker reasons can explain the difference
- this phase remains a future-plan draft and is not an implementation claim by itself
