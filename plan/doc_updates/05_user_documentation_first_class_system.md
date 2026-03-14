# Phase DU-05: User Documentation First-Class System Adoption

## Goal

Adopt user and operator documentation as a first-class governed system in the repository so plans, checklists, flow traceability, and canonical docs stop treating documentation updates as an implicit side effect of note maintenance.

## Rationale

- Rationale: The repository already has walkthroughs, command-entry docs, scenario notes, and YAML `docs` assets, but they are governed inconsistently and are not part of the declared primary-system model.
- Reason for existence: This phase exists to make user documentation impact explicit whenever features, flows, commands, setup steps, or recovery paths change.

## Related Features

Read these implementation plans for context and interaction boundaries:

- `plan/features/14_F10_ai_facing_cli_command_loop.md`
- `plan/features/37_F10_top_level_workflow_creation_commands.md`
- `plan/features/39_F12_tmux_session_manager.md`
- `plan/features/66_F05_execution_orchestration_and_result_capture.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `README.md`
- `notes/catalogs/checklists/feature_checklist_standard.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/catalogs/traceability/relevant_user_flow_inventory.yaml`
- `notes/scenarios/journeys/common_user_journeys_analysis.md`
- `notes/scenarios/walkthroughs/getting_started_hypothetical_task_guide.md`
- `notes/planning/implementation/project_development_flow_doctrine.md`

## Scope

- Database: define when DB-backed user-visible or operator-visible behavior changes require documentation updates, but do not alter runtime schema in this phase.
- CLI: define how command-surface changes, examples, and operator procedures must link to authoritative documentation surfaces.
- Daemon: define how runtime behavior, recovery posture, and daemon-backed operator flows map to user/operator docs.
- YAML: distinguish machine-readable `docs` YAML assets from the consumer-facing documentation system and define how they relate.
- Prompts: define when prompt-backed workflows or prompt-surface changes require documentation updates.
- Tests: plan the bounded document-schema and family tests required to enforce the new documentation obligations.
- Performance: keep this phase at the governance and planning layer; do not widen it into runtime or frontend implementation work.
- Notes: update doctrine, README, checklist standards, traceability notes, and documentation-family notes so user documentation becomes explicit.

## Work

- extend the core doctrine to recognize user documentation as a declared primary system alongside database, CLI, daemon, YAML, prompts, and website UI
- define the authoritative boundary between:
  - `notes/` as governance/spec/traceability artifacts
  - `docs/` as user-facing and operator-facing documentation
  - `notes/scenarios/` as either transitional or still-authoritative documentation until migrated
  - YAML `docs` assets as machine-readable documentation definitions rather than the whole documentation system
- require every meaningful task and feature plan to record one of:
  - documentation update required
  - documentation reviewed with no change required
  - documentation not applicable
- require feature checklist entries and relevant-flow traceability entries to name documentation impact explicitly
- update the README and current onboarding surface so contributors can find the authoritative documentation boundary without inferring it
- define the follow-up migration posture for existing walkthroughs and scenario docs rather than silently leaving them in an ambiguous role

## Current DU-05 Outputs

- planned doctrine updates in `AGENTS.md`
- a future user-documentation contract note under `notes/`
- a future top-level `docs/` tree with audience-oriented subdirectories
- updated checklist, traceability, and README guidance naming documentation impact explicitly

## Canonical Verification Command

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_feature_checklist_docs.py tests/unit/test_notes_quickstart_docs.py -q
```

## Exit Criteria

- the repository doctrine names user documentation as a first-class system
- the authoritative boundary among `docs/`, `notes/`, `notes/scenarios/`, and YAML `docs` assets is explicit
- task plans, feature plans, and checklists all require an explicit documentation-impact decision
- relevant user-flow tracking names documentation impact and affected documentation surfaces
- the canonical README and onboarding docs point contributors to the documentation-governance surface instead of leaving it implicit
