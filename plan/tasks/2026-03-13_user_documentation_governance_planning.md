# Task: User Documentation Governance Planning

## Goal

Create the authoritative plan artifacts for adopting user documentation as a first-class system in the live repository, including the doc-update phase plan and the corresponding document-schema phase plan.

## Rationale

- Rationale: The repository already has scenario walkthroughs, command-entry docs, and YAML `docs` assets, but the governance layer still lacks one explicit plan for making documentation impact part of the core system and schema model.
- Reason for existence: This task exists to capture the required doctrine, schema, and traceability work as governed plan artifacts before implementation edits begin.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/14_F10_ai_facing_cli_command_loop.md`
- `plan/features/37_F10_top_level_workflow_creation_commands.md`
- `plan/features/39_F12_tmux_session_manager.md`
- `plan/features/66_F05_execution_orchestration_and_result_capture.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `README.md`
- `notes/catalogs/checklists/authoritative_document_family_inventory.md`
- `notes/catalogs/checklists/document_schema_rulebook.md`
- `notes/catalogs/checklists/feature_checklist_standard.md`
- `notes/catalogs/traceability/relevant_user_flow_inventory.yaml`
- `notes/scenarios/walkthroughs/getting_started_hypothetical_task_guide.md`

## Scope

- Database: capture the planning posture for documentation obligations when DB-backed behavior is exposed to users or operators, without changing runtime persistence.
- CLI: capture the planning posture for command-surface documentation requirements and examples.
- Daemon: capture the planning posture for runtime, recovery, and operator-surface documentation obligations.
- YAML: capture the planning posture that distinguishes YAML `docs` assets from authoritative user documentation surfaces.
- Prompts: capture the planning posture for prompt-backed workflow documentation obligations.
- Tests: run the bounded task-plan and document-schema tests that enforce these planning families.
- Performance: keep this batch at the planning/document-governance layer only.
- Notes: add the new doc-update and doc-schema plans, update the plan indexes, and record the planning work in the development log.

## Documentation Impact

- Status: required_update
- Affected documentation surfaces:
  - `README.md`
  - `docs/README.md`
  - `notes/specs/product/user_documentation_contract.md`
- Rationale: the planning batch establishes the documentation-governance rollout itself and therefore changes the authoritative documentation boundary.

## Documentation Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_user_documentation_governance_docs.py tests/unit/test_task_plan_docs.py -q
```

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- `plan/doc_updates/` contains a governed phase plan for adopting user documentation as a first-class system
- `plan/doc_schemas/` contains a governed phase plan for the required schema and document-test changes
- the relevant plan-family README indexes reference the new plans
- the development log records the work and the bounded verification result honestly
