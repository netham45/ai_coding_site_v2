# Phase DS-04: Logs And Operational Document Schema Family

## Goal

Define schema and enforcement rules for required development logs and other operational document families that record implementation activity.

## Rationale

- Rationale: If development logs become required artifacts, they also need a constrained structure so they remain useful instead of turning into unstructured journals.
- Reason for existence: This phase exists to keep development-operation logging compact, consistent, and machine-checkable.

## Related Features

Read these implementation plans for context and interaction boundaries:

- `plan/doc_schemas/00_document_schema_master_plan.md`
- `plan/doc_updates/00_repo_alignment_master_plan.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/planning/implementation/project_development_flow_doctrine.md`

## Scope

- Database: log schemas do not replace DB truth, but they must accurately reflect DB-affecting work where logged.
- CLI: logs should record canonical commands and command/test execution in a structured way.
- Daemon: logs should be able to record runtime-boundary work and blockers consistently.
- YAML: logs should be able to record changed authoritative doc families and schema impacts.
- Prompts: logs should support recording prompt/E2E impacts where applicable.
- Notes: define required log fields, allowed statuses, file naming, and directory layout.
- Tests: add family-level tests for required sections/fields/statuses and directory placement.
- Performance: keep log tests lightweight enough to run after doc changes.

## Work

- define required log file naming rules
- define required log folder layout under `notes/logs/`
- define required log sections or fields
- define allowed log status vocabulary
- define required command/test/result fields
- define optional but recommended fields
- add tests to enforce the log family structure

## Current DS-04 Outputs

- log-family adoption is explicitly marked deferred in `notes/catalogs/checklists/authoritative_document_family_inventory.md`
- deferred log-family rules are recorded in `notes/catalogs/checklists/document_schema_rulebook.md`

## Canonical Verification Command

```bash
python3 -m pytest tests/unit/test_document_schema_docs.py
```

## Exit Criteria

- required development logs have an enforceable schema
- missing or malformed required log entries become mechanically detectable
- the logging doctrine remains compact rather than devolving into free-form prose
