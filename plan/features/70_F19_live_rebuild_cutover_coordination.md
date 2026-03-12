# Phase F19-S1: Live Rebuild Cutover Coordination

## Goal

Coordinate regeneration and cutover safely when active runs, sessions, or other live runtime state still exist.

## Rationale

- Rationale: Regeneration and upstream rectification already persist rebuild lineage, but Flow 10 still stops short of a richer live coordination contract for active runs and candidate cutover.
- Reason for existence: This phase exists to make rebuild and cutover safe under live conditions instead of leaving the runtime conservative but under-specified.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/24_F19_regeneration_and_upstream_rectification.md`: F19 introduced durable rebuild events and rebuild lineage.
- `plan/features/05_F02_node_versioning_and_supersession.md`: F02 owns cutover mechanics that live rebuild coordination must protect.
- `plan/features/16_F12_session_binding_and_resume.md`: F12 provides active session ownership that rebuild coordination must not silently violate.
- `plan/features/35_F36_auditable_history_and_reproducibility.md`: F36 must remain able to reconstruct rebuild and cutover decisions.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/specs/git/git_rectification_spec_v2.md`
- `notes/contracts/runtime/cutover_policy_note.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/specs/database/database_schema_spec_v2.md`
- `notes/specs/runtime/tmux_session_lifecycle_spec_v1.md#recovery-classification-and-actions`
- `notes/planning/implementation/per_flow_gap_remediation_plan.md`

## Scope

- Database: persist any additional live-conflict, cutover-block, or rebuild-coordination records required to explain why cutover is blocked or allowed.
- CLI: extend the existing rebuild, cutover-readiness, and rebuild-coordination reads with replay-specific blockers, required-scope detail, and authoritative-baseline drift rather than inventing parallel surfaces.
- Daemon: implement live rebuild coordination rules for active runs, active sessions, and cutover safety.
- YAML: keep rebuild coordination and cutover safety code-owned rather than declarative.
- Prompts: update rebuild, rectification, and intervention prompts if live coordination introduces new operator choices.
- Tests: exhaustively cover rebuild while runs are active, rebuild while sessions are attached, blocked cutover, resumed cutover, and audit reconstruction.
- Performance: benchmark rebuild-history and cutover-read paths under larger lineages and repeated rebuild attempts.
- Notes: update regeneration, cutover, recovery, and audit notes to reflect the live coordination rules.

## Canonical CLI Surfaces

- `node rectify-upstream --node <id>`
- `node rebuild-history --node <id>`
- `rebuild show --node <id>`
- `node rebuild-coordination --node <id> --scope upstream`
- `node version cutover-readiness --version <candidate_version_id>`
- `node version cutover --version <candidate_version_id>`
- `git merge-events show --node <id>` or candidate-version scoped equivalent
- `git merge-conflicts show --version <candidate_version_id>`

## Required Live Coordination Decisions

- Cutover readiness must expose an explicit blocker vocabulary rather than a generic blocked/not-blocked answer.
- The live blocker set must include active authoritative runs, active authoritative primary sessions, candidate replay incompleteness, candidate merge conflicts, required-scope instability, approval gates, candidate supersession, and authoritative-baseline drift.
- Candidate cutover must not auto-proceed if the authoritative lineage changed after candidate rebuild started unless a later explicit override policy is documented.
- The proving path for this phase should use the canonical CLI surfaces above rather than daemon-only internal inspection.
