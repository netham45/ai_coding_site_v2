# Phase F31: Daemon Authority And Durable Orchestration Record

## Goal

Make the daemon the live orchestration authority while keeping all critical state durable and inspectable.

## Rationale

- Rationale: The system depends on one live orchestration authority with durable state behind it; this phase establishes that authority boundary instead of letting CLI calls and database writes compete.
- Reason for existence: This phase exists to prevent split-brain orchestration, where runtime decisions, recovery behavior, and inspection surfaces diverge because no single component owns live mutations.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/04_F07_durable_node_lifecycle_state.md`: F07 durable lifecycle state consumes the authority model for legal transitions and recovery.
- `plan/features/13_F09_node_run_orchestration.md`: F09 run orchestration is executed under the daemon authority boundary defined here.
- `plan/features/15_F11_operator_cli_and_introspection.md`: F11 introspection depends on the durable orchestration record being queryable.
- `plan/features/57_F31_database_runtime_state_schema_family.md`: F31A is the concrete runtime-state schema slice for this feature.
- `plan/features/58_F31_database_session_attempt_history_schema_family.md`: F31B stores session and execution history needed by daemon authority and recovery.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/catalogs/inventory/major_feature_inventory.md`
- `notes/catalogs/traceability/spec_traceability_matrix.md`
- `notes/specs/architecture/authority_and_api_model.md`
- `notes/specs/database/database_schema_spec_v2.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/catalogs/audit/auditability_checklist.md`

## Scope

- Database: durable authority-related state, mutation history, current-state views.
- CLI: route mutating operations through the daemon instead of direct state mutation.
- Daemon: request validation, mutation authorization, durable-write sequencing, authoritative orchestration boundary.
- YAML: no new semantics beyond config/bootstrap references.
- Prompts: reserve prompt issuance linkage in orchestration records.
- Tests: exhaustively cover legal mutations, illegal mutations, race-sensitive writes, and recoverability.
- Performance: benchmark hot mutation and current-state read paths.
- Notes: update authority notes if implementation changes API/process assumptions.
