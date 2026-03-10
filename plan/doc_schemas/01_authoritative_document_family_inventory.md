# Phase DS-01: Authoritative Document Family Inventory

## Goal

Inventory all authoritative document families in the repository and define which schema and testing rules apply to each.

## Rationale

- Rationale: Document schema enforcement cannot be implemented coherently until the repository has one explicit inventory of which document families are authoritative.
- Reason for existence: This phase exists to prevent over-scoping exploratory notes and under-scoping implementation-control notes.

## Related Features

Read these implementation plans for context and interaction boundaries:

- `plan/doc_schemas/00_document_schema_master_plan.md`
- `plan/doc_updates/01_feature_checklist_system_and_backfill.md`
- `plan/doc_updates/03_flow_traceability_and_e2e_status_alignment.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/catalogs/inventory/major_feature_inventory.md`
- `notes/catalogs/traceability/spec_traceability_matrix.md`
- `notes/catalogs/audit/auditability_checklist.md`
- `notes/planning/implementation/project_development_flow_doctrine.md`

## Scope

- Database: include document families that make DB-backed claims or status assertions.
- CLI: include command/reference-bearing families.
- Daemon: include runtime/flow/status-bearing families.
- YAML: include schema, library, and declarative tracking families.
- Prompts: include prompt pack, prompt mapping, and prompt/runtime contract families where authoritative.
- Notes: classify which note families are authoritative versus exploratory/archive-only.
- Tests: identify which current tests already partially cover each family and where gaps remain.
- Performance: keep the inventory itself maintainable and usable as a future update checklist.

## Candidate Authoritative Families

- setup plans
- feature plans
- verification checklists
- update-test plans
- E2E test plans
- document-schema plans
- flow markdown docs
- flow YAML asset docs
- traceability catalogs
- audit checklists
- feature checklist family
- development logs, if adopted as required artifacts
- README and canonical command docs where they are treated as authoritative

## Work

- classify each family as authoritative or non-authoritative
- define the purpose of each authoritative family
- define the minimum schema surface for each family
- define whether the family needs:
  - heading/section rules
  - field/value rules
  - cross-reference rules
  - registry completeness rules
  - command consistency rules
  - status vocabulary rules

## Current DS-01 Outputs

- `notes/catalogs/checklists/authoritative_document_family_inventory.md`

## Canonical Verification Command

```bash
python3 -m pytest tests/unit/test_document_schema_docs.py
```

## Exit Criteria

- the repository has one explicit inventory of authoritative document families
- each authoritative family has a named schema/testing strategy
- exploratory and archived documents are not accidentally forced into the same rigidity rules
