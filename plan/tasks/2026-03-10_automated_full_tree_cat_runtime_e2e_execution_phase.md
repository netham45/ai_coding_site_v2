# Task: Automated Full-Tree Cat Runtime E2E Execution Phase

## Goal

Add the real end-to-end proof that an automated epic can create the descendant hierarchy through phase, plan, and task nodes and end with a working basic `cat`-like program.

## Rationale

- Rationale: This phase only becomes honest after the runtime can use generated layouts, auto-start ready children, and compile the scoped parent decomposition ladder.
- Reason for existence: The real requested proof is the combined runtime narrative, not the bounded slices by themselves.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/13_F09_node_run_orchestration.md`
- `plan/features/20_F15_child_node_spawning.md`
- `plan/features/35_F35_project_policy_extensibility.md`
- `plan/e2e_tests/02_e2e_core_orchestration_and_cli_surface.md`
- `plan/e2e_tests/03_e2e_session_recovery_and_child_runtime.md`
- `plan/e2e_tests/06_e2e_feature_matrix.md`
- `plan/tasks/2026-03-10_automated_full_tree_cat_runtime_e2e.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/catalogs/audit/flow_coverage_checklist.md`
- `notes/catalogs/checklists/verification_command_catalog.md`

## Scope

- Database: prove durable node/version/run/session/summary history through the full hierarchy.
- CLI: prove the real flow through workflow start, session binding, subtask execution, materialization, inspection, and final verification commands.
- CLI: prove the real flow through workflow start, session binding, subtask execution, generated child-plan registration by filename, materialization, inspection, and final verification commands.
- Daemon: prove the live orchestration path across parent decomposition and leaf execution.
- YAML: use the scoped decomposition configuration from the prior phase.
- Prompts: use the real parent and leaf prompt chain, not synthetic injected summaries or direct DB shortcuts.
- Tests: add one real E2E for the automated `cat` narrative and any adjacent helper assertions needed to keep it diagnostically honest.
- Performance: keep the workspace and target program minimal enough that the E2E remains stable and inspectable.
- Notes: update runtime/E2E notes, audit surfaces, and development logs with the actual proof boundary.

## Plan

### Phase 4A: Define the real narrative

1. Create the minimal sample workspace and success checks for a basic `cat` recreation.
2. Define the durable checkpoints to assert at epic, phase, plan, and task depth.
3. Freeze the specific parent registration checkpoints: generated file exists, registration command is issued, durable registered child-plan state exists, then child materialization occurs.

Exit criteria:

- the E2E target and assertions are deterministic enough to debug failures honestly

### Phase 4B: Implement and prove the real E2E

1. Add the real tmux/Codex-driven automated full-tree test.
2. Run the real target and collect the resulting durable evidence.
3. Update notes, audit surfaces, and logs with the real result.

Exit criteria:

- a real E2E proves the automated hierarchy descent plus final program behavior

## Verification

- `timeout 300 python3 -m pytest -q tests/e2e/test_e2e_automated_full_tree_cat_runtime_real.py`
- `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_verification_command_docs.py -q`

## Exit Criteria

- The real automated full-tree `cat` narrative passes through the intended runtime boundaries.
- The resulting proof is durable and inspectable through CLI/daemon surfaces.
- The E2E proves explicit parent registration of generated child plans/layouts rather than implicit filesystem discovery.
- Notes, logs, and audit/checklist surfaces match the real E2E boundary honestly.
