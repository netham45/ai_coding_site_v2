# Task: Refactor E2E Tests To Real Runtime Only

## Goal

Remove fake or simulated proving paths from the `tests/e2e/` surface and refactor the suite so that E2E tests mean exactly “run real command, verify real state, repeat” across the real daemon, real CLI, real database, and real runtime resources required by the feature, without operator-driven subtask progression standing in for AI/runtime execution.

## Rationale

- Rationale: The current E2E surface still contains a fake default session backend, direct DB/API shortcut assertions, placeholder-style tests, and operator-driven workflow advancement that violate the repository’s own real-E2E doctrine.
- Reason for existence: This task exists to make the `tests/e2e/` family defensible as true end-to-end proof rather than a mix of real flows, helper-assisted checks, and simulated runtime shortcuts.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/14_F10_ai_facing_cli_command_loop.md`
- `plan/features/15_F11_operator_cli_and_introspection.md`
- `plan/features/16_F12_session_binding_and_resume.md`
- `plan/features/23_F18_child_merge_and_reconcile_pipeline.md`
- `plan/features/24_F19_regeneration_and_upstream_rectification.md`
- `plan/features/35_F36_auditable_history_and_reproducibility.md`
- `plan/features/39_F12_tmux_session_manager.md`
- `plan/features/50_F12_session_attach_resume_and_control_commands.md`
- `plan/features/70_F19_live_rebuild_cutover_coordination.md`
- `plan/features/71_F11_live_git_merge_and_finalize_execution.md`
- `plan/e2e_tests/00_e2e_feature_generation_strategy.md`
- `plan/e2e_tests/01_e2e_harness_and_command_foundation.md`
- `plan/e2e_tests/02_e2e_core_orchestration_and_cli_surface.md`
- `plan/e2e_tests/03_e2e_session_recovery_and_child_runtime.md`
- `plan/e2e_tests/04_e2e_quality_docs_provenance_audit.md`
- `plan/e2e_tests/05_e2e_git_rectification_and_cutover.md`
- `plan/e2e_tests/06_e2e_feature_matrix.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/contracts/persistence/compile_failure_persistence.md`
- `notes/contracts/runtime/session_recovery_appendix.md`
- `notes/contracts/parent_child/child_session_mergeback_contract.md`
- `notes/planning/implementation/real_e2e_flow_contract_phase1_decisions.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/specs/database/database_schema_spec_v2.md`
- `notes/specs/git/git_rectification_spec_v2.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`

## Scope

- Database: remove direct SQL-based proof from the real E2E family and replace it with operator-visible or CLI-visible state checks.
- CLI: keep the CLI subprocess path as the primary command surface for all E2E narratives.
- Daemon: remove direct daemon helper/API proof as the strongest claim in E2E tests and keep the E2E family centered on CLI-driven runtime narratives.
- YAML: keep YAML-linked proof on real compile/runtime commands and remove helper-only validation as E2E completion proof.
- Prompts: ensure prompt-linked E2E proof uses actual prompt delivery/history rather than direct record inspection shortcuts.
- Tests: refactor invalid E2E tests in place, remove placeholder behavior, eliminate operator-driven subtask/run advancement as E2E proof, and tighten marker/command coverage to reflect only real-runtime suites.
- Performance: preserve per-test DB isolation while accepting that tmux/git-backed real E2E may need explicit gating and staged execution.
- Notes: update command catalogs, execution policy, and any E2E plan/checklist surfaces that overstate current realness.

## Plan

### Phase 1: Fix the shared harness contract

1. Remove the fake default session backend from the shared E2E harness.
2. Make session backend selection explicit per suite:
   - `tmux` for session/recovery flows
   - real git where git is part of the story
   - no silent fallback to fake backends
3. Update `verification_command_catalog.md` and `e2e_execution_policy.md` so command tiers reflect the new gating requirements.

### Phase 2: Triage the current E2E inventory

1. Classify each `tests/e2e/*.py` file into one of:
   - valid real E2E
   - real command flow but incomplete due shortcut mutations
   - helper-assisted and must be rewritten around real runtime proof
   - placeholder/skeleton and must be rewritten in place before the E2E family can be described as real
2. Rewrite any file that still contains:
   - direct SQL reads as primary proof
   - direct daemon HTTP requests as primary proof
   - intentional `pytest.fail(...)` placeholders
   - lifecycle transition shortcuts standing in for real flow progression
   - operator-issued `subtask start`, `subtask complete`, `subtask fail`, `summary register`, `session pop`, or `workflow advance` calls that stand in for AI/runtime execution instead of observing it

### Phase 3: Replace shortcut flows with real narratives

1. Replace lifecycle-transition shortcuts in failure/escalation and git/finalize flows with actual subtask/run progression.
2. Replace child-result shortcuts with real child execution and real mergeback where the feature depends on that boundary.
3. Replace “create child then force state” flows with actual parent materialization, child scheduling, child execution, and parent observation.
4. Replace operator-driven subtask progression with real runtime execution:
   - no manual `subtask start`
   - no manual `subtask complete`
   - no manual `subtask fail`
   - no manual `summary register` as a stand-in for generated output
   - no manual `workflow advance` unless the runtime itself has already completed the prerequisite step and the command is the actual operator-facing contract being tested

### Phase 4: Rebuild the session/runtime family on real resources

1. Introduce explicit tmux-backed session E2E suites for session binding, stale detection, resume, and control commands.
2. Keep provider-backed flows separate and gated instead of silently downgraded.
3. Ensure session-dependent flows no longer share the fake default backend path.

### Phase 5: Rebuild the git/rectification family on real repos

1. Convert finalize/merge/rectify/cutover flows to prove actual working-tree and branch behavior without lifecycle forcing.
2. Require real git repo bootstrap, real commits, real merge conflict creation where applicable, and runtime-visible readiness/blocker checks.
3. Split any residual staging-only proof into integration tests rather than E2E.

### Phase 6: Finish invalid E2E artifact rewrites

1. Rewrite `test_e2e_full_epic_tree_runtime_real.py` and any similar files in place so they no longer use direct DB/API helpers and no longer end in intentional failure.
2. Keep any DB/API-heavy assertions in separate integration or audit-oriented coverage without using them as the real-E2E claim.
3. Keep the E2E directory reserved for passing, runtime-complete narratives only.

### Phase 7: Re-prove and restate the suite honestly

1. Rerun the non-gated real-E2E command set after the harness cleanup.
2. Add or update gated commands for tmux/git/provider-backed families.
3. Update logs, plan docs, command docs, and E2E status surfaces so they no longer overclaim realness.

## Verification

- Review/audit evidence: `rg -n "session_backend|fake|daemon_bridge|app_client|create_engine\\(|_db_|request\\(|pytest\\.fail|lifecycle\", \"transition" tests/e2e tests/helpers/e2e.py tests/fixtures/e2e.py`
- Review/audit evidence 2: `rg -n "subtask\", \"(start|complete|fail)|summary\", \"register|session\", \"pop|workflow\", \"advance" tests/e2e`
- Document-schema targeted suite: `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py -q`
- Post-refactor proving target 1: `python3 -m pytest tests/e2e -q -m 'e2e_real and not requires_tmux and not requires_git and not requires_ai_provider'`
- Post-refactor proving target 2: gated reruns for tmux/git/provider families from `notes/catalogs/checklists/e2e_execution_policy.md`

## Exit Criteria

- The shared E2E harness no longer defaults to a fake backend.
- No file in `tests/e2e/` relies on direct DB/API shortcut proof as its primary E2E claim.
- No file in `tests/e2e/` intentionally fails as a placeholder.
- Session, child, git, rectification, and cutover narratives use real runtime progression rather than lifecycle forcing, staged durable-state shortcuts, or operator-driven subtask advancement.
- No file in `tests/e2e/` manually drives workflow progress with `subtask start`, `subtask complete`, `subtask fail`, `summary register`, `session pop`, or equivalent result injection when the claimed behavior is supposed to come from the live runtime.
- The command catalog and E2E execution policy describe only truly real E2E suites.
