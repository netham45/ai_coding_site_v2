# Feature 23: Workflow-Overhaul Note And Code Update Reconciliation

## Goal

Make the workflow-overhaul note/code-update bundle executable by turning its broad repo-change inventory into a tracked implementation slice.

## Main Work

- reconcile which authoritative notes, inventories, and supporting assets must change as workflow-profile work lands
- keep note updates coupled to implementation rather than relying on a one-time umbrella note
- prevent workflow-overhaul code from landing without its adjacent note maintenance work

## Implementation Subtasks

- define the note families that must update when workflow-profile runtime, prompts, or flows change
- define the checklist and development-log maintenance expectations for workflow-overhaul implementation slices
- map code surfaces to their required note updates so plan execution can track them explicitly
- document the minimal repo-wide note update batch that must accompany each major workflow-profile runtime milestone

## Main Dependencies

- Setup 00
- Setup 03
- Feature 01
- Feature 05
- Feature 06

## Flows Touched

- touches all workflow-overhaul-affected flows indirectly by constraining note maintenance and verification behavior

## Relevant Current Code

- `tests/unit/test_task_plan_docs.py`
- `tests/unit/test_document_schema_docs.py`
- `notes/catalogs/checklists/authoritative_document_family_inventory.md`
- `notes/catalogs/checklists/document_schema_rulebook.md`

## Current Gaps

- the future-plan bundle had a proposed note/code-update note, but the draft queue did not have a standalone execution slice for reconciling those updates
- current workflow-overhaul planning still depends on manual cross-reading of support notes rather than one explicit reconciliation slice
