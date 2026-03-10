# Phase F11: Operator CLI And Introspection

## Goal

Provide operators with full visibility into state, history, and rationale.

## Rationale

- Rationale: The system is intentionally stateful and audit-heavy, so operators need first-class inspection surfaces rather than direct database spelunking.
- Reason for existence: This phase exists to expose runtime, history, lineage, and rationale in a way humans and tools can actually use during debugging and operations.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/01_F31_daemon_authority_and_durable_orchestration_record.md`: F31 provides the durable state the operator CLI inspects.
- `plan/features/35_F36_auditable_history_and_reproducibility.md`: F36 sets the inspection and audit bar for operator surfaces.
- `plan/features/48_F11_operator_structure_and_state_commands.md`: F11-S1 handles structure and current-state commands.
- `plan/features/49_F11_operator_history_and_artifact_commands.md`: F11-S2 handles history, artifacts, docs, and provenance commands.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/catalogs/inventory/major_feature_inventory.md`
- `notes/catalogs/traceability/spec_traceability_matrix.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/catalogs/traceability/action_automation_matrix.md`
- `notes/specs/database/database_schema_spec_v2.md`
- `notes/catalogs/audit/auditability_checklist.md`

## Scope

- Database: build read models for history and current-state inspection.
- CLI: node/tree/show, workflow, runs, prompts, summaries, sessions, blockers, merge, docs, provenance, and database-navigation commands.
- Daemon: serve or validate daemon-owned introspection surfaces.
- YAML: expose source versus resolved YAML.
- Prompts: prompt lineage inspection only.
- Tests: exhaustive command coverage for structure, history visibility, and edge cases.
- Performance: benchmark common inspection commands and tree rendering.
- Notes: update introspection notes if more surfaces prove necessary.
