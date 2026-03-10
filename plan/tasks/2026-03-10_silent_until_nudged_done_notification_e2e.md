# Task: Silent-Until-Nudged Done Notification E2E

## Goal

Define and then implement a real end-to-end test proving this exact runtime narrative:

- start a real workflow and bind a real tmux/Codex primary session
- give the AI a prompt that explicitly tells it not to run the done-notification CLI path until nudged
- let the AI go intentionally quiet long enough to cross the real idle timeout
- issue or observe the daemon-owned nudge through the real CLI/daemon/runtime path
- confirm the nudge reminds the AI to perform the blocked action
- confirm the live tmux/Codex session then emits the required done-notification CLI commands from inside the session rather than from the outer test process

## Rationale

- Rationale: The repository already has real tmux/Codex launch coverage and bounded nudge behavior, but it does not yet prove the specific adversarial flow where the AI is instructed to withhold completion signaling until an idle nudge arrives and then completes only because of that reminder.
- Reason for existence: This task exists to create the exact E2E proof for the silent-until-nudged behavior the runtime is supposed to supervise, while documenting the current prompt/runtime mismatches that must be resolved for the test to be honest and repeatable.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/13_F09_node_run_orchestration.md`
- `plan/features/14_F10_ai_facing_cli_command_loop.md`
- `plan/features/16_F12_session_binding_and_resume.md`
- `plan/features/18_F13_idle_detection_and_nudge_behavior.md`
- `plan/features/39_F12_tmux_session_manager.md`
- `plan/features/46_F10_ai_cli_bootstrap_and_work_retrieval_commands.md`
- `plan/features/50_F12_session_attach_resume_and_control_commands.md`
- `plan/e2e_tests/03_e2e_session_recovery_and_child_runtime.md`
- `plan/e2e_tests/06_e2e_feature_matrix.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/runtime/tmux_session_lifecycle_spec_v1.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/specs/prompts/prompt_library_plan.md`
- `notes/planning/implementation/idle_detection_and_nudge_behavior_decisions.md`
- `notes/planning/implementation/idle_screen_polling_and_classifier_decisions.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`
- `notes/catalogs/checklists/verification_command_catalog.md`

## Scope

- Database: verify the durable session events, prompt history, summary history, attempt state, and run-state transitions that explain the quiet period, nudge event, and post-nudge done notification.
- CLI: keep the done-notification contract on real CLI commands emitted from inside the tmux/Codex session, and use the outer test process only for operator-visible inspection and the explicit `session nudge --node <id>` trigger if autonomous polling is still out of scope.
- Daemon: exercise real idle classification, real nudge handling, and the real run/session mutation path without direct DB forcing or synthetic lifecycle shortcuts.
- YAML: use the compiled workflow and runtime-policy surface honestly, and add a documented test-only workflow/prompt asset only if the default execution prompt cannot represent the silent-wait behavior without contradicting the product contract.
- Prompts: define a deterministic workload prompt that explicitly instructs the AI to withhold the done-notification commands until nudged, then perform the exact required command sequence after the reminder.
- Tests: extend the real tmux/Codex E2E family with one dedicated scenario for the silent-until-nudged flow and any supporting helper assertions needed at the real tmux boundary.
- Performance: keep the idle timeout and polling thresholds low enough for targeted reruns while still exercising the real classifier and avoiding fake timer shortcuts.
- Notes: update runtime, prompt, and verification notes if the current contracts are too ambiguous or contradictory to support a deterministic real E2E for this scenario.

## Plan

### Phase 1: Freeze the exact done-notification contract

1. Reconcile what “notify it is done” means in the current runtime, because the existing contract separates `summary register`, `subtask complete`, and `workflow advance`.
2. Decide which command sequence the E2E must observe from inside tmux before the node is considered honestly “done” for this scenario.
3. Record that contract in the plan, adjacent notes, or prompt asset so the test does not pass on a weaker interpretation than the product uses.

Exit criteria:

- the exact post-nudge command sequence is explicit
- the planned assertions match the real runtime contract rather than an informal shorthand

### Phase 2: Reconcile the prompt contract with the requested silent behavior

1. Compare the requested scenario against the current default execution prompt, which currently says “do not stall silently.”
2. Decide whether to:
   - add a dedicated test-only prompt/workload asset for this adversarial flow
   - or revise the runtime/prompt notes so the behavior is supported more generally
3. Keep the behavior documented; do not hide the contradiction inside fixture-only prompt injection.

Exit criteria:

- the repository has a documented way to instruct the AI to stay quiet until nudged
- the silent-wait behavior is no longer in undocumented conflict with the default execution contract

### Phase 3: Design a deterministic live workload

1. Build a workload that can be executed by a real tmux/Codex session and is expected to:
   - start normally
   - intentionally go quiet
   - remain incomplete before the nudge
   - complete only after the nudge text arrives
2. Ensure the workload leaves operator-visible evidence in tmux output and durable CLI-visible evidence in prompt/session history.
3. Keep the workload minimal so failures can be diagnosed from pane capture and session events.

Exit criteria:

- one reproducible workload exists for the silent -> nudged -> done path
- the workload can fail with useful diagnostics rather than timing out opaquely

### Phase 4: Extend the tmux E2E helpers for causal assertions

1. Add helper assertions that can distinguish:
   - pre-nudge quiet state
   - durable nudge event
   - post-nudge CLI activity originating from inside tmux
2. Capture enough pane text and session-event history to prove the outer test process did not emit the done-notification commands on behalf of the session.
3. Keep the strongest proof on real tmux and operator-visible CLI surfaces.

Exit criteria:

- the helper layer can prove “quiet before nudge” and “done-notification commands after nudge”
- failures print the relevant pane and session-event diagnostics

### Phase 5: Implement the real E2E narrative

1. Start a real workflow with low idle thresholds and bind a real tmux/Codex primary session.
2. Wait until the session is active, then confirm it stops short of the done-notification path.
3. Wait for real idle classification.
4. Trigger the real nudge through `session nudge --node <id>` unless autonomous background nudging becomes active first.
5. Assert that:
   - a durable nudge event is recorded
   - the tmux pane changes after the nudge
   - the post-nudge pane/CLI activity includes the agreed done-notification command sequence
   - the run/session state becomes complete through the real runtime path

Exit criteria:

- one real E2E test proves the exact requested silent-until-nudged behavior
- the post-nudge completion signal is session-originated, not test-originated

### Phase 6: Add adversarial assertions and negative checks

1. Assert the done-notification command sequence was not observed before the nudge.
2. Assert the session was actually classified idle before the nudge rather than merely slow.
3. Assert the nudge event text/path matches the idle-nudge recovery prompt used by the daemon.
4. If the session exits early or never emits the commands, fail with clear diagnostics and record the gap in notes/checklists rather than weakening the test.

Exit criteria:

- the test distinguishes the causal ordering of quiet -> idle -> nudge -> done
- early or ambiguous completion cannot produce a false pass

### Phase 7: Reconcile notes, logs, and verification surfaces

1. Update any notes that currently overstate or contradict the supported prompt behavior.
2. Record the implementation and proving result in the development log with honest status values.
3. Update checklist or E2E-mapping surfaces only if the new test actually lands and runs.

Exit criteria:

- the plan, notes, and logs describe the exact proof boundary honestly
- no authoritative document claims this flow is covered before the test actually passes

## Verification

- Document-family checks after plan creation: `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py -q`
- Current runtime and tmux baseline review: `python3 -m pytest -q tests/unit/test_session_records.py tests/integration/test_session_cli_and_daemon.py tests/e2e/test_tmux_codex_idle_nudge_real.py`
- Future targeted E2E execution after implementation: `python3 -m pytest -q tests/e2e/test_tmux_codex_idle_nudge_real.py -k silent_until_nudged`
- Future document consistency rerun if notes or checklist surfaces change: `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_verification_command_docs.py -q`

## Exit Criteria

- The repository has a governing task plan for the exact silent-until-nudged done-notification E2E scenario.
- The plan explicitly handles the current mismatch between the default execution prompt and the requested silent-wait behavior.
- The plan freezes the exact done-notification CLI contract the test must observe after nudging.
- The plan keeps the strongest proof on the real tmux/Codex, CLI, daemon, and durable runtime surfaces.
