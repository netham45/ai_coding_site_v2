# Task: Workflow Overhaul Authoritative Plan Family Breakdown

## Goal

Review the current workflow-overhaul future-plan bundle against the real repository code, tests, YAML assets, and authoritative notes, then produce a future-plan breakdown that shows how the bundle should eventually be promoted into an authoritative plan family with concrete implementation subtasks, missing contracts, dependencies, and proof surfaces.

## Rationale

- Rationale: The current `plan/future_plans/workflow_overhaul/draft/` bundle has useful direction and draft assets, but it is still idea-heavy and does not yet decompose cleanly into repo-standard implementation plans with code-grounded checklists.
- Reason for existence: This task exists to bridge the gap between the current future-plan notes and a later authoritative plan family by identifying the real code surfaces, contract gaps, and verification work each future slice would require.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/02_F01_configurable_node_hierarchy.md`
- `plan/features/07_F03_immutable_workflow_compilation.md`
- `plan/features/08_F05_default_yaml_library.md`
- `plan/features/37_F10_top_level_workflow_creation_commands.md`
- `plan/features/65_F04_layout_replacement_and_hybrid_reconciliation.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/future_plans/workflow_overhaul/2026-03-10_self_hosted_workflow_overhaul_notes.md`
- `plan/future_plans/workflow_overhaul/2026-03-10_proposed_note_and_code_updates.md`
- `plan/future_plans/workflow_overhaul/2026-03-10_workflow_profile_support_gap_closure.md`
- `plan/future_plans/workflow_overhaul/2026-03-10_workflow_profile_definition_schema_draft.md`
- `plan/future_plans/workflow_overhaul/2026-03-10_workflow_profile_route_design.md`
- `plan/future_plans/workflow_overhaul/2026-03-10_workflow_profile_e2e_coverage_matrix.md`
- `plan/reconcilliation/01_top_level_node_hierarchy_reconciliation.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/specs/yaml/yaml_schemas_spec_v2.md`
- `notes/specs/cli/cli_surface_spec_v2.md`

## Scope

- Database: review the current persistence model and identify what profile-related durable state and inspections would need authoritative contracts before implementation.
- CLI: review the existing parser and handler surfaces to determine which commands and flags would need real feature-plan coverage and what subtasks they imply.
- Daemon: review current startup, materialization, app, hierarchy, and workflow compilation surfaces so future-plan subtasks reflect the actual code structure.
- YAML: review schema and built-in hierarchy/layout assets to identify the real schema-family and validation work needed for workflow-profile adoption.
- Prompts: review the draft prompt bundle only enough to place prompt-selection and prompt-contract work into the right future slices.
- Tests: inspect existing unit, integration, and E2E surfaces to identify what new proving layers and mappings each future slice would require.
- Performance: identify any likely hot paths or inspection-heavy reads that need to be called out in future plan slices rather than treated as an afterthought.
- Notes: produce a future-plan artifact that can later be used to open authoritative feature plans with less ambiguity and less silent scope drift.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- a future-plan breakdown exists that decomposes workflow-overhaul into likely authoritative plan slices
- each slice lists real current code surfaces, missing contracts, implementation subtasks, dependencies, and verification expectations
- the breakdown is grounded in the actual repository rather than only restating the existing future-note bundle
- the required development log records the review inputs, files examined, and tests run
