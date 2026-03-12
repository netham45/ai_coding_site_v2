# Task: Tmux Session Supervision, Restart, And Run Failure Plan

## Goal

Define the implementation plan required to make the daemon continuously supervise tracked tmux sessions, recreate them when safe, and fail unfinished tasks when recovery cannot succeed.

## Rationale

- Rationale: The current codebase can bind and explicitly recover tmux-backed primary sessions, but it does not have a daemon-owned supervision loop that ensures tracked sessions stay alive once work is underway.
- Reason for existence: This task exists to close the gap between the documented tmux recovery model and the actual runtime posture by turning recovery from an operator-triggered path into continuous daemon-owned enforcement.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/16_F12_session_binding_and_resume.md`: session ownership and single-authoritative-primary-session invariants still govern the supervision loop.
- `plan/features/17_F34_provider_agnostic_session_recovery.md`: the supervision loop should reuse the existing recovery classification and replacement semantics rather than inventing a second recovery path.
- `plan/features/18_F13_idle_detection_and_nudge_behavior.md`: idle nudging already runs in a background loop and is the closest existing supervision seam.
- `plan/features/39_F12_tmux_session_manager.md`: tmux session creation and identity remain the concrete transport/backend being supervised.
- `plan/features/50_F12_session_attach_resume_and_control_commands.md`: CLI and operator surfaces must expose the new autonomous supervision evidence and failure cause cleanly.

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/specs/runtime/tmux_session_lifecycle_spec_v1.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/contracts/runtime/session_recovery_appendix.md`
- `notes/catalogs/checklists/feature_checklist_backfill.md`
- `plan/checklists/05_tmux_session_and_idle_verification.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`

## Scope

- Database: reuse durable session rows and session events for supervision evidence; add any missing run/session failure event recording needed to explain restart attempts, restart rejection, and terminal recovery failure.
- CLI: preserve existing `session show`, `session events`, `node recovery-status`, and run-inspection surfaces, but extend them so operators can see that supervision attempted restart automatically and why a run was failed when recovery was impossible.
- Daemon: add a daemon-owned background supervision loop for active primary sessions, guard it with runnable-state checks, attempt replacement only for eligible nodes/runs, and fail unfinished runs when restart cannot be completed safely.
- YAML: no YAML-owned orchestration decisions should be added; polling cadence and thresholds may remain runtime config, but restart legality and terminal failure rules stay code-owned.
- Prompts: no new semantic prompt family is required for the planning pass, but implementation must confirm that fresh replacement launches and any recovery/failure guidance prompts remain aligned with the real daemon behavior.
- Tests: add bounded unit/integration proof for supervision candidate selection, restart attempt behavior, replacement failure handling, and run-failure transitions; add real tmux E2E proof for killed-session replacement and unrecoverable-session failure.
- Performance: ensure the new supervision loop does not duplicate expensive polling or hot-spin alongside the existing idle-nudge loop; prefer one shared candidate scan or one shared session snapshot pass per iteration.
- Notes: update tmux lifecycle, runtime loop, checklist, and feature-checklist surfaces so the autonomous supervision contract and its limits are explicit.

## Verification

Canonical verification commands for this planning task:

```bash
python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py -q
```

Candidate verification commands for the later implementation:

```bash
python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py -q
python3 -m pytest tests/unit/test_session_records.py tests/unit/test_session_manager.py tests/unit/test_daemon_orchestration.py tests/unit/test_run_orchestration.py -q
python3 -m pytest tests/integration/test_session_cli_and_daemon.py tests/integration/test_daemon.py -q
python3 -m pytest tests/e2e/test_flow_07_pause_resume_and_recover_real.py tests/e2e/test_tmux_codex_idle_nudge_real.py -q
```

Those implementation commands are targets for the follow-on coding pass, not a claim that supervision is already implemented.

## Exit Criteria

- A governing task plan exists for the tmux-session supervision gap requested in this review.
- The plan states clearly that the current runtime lacks continuous daemon-owned session supervision and relies on explicit bind/recover paths instead.
- The plan defines the eligibility rule for autonomous restart attempts so tmux sessions are only created or replaced for runnable or already-active work, not for terminal or blocked nodes.
- The plan defines the terminal behavior that an unfinished task/run becomes `FAILED` when supervision cannot recreate or rebind the required session safely.
- The plan distinguishes note updates, bounded proof, and real tmux E2E proof.
- The governing task plan is listed in `plan/tasks/README.md`.
- The paired development log exists and cites this task plan.

## Proposed Execution Stages

### Stage 1: Supervision Contract And Eligibility Audit

- Audit the current session candidate logic in `auto_nudge_idle_primary_sessions(...)`, `bind_primary_session(...)`, and `recover_primary_session(...)`.
- Define one daemon-owned candidate selector for supervised primary sessions keyed by active durable run plus authoritative node lifecycle.
- Freeze the eligibility rule in code and notes:
  - supervise only authoritative primary sessions for unfinished work
  - only create or replace tmux sessions when the node/run is still runnable or already in progress
  - never auto-start sessions for `COMPLETE`, `FAILED_TO_PARENT`, `CANCELLED`, `SUPERSEDED`, or other non-runnable states

### Stage 2: Daemon Background Supervision Loop

- Add a dedicated session-supervision helper in `session_records.py` that:
  - enumerates supervised primary-session candidates
  - classifies each candidate as healthy, stale, lost, missing, ambiguous, or non-resumable
  - reuses the current recovery/replacement helpers wherever possible
- Wire a new background loop into `src/aicoding/daemon/app.py` rather than depending on manual `session resume` or `node recovery-status` calls.
- Avoid split-brain between idle nudging and restart supervision by reusing candidate discovery or merging the scans if that keeps the polling cost and logic cleaner.

### Stage 3: Failure Escalation On Unrecoverable Session Loss

- Define one daemon-owned failure path for unfinished runs when restart cannot happen:
  - tmux replacement launch fails
  - recovery is rejected for a run that is still unfinished but no safe session can exist
  - supervision finds an invariant violation that blocks safe automatic recovery and policy requires terminal failure instead of silent retry
- Update run/session state atomically so the result is inspectable:
  - mark the stale session row lost or invalidated
  - record a durable supervision/recovery-failed session event
  - mark the active run `FAILED`
  - mirror lifecycle visibility to `FAILED_TO_PARENT` when appropriate
- Keep the failure reason explicit in the durable event payload and run summary.

### Stage 4: CLI And Inspection Surface Alignment

- Extend `session show`, `session events`, and `node recovery-status` payloads with any missing supervision evidence fields.
- Ensure operator-visible outputs can answer:
  - was the session supervised automatically
  - was restart attempted
  - why was replacement allowed or rejected
  - why was the unfinished run failed
- Keep the daemon as the authority; the browser/CLI should report daemon legality and cause, not recreate supervision logic client-side.

### Stage 5: Bounded Proof

- Add unit coverage for:
  - supervision candidate filtering
  - lost-session detection in the background path
  - successful replacement of a killed session
  - replacement launch failure causing durable run failure
  - guardrails that skip terminal or non-runnable nodes
- Add integration coverage that exercises the real daemon background loop with the fake session backend so the behavior is proven without manual API calls.

### Stage 6: Real Tmux E2E Proof

- Extend the real tmux recovery E2E so killing the primary tmux session leads to daemon-owned replacement without a manual `session resume`.
- Add a real tmux failure E2E where replacement is intentionally impossible and the unfinished run becomes durably failed.
- Update the relevant checklist and feature-checklist E2E status honestly based on those results.
