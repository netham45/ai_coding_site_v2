# Feature 27: Templated Task Generation Note And Code Update Reconciliation

## Goal

Reconcile note, command, checklist, and code-update expectations around templated task generation so the future plan stays aligned with the actual implementation path.

## Main Work

- align notes with template-driven generation
- remove checklist-runtime language from active planning
- define the documentation and command surfaces the new model will need

## Implementation Subtasks

- update workflow-overhaul future-plan notes to use template-generation language consistently
- identify which authoritative notes need revision when implementation starts
- align command, proving, and checklist surfaces with generated-task narratives
- keep historical checklist drafts clearly marked as superseded rather than silently active

## Main Dependencies

- Setup 03
- Features 08 through 16

## Flows Touched

- `02_compile_or_recompile_workflow_flow`
- `06_inspect_state_and_blockers_flow`

## Relevant Current Code

- `notes/`
- `plan/future_plans/workflow_overhaul/`
- `notes/catalogs/checklists/verification_command_catalog.md`

## Current Gaps

- the workflow-overhaul bundle still contains active-seeming checklist-runtime planning documents
- note and command reconciliation for template-driven generation has not yet been authored
