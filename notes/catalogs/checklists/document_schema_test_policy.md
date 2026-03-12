# Document Schema Test Policy

## Purpose

This note defines how document-schema tests are run, adopted, and maintained in normal repository work.

It is the implementation surface for DS-05.

## Canonical Commands

### Core document-schema suite

```bash
python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_feature_plan_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_feature_checklist_docs.py tests/unit/test_verification_command_docs.py tests/unit/test_flow_e2e_alignment_docs.py tests/unit/test_e2e_execution_policy_docs.py tests/unit/test_notes_quickstart_docs.py tests/unit/test_relevant_user_flow_inventory.py
```

### Targeted reruns

Use the smallest relevant family-level test when a change is tightly scoped:

- plan/checklist family changes: `tests/unit/test_document_schema_docs.py tests/unit/test_feature_plan_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_feature_checklist_docs.py`
- command/policy changes: `tests/unit/test_verification_command_docs.py tests/unit/test_e2e_execution_policy_docs.py`
- flow/traceability/E2E doc changes: `tests/unit/test_flow_e2e_alignment_docs.py tests/unit/test_notes_quickstart_docs.py tests/unit/test_document_schema_docs.py`
- structured relevant-flow inventory changes: `tests/unit/test_relevant_user_flow_inventory.py tests/unit/test_document_schema_docs.py tests/unit/test_notes_quickstart_docs.py`

## Adoption Rules

- new authoritative document families must be added to `authoritative_document_family_inventory.md`
- new schema rules must be added to `document_schema_rulebook.md`
- new family-level tests must be added to `tests/unit/test_document_schema_docs.py` or another clearly named family-level test file
- task plans under `plan/tasks/` must follow the standard richer plan schema and include task-specific verification and exit-criteria sections
- plan files under `plan/doc_updates/` and `plan/doc_schemas/` must record current outputs and canonical verification commands once implementation begins

## Failure Triage

When a document-schema test fails:

1. confirm whether the changed doc is authoritative
2. if authoritative, update the doc or the declared schema rule
3. if the family changed shape legitimately, update the inventory, rulebook, and tests in the same change
4. do not silence the failure by weakening the test unless the schema rule itself has been deliberately revised

## Execution Policy Link

- use `notes/catalogs/checklists/e2e_execution_policy.md` for local/CI/gated/release proving tiers
- document-schema tests belong in local default iteration and standard CI because they are lightweight structural checks
