# Authoritative Document Family Inventory

## Purpose

This note inventories the repository document families that are treated as authoritative implementation assets and records the schema/testing strategy for each family.

Use this as the DS-01 inventory surface for document-schema adoption.

## Family Inventory

| Family ID | Family | Authoritative | Primary locations | Schema/testing strategy |
| --- | --- | --- | --- | --- |
| DF-01 | Repo README and command entry docs | yes | `README.md` | command-link and posture consistency tests |
| DF-02 | Setup plans | yes | `plan/setup/*.md` | required-section rules plus required notes/related-features guidance where applicable |
| DF-03 | Feature plans | yes | `plan/features/*.md` | required-section rules and related-features/required-notes structure |
| DF-04 | Task plans | yes | `plan/tasks/*.md` | standard richer plan schema plus task verification and exit-criteria rules |
| DF-05 | Verification checklists | yes | `plan/checklists/*.md` | checklist-purpose and release/readiness linkage rules |
| DF-06 | Update-test plans | yes | `plan/update_tests/*.md` | phase structure and command/status alignment rules |
| DF-07 | E2E plans | yes | `plan/e2e_tests/*.md` | target-assignment and required-notes/rationale rules |
| DF-08 | Doc-update plans | yes | `plan/doc_updates/*.md` | current outputs plus canonical verification command rules |
| DF-09 | Doc-schema plans | yes | `plan/doc_schemas/*.md` | current outputs plus canonical verification command rules |
| DF-10 | Flow markdown docs and flow coverage notes | yes | `flows/*.md`, `notes/catalogs/audit/flow_coverage_checklist.md`, `notes/planning/implementation/scenario_and_flow_pytest_plan.md`, `notes/planning/implementation/per_flow_gap_remediation_plan.md` | registry completeness, bounded-vs-E2E alignment, support-status rules |
| DF-11 | Flow YAML asset docs | yes | `flows/*.yaml`, `tests/unit/test_flow_assets.py`, `tests/integration/test_flow_yaml_contract_suite.py` | inventory and flow-asset contract tests |
| DF-12 | Traceability catalogs | yes | `notes/catalogs/traceability/*.md` | interpretation-rule, mapping-completeness, and cross-link rules |
| DF-13 | Audit checklists | yes | `notes/catalogs/audit/*.md` | status-scope rules and command-policy linkage rules |
| DF-14 | Feature checklist family | yes | `notes/catalogs/checklists/feature_checklist_*.md` | status vocabulary, coverage completeness, and command-link rules |
| DF-15 | Verification command and execution policy docs | yes | `notes/catalogs/checklists/verification_command_catalog.md`, `notes/catalogs/checklists/e2e_execution_policy.md` | canonical command and execution-tier rules |
| DF-16 | Development logs and operational logs | yes | `notes/logs/**/*.md` | required field, status-vocabulary, and command/result structure tests |
| DF-17 | Exploratory and archived notes | no | `notes/explorations/**`, `notes/archive/**` | no schema enforcement beyond basic repository hygiene |

## Family Rules

- `Authoritative = yes` means the family participates in implementation, verification, or release/readiness control and should have machine-enforced structure.
- `Authoritative = deferred` means the family has a planned schema surface but is not yet adopted as a required artifact family.
- `Authoritative = no` means the family is intentionally excluded from these rigidity rules.

## Current Test Coverage

- Existing partial coverage already exists through:
  - `tests/unit/test_feature_plan_docs.py`
  - `tests/unit/test_task_plan_docs.py`
  - `tests/unit/test_feature_checklist_docs.py`
  - `tests/unit/test_verification_command_docs.py`
  - `tests/unit/test_flow_e2e_alignment_docs.py`
  - `tests/unit/test_notes_quickstart_docs.py`
- DS-family adoption extends that surface with document-family inventory and schema policy tests.

## Maintenance Rule

When a new document family becomes authoritative, update this inventory and add or extend the corresponding family-level tests in the same change.
