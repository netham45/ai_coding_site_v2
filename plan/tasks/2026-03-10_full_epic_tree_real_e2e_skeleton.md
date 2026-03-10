# Task: Full Epic Tree Real E2E Skeleton Bring-Up

## Goal

Create the initial real end-to-end skeleton for the full epic-tree runtime narrative so one test can start from an epic, materialize down through phase, plan, and task nodes, execute a leaf task through the real runtime path, and then fail honestly at the still-missing mergeback and rectification stages.

## Rationale

- Rationale: The repository has real E2E slice tests for startup, materialization, execution, regeneration, and merge, but it still lacks one cross-system narrative that proves the intended hierarchy story as one runtime interaction chain.
- Reason for existence: This task exists to turn the full-tree plan into executable scaffolding that exercises CLI, daemon, database, YAML, and prompt-backed behavior together and exposes the remaining runtime gaps without weakening the claim.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/02_F01_configurable_node_hierarchy.md`: hierarchy legality and parent-child shape must remain durable and inspectable.
- `plan/features/13_F09_node_run_orchestration.md`: the task stage must use the real run-control loop and durable attempt records.
- `plan/features/15_F11_operator_cli_and_introspection.md`: the suite must verify operator-facing inspection surfaces, not just internal state.
- `plan/features/20_F15_child_node_spawning.md`: the epic, phase, and plan layers must materialize real descendants through shipped layout/runtime behavior.
- `plan/features/23_F18_child_merge_and_reconcile_pipeline.md`: the later stages of the suite are intended to prove real mergeback rather than synthetic collapse.
- `plan/features/24_F19_regeneration_and_upstream_rectification.md`: the narrative must eventually cover modifying a merged phase, regenerating downward, and rebuilding upward.
- `plan/features/71_F11_live_git_merge_and_finalize_execution.md`: the end state of the narrative depends on live merge/finalize behavior, even if the first skeleton does not reach that stage yet.

## Required Notes

Read these note files before implementing or revising this phase:

- `plan/reconcilliation/02_full_epic_tree_real_e2e_plan.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/yaml/yaml_schemas_spec_v2.md`
- `notes/catalogs/audit/flow_coverage_checklist.md`
- `notes/catalogs/checklists/feature_checklist_backfill.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `plan/e2e_tests/06_e2e_feature_matrix.md`
- `AGENTS.md`

## Scope

- Database: add direct durable-state assertions for nodes, current versions, compiled workflows, child edges, runs, attempts, prompts, summaries, and workflow events.
- CLI: drive the skeleton through real CLI subprocess commands for startup, materialization, run control, and inspection.
- Daemon: verify real API responses alongside CLI results for node, workflow, child, and current-subtask surfaces.
- YAML: exercise the shipped built-in hierarchy and default layouts for `epic`, `phase`, `plan`, and `task`.
- Prompts: verify prompt delivery and context retrieval through the task runtime path.
- Tests: add `tests/e2e/test_e2e_full_epic_tree_runtime_real.py` as an expected-failing narrative skeleton.
- Performance: not a proving target for this task; keep the skeleton diagnostically small and bounded enough to iterate on.
- Notes: update the E2E target matrix, checklist backfill, command catalog, and development logs so the new suite is tracked honestly.

## Verification

- Document consistency and note alignment: `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_feature_checklist_docs.py tests/unit/test_feature_plan_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_flow_e2e_alignment_docs.py tests/unit/test_verification_command_docs.py tests/unit/test_notes_quickstart_docs.py -q`
- New skeleton target: `python3 -m pytest tests/e2e/test_e2e_full_epic_tree_runtime_real.py -q`

## Exit Criteria

- `tests/e2e/test_e2e_full_epic_tree_runtime_real.py` exists and reaches real epic -> phase -> plan -> task interactions before failing honestly at the unfinished mergeback/rectification portion.
- The skeleton contains explicit CLI, daemon, and direct database assertions instead of proving only one system surface.
- The new suite is mapped in the authoritative E2E planning and checklist notes.
- A development log records the task start and the resulting stop point or partial status.
