# Development Log: E2E Live-Run Equivalence Inventory

## Entry 1

- Timestamp: 2026-03-12
- Task ID: full_real_e2e_workflow_enforcement
- Task title: E2E live-run equivalence inventory review
- Status: complete
- Affected systems: cli, daemon, database, yaml, prompts, website_ui, tests, notes
- Summary: Reviewed the current `tests/e2e/` inventory against the new live-run-equivalence doctrine and classified the first set of canonical-safe files, quarantined files, and operator-surface exceptions.
- Plans and notes consulted:
  - `plan/tasks/2026-03-12_full_real_e2e_workflow_enforcement.md`
  - `AGENTS.md`
  - `notes/catalogs/checklists/e2e_execution_policy.md`
  - `notes/catalogs/checklists/verification_command_catalog.md`
  - `plan/checklists/16_e2e_real_runtime_gap_closure.md`
- Commands and tests run:
  - `python3 - <<'PY' ... scan tests/e2e for /api/subtasks/complete, subtask start/complete/fail, summary register, workflow advance, lifecycle transition, materialize-children, request(...) ... PY`
  - `sed -n '1,220p' tests/e2e/test_e2e_incremental_parent_merge_real.py`
  - `sed -n '1,220p' tests/e2e/test_e2e_rebuild_cutover_coordination_real.py`
  - `sed -n '1,240p' tests/e2e/test_tmux_codex_idle_nudge_real.py`
  - `sed -n '1,180p' tests/e2e/test_web_project_top_level_browser_real.py`
  - `sed -n '1,240p' tests/e2e/test_e2e_prompt_and_summary_history_real.py`
  - `sed -n '1,240p' tests/e2e/test_flow_12_query_provenance_and_docs_real.py`
- Result: Initial classification is now explicit.

Canonical passing checkpoint candidates under the current doctrine:

- `tests/e2e/test_web_project_top_level_bootstrap_real.py`
- `tests/e2e/test_web_project_top_level_browser_real.py`
- `tests/e2e/test_flow_01_create_top_level_node_real.py`
- `tests/e2e/test_flow_02_compile_or_recompile_workflow_real.py`
- `tests/e2e/test_flow_03_materialize_and_schedule_children_real.py`
- `tests/e2e/test_flow_04_manual_tree_edit_and_reconcile_real.py`
- `tests/e2e/test_flow_05_admit_and_execute_node_run_real.py`
- `tests/e2e/test_e2e_operator_cli_surface.py`
- `tests/e2e/test_e2e_prompt_and_summary_history_real.py`
- `tests/e2e/test_e2e_compile_variants_and_diagnostics.py`
- `tests/e2e/test_e2e_live_git_merge_and_finalize_real.py`

Operator-surface exceptions that are allowed even though they use commands such as `subtask start` or `summary register`:

- `tests/e2e/test_e2e_prompt_and_summary_history_real.py`
- `tests/e2e/test_flow_12_query_provenance_and_docs_real.py`

Reason:

- those commands are the actual operator/AI-facing surface being tested rather than hidden substitutes for a runtime-owned workflow step

Quarantined from canonical passing E2E status:

- `tests/e2e/test_flow_21_child_session_round_trip_and_mergeback_real.py`
- `tests/e2e/test_e2e_automated_full_tree_cat_runtime_real.py`
- `tests/e2e/test_e2e_full_epic_tree_runtime_real.py`
- `tests/e2e/test_e2e_incremental_parent_merge_real.py`
- `tests/e2e/test_e2e_rebuild_cutover_coordination_real.py`
- `tests/e2e/test_tmux_codex_idle_nudge_real.py`

Reason categories:

- real runtime currently broken
- lifecycle forcing or synthetic workflow progression
- manual descendant materialization inside a workflow that claims AI/runtime-driven descent


- Next step: continue Phase 1 by reviewing the remaining non-canonical E2E files one by one and then start Phase 2 rewrites beginning with the most clearly invalid synthetic-progression suites.
