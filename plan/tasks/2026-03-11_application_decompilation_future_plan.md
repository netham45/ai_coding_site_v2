# Task: Capture Application Decompilation Future Plan

## Goal

Capture an exploratory future-plan bundle for a workflow that takes an existing application, decomposes it into testable behavioral coverage and reconstruction planning assets, and emits epics, phases, plans, and tasks for recreating the application.

## Rationale

- Rationale: The repository is already moving toward richer workflow profiles and reusable project bootstrap patterns, and this idea is a natural later-stage extension that applies those orchestration concepts to reverse-engineering an existing application into prompts, tests, and reconstruction plans.
- Reason for existence: This task exists to preserve the user's undeveloped application-cloning and prompt-decompilation idea in a way that is aligned with the current notes, explicitly marked exploratory, and grounded in the adjacent `workflow_overhaul` and `project_skeleton_generator` future-plan bundles.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/07_F03_immutable_workflow_compilation.md`: the future decompilation flow would eventually need compiled workflow state rather than ad hoc prompt-only execution.
- `plan/features/28_F23_testing_framework_integration.md`: the core premise depends on generating and proving unit, integration, and E2E test surfaces intentionally.
- `plan/features/33_F29_documentation_generation.md`: the output is partly a documentation and planning artifact family, not only code or test generation.
- `plan/features/34_F32_automation_of_all_user_visible_actions.md`: the long-term value depends on making the decompilation pipeline inspectable and reproducible through real operator surfaces.
- `plan/features/63_F03_candidate_and_rebuild_compile_variants.md`: the idea likely depends on candidate, rebuild, and parity-validation compile variants for source-vs-rebuild comparison.

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/future_plans/README.md`
- `plan/future_plans/workflow_overhaul/2026-03-10_self_hosted_workflow_overhaul_notes.md`
- `plan/future_plans/project_skeleton_generator/README.md`
- `plan/future_plans/project_skeleton_generator/2026-03-10_workflow_overhaul_integration.md`
- `notes/planning/implementation/project_development_flow_doctrine.md`
- `notes/catalogs/checklists/authoritative_document_family_inventory.md`
- `notes/catalogs/checklists/document_schema_rulebook.md`
- `notes/catalogs/checklists/document_schema_test_policy.md`
- `notes/catalogs/checklists/verification_command_catalog.md`

## Scope

- Database: not applicable for implementation; this task does not change the current durable product-state schema, though the future note discusses decompilation lineage, artifact storage, and parity-result persistence needs.
- CLI: not applicable for implementation; this task does not change the current CLI surface, though the future note describes likely operator commands for ingest, inspection, and export.
- Daemon: not applicable for implementation; this task does not change live orchestration behavior, though the future note describes a likely staged orchestration pipeline.
- YAML: not applicable for implementation; this task does not add runtime YAML assets, though the future note discusses future workflow-profile and layout needs.
- Prompts: not applicable for implementation; this task does not modify active prompt packs, though the note describes future prompt families for analysis, test synthesis, and rebuild planning.
- Tests: run the authoritative document tests needed for the new task plan and development log surfaces.
- Performance: negligible for this task; documentation-only planning work, with future-note discussion of likely expensive analysis and execution stages.
- Notes: add a non-authoritative future-plan bundle under `plan/future_plans/` that explains how an application-to-prompt decompilation workflow might work, what phases it would likely contain, how it would depend on the adjacent future plans, and which risks and invariants make it exploratory rather than implementation-ready.

## Verification

- Document-schema coverage: `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py`

## Exit Criteria

- `plan/future_plans/application_decompilation/` exists as a non-authoritative working-note bundle.
- The bundle states explicitly that it is exploratory and does not make implementation or verification claims.
- The bundle explains how the idea follows after `workflow_overhaul` and `project_skeleton_generator`.
- The bundle includes a rough staged flow from source-application ingest through test capture, architecture extraction, planning synthesis, and optional parity verification.
- The bundle calls out major feasibility limits, especially around the meaning of "100% coverage" and the difference between observed behavior and inferred design intent.
- `plan/future_plans/README.md` lists the new bundle.
- The governing task plan and development log exist and cite each other.
- The documented verification command passes.
