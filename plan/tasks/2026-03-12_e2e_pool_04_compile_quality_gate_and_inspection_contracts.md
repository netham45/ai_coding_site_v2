# Task: E2E Pool 04 Compile Quality-Gate And Inspection Contracts

## Goal

Fix the remaining CLI/daemon contract gaps around compile, failed-compile inspection, quality-gate progression, and rebuild blocker reporting.

## Rationale

- These failures are narrower than the session/decomposition pools and can be repaired independently.
- They mostly live in operator-facing inspection and compile surfaces.
- Rationale: The remaining compile and inspection failures form a small CLI/daemon contract cluster that should not wait on the larger runtime pools.
- Reason for existence: This plan exists to isolate the active-run compile, failed-compile inspection, and quality-gate contract fixes into a focused workstream.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/14_F10_ai_facing_cli_command_loop.md`
- `plan/features/15_F11_operator_cli_and_introspection.md`
- `plan/features/16_F12_session_binding_and_resume.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/checklists/16_e2e_real_runtime_gap_closure.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`
- `notes/catalogs/checklists/verification_command_catalog.md`

## Scope

- Database: preserve compile and quality-gate inspection state durably when a run is active or compilation fails.
- CLI: keep compile, source-discovery, quality-chain, and rebuild-coordination commands as the proof surface.
- Daemon: repair compile legality, failed-compile persistence, quality-gate scheduling, and blocker classification.
- YAML: treat YAML as secondary here unless compile/quality behavior depends on builtin workflow policy.
- Prompts: treat prompts as secondary unless a quality-gate entry bug is caused by prompt-stage routing.
- Tests: rerun only the owned compile/inspection narratives until their command contracts match the real runtime expectation.
- Performance: keep reruns short and command-focused so this pool can iterate faster than the tmux-heavy pools.
- Notes: update the checklist whenever the compile or inspection contract changes.

## Owned Files

- `tests/e2e/test_flow_02_compile_or_recompile_workflow_real.py`
- `tests/e2e/test_flow_09_run_quality_gates_real.py`
- `tests/e2e/test_flow_20_compile_failure_and_reattempt_real.py`
- blocker-surface branch of `tests/e2e/test_e2e_rebuild_cutover_coordination_real.py`

## Runtime Focus

- compile legality during active runs
- failed-compile inspection persistence
- quality-gate runtime entry / scheduling
- rebuild-coordination blocker classification

## Primary Failure Signatures

- `cannot compile a node with an active lifecycle run`
- `compiled workflow not found` after failed compile
- `node quality-chain` stays blocked
- active primary session blocker not surfaced in rebuild coordination

## Plan

1. Decide and implement the intended compile contract for active runs.
2. Preserve or expose failed-compile inspection state through operator commands.
3. Fix quality-gate progression so the runtime actually enters the expected chain.
4. Once Pool 01 restores child bindability, rerun rebuild-cutover to verify the blocker list includes the primary-session blocker.

## Status

- 2026-03-12 rerun status:
  - `tests/e2e/test_flow_02_compile_or_recompile_workflow_real.py` now passes. The compile guard now rejects authoritative recompiles whenever the authoritative lifecycle or daemon state still indicates an active run, and the E2E proves the rejection plus the surviving inspection surfaces through the real CLI.
  - `tests/e2e/test_flow_09_run_quality_gates_real.py` now passes. The daemon-owned quality chain now accepts the quality-stage fixture and completes the validate/review/test path with the expected persisted outputs.
  - `tests/e2e/test_flow_20_compile_failure_and_reattempt_real.py` now passes. Failed compile state remains inspectable through `workflow source-discovery`, and the repaired compile path returns the node to compiled lifecycle state.
  - `tests/e2e/test_e2e_rebuild_cutover_coordination_real.py -q -k blocks_upstream_rectify` now passes. The live run binds successfully and the upstream rebuild-coordination payload now reports both `active_or_paused_run` and `active_primary_sessions`.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/e2e/test_flow_02_compile_or_recompile_workflow_real.py -q
PYTHONPATH=src python3 -m pytest tests/e2e/test_flow_09_run_quality_gates_real.py -q
PYTHONPATH=src python3 -m pytest tests/e2e/test_flow_20_compile_failure_and_reattempt_real.py -q
PYTHONPATH=src python3 -m pytest tests/e2e/test_e2e_rebuild_cutover_coordination_real.py -q -k blocks_upstream_rectify
```

## Exit Criteria

- active-run compile behavior is explicit and matches the E2E contract
- failed-compile inspection surfaces remain usable
- quality-gate runtime entry works for the owned narrative
- rebuild-cutover blocker reporting is correct once bind succeeds
