# Phase 04: Dependent Child Parent Refresh

## Goal

Prevent dependent children from starting from stale parent bootstrap state.

## Rationale

- Rationale: Even if merge-backed readiness is correct, a dependent child can still start from stale parent ancestry unless the daemon tracks and refreshes child bootstrap truth explicitly.
- Reason for existence: This phase exists to ensure that newly unblocked children actually run against parent state that includes the prerequisite sibling merges they depend on.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/12_F17_deterministic_branch_model.md`: parent and child branch ancestry must remain deterministic after refresh.
- `plan/features/20_F15_child_node_spawning.md`: child creation/bootstrap rules interact directly with refresh semantics.
- `plan/features/71_F11_live_git_merge_and_finalize_execution.md`: child refresh and parent bootstrap behavior should reuse the existing live-git substrate.
- `plan/features/11_F08_dependency_graph_and_admission_control.md`: readiness and refresh truth must align so a child is not admitted while stale.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/specs/git/git_rectification_spec_v2.md`
- `notes/contracts/parent_child/child_materialization_and_scheduling.md`
- `notes/specs/database/database_schema_spec_v2.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `plan/features/74_F08_F18_incremental_parent_merge_overview.md`

## Scope

- Database: persist child bootstrap parent-head truth and refresh-required state.
- CLI: eventual operator reads should be able to show when a child is stale versus current relative to parent state.
- Daemon: detect stale bootstrap ancestry and require refresh or fresh bootstrap before admission.
- YAML: no new YAML semantics required in this phase unless a narrower merge/refresh policy is later declared.
- Prompts: child startup prompt context will later consume refreshed parent-head truth; this phase is mainly runtime alignment.
- Tests: bounded stale-bootstrap detection and refresh-clearance coverage, plus real proof that dependent children start from updated parent ancestry.
- Performance: child refresh checks should remain cheap enough to run whenever parent merge state changes.
- Notes: document stale-bootstrap and refresh invariants so the runtime does not silently admit outdated children.

## Verification

- Bounded proof:
  - stale bootstrap detection
  - refresh-required blocker persistence
  - refresh clears blocker when successful
- Real proof:
  - dependent child starts from updated parent ancestry after prerequisite merge

## Exit Criteria

- dependent children no longer start from stale parent state
- refresh truth is durable and admission-safe
- this phase is an authoritative feature plan and not an implementation claim by itself
