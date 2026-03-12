# Development Log: Incremental Parent Merge Real E2E Repair

## Entry 1
- Timestamp: 2026-03-12
- Task ID: 2026-03-12_full_real_e2e_workflow_enforcement
- Task title: Repair `test_e2e_incremental_parent_merge_real.py` in place to remove synthetic workflow progression
- Status: started
- Affected systems: database, cli, daemon, yaml, prompts, website_ui, tests, notes
- Summary: Started direct repair of the incremental parent merge E2E suite. The immediate target is the helper path that still performs test-side `subtask start`, direct `/api/subtasks/complete`, `workflow advance`, and lifecycle forcing instead of letting the real daemon and session workflow progress.
- Plans and notes consulted:
  - `plan/tasks/2026-03-12_full_real_e2e_workflow_enforcement.md`
  - `notes/catalogs/checklists/e2e_execution_policy.md`
  - `notes/catalogs/checklists/verification_command_catalog.md`
- Commands and tests run:
  - `sed -n '1,260p' tests/e2e/test_e2e_incremental_parent_merge_real.py`
  - `rg -n "subtask start|/api/subtasks/complete|workflow advance|lifecycle transition|node run start|summary register|materialize-children" tests/e2e/test_e2e_incremental_parent_merge_real.py src tests/helpers tests/fixtures -S`
  - `sed -n '2680,2765p' src/aicoding/daemon/workflows.py`
  - `sed -n '1,220p' tests/e2e/test_flow_05_admit_and_execute_node_run_real.py`
  - `sed -n '480,620p' tests/e2e/test_e2e_full_epic_tree_runtime_real.py`
- Result: Confirmed the E2E still contains explicit synthetic completion helpers and that the repo already has a valid tmux and provider-driven session progression pattern that can be used as the replacement path.
- Next step: Replace the synthetic completion helper with a real `node run start` plus `session bind` polling flow, then rerun an incremental-parent-merge slice against that real runtime path.

## Entry 2
- Timestamp: 2026-03-12
- Task ID: 2026-03-12_full_real_e2e_workflow_enforcement
- Task title: Repair `test_e2e_incremental_parent_merge_real.py` in place to remove synthetic workflow progression
- Status: changed_plan
- Affected systems: database, cli, daemon, yaml, prompts, website_ui, tests, notes
- Summary: Replaced the synthetic node-completion helper with a real tmux/provider session wait loop and reran the grouped-cutover incremental-parent-merge E2E. The test now progresses through real session-owned CLI calls, but it exposes a workflow-contract bug in the live parent-node runtime rather than a test-harness shortcut.
- Plans and notes consulted:
  - `plan/tasks/2026-03-12_full_real_e2e_workflow_enforcement.md`
  - `src/aicoding/resources/yaml/builtin/system-yaml/nodes/epic.yaml`
  - `src/aicoding/resources/yaml/builtin/system-yaml/nodes/phase.yaml`
  - `src/aicoding/resources/yaml/builtin/system-yaml/nodes/plan.yaml`
  - `src/aicoding/resources/yaml/builtin/system-yaml/tasks/execute_node.yaml`
- Commands and tests run:
  - `PYTHONPATH=src python3 -m pytest tests/e2e/test_e2e_incremental_parent_merge_real.py -q -k grouped_cutover_rematerializes_authoritative_child`
  - `tail -n 120 /tmp/pytest-of-netham45/pytest-1236/test_e2e_incremental_parent_me0/.runtime-0/daemon.stdout.log`
  - `rg -n "generate_child_layout|spawn_children|review_child_layout|available_tasks:|entry_task:" tests src/aicoding/resources/yaml/builtin/system-yaml notes -S | head -n 200`
  - `sed -n '1,240p' src/aicoding/resources/yaml/builtin/system-yaml/nodes/phase.yaml`
  - `sed -n '1,260p' src/aicoding/resources/yaml/builtin/system-yaml/tasks/execute_node.yaml`
- Result: The test no longer advances the workflow through `subtask start`, `/api/subtasks/complete`, or `workflow advance` from test code. The live daemon/session path now reaches a real pause: the phase child completes `research_context`, then routes into `execute_node.run_leaf_prompt`, and the daemon eventually pauses the run with `idle_nudge_limit_exceeded`. The built-in YAML currently lists `execute_node` as an available task for `epic`, `phase`, and `plan`, even though `tasks/execute_node.yaml` applies only to `task`, so the runtime is sending a phase node into a leaf-task implementation prompt.
- Next step: Repair the parent-node workflow contract or rewrite the incremental-parent-merge E2E around a real `phase -> plan -> task` descendant chain so the merge proof depends on a real leaf execution path instead of direct phase execution.

## Entry 3
- Timestamp: 2026-03-12
- Task ID: 2026-03-12_full_real_e2e_workflow_enforcement
- Task title: Record current real E2E runtime failures in an authoritative checklist
- Status: partial
- Affected systems: cli, daemon, yaml, prompts, tests, notes
- Summary: Updated the real-runtime gap checklist so the currently observed failures are stored in one explicit checklist with the relevant runtime details instead of being scattered only across logs.
- Plans and notes consulted:
  - `plan/checklists/16_e2e_real_runtime_gap_closure.md`
  - `notes/logs/reviews/2026-03-12_e2e_live_run_equivalence_inventory.md`
  - `notes/logs/e2e/2026-03-12_incremental_parent_merge_real_repair.md`
- Commands and tests run:
  - `sed -n '1,260p' plan/checklists/16_e2e_real_runtime_gap_closure.md`
  - `sed -n '1,260p' notes/logs/reviews/2026-03-12_e2e_live_run_equivalence_inventory.md`
  - `sed -n '1,220p' notes/logs/e2e/2026-03-12_incremental_parent_merge_real_repair.md`
  - `PYTHONPATH=src python3 -m pytest tests/unit/test_document_schema_docs.py -q`
- Result: `plan/checklists/16_e2e_real_runtime_gap_closure.md` now records the incremental-parent-merge real-runtime failure mode, the builtin parent-node/task-contract mismatch, and the known live failure modes for Flows 05, 08, 09, 13, 20, 21, and 22. The document-schema check passed after the checklist update.
- Next step: Use the checklist entries as the fix queue and resolve the runtime blockers one by one without reintroducing synthetic E2E progression.

## Entry 4
- Timestamp: 2026-03-12
- Task ID: 2026-03-12_full_real_e2e_workflow_enforcement
- Task title: Repair `test_e2e_incremental_parent_merge_real.py` in place to remove synthetic workflow progression
- Status: partial
- Affected systems: database, cli, daemon, yaml, prompts, tests, notes
- Summary: Tightened the grouped-cutover incremental-parent-merge narrative further by removing `node materialize-children` from the blocked sibling setup. The test now starts the sibling phase for real, binds a tmux/provider session, and waits for the runtime to create the expected `plan` child before the dependency/cutover flow continues.
- Plans and notes consulted:
  - `plan/tasks/2026-03-12_full_real_e2e_workflow_enforcement.md`
  - `plan/checklists/16_e2e_real_runtime_gap_closure.md`
  - `notes/catalogs/checklists/e2e_execution_policy.md`
  - `notes/catalogs/checklists/verification_command_catalog.md`
  - `AGENTS.md`
- Commands and tests run:
  - `PYTHONPATH=src python3 -m pytest tests/e2e/test_e2e_incremental_parent_merge_real.py -q -k grouped_cutover_rematerializes_authoritative_child`
- Result: Failed in `186.57s`. The converted test no longer seeds the blocked sibling's child tree from test code, but the live sibling phase still never created a `plan` child. The captured tmux pane showed the phase running `research_context`, then `execute_node.run_leaf_prompt`, then `validate_node.run_validation_gate`, and finally failing because `python3 -m pytest -q` returned exit code 5 with no tests collected. `node children --node <right_id> --versions` remained empty throughout the wait window.
- Next step: Continue converting remaining E2E shortcuts while tracking that the parent-node workflow contract is still routing phases through leaf execution and validation instead of creating descendants during real runtime.

## Entry 5
- Timestamp: 2026-03-12
- Task ID: 2026-03-12_full_real_e2e_workflow_enforcement
- Task title: Remove helper-level lifecycle forcing from incremental parent merge
- Status: partial
- Affected systems: cli, daemon, prompts, sessions, incremental_parent_merge, tests, notes
- Summary: Tightened the shared `_compile_ready_and_start_node(...)` helper so it no longer forces `READY` before `node run start`, then reran the grouped-cutover narrative against that stricter setup.
- Plans and notes consulted:
  - `plan/tasks/2026-03-12_full_real_e2e_workflow_enforcement.md`
  - `plan/checklists/16_e2e_real_runtime_gap_closure.md`
  - `notes/catalogs/checklists/e2e_execution_policy.md`
  - `notes/catalogs/checklists/verification_command_catalog.md`
  - `AGENTS.md`
- Commands and tests run:
  - `PYTHONPATH=src python3 -m pytest tests/e2e/test_e2e_incremental_parent_merge_real.py -q -k grouped_cutover_rematerializes_authoritative_child`
- Result: Failed in `20.18s`. Once the helper-level lifecycle shortcut is removed, the blocked sibling is still compiled and admitted through `node run start`, but `session bind --node <right_id>` immediately returns daemon conflict `active durable run not found`. That means the stricter live-run-equivalent version now fails even earlier than the previous child-creation wait and does not reach runtime-created descendant checks.
- Next step: Keep removing the remaining direct lifecycle pushes from incremental parent merge and track that the file now shares the same child run/session bind contract break seen in the other partially converted child-backed flows.

## Entry 6
- Timestamp: 2026-03-12
- Task ID: 2026-03-12_full_real_e2e_workflow_enforcement
- Task title: Remove the last helper-level lifecycle forcing from incremental parent merge
- Status: partial
- Affected systems: cli, daemon, prompts, sessions, incremental_parent_merge, tests, notes
- Summary: Removed the direct `READY` transitions from `_setup_parent_and_children(...)` and `_setup_parent_with_conflict_chain(...)`, then reran the helper-driven dependency and conflict narratives against the stricter setup.
- Plans and notes consulted:
  - `plan/tasks/2026-03-12_full_real_e2e_workflow_enforcement.md`
  - `plan/checklists/16_e2e_real_runtime_gap_closure.md`
  - `notes/catalogs/checklists/e2e_execution_policy.md`
  - `notes/catalogs/checklists/verification_command_catalog.md`
  - `AGENTS.md`
- Commands and tests run:
  - `PYTHONPATH=src python3 -m pytest tests/e2e/test_e2e_incremental_parent_merge_real.py -q -k unblocks_dependent_child_only_after_merge_and_refresh`
  - `PYTHONPATH=src python3 -m pytest tests/e2e/test_e2e_incremental_parent_merge_real.py -q -k conflict`
  - `rg -n '"transition"|"materialize-children"|"workflow", "advance"|"summary", "register"|"subtask", "start"|"subtask", "complete"|"subtask", "fail"|"/api/subtasks/complete"|"--no-run"' tests/e2e/test_e2e_incremental_parent_merge_real.py`
- Result:
  - `test_e2e_incremental_parent_merge_unblocks_dependent_child_only_after_merge_and_refresh` failed in `52.57s`. After real `git finalize-node` on the prerequisite child, `_complete_node_run(...)` attempted `session bind --node <child_a>` and the daemon returned `active durable run not found`.
  - `test_e2e_incremental_parent_merge_conflict_resolution_unblocks_dependent_child_real` failed in `61.36s` with the same real bind/runtime contract failure after the conflict-precursor child reached `git finalize-node`.
  - The shortcut audit returned no matches, so `tests/e2e/test_e2e_incremental_parent_merge_real.py` no longer carries the shortcut classes being removed in this pass.
- Next step: Stop treating incremental-parent-merge as still synthetic and keep it in the checklist only as a fully converted E2E file blocked by real runtime failures.
