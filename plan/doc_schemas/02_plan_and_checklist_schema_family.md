# Phase DS-02: Plan And Checklist Schema Family

## Goal

Define schema and enforcement rules for plan documents and checklist documents, including the newer per-feature per-system checklist surface.

## Rationale

- Rationale: Plans and checklists are among the highest-value authoritative docs in this repo because they govern implementation order, completion criteria, and status claims.
- Reason for existence: This phase exists to make plan and checklist drift mechanically detectable instead of review-only.

## Related Features

Read these implementation plans for context and interaction boundaries:

- `plan/features/README.md`
- `plan/checklists/04_test_coverage_and_release_readiness.md`
- `plan/doc_updates/01_feature_checklist_system_and_backfill.md`
- `plan/doc_schemas/01_authoritative_document_family_inventory.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/README.md`
- `notes/planning/implementation/project_development_flow_doctrine.md`

## Scope

- Database: plan/checklist schemas must support explicit DB status tracking where features affect the database.
- CLI: plan/checklist schemas must support CLI/API status and command tracking.
- Daemon: plan/checklist schemas must support daemon/runtime status and proving commands.
- YAML: plan/checklist schemas must support YAML/schema status where applicable.
- Prompts: plan/checklist schemas must support prompt status and prompt-related proving fields where applicable.
- Notes: define the required plan and checklist section structure and status field structure.
- Tests: add family-level tests for section presence, allowed values, required references, and required mapping fields.
- Performance: keep schema tests focused on structure and consistency, not fragile prose text.

## Work

- define required sections for:
  - setup plans
  - feature plans
  - verification checklists
  - feature checklists
  - update-test plans
  - E2E plans
  - doc-schema plans
- define required status fields and allowed status vocabulary
- define required affected-systems coverage fields
- define required canonical command fields or sections where applicable
- define required E2E target/status fields where applicable
- define required checklist linkage where applicable
- add or expand tests to enforce these rules

## Current DS-02 Outputs

- `notes/catalogs/checklists/document_schema_rulebook.md`
- plan/checklist family enforcement in `tests/unit/test_document_schema_docs.py`

## Canonical Verification Command

```bash
python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_feature_plan_docs.py tests/unit/test_feature_checklist_docs.py
```

## Exit Criteria

- plan/checklist families have explicit schema rules
- feature checklist format is enforceable by tests
- status and command drift in plans/checklists becomes mechanically detectable
