# Task: E2E Pool 01 Run Bind And Durable Session Visibility

## Goal

Fix the runtime contract where `node run start` succeeds but the corresponding real `session bind --node <id>` fails with `active durable run not found`.

## Rationale

- This is the most repeated blocker across the remaining real E2E failures.
- It spans child finalize/merge flows, rebuild-cutover, blueprint runs, compile variants, and parts of incremental parent merge.
- One fix should unlock many files at once.
- Rationale: A single run/bind visibility defect is blocking a broad set of otherwise unrelated E2E narratives.
- Reason for existence: This plan exists to give one agent ownership of the repeated `active durable run not found` failure family.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/15_F11_operator_cli_and_introspection.md`
- `plan/features/16_F12_session_binding_and_resume.md`
- `plan/features/39_F12_tmux_session_manager.md`
- `plan/features/50_F12_session_attach_resume_and_control_commands.md`
- `plan/features/71_F11_live_git_merge_and_finalize_execution.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/checklists/16_e2e_real_runtime_gap_closure.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/specs/runtime/tmux_session_lifecycle_spec_v1.md`
- `notes/contracts/parent_child/child_session_mergeback_contract.md`

## Scope

- Database: inspect durable node-run and session-binding records for the admitted-but-unbindable run cases.
- CLI: keep `node run start` and `session bind` as the proving surface for the owned files.
- Daemon: repair the admission-to-bind visibility contract and any child-run ownership defects behind it.
- YAML: treat YAML as not the primary fix surface here unless bind failure is caused by compile/runtime metadata gaps.
- Prompts: ensure prompt/session metadata remains attached to the durable run rows bind expects to find.
- Tests: rerun only the owned bind-failure narratives until they fail for a different reason or pass.
- Performance: keep reruns focused on the smallest bind-failure narratives first.
- Notes: update the gap checklist and development logs whenever a bind failure changes class.

## Owned Files

- `tests/e2e/test_flow_11_finalize_and_merge_real.py`
- `tests/e2e/test_e2e_live_git_merge_and_finalize_real.py`
- `tests/e2e/test_e2e_rebuild_cutover_coordination_real.py`
- `tests/e2e/test_e2e_incremental_parent_merge_real.py`
- `tests/e2e/test_flow_14_project_bootstrap_and_yaml_onboarding_real.py`
- `tests/e2e/test_flow_15_to_18_default_blueprints_real.py`
- `tests/e2e/test_flow_19_hook_expansion_compile_stage_real.py`
- `tests/e2e/test_flow_20_compile_failure_and_reattempt_real.py`
- `tests/e2e/test_e2e_compile_variants_and_diagnostics.py`

## Runtime Focus

- durable node-run row creation
- run-to-session visibility timing
- `session bind` lookup rules
- child run admission and bindability
- run ownership after `git finalize-node`

## Primary Failure Signatures

- `active durable run not found`
- `session bind --node <id>` fails immediately after `node run start`
- child workflows admitted by daemon but not bindable through the operator surface

## Plan

1. Identify the daemon/runtime read path that `session bind` uses to find the active durable run.
2. Compare that path against the write path used by `node run start` and post-finalize progression.
3. Repair the durable-run visibility contract so bind sees the exact run that admission created.
4. Rerun the smallest representative file first:
   - `tests/e2e/test_flow_19_hook_expansion_compile_stage_real.py`
5. Then rerun the broader dependent files in this order:
   - `tests/e2e/test_flow_15_to_18_default_blueprints_real.py`
   - `tests/e2e/test_e2e_compile_variants_and_diagnostics.py`
   - `tests/e2e/test_flow_11_finalize_and_merge_real.py`
   - `tests/e2e/test_e2e_live_git_merge_and_finalize_real.py`
   - `tests/e2e/test_e2e_rebuild_cutover_coordination_real.py`
   - the bind-related branches of `tests/e2e/test_e2e_incremental_parent_merge_real.py`
6. Record any remaining non-bind failures after the bind contract is fixed.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/e2e/test_flow_19_hook_expansion_compile_stage_real.py -q
PYTHONPATH=src python3 -m pytest tests/e2e/test_flow_15_to_18_default_blueprints_real.py -q
PYTHONPATH=src python3 -m pytest tests/e2e/test_e2e_compile_variants_and_diagnostics.py -q
PYTHONPATH=src python3 -m pytest tests/e2e/test_flow_11_finalize_and_merge_real.py -q
PYTHONPATH=src python3 -m pytest tests/e2e/test_e2e_live_git_merge_and_finalize_real.py -q -k verifies_parent_repo_contents
PYTHONPATH=src python3 -m pytest tests/e2e/test_e2e_rebuild_cutover_coordination_real.py -q
PYTHONPATH=src python3 -m pytest tests/e2e/test_e2e_incremental_parent_merge_real.py -q -k "grouped_cutover_rematerializes_authoritative_child or unblocks_dependent_child_only_after_merge_and_refresh or conflict_resolution_unblocks_dependent_child_real"
```

## Exit Criteria

- `session bind --node <id>` no longer fails with `active durable run not found` immediately after real admission in the owned files
- any remaining failures in those files are downstream runtime issues, not the run/bind visibility contract
