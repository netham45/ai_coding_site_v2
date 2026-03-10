# Phase DS-00: Document Schema Master Plan

## Goal

Define and implement schema and rigidity rules for all authoritative document families in the repository, and enforce them with automated consistency tests.

## Rationale

- Rationale: The repository now treats many document families as part of the implementation surface, which means they need machine-enforced structure and consistency rather than manual discipline alone.
- Reason for existence: This phase exists to prevent silent drift in plans, checklists, flow docs, traceability docs, E2E mappings, and development logs.

## Related Features

Read these implementation plans for context and interaction boundaries:

- `plan/doc_updates/00_repo_alignment_master_plan.md`
- `plan/doc_updates/01_feature_checklist_system_and_backfill.md`
- `plan/doc_updates/03_flow_traceability_and_e2e_status_alignment.md`
- `plan/update_tests/00_raise_existing_tests_to_doctrine_level.md`
- `plan/e2e_tests/06_e2e_feature_matrix.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `README.md`
- `notes/planning/implementation/project_development_flow_doctrine.md`
- `notes/catalogs/traceability/spec_traceability_matrix.md`
- `notes/catalogs/audit/flow_coverage_checklist.md`

## Scope

- Database: document-schema work must accurately track DB-backed feature and verification claims where authoritative docs express them.
- CLI: command-bearing documents must have enforceable structure and canonical command consistency rules.
- Daemon: daemon/runtime-facing flow and verification docs must have enforceable mappings and status fields where applicable.
- YAML: schema-bearing and declarative-contract documents must distinguish family shape from runtime proof and remain structurally consistent.
- Prompts: prompt-related documents and prompt/E2E mapping docs must stay consistent where they are authoritative.
- Notes: define which note families are authoritative and what schema rules apply to each.
- Tests: create document-family consistency tests appropriate to each family, not one bespoke test per file.
- Performance: ensure the document-test surface remains maintainable and fast enough to run after doc changes.

## Deliverables

- an inventory of authoritative document families
- a schema rule set for each family
- a testing strategy for each family
- an adoption/execution policy for document tests
- a rollout plan for backfilling existing documents into the schema families

## Current DS-00 Outputs

- `notes/catalogs/checklists/authoritative_document_family_inventory.md`
- `notes/catalogs/checklists/document_schema_rulebook.md`
- `notes/catalogs/checklists/document_schema_test_policy.md`
- `tests/unit/test_document_schema_docs.py`

## Canonical Verification Command

```bash
python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_feature_plan_docs.py tests/unit/test_feature_checklist_docs.py tests/unit/test_flow_e2e_alignment_docs.py tests/unit/test_verification_command_docs.py tests/unit/test_e2e_execution_policy_docs.py
```

## Exit Criteria

- every authoritative document family has an explicit schema or rigidity rule set
- every authoritative document family has automated consistency tests
- document changes have a defined proving path instead of ad hoc review only
