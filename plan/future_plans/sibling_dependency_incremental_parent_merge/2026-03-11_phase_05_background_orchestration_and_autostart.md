# Phase 05 Draft: Background Orchestration And Autostart Wiring

## Goal

Run the parent incremental-merge lane automatically in the daemon and let the existing child auto-start loop consume the resulting `READY` children.

## Rationale

- Rationale: The feature is not operationally meaningful until the daemon can process parent merge lanes continuously and let dependent siblings unblock without manual babysitting.
- Reason for existence: This phase exists to wire the incremental merge lane into the live daemon background runtime while keeping child auto-start constrained to already-ready children.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/13_F09_node_run_orchestration.md`: background orchestration must remain consistent with existing run advancement behavior.
- `plan/features/12_F17_deterministic_branch_model.md`: repeated background merges and child starts must preserve deterministic parent ancestry.
- `plan/features/20_F15_child_node_spawning.md`: child auto-start behavior remains a direct dependency of this phase.
- `plan/features/64_F08_F15_richer_child_scheduling_and_blocker_explanation.md`: the background path should eventually surface richer scheduling explanation without contradiction.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/contracts/parent_child/child_materialization_and_scheduling.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`
- `plan/future_plans/sibling_dependency_incremental_parent_merge/2026-03-11_overview.md`

## Scope

- Database: background lane processing must respect durable merge-lane and blocker state.
- CLI: operator reads should eventually reflect background lane progress, but command-surface expansion is not the primary goal here.
- Daemon: wire the parent merge lane into background scan processing and keep child auto-start limited to children already made ready by merge-backed truth.
- YAML: no new declarative behavior in this phase; the daemon wiring remains code-owned.
- Prompts: no additional happy-path parent prompts; ordinary lane processing remains daemon-owned.
- Tests: integration proof that background merge processing and child auto-start cooperate correctly, plus real daemon-runtime happy-path coverage.
- Performance: background scanning and lane processing must stay cheap enough for repeated daemon ticks and avoid unnecessary full-tree rescans.
- Notes: revise runtime doctrine so the background daemon path, not the parent AI, owns the happy path, and define how parent pause/cancel stops incremental merge progression without erasing durable merge history.

## Verification

- Bounded proof:
  - background worker processes pending merge lanes
  - child auto-start loop does not bypass merge-backed readiness
- Real proof:
  - child completion triggers parent merge and then dependent-child autostart through real daemon runtime flow

## Exit Criteria

- happy-path orchestration works end to end without parent AI involvement
- the child auto-start loop remains narrow and does not own merge policy
- this phase remains a future-plan draft and is not an implementation claim by itself
