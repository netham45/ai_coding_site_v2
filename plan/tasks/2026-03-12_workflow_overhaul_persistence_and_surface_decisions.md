# Task: Workflow Overhaul Persistence And Surface Decisions

## Goal

Turn the current workflow-overhaul planning questions around profile persistence, layout selection timing, compiled-state freezing, database storage shape, top-level parentless built-ins, operator inspection surfaces, workflow brief scope, and prompt-bundle promotion into explicit future-plan decisions grounded in the current codebase.

## Rationale

- Rationale: The workflow-overhaul breakdown identified several open planning questions, but leaving them open would make later authoritative plans too ambiguous and would force repeated re-analysis of the same runtime and database boundaries.
- Reason for existence: This task exists to capture the user's decisions and the resulting implementation-direction guidance in the future-plan notes before any authoritative implementation plans are opened.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/02_F01_configurable_node_hierarchy.md`
- `plan/features/07_F03_immutable_workflow_compilation.md`
- `plan/features/37_F10_top_level_workflow_creation_commands.md`
- `plan/features/65_F04_layout_replacement_and_hybrid_reconciliation.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/future_plans/workflow_overhaul/2026-03-10_self_hosted_workflow_overhaul_notes.md`
- `plan/future_plans/workflow_overhaul/2026-03-10_proposed_note_and_code_updates.md`
- `plan/future_plans/workflow_overhaul/2026-03-10_workflow_profile_support_gap_closure.md`
- `plan/future_plans/workflow_overhaul/2026-03-12_authoritative_plan_family_breakdown.md`
- `notes/specs/database/database_schema_spec_v2.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `src/aicoding/db/models.py`

## Scope

- Database: review current durable models and define the future intended split between first-class columns and compiled JSON payloads for workflow-profile state.
- CLI: define the intended split between global catalog surfaces and richer node-context inspection surfaces.
- Daemon: define where startup, materialization, and compile should own workflow-profile decisions.
- YAML: preserve the future built-in parentless rule and profile applicability shape.
- Prompts: define whether prompt-pack adoption should be piecemeal or bundled in the future authoritative plan family.
- Tests: update future-plan notes so later implementation slices know which decisions are already fixed and which proof surfaces they imply.
- Performance: bias the storage and API-shape decisions toward stable selectors in columns and richer evolving payloads in compiled JSON.
- Notes: add or update future-plan notes so these decisions are durable and reviewable.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- the workflow-overhaul future-plan bundle records explicit decisions for profile persistence, layout timing, compiled-state freezing, DB storage, parentless built-ins, operator surfaces, workflow brief scope, and prompt-bundle promotion
- the breakdown note is updated so those items no longer read as fully open questions
- the required development log records the reviewed files, commands run, and results
