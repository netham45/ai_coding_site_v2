# Task: Workflow Profile E2E Coverage Plan

## Goal

Author an end-to-end planning document that defines how every draft workflow profile in the workflow-overhaul bundle should be proven through real runtime coverage.

## Rationale

- Rationale: The workflow-overhaul bundle now includes a complete draft prompt and YAML stack across epic, phase, plan, and task profiles, but it does not yet have a matching E2E proving plan that explains how those profiles should be exercised as real runtime behavior.
- Reason for existence: This task exists to ensure the profile-aware workflow direction has an explicit real-E2E proving strategy before any implementation work promotes these design assets into runtime-facing code.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/37_F10_top_level_workflow_creation_commands.md`: profile-aware E2E work will need to prove create/start surfaces once workflow-profile selection is implemented.
- `plan/features/65_F04_layout_replacement_and_hybrid_reconciliation.md`: profile-driven layout selection and replacement need real narrative coverage, not just unit validation.
- `plan/features/71_F11_live_git_merge_and_finalize_execution.md`: profile-aware full-tree narratives should eventually prove real merge/finalize behavior under a selected workflow profile.

## Required Notes

Read these note files before implementing or revising this phase:

- `plan/future_plans/workflow_overhaul/2026-03-10_self_hosted_workflow_overhaul_notes.md`
- `plan/future_plans/workflow_overhaul/starter_workflow_profiles/README.md`
- `plan/future_plans/workflow_overhaul/rich_layout_examples/README.md`
- `plan/e2e_tests/README.md`
- `plan/e2e_tests/06_e2e_feature_matrix.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/catalogs/checklists/document_schema_rulebook.md`
- `notes/catalogs/checklists/document_schema_test_policy.md`
- `AGENTS.md`

## Scope

- Database: not applicable; this task does not change the active durable schema.
- CLI: document the future CLI/runtime surfaces that the profile-aware E2E narratives must exercise.
- Daemon: document the future daemon/compiler/materialization behaviors that must be proven by real runtime tests.
- YAML: document the draft starter profiles and rich layout examples that each E2E narrative should cover.
- Prompts: document the prompt-stack and brief/result surfaces that profile-aware E2E tests should inspect.
- Tests: run relevant document-schema tests for the new task plan, development log, and E2E plan note.
- Performance: note where full profile-matrix E2E coverage should bias toward representative narrative grouping rather than one tiny test per profile if runtime cost becomes high.
- Notes: add an E2E planning document under `plan/e2e_tests/` that maps every workflow profile to proposed real-runtime test coverage.

## Verification

- Document-schema coverage: `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py`

## Exit Criteria

- `plan/e2e_tests/` contains a workflow-profile E2E plan that covers every draft epic, phase, plan, and task profile.
- The E2E plan names the proposed future real-runtime test narratives, the profile surfaces they should prove, and the CLI/daemon/compiler/materialization boundaries they must exercise.
- The E2E plan explains how to keep the matrix real without exploding into low-value one-assertion tests.
- The governing task plan and development log exist and point to each other.
- The documented verification command passes.
