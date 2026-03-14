# Task: User Documentation Governance Implementation

## Goal

Implement the first-class user-documentation governance model in the live repository by updating the doctrine, adding the documentation contract and starter `docs/` tree, extending flow/checklist/document-family surfaces, and adding bounded tests for the new rules.

## Rationale

- Rationale: The repository already has walkthroughs, scenario docs, and YAML `docs` assets, but it still lacks one explicit doctrine and schema model that treats user documentation as part of feature and flow completion.
- Reason for existence: This task exists to move the user-documentation governance work from planning into the actual authoritative repository surfaces without waiting for a future cleanup pass.

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
- `plan/doc_updates/05_user_documentation_first_class_system.md`
- `plan/doc_schemas/06_user_documentation_and_documentation_impact_schema.md`
- `notes/catalogs/checklists/authoritative_document_family_inventory.md`
- `notes/catalogs/checklists/document_schema_rulebook.md`
- `notes/catalogs/checklists/feature_checklist_standard.md`
- `notes/catalogs/traceability/relevant_user_flow_inventory.yaml`
- `notes/scenarios/walkthroughs/getting_started_hypothetical_task_guide.md`

## Scope

- Database: document when DB-backed user-visible or operator-visible behavior changes require docs updates, but do not alter runtime persistence.
- CLI: add documentation-governance rules for command and operator-surface changes and update authoritative command/docs references.
- Daemon: add documentation-governance rules for daemon-backed runtime and recovery surfaces, but do not alter runtime behavior.
- YAML: clarify the boundary between YAML `docs` assets and the user-facing documentation system; extend structured flow metadata as needed.
- Prompts: add documentation-governance rules for prompt-backed workflows where they are user-visible or operator-visible.
- Tests: add or update bounded document-schema tests covering the new doctrine, contract, docs tree, checklist standard, and flow-inventory documentation linkage.
- Performance: keep this batch at the documentation and schema layer only.
- Notes: update doctrine, README, checklist/docs standards, traceability notes, and implementation logs.

## Documentation Impact

- Status: required_update
- Affected documentation surfaces:
  - `README.md`
  - `docs/README.md`
  - `docs/user/README.md`
  - `docs/operator/README.md`
  - `docs/reference/README.md`
  - `docs/runbooks/README.md`
  - `notes/scenarios/journeys/common_user_journeys_analysis.md`
  - `notes/scenarios/walkthroughs/getting_started_hypothetical_task_guide.md`
- Rationale: this task establishes the documentation-governance model itself and must therefore update the authoritative documentation entrypoints and boundaries explicitly.

## Documentation Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_user_documentation_governance_docs.py tests/unit/test_relevant_user_flow_inventory.py tests/unit/test_notes_quickstart_docs.py -q
```

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_feature_checklist_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_verification_command_docs.py tests/unit/test_relevant_user_flow_inventory.py tests/unit/test_notes_quickstart_docs.py tests/unit/test_user_documentation_governance_docs.py -q
```

## Exit Criteria

- `AGENTS.md` recognizes user documentation as a first-class system and defines the maintenance boundary with `notes/`
- the repository contains a starter top-level `docs/` tree
- the authoritative document-family inventory, rulebook, and test policy recognize the user-documentation family and documentation-impact adoption posture
- the feature checklist standard and relevant-user-flow inventory explicitly link documentation impact
- the README and current onboarding docs point to the user-documentation governance boundary
- the bounded tests for the new documentation-governance surfaces pass and the development log records the actual results
