# Task: Task Plan Policy And Schema Adoption

## Goal

Adopt a repository rule that every meaningful code change is governed by a task plan under `plan/tasks/`, and formalize the feature-plan schema as the standard plan schema reused by task plans.

## Rationale

- Rationale: The repository already treats plans as implementation assets, but it does not yet require a task-scoped governing plan for each code change or define task plans as a tested authoritative document family.
- Reason for existence: This task exists to prevent unplanned code changes, undocumented execution scope, and drift between feature plans, task execution, document rules, and verification claims.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/28_F23_testing_framework_integration.md`: document-schema enforcement is part of the repository testing surface.
- `plan/features/33_F29_documentation_generation.md`: authoritative documentation changes are part of the implementation surface.
- `plan/features/34_F32_automation_of_all_user_visible_actions.md`: user-visible workflow doctrine must remain explicit and enforceable.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/catalogs/checklists/authoritative_document_family_inventory.md`
- `notes/catalogs/checklists/document_schema_rulebook.md`
- `notes/catalogs/checklists/document_schema_test_policy.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/planning/implementation/project_development_flow_doctrine.md`
- `AGENTS.md`

## Scope

- Database: not applicable; no durable product-state schema change is intended.
- CLI: not applicable; no CLI command surface change is intended.
- Daemon: not applicable; no daemon runtime behavior change is intended.
- YAML: not applicable; no YAML schema or runtime policy change is intended.
- Prompts: not applicable; no prompt-contract change is intended.
- Tests: extend document consistency coverage to the new `plan/tasks/*.md` family and the adopted development-log family.
- Performance: negligible; documentation and lightweight unit doc tests only.
- Notes: update `AGENTS.md`, document-schema notes, command catalog, and plan family READMEs for the new task-plan rule.

## Verification

- Document-schema suite: `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_feature_plan_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_feature_checklist_docs.py tests/unit/test_verification_command_docs.py tests/unit/test_flow_e2e_alignment_docs.py tests/unit/test_e2e_execution_policy_docs.py tests/unit/test_notes_quickstart_docs.py`

## Exit Criteria

- `AGENTS.md` requires a task plan under `plan/tasks/` for meaningful code changes.
- The standard richer plan schema is explicitly documented as the formal feature/task plan schema.
- `plan/tasks/` is treated as an authoritative document family with schema coverage.
- Development logs are treated as an adopted authoritative document family instead of a deferred placeholder.
- The updated document-schema tests pass.
