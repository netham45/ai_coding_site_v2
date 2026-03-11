# Task: Expand Project Skeleton Generator Post-V1 Lifecycle

## Goal

Extend the `project_skeleton_generator` future-plan bundle so it covers the post-v1 lifecycle in a concrete way, including how a generated repository should govern major feature waves, architectural overhauls, security or compliance audits, migration and offloading work, and sunsetting.

## Rationale

- Rationale: The current bundle explains how to bootstrap a disciplined repository and get it through initial feature delivery and hardening, but it does not yet define how the repository should behave once a first release exists and work becomes choice-driven rather than purely linear.
- Reason for existence: This task exists to preserve and elaborate the user's v1-onward lifecycle idea in the same planning language already used by the skeleton-generator bundle, instead of leaving post-release work as a vague list of continuation states.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/15_F11_operator_cli_and_introspection.md`: the post-v1 model needs operator-visible status and audit surfaces rather than only implementation guidance.
- `plan/features/28_F23_testing_framework_integration.md`: every post-v1 workstream still needs bounded proof and real E2E progression.
- `plan/features/35_F36_auditable_history_and_reproducibility.md`: security audits, migrations, and sunsets depend on durable inspectability and reconstructible history.
- `plan/features/63_F03_candidate_and_rebuild_compile_variants.md`: major overhauls and migration paths likely depend on candidate-versus-current comparison and staged cutover thinking.
- `plan/features/70_F19_live_rebuild_cutover_coordination.md`: migration, offload, and overhaul work all intersect with cutover discipline rather than simple in-place feature edits.

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/future_plans/README.md`
- `plan/future_plans/project_skeleton_generator/README.md`
- `plan/future_plans/project_skeleton_generator/2026-03-10_project_skeleton_generator_overview.md`
- `plan/future_plans/project_skeleton_generator/2026-03-10_project_lifecycle_note_set.md`
- `plan/future_plans/project_skeleton_generator/2026-03-10_project_operational_state_checklist.md`
- `plan/future_plans/project_skeleton_generator/2026-03-10_workflow_overhaul_integration.md`
- `notes/planning/implementation/project_development_flow_doctrine.md`
- `notes/catalogs/checklists/authoritative_document_family_inventory.md`
- `notes/catalogs/checklists/document_schema_rulebook.md`
- `notes/catalogs/checklists/document_schema_test_policy.md`
- `notes/catalogs/checklists/verification_command_catalog.md`

## Scope

- Database: not applicable for implementation; this task does not change the current product schema, though the future-plan notes discuss how post-v1 workstreams would reopen database design and migration concerns when they are actually chosen.
- CLI: not applicable for implementation; this task does not change current CLI commands, though the future-plan notes explain how later generated repos should inspect workstream state, audit passes, migration readiness, and sunset posture.
- Daemon: not applicable for implementation; this task does not change current runtime behavior, though the future-plan notes describe later post-v1 orchestration modes that would need daemon support.
- YAML: not applicable for implementation; this task does not add active YAML assets, though the future-plan notes describe how later workstreams should still map onto workflow profiles and layouts.
- Prompts: not applicable for implementation; this task does not modify active prompt packs, though the future-plan notes describe future prompt families for audit, overhaul, migration, and deprecation work.
- Tests: run the authoritative document tests needed for the new task-plan and development-log surfaces after the doc updates land.
- Performance: negligible for this task; documentation-only planning work, with future-note discussion of performance and resilience requalification during post-v1 changes.
- Notes: update the `project_skeleton_generator` future-plan bundle so it no longer ends at first release, and instead defines a reusable post-v1 operating model with explicit workstream categories, lifecycle guidance, and operational-state implications.

## Verification

- Document-schema coverage: `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py`

## Exit Criteria

- The `project_skeleton_generator` bundle explicitly states that lifecycle governance continues after `flow_complete` and `release_ready`.
- The bundle defines a concrete post-v1 operating model rather than only placeholder continuation states.
- The bundle describes how a generated repository should choose between at least these workstreams: major feature expansion, architectural overhaul, assurance or audit work, migration or offloading, and sunset or archival work.
- The lifecycle note set includes a dedicated post-v1 stage note or equivalent starter-note guidance.
- The operational-state checklist note explains how post-v1 workstreams coexist with baseline maturity rather than pretending the repo is back in a single linear stage.
- The workflow-overhaul integration note explains how post-v1 workstreams can still map onto profile-aware node variants.
- The governing task plan and development log exist and cite each other.
- The documented verification command passes.
