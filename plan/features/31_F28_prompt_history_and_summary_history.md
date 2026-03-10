# Phase F28: Prompt History And Summary History

## Goal

Persist prompts, prompt-template identity, and summaries as durable audit artifacts.

## Rationale

- Rationale: Prompt deliveries and summaries are part of the audit surface because they explain what the AI saw and what it reported back.
- Reason for existence: This phase exists to preserve prompt and summary lineage for later recovery, review, and provenance queries.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/13_F09_node_run_orchestration.md`: F09 determines when prompts are delivered and summaries are registered.
- `plan/features/15_F11_operator_cli_and_introspection.md`: F11 exposes the history surfaces that read these records.
- `plan/features/01_F31_daemon_authority_and_durable_orchestration_record.md`: F31 requires these artifacts to be stored durably under daemon control.
- `plan/features/35_F36_auditable_history_and_reproducibility.md`: F36 depends on prompt and summary history to reconstruct what happened.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/catalogs/inventory/major_feature_inventory.md`
- `notes/catalogs/traceability/spec_traceability_matrix.md`
- `notes/specs/database/database_schema_spec_v2.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/catalogs/vocabulary/state_value_catalog.md`
- `notes/specs/prompts/prompt_library_plan.md`

## Scope

- Database: prompt history, prompt roles, summary taxonomy, prompt-template identity.
- CLI: prompt list/show and summary history commands.
- Daemon: correct prompt issuance and summary registration timing.
- YAML: clean prompt references from compiled tasks and quality gates.
- Prompts: finalize prompt-pack roles, identity, and retrieval behavior.
- Tests: exhaustive prompt lineage, summary registration, role correctness, and historical retrieval coverage.
- Performance: benchmark prompt-history queries.
- Notes: update prompt and summary taxonomy notes if needed.
