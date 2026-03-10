# Development Log: Full Epic Tree Real E2E Skeleton Bring-Up

## Entry 1

- Timestamp: 2026-03-10
- Task ID: full_epic_tree_real_e2e_skeleton
- Task title: Full epic tree real E2E skeleton bring-up
- Status: started
- Affected systems: database, CLI, daemon, YAML, prompts, tests, notes, development logs
- Summary: Started the initial full-tree real E2E task to turn the reconciliation plan into an executable skeleton that descends from an epic to phases, plans, and tasks while proving CLI, daemon, and durable database state together.
- Plans and notes consulted:
  - `plan/tasks/2026-03-10_full_epic_tree_real_e2e_skeleton.md`
  - `plan/reconcilliation/02_full_epic_tree_real_e2e_plan.md`
  - `plan/e2e_tests/06_e2e_feature_matrix.md`
  - `notes/catalogs/audit/flow_coverage_checklist.md`
  - `notes/catalogs/checklists/feature_checklist_backfill.md`
  - `notes/catalogs/checklists/verification_command_catalog.md`
  - `notes/specs/runtime/node_lifecycle_spec_v2.md`
  - `notes/specs/runtime/runtime_command_loop_spec_v2.md`
  - `notes/specs/yaml/yaml_schemas_spec_v2.md`
  - `AGENTS.md`
- Commands and tests run:
  - `sed -n '1,260p' plan/reconcilliation/02_full_epic_tree_real_e2e_plan.md`
  - `sed -n '1,260p' tests/helpers/e2e.py`
  - `sed -n '1,260p' tests/fixtures/e2e.py`
  - `sed -n '1,260p' tests/e2e/test_flow_01_create_top_level_node_real.py`
  - `sed -n '1,260p' tests/e2e/test_flow_03_materialize_and_schedule_children_real.py`
  - `sed -n '1,260p' tests/e2e/test_flow_05_admit_and_execute_node_run_real.py`
  - `sed -n '1,260p' tests/e2e/test_flow_10_regenerate_and_rectify_real.py`
  - `sed -n '1,260p' tests/e2e/test_flow_11_finalize_and_merge_real.py`
  - `sed -n '1,260p' src/aicoding/db/models.py`
- Result: Existing real E2E slices and durable schema surfaces were identified; the new work can reuse the real daemon harness and direct DB assertions without introducing a synthetic bridge.
- Next step: Add the task plan, create the expected-failing skeleton test, and update the authoritative E2E mapping notes to track the new suite honestly.

## Entry 2

- Timestamp: 2026-03-10
- Task ID: full_epic_tree_real_e2e_skeleton
- Task title: Full epic tree real E2E skeleton bring-up
- Status: partial
- Affected systems: database, CLI, daemon, YAML, prompts, tests, notes, development logs
- Summary: Added the initial full-tree real E2E skeleton and tightened it so the test verifies hierarchy descent, workflow/source/rendering surfaces, prompt/context surfaces, and durable database state at epic, phase, plan, and task depth before stopping on the first real YAML-to-runtime contract failure.
- Plans and notes consulted:
  - `plan/tasks/2026-03-10_full_epic_tree_real_e2e_skeleton.md`
  - `plan/reconcilliation/02_full_epic_tree_real_e2e_plan.md`
  - `plan/e2e_tests/06_e2e_feature_matrix.md`
  - `notes/catalogs/checklists/feature_checklist_backfill.md`
  - `notes/catalogs/checklists/verification_command_catalog.md`
  - `AGENTS.md`
- Commands and tests run:
  - `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_feature_checklist_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_flow_e2e_alignment_docs.py tests/unit/test_verification_command_docs.py tests/unit/test_notes_quickstart_docs.py -q`
  - `python3 -m pytest tests/e2e/test_e2e_full_epic_tree_runtime_real.py -q`
- Result: The document and note checks passed. The new real E2E skeleton fails intentionally, but now at a precise product gap: `tasks/validate_node.yaml` resolves with validation `checks`, the compiled task preserves the validation command, and the runtime still fails with `validation subtask has no compiled checks` when the leaf task advances into validation.
- Next step: Fix the compiled-subtask validation-check persistence/runtime handoff so the leaf task can complete validation, then extend the same suite into review, mergeback, merged-phase modification, downward regeneration, and rebuilt-lineage re-merge.

## Entry 3

- Timestamp: 2026-03-10
- Task ID: full_epic_tree_real_e2e_skeleton
- Task title: Full epic tree real E2E skeleton bring-up
- Status: changed_plan
- Affected systems: database, CLI, daemon, YAML, prompts, tests, notes, development logs
- Summary: Replaced the earlier fake-session scaffold with a tmux-backed real-boundary test after confirming that the user requirement was true end-to-end decomposition rather than daemon/CLI runtime scaffolding.
- Plans and notes consulted:
  - `plan/tasks/2026-03-10_full_epic_tree_real_e2e_skeleton.md`
  - `plan/reconcilliation/02_full_epic_tree_real_e2e_plan.md`
  - `notes/catalogs/checklists/verification_command_catalog.md`
  - `AGENTS.md`
- Commands and tests run:
  - `python3 -m pytest tests/e2e/test_e2e_full_epic_tree_runtime_real.py -q`
- Result: The test now proves the real tmux session boundary. It starts a real epic run, verifies compiled YAML/workflow/prompt state across CLI, daemon, and database surfaces, binds a real tmux session, verifies durable `sessions` and `session_events` rows, and then fails at the true missing end-to-end behavior: the tmux launch command is `/bin/bash -lc 'exec /bin/bash -li'`, so the session is only a shell and does not invoke Codex to generate phase children.
- Next step: Change the primary tmux session launch path from an interactive shell to a real Codex invocation and add the daemon-owned prompt injection/result-handling needed for session-driven epic -> phase -> plan -> task generation.
