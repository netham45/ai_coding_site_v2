# Task: Capture Project Skeleton Generator Future Plan

## Goal

Capture a reusable future-plan bundle for extracting this repository's operational framework into a new skeleton-project generator concept.

## Rationale

- Rationale: The repository already contains a strong operational doctrine for plans, notes, logs, checklists, testing, and multi-system feature thinking, but that doctrine is currently embedded across many repository-specific artifacts.
- Reason for existence: This task exists to preserve a concrete strategy for turning that doctrine into a reusable project-bootstrap capability without prematurely promoting the idea into active implementation plans.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/08_F05_default_yaml_library.md`: the future generator would need a default declarative library and starter artifact layout for new projects.
- `plan/features/15_F11_operator_cli_and_introspection.md`: the generated project should preserve inspectability and operator-facing command doctrine as a first-class concern.
- `plan/features/28_F23_testing_framework_integration.md`: the future generator is explicitly meant to carry forward bounded-test and real-E2E expectations.
- `plan/features/33_F29_documentation_generation.md`: the future generator must seed notes, checklists, and lifecycle documentation intentionally rather than treating them as afterthoughts.
- `plan/features/34_F32_automation_of_all_user_visible_actions.md`: the future generator should eventually support reproducible bootstrap behavior instead of manual repo shaping.

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/future_plans/README.md`
- `plan/README.md`
- `notes/planning/implementation/project_development_flow_doctrine.md`
- `notes/catalogs/checklists/authoritative_document_family_inventory.md`
- `notes/catalogs/checklists/document_schema_rulebook.md`
- `notes/catalogs/checklists/document_schema_test_policy.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`

## Scope

- Database: not applicable for implementation; this planning task does not change durable product-state schema.
- CLI: not applicable for implementation; this task does not change the current repository CLI surface.
- Daemon: not applicable for implementation; this task does not change active orchestration behavior.
- YAML: not applicable for implementation; this task may describe future scaffold YAML assets but does not modify runtime YAML schemas.
- Prompts: not applicable for implementation; this task discusses future prompt and AGENTS seeding strategy but does not change active prompts.
- Tests: run the authoritative document tests needed for the new task plan and development log surfaces.
- Performance: negligible; documentation-only planning work.
- Notes: add a future-plan bundle that explains how to extract this repo's operational framework into a reusable skeleton-project bootstrap approach, including lifecycle-stage governance, stage sub-steps, and an operational-state checklist for generated repositories.

## Verification

- Document-schema coverage: `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py`

## Exit Criteria

- `plan/future_plans/project_skeleton_generator/` exists as a non-authoritative working-note bundle.
- The bundle explains the extraction model, generated scaffold shape, lifecycle note set, operational-state checklist model, and checklist strategy for a future skeleton generator.
- The governing task plan and development log exist and cite each other.
- The documented verification command passes.
