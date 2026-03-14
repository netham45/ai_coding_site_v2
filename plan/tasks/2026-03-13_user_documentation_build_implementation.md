# Task: User Documentation Build Implementation

## Goal

Author the first real docs under `docs/`, link those docs to the current flow inventory, and add bounded tests that verify the new docs against the live CLI, config, and flow surfaces.

## Rationale

- Rationale: The repository has a documentation-governance model and a docs build plan, but it still needs the first concrete docs set plus code-alignment tests to make that governance useful.
- Reason for existence: This task exists to turn the `docs/` tree into a real user/operator surface and prove that the first docs batch matches the live implementation.

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
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/catalogs/traceability/relevant_user_flow_inventory.yaml`
- `notes/scenarios/walkthroughs/getting_started_hypothetical_task_guide.md`

## Scope

- Database: document and verify only the DB-facing setup and inspection claims that are currently user-visible or operator-visible, without changing runtime persistence code.
- CLI: author reference and workflow docs around the current CLI surface and verify documented command paths against the real argparse parser.
- Daemon: author operator/runbook docs for daemon-backed runtime inspection and recovery paths without changing runtime behavior.
- YAML: keep documentation claims aligned with the structured relevant-flow inventory and clarify only the currently user-visible YAML role.
- Prompts: document prompt-backed inspection touchpoints only where they are directly user-visible or operator-visible.
- Tests: add bounded docs-vs-code alignment tests for CLI command paths, configuration fields, and flow-id mapping.
- Performance: keep the new documentation tests lightweight and deterministic.
- Notes: update the docs entrypoint, relevant flow inventory surfaces, verification catalog, and development log.

## Documentation Impact

- Status: required_update
- Affected documentation surfaces:
  - `docs/README.md`
  - `docs/user/getting-started.md`
  - `docs/operator/first-live-run.md`
  - `docs/operator/inspect-state-and-blockers.md`
  - `docs/reference/cli.md`
  - `docs/reference/configuration.md`
  - `docs/runbooks/pause-resume-recovery.md`
  - `notes/scenarios/walkthroughs/getting_started_hypothetical_task_guide.md`
  - `notes/catalogs/traceability/relevant_user_flow_inventory.yaml`
- Rationale: this task creates the first real docs set and therefore must update both the user-facing docs and the structured linkage surfaces that govern them.

## Documentation Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_docs_code_alignment.py tests/unit/test_user_documentation_governance_docs.py tests/unit/test_relevant_user_flow_inventory.py tests/unit/test_notes_quickstart_docs.py -q
```

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_feature_checklist_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_verification_command_docs.py tests/unit/test_relevant_user_flow_inventory.py tests/unit/test_notes_quickstart_docs.py tests/unit/test_user_documentation_governance_docs.py tests/unit/test_docs_code_alignment.py -q
```

## Exit Criteria

- the first real docs set exists under `docs/` for getting started, operator flows, reference material, and pause/resume recovery
- each authored doc carries machine-checkable metadata linking it to live CLI/config/flow surfaces
- the relevant flow inventory names the new docs where appropriate
- bounded docs-vs-code tests pass for the new docs
- the verification catalog names the docs-vs-code test command explicitly
