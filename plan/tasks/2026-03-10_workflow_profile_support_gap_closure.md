# Task: Capture Workflow Profile Support Gap Closure Plan

## Goal

Record the concrete proposed note, backend, CLI/API, and test updates needed to support workflow-profile-driven node variants described in the workflow-overhaul notes.

## Rationale

- Rationale: The repository now has future-plan notes that rely on workflow profiles and role-bearing layout children, but the active runtime and CLI surfaces still only support kind-based hierarchy and fixed default layouts.
- Reason for existence: This task exists to preserve the review result as an actionable repository-local plan under `plan/` so later implementation can close the note-to-code gap deliberately instead of rediscovering it.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/02_F01_configurable_node_hierarchy.md`: workflow profiles extend the existing node-hierarchy model without replacing the stable kind ladder.
- `plan/features/07_F03_immutable_workflow_compilation.md`: profile-aware behavior must become part of compiled and inspectable workflow state.
- `plan/features/08_F05_default_yaml_library.md`: new profile-aware YAML families and richer layouts would extend the default built-in library.
- `plan/features/37_F10_top_level_workflow_creation_commands.md`: top-level start/create surfaces would need profile-aware selection and inspection.
- `plan/features/65_F04_layout_replacement_and_hybrid_reconciliation.md`: layout/profile compatibility and replacement semantics interact directly with this slice.

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/specs/architecture/code_vs_yaml_delineation.md`
- `plan/future_plans/workflow_overhaul/2026-03-10_self_hosted_workflow_overhaul_notes.md`
- `plan/future_plans/project_skeleton_generator/2026-03-10_workflow_overhaul_integration.md`
- `notes/catalogs/checklists/document_schema_rulebook.md`
- `notes/catalogs/checklists/document_schema_test_policy.md`

## Scope

- Database: document proposed persistence updates for workflow-profile selection, profile-aware hierarchy metadata, and compiled-profile context.
- CLI: document the proposed create/start/materialize/inspect command extensions and new profile/layout inspection commands.
- Daemon: document required API, validation, compiler, and materialization changes for profile-aware behavior.
- YAML: document the new `workflow_profile_definition` family and richer `node_definition` / `layout_definition` fields.
- Prompts: document the prompt-reference impact and the compiler-generated epic-brief surface.
- Tests: document required unit, integration, CLI, and E2E proving additions.
- Performance: call out compile/materialization/inspection paths that gain profile-aware validation work and need budget review.
- Notes: add a concrete plan note under `plan/future_plans/workflow_overhaul/draft/` capturing the required support delta.

## Verification

- Document-schema coverage: `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py`

## Exit Criteria

- A plan note under `plan/future_plans/workflow_overhaul/draft/` captures the proposed note and code updates needed for workflow-profile support.
- The note distinguishes existing support from missing support across database, CLI, daemon, YAML, prompts, and tests.
- The governing task plan and development log exist and cite each other.
- The documented verification command passes.
