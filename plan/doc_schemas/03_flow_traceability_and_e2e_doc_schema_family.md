# Phase DS-03: Flow, Traceability, And E2E Document Schema Family

## Goal

Define schema and enforcement rules for flow docs, traceability docs, E2E matrix docs, and related coverage-tracking documents.

## Rationale

- Rationale: Flow and traceability documents now carry completion and E2E coverage meaning, which makes them too important to leave structurally loose.
- Reason for existence: This phase exists to make feature-to-flow, flow-to-test, and feature-to-E2E mappings mechanically enforceable.

## Related Features

Read these implementation plans for context and interaction boundaries:

- `plan/doc_updates/03_flow_traceability_and_e2e_status_alignment.md`
- `plan/e2e_tests/06_e2e_feature_matrix.md`
- `notes/planning/implementation/scenario_and_flow_pytest_plan.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/catalogs/audit/flow_coverage_checklist.md`
- `notes/catalogs/traceability/spec_traceability_matrix.md`
- `notes/catalogs/traceability/cross_spec_gap_matrix.md`
- `notes/planning/implementation/full_real_end_to_end_flow_hardening_plan.md`

## Scope

- Database: flow/traceability docs that claim DB-backed proof or status must be structurally able to express that honestly.
- CLI: flow and E2E docs must consistently express real CLI/runtime proof targets where applicable.
- Daemon: flow and E2E docs must consistently express daemon/runtime proof targets and support levels where applicable.
- YAML: flow and traceability docs must distinguish schema/asset coverage from runtime-proven coverage where needed.
- Prompts: flow and E2E docs must include prompt-related coverage fields where prompts are part of the claimed runtime behavior.
- Notes: define required columns/rows/registry fields for these families.
- Tests: add family-level tests for completeness, mapping integrity, and status vocabulary.
- Performance: ensure tests remain fast enough to run after doc changes.

## Work

- define required fields for flow coverage rows
- define required fields for feature-to-E2E matrix rows
- define required support-level vocabulary
- define required mapping completeness between:
  - features and E2E targets
  - flows and executable tests
  - flow coverage docs and current flow inventory
  - traceability docs and feature inventory
- add or extend tests for those mappings

## Current DS-03 Outputs

- `notes/catalogs/checklists/document_schema_rulebook.md`
- flow/traceability/E2E family enforcement in `tests/unit/test_document_schema_docs.py`
- E2E plan canonical command-policy linkage through `plan/e2e_tests/README.md` and each `plan/e2e_tests/*.md`

## Canonical Verification Command

```bash
python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_flow_e2e_alignment_docs.py tests/unit/test_notes_quickstart_docs.py
```

## Exit Criteria

- flow and traceability docs have enforceable schemas
- missing feature/flow/E2E mappings are detectable by tests
- support-level drift becomes mechanically detectable
