# Phase DS-06: User Documentation And Documentation-Impact Schema

## Goal

Adopt schema and automated document-test rules for the repository's user-documentation family and for the new documentation-impact fields required in plans, checklists, and flow-traceability assets.

## Rationale

- Rationale: Once user documentation becomes a first-class system, the repository cannot rely on manual discipline to keep plan-level documentation decisions, flow-level documentation linkage, and authoritative documentation surfaces consistent.
- Reason for existence: This phase exists to give the documentation-governance model machine-enforced structure instead of treating it as a prose-only convention.

## Related Features

Read these implementation plans for context and interaction boundaries:

- `plan/doc_schemas/02_plan_and_checklist_schema_family.md`
- `plan/doc_schemas/03_flow_traceability_and_e2e_doc_schema_family.md`
- `plan/doc_updates/05_user_documentation_first_class_system.md`
- `plan/update_tests/00_raise_existing_tests_to_doctrine_level.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/catalogs/checklists/authoritative_document_family_inventory.md`
- `notes/catalogs/checklists/document_schema_rulebook.md`
- `notes/catalogs/checklists/document_schema_test_policy.md`
- `notes/catalogs/checklists/feature_checklist_standard.md`
- `notes/catalogs/traceability/relevant_user_flow_inventory.yaml`
- `README.md`

## Scope

- Database: enforce schema only for documentation fields that describe DB-backed user-visible behavior; do not alter database runtime behavior in this phase.
- CLI: enforce required documentation-impact structure for command-bearing plans and command-surface documentation references.
- Daemon: enforce required documentation-impact structure for runtime and recovery-plan docs that claim operator-facing guidance.
- YAML: enforce the documentation-family boundary between YAML `docs` assets and user-facing documentation surfaces.
- Prompts: enforce documentation-impact fields where prompt-backed workflows are described in authoritative plan families.
- Tests: add or extend unit-level document-schema tests so authoritative documentation families and documentation-impact fields are machine-validated.
- Performance: keep the document-test additions narrow, deterministic, and fast enough to remain in the bounded documentation suite.
- Notes: update the document-family inventory, rulebook, and policy docs to recognize the new family and field requirements explicitly.

## Work

- add a new authoritative document family for user/operator documentation surfaces
- decide whether `notes/scenarios/**/*.md` belong in that family during transition or should be tracked as a separate transitional family with explicit boundaries
- extend the richer plan schema to require:
  - `## Documentation Impact`
  - `## Documentation Verification`
- extend the feature-checklist schema to require:
  - user documentation status
  - documentation surfaces affected
- extend the structured relevant-user-flow inventory schema to require:
  - documentation_required
  - documentation_surfaces
  - documentation invariants or equivalent explicit linkage
- add or extend family-level tests so the new documentation-governance rules are enforced alongside current task-plan, checklist, and flow-inventory rules

## Current DS-06 Outputs

- planned additions to `notes/catalogs/checklists/authoritative_document_family_inventory.md`
- planned rulebook and policy updates for documentation-impact fields
- planned bounded tests for user-documentation family rigidity and plan/checklist/flow documentation-link enforcement

## Canonical Verification Command

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_feature_checklist_docs.py tests/unit/test_relevant_user_flow_inventory.py tests/unit/test_notes_quickstart_docs.py -q
```

## Exit Criteria

- the authoritative document-family inventory lists the user-documentation family and its schema/testing strategy
- the rulebook and policy docs define the required documentation-impact fields and enforcement posture
- automated tests fail if authoritative plans omit documentation-impact sections
- automated tests fail if checklist or flow-traceability surfaces omit the adopted documentation-linkage fields
- the documentation-governance family is part of the normal bounded document-proof surface
