# Phase F07: Durable Node Lifecycle State

## Goal

Persist lifecycle and cursor state durably and enforce legal transitions.

## Rationale

- Rationale: Resumable orchestration only works if lifecycle state and cursor position are durable, legal, and inspectable at every transition.
- Reason for existence: This phase exists because lifecycle behavior cannot live in process memory or terminal context if pause, recovery, and auditing are supposed to be reliable.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/01_F31_daemon_authority_and_durable_orchestration_record.md`: F31 defines who owns live lifecycle mutations.
- `plan/features/05_F02_node_versioning_and_supersession.md`: F02 changes how lifecycle state behaves across superseded versions.
- `plan/features/13_F09_node_run_orchestration.md`: F09 advances lifecycle state during execution.
- `plan/features/29_F24_user_gating_and_pause_flags.md`: F24 adds pause states and gating behavior onto the lifecycle model.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/catalogs/inventory/major_feature_inventory.md`
- `notes/catalogs/traceability/spec_traceability_matrix.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/specs/database/database_schema_spec_v2.md`
- `notes/catalogs/vocabulary/state_value_catalog.md`
- `notes/pseudocode/state_machines/node_lifecycle.md`

## Scope

- Database: node/run lifecycle fields, cursor state, bounded vocabularies.
- CLI: lifecycle and current-state inspection surfaces.
- Daemon: legal transition enforcement and invariant checks.
- YAML: policy inputs only; no YAML-owned transition logic.
- Prompts: lifecycle-linked pause/failure hooks only.
- Tests: exhaustive legal/illegal transition coverage plus resume-safe cursor persistence.
- Performance: benchmark current-state lookups and transition writes.
- Notes: document lifecycle edge cases discovered during implementation.
