# Task: Relevant User Flow Inventory YAML Adoption

## Goal

Adopt an authoritative YAML-backed relevant user flow inventory under `notes/`, wire it into the existing flow doctrine, and add document/schema tests so flow relevance tracking is maintained as implementation work evolves.

## Rationale

- Rationale: The repo already has authoritative narrative flow specs in `flows/*.md`, but it does not have a structured note-family asset that tracks which user/operator flows are currently relevant, why they matter, what systems they touch, and what proof surfaces defend them.
- Reason for existence: This task exists to prevent the growing flow/checklist/traceability surfaces from drifting by adding one machine-validated YAML inventory under `notes/` instead of creating a second prose-only canonical flow registry.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/14_F10_ai_facing_cli_command_loop.md`
- `plan/features/37_F10_top_level_workflow_creation_commands.md`
- `plan/features/38_F10_stage_context_retrieval_and_startup_context.md`
- `plan/features/39_F12_tmux_session_manager.md`
- `plan/features/43_F05_prompt_pack_authoring.md`
- `plan/features/46_F10_ai_cli_bootstrap_and_work_retrieval_commands.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `flows/README.md`
- `notes/scenarios/journeys/common_user_journeys_analysis.md`
- `notes/catalogs/audit/flow_coverage_checklist.md`
- `notes/catalogs/traceability/simulation_flow_union_inventory.md`
- `notes/catalogs/checklists/authoritative_document_family_inventory.md`
- `notes/catalogs/checklists/document_schema_rulebook.md`
- `notes/planning/implementation/flow_yaml_schema_and_harness_decisions.md`

## Scope

- Database: not affected by this documentation-and-schema adoption slice.
- CLI: not directly affected, but the inventory must record CLI-facing entrypoints and proof commands where relevant.
- Daemon: not directly affected, but the inventory must remain aligned with daemon-owned runtime flow authority described in the notes.
- Website: not directly affected in this slice, but the inventory should still track website involvement for operator flows that span the browser surface.
- YAML: add a new authoritative YAML document family under `notes/` for structured relevant-flow tracking; do not collapse it into runtime workflow YAML.
- Prompts: not directly affected in this slice.
- Tests: extend document/schema coverage so the new inventory family is structurally validated and cross-checked against canonical flow docs.
- Performance: keep the inventory and tests lightweight so document validation remains fast in normal repo verification runs.
- Notes: amend `AGENTS.md`, document-family inventory/rulebook surfaces, and adjacent flow docs so the new YAML family has an explicit role and maintenance rule.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_flow_assets.py tests/unit/test_document_schema_docs.py tests/unit/test_notes_quickstart_docs.py tests/unit/test_flow_e2e_alignment_docs.py -q
PYTHONPATH=src python3 -m pytest tests/integration/test_flow_yaml_contract_suite.py -q
```

## Exit Criteria

- `AGENTS.md` explicitly requires relevant user/operator flow inventory updates when implementation changes affect flow relevance or boundaries
- a structured YAML inventory exists under `notes/` and records the current canonical runtime flow set with required metadata
- the authoritative document family inventory and schema rulebook recognize the new YAML family explicitly
- tests validate the new inventory family and cross-link it to the canonical `flows/*.md` documents
- required development log entries honestly record the work, commands run, and resulting status
