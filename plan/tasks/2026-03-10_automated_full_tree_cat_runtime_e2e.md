# Task: Automated Full-Tree Cat Runtime E2E

## Goal

Implement and prove a real runtime E2E where an automated epic drives automated child creation down through phase, plan, and task nodes and ultimately produces a small sample program that recreates the basic `cat` command behavior.

This document is now the umbrella plan for a phased remediation sequence. Implementation should proceed through the child plans listed below rather than treating the entire runtime gap as one batch.

## Rationale

- Rationale: The repository has real E2E coverage for top-level workflow start, explicit child materialization, live tmux/Codex task execution, and partial full-tree runtime slices, but it still does not prove AI-driven decomposition through the whole hierarchy.
- Reason for existence: This task exists to close the gap between "operators can materialize the hierarchy" and "the runtime can autonomously create and execute the hierarchy through the intended AI command loop."
- The user's requested proof is not satisfied by the current full-tree test because that suite still uses operator-issued `node materialize-children --node <id>` calls instead of proving parent-session-driven descendant creation.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/02_F01_configurable_node_hierarchy.md`
- `plan/features/13_F09_node_run_orchestration.md`
- `plan/features/20_F15_child_node_spawning.md`
- `plan/features/23_F18_child_merge_and_reconcile_pipeline.md`
- `plan/features/37_F10_top_level_workflow_creation_commands.md`
- `plan/e2e_tests/02_e2e_core_orchestration_and_cli_surface.md`
- `plan/e2e_tests/03_e2e_session_recovery_and_child_runtime.md`
- `plan/e2e_tests/06_e2e_feature_matrix.md`

## Child Phase Plans

- `plan/tasks/2026-03-10_automated_full_tree_cat_runtime_preimplementation_planning.md`
- `plan/tasks/2026-03-10_generated_layout_materialization_runtime_phase.md`
- `plan/tasks/2026-03-10_auto_child_run_binding_runtime_phase.md`
- `plan/tasks/2026-03-10_scoped_parent_decomposition_runtime_phase.md`
- `plan/tasks/2026-03-10_automated_full_tree_cat_runtime_e2e_execution_phase.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/tasks/2026-03-10_full_epic_tree_real_e2e_skeleton.md`
- `plan/reconcilliation/02_full_epic_tree_real_e2e_plan.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/catalogs/audit/flow_coverage_checklist.md`
- `notes/catalogs/checklists/verification_command_catalog.md`

## Scope

- Database: verify durable node/version/run/session/attempt/history state across epic, phase, plan, and task creation plus leaf completion.
- CLI: prove the AI-facing decomposition and execution loop through real CLI mutations and inspection surfaces, not direct DB shortcuts.
- Daemon: add or reconcile the parent-node runtime path so child layout generation and child spawning can be driven by live sessions rather than by operator-only materialization.
- YAML: ensure the built-in parent-node workflow/task chain includes the decomposition tasks required for AI-driven child creation, or document and fix the mismatch if the existing notes overstate that behavior.
- Prompts: make the parent-node prompt contract explicit enough for the AI to generate the hierarchy needed for the sample `cat` program and then let the leaf task implement it.
- Tests: add a real E2E that starts from an epic and proves automated epic -> phase -> plan -> task descent plus live task execution for the sample program.
- Performance: keep the sample project and hierarchy narrow enough that the real E2E remains diagnostically useful rather than becoming an opaque long-running provider test.
- Git/workspace: use a real workspace-backed sample project with executable verification for a minimal `cat`-like CLI.
- Notes: update the runtime/E2E notes and logs so the proving boundary is honest.

## Plan

### Phase sequencing

1. Complete the dedicated preimplementation planning/note batch first.
2. Then complete generated-layout materialization support.
3. Then add daemon-owned auto-admission and session binding for ready children.
4. Then add a scoped parent decomposition workflow for this runtime narrative without silently changing the global default ladders.
5. Only after those runtime slices are proven should the real automated `cat` E2E be implemented.
6. Each phase must update notes and logs before the next phase begins.

### Governing rule

- No later phase may claim the automated full-tree narrative is implemented until the earlier phase plans have been completed or explicitly marked partial with documented residual gaps.

## Verification

- Document-family checks after plan/log updates: `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_verification_command_docs.py -q`
- Phase 1 bounded proof: `python3 -m pytest tests/unit/test_materialization.py tests/integration/test_session_cli_and_daemon.py -q`
- Phase 2 bounded proof: `python3 -m pytest tests/integration/test_daemon.py -q`
- Phase 3 bounded proof: `python3 -m pytest tests/unit/test_workflows.py tests/integration/test_workflow_compile_flow.py -q`
- Phase 4 real target: `timeout 300 python3 -m pytest -q tests/e2e/test_e2e_automated_full_tree_cat_runtime_real.py`

## Exit Criteria

- The preimplementation planning and note surface exists before runtime implementation begins.
- Parent-node runtime behavior can create descendant nodes through the intended AI-driven command loop.
- A real E2E proves automated epic -> phase -> plan -> task descent and live task execution for a basic `cat`-like program.
- The test asserts durable CLI/daemon/database evidence rather than only tmux text or in-memory state.
- Notes, logs, and verification commands reflect the new runtime proof honestly.
