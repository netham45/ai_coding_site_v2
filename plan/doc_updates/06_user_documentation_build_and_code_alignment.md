# Phase DU-06: User Documentation Build And Code Alignment

## Goal

Build the first real user/operator documentation set under `docs/` and verify that those docs stay aligned with the live code, command surfaces, configuration model, and relevant runtime flows.

## Rationale

- Rationale: The repository now has a first-class documentation-governance model, but that model is still mostly structural until the `docs/` tree contains real content tied to actual code and runtime flows.
- Reason for existence: This phase exists to replace transitional walkthrough ambiguity with real user/operator docs and to make those docs provable against the current implementation rather than relying on prose review alone.

## Related Features

Read these implementation plans for context and interaction boundaries:

- `plan/features/14_F10_ai_facing_cli_command_loop.md`
- `plan/features/15_F11_operator_cli_and_introspection.md`
- `plan/features/37_F10_top_level_workflow_creation_commands.md`
- `plan/features/39_F12_tmux_session_manager.md`
- `plan/features/66_F05_execution_orchestration_and_result_capture.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `README.md`
- `notes/specs/product/user_documentation_contract.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/catalogs/traceability/relevant_user_flow_inventory.yaml`
- `notes/scenarios/journeys/common_user_journeys_analysis.md`
- `notes/scenarios/walkthroughs/getting_started_hypothetical_task_guide.md`
- `notes/planning/implementation/project_development_flow_doctrine.md`

## Scope

- Database: document only behavior and operational expectations that are genuinely user-visible or operator-visible, and verify any documented DB-related commands or states against the real code and canonical command catalog.
- CLI: build reference and workflow docs around the actual CLI command surface and add tests that prove documented commands and flags exist.
- Daemon: build operator and runbook docs around the daemon-backed runtime surface and verify documented startup, inspection, and recovery claims against the real code and current authoritative notes.
- YAML: document the user-visible role of YAML-backed workflow behavior where needed, and verify any documented YAML/config claims against the current schema and inventory surfaces.
- Prompts: document prompt-backed workflow touchpoints only where users or operators are expected to understand them, and verify those claims against current prompt/runtime contracts.
- Tests: add bounded documentation-alignment tests that compare docs with the real CLI/config/flow/code surfaces.
- Performance: keep documentation verification lightweight and deterministic so it remains part of the bounded document-proof layer.
- Notes: migrate or reclassify transitional `notes/scenarios/` material deliberately instead of leaving duplicate guidance surfaces unmanaged.

## Work Streams

1. Build the first real docs set under `docs/`.
2. Migrate or supersede the current transitional walkthroughs in `notes/scenarios/`.
3. Add machine-checkable linkage from docs to the code and flow surfaces they describe.
4. Add bounded alignment tests that fail when docs drift from the real command/config/runtime surface.

## Initial Documentation Targets

- `docs/user/getting-started.md`
- `docs/operator/first-live-run.md`
- `docs/operator/inspect-state-and-blockers.md`
- `docs/reference/cli.md`
- `docs/reference/configuration.md`
- `docs/runbooks/pause-resume-recovery.md`
- `docs/runbooks/failure-escalation.md`

## Initial Verification Targets

- CLI command docs vs real CLI command paths and options
- configuration docs vs real settings/env-variable model
- flow docs vs `notes/catalogs/traceability/relevant_user_flow_inventory.yaml`
- runbook commands vs real command surfaces and runtime vocabulary
- onboarding docs vs canonical verification command catalog and current supported bootstrap path

## Documentation Metadata Strategy

Prefer lightweight machine-checkable metadata in each real doc, such as frontmatter or a compact header block, so tests can verify:

- doc type
- covered flow ids
- referenced command surfaces
- referenced config/env keys
- bounded verification command
- backing real E2E target where applicable

## Current DU-06 Outputs

- planned first-pass docs set under `docs/`
- planned migration path for `notes/scenarios/` walkthroughs
- planned bounded documentation-alignment tests for CLI, configuration, flow mapping, and runbook alignment

## Canonical Verification Command

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_user_documentation_governance_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_notes_quickstart_docs.py -q
```

## Exit Criteria

- the repository has a first real docs set under `docs/` covering onboarding, operator flows, references, and runbooks for the current supported scope
- each new doc names the code, command, config, or flow surfaces it is supposed to match
- bounded tests exist that compare those docs with the current implementation surface
- transitional `notes/scenarios/` docs are either migrated, superseded, or explicitly retained with a documented reason
- the canonical docs entrypoints point readers to the new docs rather than to stale transitional walkthroughs
