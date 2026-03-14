# Task: User Documentation Build Planning

## Goal

Add the authoritative plan artifact for building the first real `docs/` set and verifying that those docs remain aligned with the live code and flow surfaces.

## Rationale

- Rationale: The repository now has documentation-governance doctrine and schema adoption, but it still needs one explicit implementation plan for the actual documentation content and code-alignment verification work.
- Reason for existence: This task exists to turn the proposed docs-build and docs-vs-code verification work into a governed repository plan before implementation starts.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/14_F10_ai_facing_cli_command_loop.md`
- `plan/features/15_F11_operator_cli_and_introspection.md`
- `plan/features/37_F10_top_level_workflow_creation_commands.md`
- `plan/features/39_F12_tmux_session_manager.md`
- `plan/features/66_F05_execution_orchestration_and_result_capture.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `README.md`
- `plan/doc_updates/06_user_documentation_build_and_code_alignment.md`
- `notes/specs/product/user_documentation_contract.md`
- `notes/catalogs/checklists/document_schema_rulebook.md`
- `notes/catalogs/traceability/relevant_user_flow_inventory.yaml`
- `notes/scenarios/walkthroughs/getting_started_hypothetical_task_guide.md`

## Scope

- Database: capture the planning posture for any docs that describe DB-backed setup or inspection behavior, without changing runtime persistence.
- CLI: capture the planning posture for CLI reference docs and command-alignment tests.
- Daemon: capture the planning posture for daemon/operator docs and runtime/runbook verification.
- YAML: capture the planning posture for documentation claims that depend on YAML-backed behavior or machine-readable docs assets.
- Prompts: capture the planning posture for prompt-backed workflow docs where those surfaces are user-visible or operator-visible.
- Tests: run the task-plan and document-schema verification surfaces for the new planning artifact.
- Performance: keep this batch at the planning layer only.
- Notes: add the new doc-update phase plan, update the plan index, and record the work in the development log.

## Documentation Impact

- Status: required_update
- Affected documentation surfaces:
  - `docs/README.md`
  - `notes/specs/product/user_documentation_contract.md`
  - `plan/doc_updates/06_user_documentation_build_and_code_alignment.md`
- Rationale: this planning batch defines the next documentation implementation wave and therefore changes the authoritative documentation-governance surface.

## Documentation Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_user_documentation_governance_docs.py tests/unit/test_task_plan_docs.py -q
```

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- `plan/doc_updates/` contains a governed phase plan for building the first real docs set and verifying it against the live code
- the doc-update plan index references the new phase
- the governing development log records the planning work and verification result honestly
