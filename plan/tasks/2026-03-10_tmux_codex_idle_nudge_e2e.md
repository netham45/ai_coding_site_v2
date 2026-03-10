# Task: Tmux Codex Idle And Nudge E2E

## Goal

Define the implementation plan for a real tmux-backed end-to-end test family that proves the actual runtime sequence:

- create a real tmux session
- launch a real Codex process inside that tmux session
- run a real prompt through the Codex session
- observe the live tmux session go idle through real pane polling
- issue a real `session nudge` command through the CLI/daemon boundary
- confirm the nudged session becomes active again
- wait for the same real session to go idle again without using fake tmux adapters or synthetic progress injection

## Rationale

- Rationale: The current tmux/session test surface proves some real tmux creation and stale-session recovery, but the idle and nudge semantics are still strongest at the fake-adapter layer and the launch path still defaults to an interactive shell instead of Codex.
- Reason for existence: This task exists to define the exact implementation phases needed to replace shell-placeholder and fake-adapter proof with a defensible real-runtime tmux/Codex E2E narrative.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/13_F09_node_run_orchestration.md`
- `plan/features/14_F10_ai_facing_cli_command_loop.md`
- `plan/features/16_F12_session_binding_and_resume.md`
- `plan/features/17_F34_provider_agnostic_session_recovery.md`
- `plan/features/18_F13_idle_detection_and_nudge_behavior.md`
- `plan/features/39_F12_tmux_session_manager.md`
- `plan/features/46_F10_ai_cli_bootstrap_and_work_retrieval_commands.md`
- `plan/features/50_F12_session_attach_resume_and_control_commands.md`
- `plan/e2e_tests/01_e2e_harness_and_command_foundation.md`
- `plan/e2e_tests/03_e2e_session_recovery_and_child_runtime.md`
- `plan/e2e_tests/06_e2e_feature_matrix.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/reconcilliation/04_tmux_codex_session_launch_reconciliation.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/specs/prompts/prompt_library_plan.md`
- `notes/contracts/runtime/session_recovery_appendix.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`
- `notes/planning/implementation/full_real_end_to_end_flow_hardening_plan.md`
- `notes/planning/implementation/idle_detection_and_nudge_behavior_decisions.md`
- `notes/planning/implementation/idle_screen_polling_and_classifier_decisions.md`

## Scope

- Database: define and verify the durable records needed to explain real tmux/Codex launch, idle classification, nudge events, repeated idle detection, and any follow-on completion or failure outcomes.
- CLI: keep the real CLI subprocess path as the operator and AI-facing control surface for prompt retrieval, `session bind`, `session show-current`, `session nudge`, and any completion or failure commands emitted from inside tmux.
- Daemon: implement the real tmux/Codex launch path, real idle classification over live tmux state, and durable nudge handling without falling back to fake adapters for the strongest proof.
- YAML: keep prompt/stage selection and runtime policy declarative while leaving tmux launch orchestration, idle inspection, and nudge execution in code.
- Prompts: define the deterministic prompt payloads and nudge prompt surfaces needed for reproducible real E2E behavior.
- Tests: add bounded support where useful, but make the strongest proof a real tmux/Codex E2E suite that exercises live pane changes and repeated idle detection.
- Performance: keep the real tmux polling and idle waits bounded enough for targeted reruns while still proving the real idle threshold and repeated-idle behavior honestly.
- Notes: update runtime, recovery, nudge, and verification-command notes so they match the implemented tmux/Codex behavior and the actual proving level.

## Plan

### Phase 1: Reconcile the tmux launch contract

1. Replace the current shell-only tmux launch contract with a Codex-aware launch contract for real session E2E coverage.
2. Decide the exact fresh-session bootstrap command and any resume command needed for dead-session recovery.
3. Define what durable launch metadata must be recorded so operators can inspect whether a real Codex process, not a shell placeholder, was started.

Exit criteria:

- the launch contract explicitly targets Codex inside tmux
- the durable session metadata needed for launch inspection is identified
- the notes and E2E expectations stop treating an interactive shell as valid proof for the real runtime path

### Phase 2: Add a deterministic test workload for live tmux/Codex behavior

1. Define one reproducible prompt/workload that can be executed by a real Codex session and observed through tmux.
2. Ensure the workload has a detectable active phase, an idle phase, a post-nudge active phase, and a second idle phase.
3. If the raw product prompt surface is too nondeterministic for repeated idle/nudge proof, introduce a documented test harness prompt or wrapper contract rather than relying on manual timing luck.

Exit criteria:

- one documented workload can reliably produce the active -> idle -> nudged -> idle-again sequence
- the workload’s output can be inspected through pane text and/or durable runtime surfaces
- any test-only constraints are documented rather than hidden in fixtures

### Phase 3: Extend the real E2E harness for tmux/Codex inspection

1. Extend the real daemon harness and helper layer with explicit tmux inspection helpers for:
   - session existence
   - pane capture
   - repeated pane polling
   - bounded wait-for-idle
   - bounded wait-for-post-nudge-activity
2. Keep all helper behavior at the real tmux/process boundary; no fake tmux adapters may be used in the E2E proof path.
3. Ensure cleanup logic is strong enough to remove live tmux sessions even after failed or interrupted E2E runs.

Exit criteria:

- the E2E fixture can observe real tmux pane changes and repeated idle transitions
- cleanup is deterministic enough for repeated local reruns
- the helper layer makes the real tmux assertions readable without weakening the proof boundary

### Phase 4: Implement the primary bind-and-launch E2E narrative

1. Add a dedicated real E2E suite for primary-session bind and launch through the real daemon, real CLI, real database, and real tmux path.
2. Assert that:
   - a tmux session is created
   - the pane shows a real Codex launch rather than a shell placeholder
   - the intended prompt/workload is running
   - the session surfaces expose inspectable metadata consistent with the launch
3. Keep direct DB or direct API helper inspection out of the strongest narrative unless used only as secondary diagnostics.

Exit criteria:

- one real E2E test proves tmux session creation and Codex launch through the real command path
- the strongest assertions are operator-visible or tmux-visible rather than helper-injected

### Phase 5: Implement the real idle-and-nudge E2E narrative

1. Add the main idle/nudge E2E flow on top of the live tmux/Codex session:
   - wait for first idle classification
   - issue `session nudge --node <id>` through the CLI
   - assert durable nudge visibility
   - assert the pane shows post-nudge activity
2. Confirm the nudge did not merely mutate durable state while the tmux session remained unchanged.
3. Keep the proof centered on real pane change plus real CLI/daemon-visible nudge state.

Exit criteria:

- the test proves a real live session reaches idle and is actually nudged
- post-nudge activity is visible from real tmux output or another real operator-facing surface
- the nudge path is durably inspectable

### Phase 6: Implement repeated-idle proof and follow-on runtime cases

1. Extend the E2E narrative or add an adjacent suite to prove the same session becomes idle again after the nudge-driven activity subsides.
2. Decide whether repeated-nudge and escalation-to-pause belong in the same suite or a separate gated suite.
3. Define separate follow-on E2E cases for:
   - session-originated completion notification
   - session-originated failure/error notification
4. Keep completion/failure proof honest by requiring the commands to originate from the process running inside tmux rather than from the outer test process.

Exit criteria:

- the real runtime proves the idle -> nudge -> idle-again loop
- the completion and failure follow-on E2E targets are explicitly assigned
- no synthetic outer-process shortcut is used as the strongest proof for done/error behavior

### Phase 7: Reconcile notes, checklists, and canonical commands

1. Update the relevant notes, plan/checklist surfaces, and execution-policy docs to reflect the real tmux/Codex E2E coverage and any remaining gaps.
2. Add or update the checklist entries that track tmux/session/idle verification status across database, CLI, daemon, YAML, prompts, bounded tests, and real E2E tests.
3. Record the implementation and proving result in the development log with honest status values if any follow-on cases remain partial.

Exit criteria:

- authoritative docs describe the real tmux/Codex E2E surface accurately
- checklist status does not overclaim beyond the actual proving layer
- canonical verification commands are written down for the new suite family

## Verification

- Document-family checks after plan creation: `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py -q`
- Current surface audit before implementation: `python3 -m pytest -q tests/unit/test_session_harness.py tests/unit/test_session_manager.py tests/unit/test_session_records.py tests/e2e/test_flow_07_pause_resume_and_recover_real.py`
- Future bounded proof target after implementation starts: `python3 -m pytest tests/unit/test_session_manager.py tests/unit/test_session_records.py tests/integration/test_session_cli_and_daemon.py -q`
- Future real tmux/Codex E2E target after implementation starts: `python3 -m pytest tests/e2e/test_flow_07_pause_resume_and_recover_real.py tests/e2e/test_tmux_codex_idle_nudge_real.py -q`
- Future gated follow-on runtime proof: `python3 -m pytest tests/e2e/test_tmux_codex_completion_and_failure_real.py -q`

## Exit Criteria

- The repository has a governing task plan for real tmux/Codex idle-and-nudge E2E implementation.
- The plan defines explicit phases for launch, workload design, harness work, first idle detection, nudge behavior, and second idle detection.
- The plan keeps completion and failure proof on the tmux-session-originated runtime boundary rather than outer-process shortcuts.
- The affected systems, note updates, and canonical verification commands are explicit before implementation begins.
