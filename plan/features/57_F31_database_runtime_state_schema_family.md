# Phase F31A: Database Runtime State Schema Family

## Goal

Implement the PostgreSQL schema family for live orchestration state.

## Rationale

- Rationale: Daemon authority needs a normalized PostgreSQL schema for live orchestration state rather than ad hoc tables or overloaded history records.
- Reason for existence: This phase exists to define the durable runtime-state backbone the scheduler, CLI, and lifecycle rules all read from.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/01_F31_daemon_authority_and_durable_orchestration_record.md`: F31 is the parent authority feature for this schema family.
- `plan/features/04_F07_durable_node_lifecycle_state.md`: F07 uses these tables to represent live lifecycle state.
- `plan/features/11_F08_dependency_graph_and_admission_control.md`: F08 uses runtime-state records for blockers and readiness.
- `plan/features/13_F09_node_run_orchestration.md`: F09 executes against this runtime-state schema.
- `plan/features/58_F31_database_session_attempt_history_schema_family.md`: F31B complements this schema with session and history records.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/specs/database/database_schema_spec_v2.md`
- `notes/planning/expansion/database_schema_v2_expansion.md`
- `notes/catalogs/vocabulary/state_value_catalog.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/specs/architecture/authority_and_api_model.md`

## Scope

- Database: define tables, constraints, indexes, and migrations for nodes, node relationships, lifecycle state, dependency state, run admission, run state, pause flags, and rebuild eligibility.
- CLI: expose read paths needed to inspect runtime state cleanly.
- Daemon: use these records as the authoritative source for scheduling and state-transition legality.
- YAML: no new YAML semantics beyond aligning runtime state names with compiled workflow expectations.
- Prompts: no direct prompt semantics beyond ensuring prompt stages map cleanly onto stored runtime state.
- Tests: exhaustively test valid state creation, illegal transitions, dependency blocking, pause semantics, rebuild eligibility, and every persistence rule.
- Performance: benchmark hot runtime reads and write-heavy transition paths.
- Notes: update runtime/database notes if the live state model needs stricter normalization or additional state categories.

## Exit Criteria

- the live orchestration state model is explicit, durable, indexed, and fully test-backed.
