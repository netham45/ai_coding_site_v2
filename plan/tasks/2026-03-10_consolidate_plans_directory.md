# Task: Consolidate Plans Directory

## Goal

Move the remaining authoritative plan families from `plans/` into `plan/`, remove the legacy `plans/` directory, and update all authoritative references and document-schema tests to match.

## Rationale

- Rationale: The repository now uses `plan/` as the canonical plan root, but `plans/doc_updates/` and `plans/doc_schemas/` still create an inconsistent parallel layout.
- Reason for existence: This task exists to eliminate path drift between policy, document-family inventory, tests, and on-disk plan locations so contributors do not need to reason about two near-identical roots.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/28_F23_testing_framework_integration.md`: document-schema tests enforce authoritative-document layout and must be updated with the move.
- `plan/features/33_F29_documentation_generation.md`: repository documentation remains part of the implementation surface and must stay internally consistent.
- `plan/features/34_F32_automation_of_all_user_visible_actions.md`: user-visible operational guidance should use one canonical path layout.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/catalogs/checklists/authoritative_document_family_inventory.md`
- `notes/catalogs/checklists/document_schema_rulebook.md`
- `notes/catalogs/checklists/document_schema_test_policy.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/planning/implementation/project_development_flow_doctrine.md`
- `AGENTS.md`

## Scope

- Database: not applicable; no product persistence change is intended.
- CLI: not applicable; no CLI surface change is intended.
- Daemon: not applicable; no daemon runtime behavior change is intended.
- YAML: not applicable; no YAML asset or schema change is intended.
- Prompts: not applicable; no prompt-contract change is intended.
- Tests: update document-schema tests to use `plan/doc_updates/` and `plan/doc_schemas/`.
- Performance: negligible; filesystem move and lightweight doc tests only.
- Notes: update authoritative notes and plan READMEs to reference `plan/` consistently.

## Verification

- Document-schema suite: `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_feature_plan_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_feature_checklist_docs.py tests/unit/test_verification_command_docs.py tests/unit/test_flow_e2e_alignment_docs.py tests/unit/test_e2e_execution_policy_docs.py tests/unit/test_notes_quickstart_docs.py`

## Exit Criteria

- All files under `plans/doc_updates/` and `plans/doc_schemas/` are moved into `plan/doc_updates/` and `plan/doc_schemas/`.
- No authoritative repository references still point at `plans/doc_updates/` or `plans/doc_schemas/`.
- The legacy `plans/` directory is removed.
- The updated document-schema suite passes.
