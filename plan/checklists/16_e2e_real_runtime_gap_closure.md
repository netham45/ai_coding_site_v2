# Checklist C16: E2E Real Runtime Gap Closure

## Goal

Track the remaining gaps that still prevent the `tests/e2e/` family from being uniformly “real command, verify real state” proof.

## Required References

- `plan/tasks/2026-03-10_refactor_e2e_tests_to_real_runtime_only.md`
- `plan/tasks/2026-03-10_e2e_realness_audit.md`
- `notes/logs/reviews/2026-03-10_e2e_realness_audit.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`

## Verify

- shared harness defaults do not silently use fake backends
- no E2E file relies on direct DB/API shortcut proof as its primary narrative
- no E2E file intentionally fails as a placeholder
- lifecycle progression is proven through actual runtime commands rather than manual transition shortcuts
- no E2E file manually advances subtasks or injects outputs as a stand-in for live AI/runtime execution
- git/finalize and rectification flows use real runtime progression before finalize/cutover actions

## Tests

- targeted reruns of refactored E2E files
- non-gated real-E2E sweep
- gated tmux/git reruns for files still under refactor

## Canonical Review Rule

- use `notes/catalogs/checklists/verification_command_catalog.md` for the canonical command set
- use `notes/catalogs/checklists/e2e_execution_policy.md` for gating and execution-tier expectations
- keep gaps explicit until the actual runtime shortcut has been removed and the affected test rerun successfully

## Notes

- Closed:
  - shared E2E harness fake default removed; tmux is now the default harness posture
  - `tests/e2e/test_flow_05_admit_and_execute_node_run_real.py` no longer manually issues `subtask start`, `summary register`, `subtask complete`, or `workflow advance`; it now waits for live primary-session progress
  - `tests/e2e/test_e2e_full_epic_tree_runtime_real.py` no longer manually issues `subtask start`, `summary register`, `subtask complete`, or `workflow advance`; it now waits for live leaf-task session progress
  - `tests/e2e/test_e2e_full_epic_tree_runtime_real.py` now passes its real leaf-runtime slice after workspace-backed fixture setup, parent-request prompt propagation, corrected compiled-subtask guidance in the prompt, and tmux/Codex trust-prompt handling
  - `tests/e2e/test_e2e_full_epic_tree_runtime_real.py` now also has a live tmux/Codex plus real git checkpoint that verifies task-repo workspace files on disk and then verifies those same files at plan, phase, and epic repo scope after real merge propagation
  - `tests/e2e/test_e2e_automated_full_tree_cat_runtime_real.py` now also survives a real bind on the runtime-created phase child, not just the top-level epic session, and still passes the full automated `epic -> phase -> plan -> task` descendant chain with working implementation and passing local pytest
  - `tests/e2e/test_e2e_operator_cli_surface.py` no longer relies on `workflow start` state alone; it now binds a real tmux/provider session, waits for durable run state, and still passes its operator inspection/pause narrative
  - `tests/e2e/test_flow_04_manual_tree_edit_and_reconcile_real.py` no longer exercises reconciliation on a cold parent node only; it now starts and binds the parent workflow first, waits for durable run state, and still passes the manual child reconciliation narrative
  - `tests/e2e/test_flow_06_inspect_state_and_blockers_real.py` no longer relies on `workflow start` state alone; it now binds a real tmux/provider session, waits for durable run state, and still passes its inspection/blocker narrative
  - `tests/e2e/test_web_project_top_level_bootstrap_real.py` no longer stops at `start_run: false`; it now keeps the API bootstrap proof and then starts a real run, binds a real tmux/provider session, waits for durable run state, and still passes
  - `tests/e2e/test_web_project_top_level_browser_real.py` no longer stops at browser/API bootstrap plus summary/audit/git inspection only; it now binds the browser-created node to a real tmux/provider session, waits for durable run state, and still passes
  - `tests/e2e/test_flow_08_handle_failure_and_escalate_real.py` rewritten to use parent child-materialization instead of forcing child readiness
  - `tests/e2e/test_flow_11_finalize_and_merge_real.py` rewritten to reach finalize and merge through real git/runtime progression instead of lifecycle forcing
  - `tests/e2e/test_flow_22_dependency_blocked_sibling_wait_real.py` rewritten to use real parent workflow start plus child materialization instead of forcing sibling readiness
- Open:
  - `tests/e2e/test_e2e_rebuild_cutover_coordination_real.py` no longer contains the shortcut patterns being removed in this cleanup pass; it is still blocked, but now only by real `node run start` / `session bind` runtime failures and the older blocker-surface mismatch
  - `tests/e2e/test_tmux_codex_idle_nudge_real.py` no longer contains the shortcut patterns being removed in this cleanup pass; it is still blocked, but now only by real `node run start` loss before `subtask prompt` and the earlier live prompt-surface mismatch
  - `tests/e2e/test_e2e_incremental_parent_merge_real.py` no longer contains the shortcut patterns being removed in this cleanup pass; it is still blocked, but now only by real runtime behavior including `session bind --node <id>` returning `active durable run not found` and phase-level runs failing to create descendants
  - `tests/e2e/test_e2e_full_epic_tree_runtime_real.py` no longer contains the shortcut patterns being removed in this cleanup pass; it is still blocked, but now only by real runtime behavior, specifically the epic session failing to create the descendant git hierarchy at all
  - `tests/e2e/test_e2e_incremental_parent_merge_real.py` no longer uses test-side `/api/subtasks/complete` or `workflow advance`, but its first real rerun now exposes a workflow-contract bug: a `phase` child completes `research_context`, routes into `execute_node.run_leaf_prompt`, and then pauses with `idle_nudge_limit_exceeded` instead of completing through a real descendant execution path
  - the same file no longer forces `READY` through `_compile_ready_and_start_node(...)`; once that helper-level lifecycle shortcut is removed, the grouped-cutover narrative now fails even earlier because the blocked sibling's admitted run cannot survive `session bind --node <phase>` and returns daemon conflict `active durable run not found`
  - the same file's grouped-cutover narrative no longer uses `node materialize-children` to seed the blocked sibling's child tree; after conversion to a real started/bound sibling phase, the live rerun shows that the phase runs its own stages, reaches `validate_node.run_validation_gate`, fails on `pytest -q` with no tests, and still never creates the expected `plan` child
  - the same file's `manual_restart_requires_explicit_reconcile` narrative no longer uses `node materialize-children` to seed the blocked sibling's initial automatic child tree; after conversion to a real started/bound sibling phase, the live rerun shows that the phase fails during `execute_node.run_leaf_prompt` without ever creating the expected `plan` child, so the earlier “passed” manual-reconciliation proof does not survive the stricter live-run-equivalence standard
  - the same file's `manual_restart_clears_after_fresh_manual_child_create` narrative no longer uses `node materialize-children` to seed the blocked sibling's initial automatic child tree; after conversion to a real started/bound sibling phase, the live rerun again shows no runtime-created `plan` child and the phase instead fails to parent during leaf execution, so the earlier “passed” fresh-manual-child-create proof also does not survive the stricter live-run-equivalence standard
  - `tests/e2e/test_e2e_full_epic_tree_runtime_real.py` no longer manually materializes `phase -> plan -> task` descendants in its first narrative; it now starts a real epic session, waits for runtime-created descendants, and fails because the runtime-driven tree does not become visible to `tree show --full` within the polling window even though daemon logs show real `children/register-layout`, `review/run`, and `children/materialize` activity for the epic node
  - the same file's bootstrapped git-hierarchy helper no longer uses `--no-run` plus chained `materialize-children` calls; after conversion to a real epic session and runtime-created descendants, the live rerun times out with a blank epic pane and no runtime-created hierarchy at all
  - the same file's first git-merge propagation narrative no longer manually pushes finalized child/plan/phase nodes to `COMPLETE` after `git finalize-node`; with those lifecycle-forcing calls removed, the stricter rerun still fails even earlier because `_setup_bootstrapped_full_tree_git_hierarchy(...)` times out waiting for the real epic session to create the descendant git hierarchy at all
  - builtin workflow contract mismatch now blocks parent-node real E2E progression:
    - `src/aicoding/resources/yaml/builtin/system-yaml/nodes/epic.yaml`
    - `src/aicoding/resources/yaml/builtin/system-yaml/nodes/phase.yaml`
    - `src/aicoding/resources/yaml/builtin/system-yaml/nodes/plan.yaml`
    - those node definitions advertise `execute_node` in `available_tasks`
    - `src/aicoding/resources/yaml/builtin/system-yaml/tasks/execute_node.yaml` applies only to `task`
    - result: parent nodes can be sent into the leaf-task implementation prompt during live E2E runs
  - `tests/e2e/test_flow_05_admit_and_execute_node_run_real.py` now exposes a real runtime gap: the primary tmux/Codex session can disappear without durable attempt, summary, or completed-subtask state being recorded
  - `tests/e2e/test_flow_08_handle_failure_and_escalate_real.py` now exposes two real runtime gaps as the test is tightened: first, when the test relied on manual child materialization, the live child tmux/Codex session stayed `RUNNING`, emitted unsupported CLI `--json` flags, and never recorded a durable failed child run; after removing the manual `node materialize-children` step, the parent tmux/Codex session still fails to create the first phase child through the runtime command loop within the polling window
  - `tests/e2e/test_flow_09_run_quality_gates_real.py` now exposes a real runtime gap: the live runtime does not advance the node into a built-in quality gate, so `node quality-chain` remains blocked with a state conflict
  - `tests/e2e/test_e2e_regeneration_and_upstream_rectification_real.py` no longer uses `node materialize-children` to seed the dependent sibling's child tree in its dependency-invalidated fresh-restart narrative; after conversion to a real started/bound phase session, the dependent phase still never creates the expected `plan` child and instead runs straight through leaf execution and validation before failing on `pytest -q` with no tests collected
  - the same rectification narrative also no longer creates the left/right phase siblings directly; after conversion to a real epic session and runtime-created sibling wait, the epic itself still never creates the two phase children and instead fails to parent during `execute_node.run_leaf_prompt`
  - `tests/e2e/test_flow_10_regenerate_and_rectify_real.py` now exposes the same stricter live-runtime gap in its broader dependency-invalidated fresh-restart narrative after removing `node materialize-children` from the dependent sibling setup: the phase still never creates the expected `plan` child and instead executes leaf stages and fails validation on `pytest -q` with no tests collected
  - the same Flow 10 narrative also no longer creates the left/right phase siblings directly; after conversion to a real epic session and runtime-created sibling wait, the epic itself still never creates the two phase children and instead fails during `execute_node.run_leaf_prompt`
  - `tests/e2e/test_flow_13_human_gate_and_intervention_real.py` now exposes a real runtime gap: the primary tmux/Codex session can disappear before the run reaches the explicit `pause_for_user` gate
  - `tests/e2e/test_flow_20_compile_failure_and_reattempt_real.py` now exposes a real runtime/contract gap: after a failed compile, `workflow source-discovery` returns `compiled workflow not found` instead of remaining inspectable through the CLI
  - `tests/e2e/test_flow_21_child_session_round_trip_and_mergeback_real.py` now exposes a real runtime gap: the delegated child tmux session receives raw prompt text with an unresolved `{{node_id}}` placeholder and never produces a durable merge-back result
  - `tests/e2e/test_flow_22_dependency_blocked_sibling_wait_real.py` now exposes two real runtime gaps as the test is tightened: first, the dependency-blocked sibling was still admitted by `node run start` before the prerequisite sibling completed; after removing the manual sibling-materialization step, the parent tmux/Codex session still fails to create the sibling phases at all and instead falls into `execute_node.run_leaf_prompt` with a durable failure summary
  - `tests/e2e/test_e2e_rebuild_cutover_coordination_real.py` now exposes a stricter live-runtime gap after conversion: when the test binds a real authoritative primary tmux session, the upstream rebuild-coordination surface still reports only `active_or_paused_run` and does not surface a dedicated active-primary-session blocker
  - `tests/e2e/test_tmux_codex_idle_nudge_real.py` conversion now uses the real routed `subtask succeed --summary-file ...` path instead of `summary register` plus `subtask complete`, and the live rerun exposes a prompt-surface mismatch: the pane no longer contains the old exact idle reminder text and is already showing the repeated missed-step reminder / Codex response by the time the assertion inspects it
  - `tests/e2e/test_flow_02_compile_or_recompile_workflow_real.py` no longer uses `workflow start --no-run`; after conversion to a real started-run path with a bound tmux/provider session, the live rerun exposes a daemon contract gap: `workflow compile --node <id>` now returns `cannot compile a node with an active lifecycle run`
  - `tests/e2e/test_flow_19_hook_expansion_compile_stage_real.py` no longer proves hook expansion through explicit compile only; after conversion to a real started task run, `node run start` succeeds but `session bind --node <task>` immediately fails with daemon conflict `active durable run not found`
  - `tests/e2e/test_flow_15_to_18_default_blueprints_real.py` no longer proves blueprint selection through compile/current/chain inspection only; after conversion to real started runs, all four blueprint kinds (`epic`, `phase`, `plan`, `task`) hit the same run/session contract gap where `node run start` succeeds but `session bind --node <id>` returns `active durable run not found`
  - `tests/e2e/test_flow_14_project_bootstrap_and_yaml_onboarding_real.py` now exposes the same run/session contract gap after conversion to a real started-run path: `node run start` succeeds, but `session bind --node <id>` returns `active durable run not found`
  - `tests/e2e/test_e2e_compile_variants_and_diagnostics.py` no longer proves authoritative/candidate/rebuild compile variants through compile-only inspection; after conversion to a real started-run path, `node run start` succeeds, but `session bind --node <id>` returns the same daemon conflict `active durable run not found`
  - `tests/e2e/test_flow_20_compile_failure_and_reattempt_real.py` no longer stops at repaired compile inspection; after conversion to a real started-run path following the repaired compile, `node run start` succeeds, but `session bind --node <id>` returns the same daemon conflict `active durable run not found`
  - `tests/e2e/test_e2e_prompt_and_summary_history_real.py` no longer relies on `workflow start` state alone; after conversion to a real started-run path with a bound tmux/provider session, the old history assertion fails because the live bound session records an earlier prompt entry before the later operator-fetched prompt is delivered
  - `tests/e2e/test_flow_11_finalize_and_merge_real.py` no longer finalizes and merges from cold created nodes only; after conversion to a live started/bound parent plus a real started child run, the parent bind succeeds but `session bind --node <child>` fails with daemon conflict `active durable run not found`
  - `tests/e2e/test_flow_07_pause_resume_and_recover_real.py` now requires the provider-backed durable-run boundary before recovery assertions; the resume path still passes, but the supervision-restart path now fails because `session show` continues to report the original lost session name instead of a replacement resumed session
  - `tests/e2e/test_e2e_live_git_merge_and_finalize_real.py` no longer proves the first merge/finalize narrative from cold created nodes only; after conversion to a live started/bound parent plus real started child runs, the parent bind succeeds but `session bind --node <child>` fails with daemon conflict `active durable run not found`
  - `tests/e2e/test_e2e_rebuild_cutover_coordination_real.py` no longer relies on a direct lifecycle transition to force `READY`; after removing that shortcut, the upstream-rectify narrative now fails earlier because the admitted child run still cannot survive `session bind --node <child>` and returns daemon conflict `active durable run not found`
  - `tests/e2e/test_tmux_codex_idle_nudge_real.py` no longer relies on a direct lifecycle transition to force `READY` in its manual task helper; after removing that shortcut, the idle-nudge narrative now fails earlier because `subtask prompt --node <task>` returns `active node run not found`
  - `tests/e2e/test_e2e_incremental_parent_merge_real.py` no longer carries the direct `READY` transitions in `_setup_parent_and_children(...)` or `_setup_parent_with_conflict_chain(...)`; after removing those last helper-level lifecycle pushes, both helper families now collapse into the same real `session bind --node <child_a>` / `active durable run not found` failure during `_complete_node_run(...)`
  - provider-backed tmux flows still need targeted reruns beyond Flow 22 to confirm they pass without any remaining runtime-surface shortcuts

## Failure Inventory

- `tests/e2e/test_e2e_incremental_parent_merge_real.py`
  - canonical failing command:
    - `PYTHONPATH=src python3 -m pytest tests/e2e/test_e2e_incremental_parent_merge_real.py -q -k grouped_cutover_rematerializes_authoritative_child`
  - current live failure:
    - after removing the helper-level forced `READY` transition, the blocked sibling is still compiled and admitted through `node run start`
    - `session bind --node <right_id>` then immediately returns daemon conflict `active durable run not found`
    - the stricter live-run-equivalent version now fails before it can even wait for runtime-created `plan` children under that phase
  - relevant runtime evidence:
    - `notes/logs/e2e/2026-03-12_incremental_parent_merge_real_repair.md`
  - additional canonical failing command:
    - `PYTHONPATH=src python3 -m pytest tests/e2e/test_e2e_incremental_parent_merge_real.py -q -k manual_restart_requires_explicit_reconcile`
  - additional live failure:
    - after removing manual child materialization for the blocked sibling's initial automatic child tree, the real run still does not create the expected `plan` child under that phase
    - the tmux/provider session now fails during `execute_node.run_leaf_prompt` because the workspace contains no repository checkout or implementation files to reconcile
    - `node children --node <right_id> --versions` remains empty throughout the wait window
  - additional canonical failing command:
    - `PYTHONPATH=src python3 -m pytest tests/e2e/test_e2e_incremental_parent_merge_real.py -q -k manual_restart_clears_after_fresh_manual_child_create`
  - additional live failure:
    - after removing manual child materialization for the blocked sibling's initial automatic child tree, the real run still does not create the expected `plan` child under that phase
    - the tmux/provider session completes `research_context`, then fails to parent during `execute_node.run_leaf_prompt` because the request requires fresh manual child creation rather than an actionable implementation slice in the workspace
    - `node children --node <right_id> --versions` remains empty throughout the wait window
  - additional canonical failing command:
    - `PYTHONPATH=src python3 -m pytest tests/e2e/test_e2e_incremental_parent_merge_real.py -q -k unblocks_dependent_child_only_after_merge_and_refresh`
  - additional live failure:
    - after removing the direct `READY` transition from `_setup_parent_and_children(...)`, the prerequisite child reaches real `git finalize-node`
    - `_complete_node_run(...)` then tries to bind the real session for `child_a`
    - `session bind --node <child_a>` returns daemon conflict `active durable run not found`
  - additional canonical failing command:
    - `PYTHONPATH=src python3 -m pytest tests/e2e/test_e2e_incremental_parent_merge_real.py -q -k conflict_resolution_unblocks_dependent_child_real`
  - additional live failure:
    - after removing the direct `READY` transition from `_setup_parent_with_conflict_chain(...)`, the conflict-precursor child also reaches real `git finalize-node`
    - `_complete_node_run(...)` then tries to bind the real session for `child_a`
    - `session bind --node <child_a>` returns the same daemon conflict `active durable run not found`
  - conversion status:
    - `rg -n '"transition"|"materialize-children"|"workflow", "advance"|"summary", "register"|"subtask", "start"|"subtask", "complete"|"subtask", "fail"|"/api/subtasks/complete"|"--no-run"' tests/e2e/test_e2e_incremental_parent_merge_real.py` now returns no matches
    - the file is no longer carrying the shortcut classes being removed in this pass and should now be treated as a fully converted E2E file that is blocked only by real runtime behavior

- `tests/e2e/test_e2e_full_epic_tree_runtime_real.py`
  - canonical failing command:
    - `PYTHONPATH=src python3 -m pytest tests/e2e/test_e2e_full_epic_tree_runtime_real.py -q -k 'full_epic_tree_runtime_real and not live_ai_workspace and not git_merge'`
  - current live failure:
    - the first full-tree narrative no longer calls manual `node materialize-children` for `epic`, `phase`, or `plan`
    - it starts a real epic session and waits for the runtime to create the `phase -> plan -> task` chain
    - the wait times out because `tree show --full` never exposes the full descendant chain within the polling window
  - relevant runtime evidence:
    - daemon stdout during the failing run shows real `children/register-layout`, `review/run`, and `children/materialize` activity for the epic node, so the remaining gap is in runtime progression and/or visibility of the runtime-created descendants rather than a test-side synthetic step
    - `notes/logs/e2e/2026-03-10_full_epic_tree_real_e2e_skeleton.md`
  - additional canonical failing command:
    - `PYTHONPATH=src python3 -m pytest tests/e2e/test_e2e_full_epic_tree_runtime_real.py -q -k live_ai_workspace_merge_propagates_repo_files`
  - additional live failure:
    - the bootstrapped git-hierarchy helper now starts a real epic session and waits for runtime-created descendants instead of chaining `materialize-children`
    - the rerun times out with `last_value=None`, a blank captured epic tmux pane, and no `phase -> plan -> task` hierarchy visible through `tree show --full`
  - additional canonical failing command:
    - `PYTHONPATH=src python3 -m pytest tests/e2e/test_e2e_full_epic_tree_runtime_real.py -q -k git_merge_propagates_task_changes_to_plan_phase_and_epic`
  - additional live failure:
    - after removing the manual post-finalize lifecycle pushes to `COMPLETE`, the stricter git-merge narrative still does not get far enough to test parent merge propagation
    - `_setup_bootstrapped_full_tree_git_hierarchy(...)` times out waiting for the real epic session to create the descendant git hierarchy
    - the captured epic pane is blank and `last_value=None` at the timeout
  - conversion status:
    - `rg -n '"transition"|"materialize-children"|"workflow", "advance"|"summary", "register"|"subtask", "start"|"subtask", "complete"|"subtask", "fail"|"/api/subtasks/complete"|"--no-run"' tests/e2e/test_e2e_full_epic_tree_runtime_real.py` now returns no matches
    - the direct lifecycle-forcing helper now waits for runtime-owned completion instead of mutating lifecycle state from test code
    - the file is no longer carrying the shortcut classes being removed in this pass and should now be treated as a fully converted E2E file that is blocked only by real runtime behavior

- `tests/e2e/test_flow_05_admit_and_execute_node_run_real.py`
  - current live failure:
    - the primary tmux/Codex session can disappear before durable attempt, summary, or completed-subtask state is recorded

- `tests/e2e/test_flow_08_handle_failure_and_escalate_real.py`
  - current live failure:
    - after removing the manual child-materialization shortcut, the parent tmux/Codex session still does not create the first phase child within the polling window
    - the captured pane shows the model inspecting `node kinds` and `node children` but never issuing the runtime action that actually creates the child
    - the earlier stricter rerun also showed the child tmux/Codex session remaining `RUNNING`, emitting unsupported CLI `--json` flags, and never recording a durable failed child-run record once a manually materialized child was bound
  - relevant runtime evidence:
    - `notes/logs/e2e/2026-03-10_real_e2e_failure_flow08_child_failure_progress.md`

- `tests/e2e/test_flow_09_run_quality_gates_real.py`
  - current live failure:
    - the live runtime does not enter the expected built-in quality stages
    - `node quality-chain` remains blocked with a state conflict instead of reaching `COMPLETE`

- `tests/e2e/test_e2e_regeneration_and_upstream_rectification_real.py`
  - canonical failing command:
    - `PYTHONPATH=src python3 -m pytest tests/e2e/test_e2e_regeneration_and_upstream_rectification_real.py -q -k dependency_invalidated_fresh_restart_is_childless_and_remapped`
  - current live failure:
    - after removing manual left/right child creation, the real epic run still does not create the expected two phase siblings
    - the tmux/provider session completes `research_context`, advances into `execute_node.run_leaf_prompt`, and fails to parent because the workspace only contains prompt logs and summaries
    - `node children --node <parent_id> --versions` remains empty throughout the wait window
  - relevant runtime evidence:
    - `notes/logs/e2e/2026-03-12_regeneration_and_upstream_rectification_real_e2e.md`

- `tests/e2e/test_flow_10_regenerate_and_rectify_real.py`
  - canonical failing command:
    - `PYTHONPATH=src python3 -m pytest tests/e2e/test_flow_10_regenerate_and_rectify_real.py -q -k dependency_invalidated_fresh_restart_is_childless_and_remapped_into_parent_candidate`
  - current live failure:
    - after removing manual left/right child creation, the real epic run still does not create the expected two phase siblings
    - the tmux/provider session completes `research_context`, advances into `execute_node.run_leaf_prompt`, and fails because the workspace contains no repository, source files, or tests
    - `node children --node <parent_id> --versions` remains empty throughout the wait window
  - relevant runtime evidence:
    - `notes/logs/e2e/2026-03-11_dependency_invalidated_fresh_restart_real_e2e.md`

- `tests/e2e/test_flow_13_human_gate_and_intervention_real.py`
  - current live failure:
    - the primary tmux/Codex session can disappear before the explicit human-pause gate is reached

- `tests/e2e/test_flow_20_compile_failure_and_reattempt_real.py`
  - canonical failing command:
    - `PYTHONPATH=src python3 -m pytest tests/e2e/test_flow_20_compile_failure_and_reattempt_real.py -q`
  - current live failure:
    - the stricter version still confirms the failed-compile CLI gap: after a failed compile, `workflow source-discovery` returns `compiled workflow not found`
    - after repairing the project policy and recompiling, the epic run is admitted through `node run start`
    - `session bind --node <id>` then returns daemon conflict `active durable run not found`
    - the repaired compile-reattempt narrative therefore cannot yet prove its runtime continuation against a real bound session
  - relevant runtime evidence:
    - `notes/logs/e2e/2026-03-12_workflow_start_and_compile_real_runtime_conversion.md`

- `tests/e2e/test_e2e_prompt_and_summary_history_real.py`
  - canonical failing command:
    - `PYTHONPATH=src python3 -m pytest tests/e2e/test_e2e_prompt_and_summary_history_real.py -q`
  - current live failure:
    - after binding a real tmux/provider session before the history assertions, the test still reaches durable run state
    - but `prompts history --node <id>` is no longer headed by the later operator-fetched prompt id from `subtask prompt --node <id>`
    - the live bound session records an earlier prompt delivery first, so the old `prompts[0]["id"] == prompt_id` assertion no longer matches real runtime ordering
  - relevant runtime evidence:
    - `notes/logs/e2e/2026-03-12_workflow_start_and_compile_real_runtime_conversion.md`

- `tests/e2e/test_flow_11_finalize_and_merge_real.py`
  - canonical failing command:
    - `PYTHONPATH=src python3 -m pytest tests/e2e/test_flow_11_finalize_and_merge_real.py -q`
  - current live failure:
    - after starting and binding the parent workflow for real, the test creates the child and starts its run through `node run start`
    - `session bind --node <child>` then returns daemon conflict `active durable run not found`
    - the stricter live-run-equivalent version therefore cannot yet prove finalize/merge behavior against a live bound child session
  - relevant runtime evidence:
    - `notes/logs/e2e/2026-03-12_workflow_start_and_compile_real_runtime_conversion.md`

- `tests/e2e/test_flow_07_pause_resume_and_recover_real.py`
  - canonical failing command:
    - `PYTHONPATH=src python3 -m pytest tests/e2e/test_flow_07_pause_resume_and_recover_real.py -q`
  - current live failure:
    - after adding the provider-backed durable-run wait, `test_flow_07_pause_resume_and_recover_runs_against_real_daemon_real_cli_and_tmux` still passes
    - but `test_flow_07_background_supervision_restarts_killed_tmux_session_automatically` now exposes that the lost session is recorded in `session list` while `session show --node <id>` continues to report the original session name instead of a replacement resumed session
    - the stricter live-run-equivalent version therefore no longer proves automatic supervision restart as a real replaced-session flow
  - relevant runtime evidence:
    - `notes/logs/e2e/2026-03-12_workflow_start_and_compile_real_runtime_conversion.md`

- `tests/e2e/test_e2e_live_git_merge_and_finalize_real.py`
  - canonical failing command:
    - `PYTHONPATH=src python3 -m pytest tests/e2e/test_e2e_live_git_merge_and_finalize_real.py -q -k verifies_parent_repo_contents`
  - current live failure:
    - after starting and binding the parent workflow for real, the test creates both child phases and admits each child through `node run start`
    - `session bind --node <child_a>` then returns daemon conflict `active durable run not found`
    - the stricter live-run-equivalent version therefore cannot yet prove the first live git merge/finalize narrative against real bound child sessions
  - relevant runtime evidence:
    - `notes/logs/e2e/2026-03-12_workflow_start_and_compile_real_runtime_conversion.md`

- `tests/e2e/test_e2e_rebuild_cutover_coordination_real.py`
  - canonical failing command:
    - `PYTHONPATH=src python3 -m pytest tests/e2e/test_e2e_rebuild_cutover_coordination_real.py -q -k blocks_upstream_rectify`
  - current live failure:
    - after removing the direct `node lifecycle transition --state READY` shortcut, the child run is compiled and admitted through `node run start`
    - `session bind --node <child>` then returns daemon conflict `active durable run not found`
    - the stricter live-run-equivalent version therefore fails before it can even re-check the upstream-rectify blocker surface
  - additional canonical failing command:
    - `PYTHONPATH=src python3 -m pytest tests/e2e/test_e2e_rebuild_cutover_coordination_real.py -q -k blocks_candidate_cutover`
  - additional live failure:
    - after removing the direct `node lifecycle transition --state READY` shortcut, the authoritative node is compiled and admitted through `node run start`
    - `session bind --node <authoritative>` then returns daemon conflict `active durable run not found`
    - the stricter live-run-equivalent version therefore fails before it can re-check the candidate cutover blocker surface too
  - conversion status:
    - `rg -n "lifecycle transition|materialize-children|workflow advance|summary register|subtask start|subtask complete|--no-run|/api/subtasks/complete" tests/e2e/test_e2e_rebuild_cutover_coordination_real.py` now returns no matches
    - the file is no longer carrying the shortcut classes being removed in this pass and should now be treated as a fully converted E2E file that is blocked only by real runtime behavior
  - relevant runtime evidence:
    - `notes/logs/e2e/2026-03-12_workflow_start_and_compile_real_runtime_conversion.md`

- `tests/e2e/test_flow_21_child_session_round_trip_and_mergeback_real.py`
  - current live failure:
    - the delegated child tmux session receives raw prompt text with unresolved `{{node_id}}`
    - no durable child-session merge-back result is recorded

- `tests/e2e/test_flow_22_dependency_blocked_sibling_wait_real.py`
  - current live failure:
    - after removing the manual sibling-materialization shortcut, the parent tmux/Codex session still does not create the sibling phases through the runtime command loop
    - the captured pane shows a durable failure summary from `execute_node.run_leaf_prompt` instead of a created sibling set
    - the earlier stricter rerun also showed `node run start` admitting the dependency-blocked sibling before the prerequisite sibling completed once the children had been materialized manually
  - relevant runtime evidence:
    - `notes/logs/e2e/2026-03-10_real_e2e_failure_flow22_dependency_gate.md`

- `tests/e2e/test_e2e_rebuild_cutover_coordination_real.py`
  - canonical failing command:
    - `PYTHONPATH=src python3 -m pytest tests/e2e/test_e2e_rebuild_cutover_coordination_real.py -q -k blocks_upstream_rectify`
  - current live failure:
    - after binding a real primary tmux session, `node rebuild-coordination --scope upstream` still reports `active_or_paused_run`
    - the blocker list does not include a dedicated `active_primary_sessions` entry for the same authoritative runtime state

- `tests/e2e/test_tmux_codex_idle_nudge_real.py`
  - canonical failing command:
    - `PYTHONPATH=src python3 -m pytest tests/e2e/test_tmux_codex_idle_nudge_real.py -q -k stays_quiet_until_daemon_nudges_then_reports_completion`
  - current live failure:
    - after removing the direct `node lifecycle transition --state READY` shortcut from the manual task helper, the task is compiled and admitted through `node run start`
    - but `subtask prompt --node <task>` then returns `active node run not found`
    - the stricter live-run-equivalent version therefore now fails before it can even reach the daemon-originated nudge/reminder assertions
  - conversion status:
    - `rg -n "lifecycle transition|materialize-children|workflow advance|summary register|subtask start|subtask complete|--no-run|/api/subtasks/complete" tests/e2e/test_tmux_codex_idle_nudge_real.py` now returns no matches
    - the file is no longer carrying the shortcut classes being removed in this pass and should now be treated as a fully converted E2E file that is blocked only by real runtime behavior

- `tests/e2e/test_flow_02_compile_or_recompile_workflow_real.py`
  - canonical failing command:
    - `PYTHONPATH=src python3 -m pytest tests/e2e/test_flow_02_compile_or_recompile_workflow_real.py -q`
  - current live failure:
    - after removing `workflow start --no-run`, the test starts a real run and binds a real tmux/provider session
    - `workflow compile --node <id>` then returns daemon conflict `cannot compile a node with an active lifecycle run`
    - the stricter live-run-equivalent version therefore no longer proves recompile behavior through an actual running workflow
  - relevant runtime evidence:
    - `notes/logs/e2e/2026-03-12_workflow_start_and_compile_real_runtime_conversion.md`

- `tests/e2e/test_flow_19_hook_expansion_compile_stage_real.py`
  - canonical failing command:
    - `PYTHONPATH=src python3 -m pytest tests/e2e/test_flow_19_hook_expansion_compile_stage_real.py -q`
  - current live failure:
    - after replacing explicit compile with `node run start`, the task run is admitted
    - `session bind --node <task>` then returns daemon conflict `active durable run not found`
    - the stricter live-run-equivalent version cannot yet prove hook expansion against a real bound run because the run/session contract is inconsistent at bind time
  - relevant runtime evidence:
    - `notes/logs/e2e/2026-03-12_workflow_start_and_compile_real_runtime_conversion.md`

- `tests/e2e/test_flow_15_to_18_default_blueprints_real.py`
  - canonical failing command:
    - `PYTHONPATH=src python3 -m pytest tests/e2e/test_flow_15_to_18_default_blueprints_real.py -q`
  - current live failure:
    - after replacing compile-only proof with `node run start` plus `session bind`, all four blueprint cases hit the same daemon conflict
    - `session bind --node <id>` returns `active durable run not found` immediately after a successful `node run start`
    - the stricter live-run-equivalent version therefore cannot yet prove default blueprint behavior against a real bound run
  - relevant runtime evidence:
    - `notes/logs/e2e/2026-03-12_workflow_start_and_compile_real_runtime_conversion.md`

- `tests/e2e/test_flow_14_project_bootstrap_and_yaml_onboarding_real.py`
  - canonical failing command:
    - `PYTHONPATH=src python3 -m pytest tests/e2e/test_flow_14_project_bootstrap_and_yaml_onboarding_real.py -q`
  - current live failure:
    - after replacing compile-only proof with `node run start` plus `session bind`, the epic run is admitted
    - `session bind --node <id>` then returns daemon conflict `active durable run not found`
    - the stricter live-run-equivalent version cannot yet prove project/YAML onboarding behavior against a real bound session
  - relevant runtime evidence:
    - `notes/logs/e2e/2026-03-12_workflow_start_and_compile_real_runtime_conversion.md`

- `tests/e2e/test_e2e_compile_variants_and_diagnostics.py`
  - canonical failing command:
    - `PYTHONPATH=src python3 -m pytest tests/e2e/test_e2e_compile_variants_and_diagnostics.py -q`
  - current live failure:
    - after replacing compile-only proof with `node run start` plus `session bind`, the authoritative epic run is admitted
    - `session bind --node <id>` then returns daemon conflict `active durable run not found`
    - the stricter live-run-equivalent version therefore cannot yet prove authoritative compile diagnostics against a real bound session before supersede/regenerate candidate checks continue
  - relevant runtime evidence:
    - `notes/logs/e2e/2026-03-12_workflow_start_and_compile_real_runtime_conversion.md`
