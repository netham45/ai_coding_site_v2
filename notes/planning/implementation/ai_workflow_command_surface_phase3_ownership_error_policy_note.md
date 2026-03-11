# AI Workflow Command Surface Phase 3 Ownership And Error Policy Note

## Purpose

This note records the Phase 3 ownership and error-policy review for `plan/tasks/2026-03-10_ai_workflow_command_surface_review_discovery.md`.

Phase 1 established the transcript-backed problems. Phase 2 grouped the current command surface. Phase 3 defines which currently observed misuse cases belong in each policy bucket:

- hard daemon rejection
- awkward but technically valid low-level operator path
- idempotent or terminal-success candidate for future AI-facing handling

This note is still discovery only. It does not implement those policy changes.

Related documents:

- `plan/tasks/2026-03-10_ai_workflow_command_surface_review_discovery.md`
- `notes/planning/implementation/ai_workflow_command_surface_phase1_evidence_note.md`
- `notes/planning/implementation/ai_workflow_command_surface_phase2_inventory_note.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `src/aicoding/daemon/run_orchestration.py`
- `src/aicoding/daemon/review_runtime.py`
- `src/aicoding/daemon/app.py`
- `src/aicoding/cli/daemon_client.py`

---

## Observed Ownership Split

The current runtime already has two different command-ownership models.

### Model A: Low-level explicit cursor mutation

Example:

- `workflow advance --node <id>`

Current behavior:

- loads the active run bundle
- requires a current compiled subtask
- requires the latest attempt for that subtask to be `COMPLETE`
- evaluates validation/review/testing state when the current subtask type requires it
- advances the cursor or closes the run

Evidence:

- `src/aicoding/daemon/run_orchestration.py`

Policy shape:

- strict
- state-sensitive
- low-level
- easy to misuse from an AI session if it appears in the ordinary happy path

### Model B: Composite daemon-owned stage outcome

Example:

- `review run --node <id> --status ... --summary ...`

Current behavior:

- checks that the route node id and request node id match
- loads the current review subtask
- starts the review attempt
- completes the review attempt
- calls `advance_workflow(...)` internally
- returns the resulting run progress

Evidence:

- `src/aicoding/daemon/app.py`

Policy shape:

- composite
- self-routing
- closer to the intended AI-facing shape

### Discovery conclusion

The repo already supports both policy models. The messy transcript is not happening because the daemon can only do low-level primitives. It is happening because only some stage types use the composite model while ordinary stage success still relies on the low-level model.

---

## Policy Buckets

### Bucket 1: Hard daemon rejection

These are cases where the session is violating an explicit workflow contract or calling the wrong class of command for the current state.

#### P1. Calling `workflow advance` before the current subtask is durably complete

Current behavior:

- daemon returns `409 current compiled subtask is not complete`

Assessment:

- this is correctly a hard rejection
- the current error is semantically right
- the deeper product problem is that AI sessions are still forced to touch this low-level command too often

Policy classification:

- keep as hard rejection

#### P2. Calling review-specific commands when the current subtask is not a review subtask

Current behavior:

- daemon returns conflicts such as:
  - `current review subtask not found`
  - `current subtask is not a review subtask`

Assessment:

- this is correctly a hard rejection
- review routing is stage-specific and should stay guarded

Policy classification:

- keep as hard rejection

#### P3. Route/request node mismatch on `review run`

Current behavior:

- daemon returns `409 review request node id does not match route node id`

Assessment:

- this is correctly a hard rejection
- it defends authority and auditability

Policy classification:

- keep as hard rejection

### Bucket 2: Low-level valid operator path but poor AI-facing happy path

These are not necessarily wrong at the low-level API boundary, but they are poor choices for ordinary AI-stage completion.

#### P4. `workflow advance` as a required ordinary success-path command

Current behavior:

- this is the documented and prompted ordinary continuation step after many successful stages

Assessment:

- this is valid
- it is also the main source of race-prone AI behavior from Phase 1
- it belongs as a low-level operator or recovery-capable primitive even if future AI prompts stop relying on it directly

Policy classification:

- keep valid at the low level
- mark as poor current AI-facing happy-path shape

#### P5. Separate `summary register` followed by `subtask complete` for routine stage success

Current behavior:

- many prompts require the AI to do both in sequence

Assessment:

- this is a valid low-level artifact-plus-stage mutation path
- it is carrying too much happy-path choreography in prompts
- it should remain available even if later AI-facing commands collapse it

Policy classification:

- keep valid at the low level
- treat as over-fragmented for ordinary AI success flow

### Bucket 3: Idempotent or terminal-success candidate

These are the cases where the current low-level response is technically correct, but the product behavior is poor for the AI-facing flow.

#### P6. `workflow advance` after the run has already completed

Observed transcript symptom:

- `404 active node run not found`

Current behavior:

- active-run lookup rejects once the run is no longer in `PENDING`, `RUNNING`, or `PAUSED`

Evidence:

- `_active_run_for_version(...)` and `_load_active_run_bundle(...)` in `src/aicoding/daemon/run_orchestration.py`
- CLI 404 mapping in `src/aicoding/cli/daemon_client.py`

Assessment:

- this is technically correct for a strict low-level “mutate the active run” primitive
- it is a poor AI-facing terminal outcome
- the session is effectively probing whether completion already happened

Policy classification:

- strong candidate for future idempotent terminal-success handling at the AI-facing layer
- low-level operator surface may still legitimately retain strict `not found`

#### P7. `review run` followed by another `workflow advance`

Observed transcript symptom:

- session behaves as if `review run` needs a second advancement step

Current behavior:

- `review run` already starts, completes, and advances internally
- a later `workflow advance` therefore becomes either:
  - an unnecessary second mutation
  - a race
  - a terminal not-found probe

Assessment:

- this is not merely awkward; it contradicts the current prompt contract
- the important discovery point is that the daemon already owns enough of the review stage to make the extra command clearly unnecessary

Policy classification:

- current session behavior is a protocol violation
- future daemon/client UX should make that unnecessary extra step harder to attempt or easier to interpret as already handled

---

## Review Of The Current Transcript Against These Buckets

### Correctly rejected today

- advancing before the daemon sees a complete current subtask
- using review-only logic on the wrong stage
- mismatched route/request identity

### Tolerated today but evidence of poor AI-facing shape

- ordinary successful stages requiring several serial low-level mutations
- repeated immediate `workflow advance` attempts after acceptance-sensitive transitions

### Technically correct but poor terminal UX

- `404 active node run not found` after the run has already finished

---

## Phase 3 Findings

1. The daemon is not uniformly permissive. It already rejects several illegal states correctly.
2. The most important ownership split is already present in code:
   - `workflow advance` is a strict low-level cursor primitive
   - `review run` is a composite daemon-owned stage-outcome command
3. The passing transcript looked messy because ordinary successful stages still use the first model while review already uses the second.
4. The best discovery framing is therefore not “make everything idempotent.” It is:
   - keep true protocol violations as hard errors
   - preserve low-level operator primitives
   - stop requiring AI sessions to use those primitives in the ordinary happy path
5. Terminal `not found` on already-complete runs is the clearest candidate for a future AI-facing terminal-success abstraction, not because the daemon is wrong, but because the current low-level correctness is exposed in the wrong context.

---

## Questions Carried Into Phase 4

Phase 3 narrows the remaining design questions to:

1. Which concrete stage-success sequences should collapse into composite daemon-owned commands?
2. Which low-level commands should remain documented as operator/debug tools even if prompts stop relying on them?
3. Should terminal completion be returned directly by a future high-level stage-success command rather than inferred through `workflow advance`?
4. How should prompts distinguish:
   - strict low-level control commands
   - ordinary AI-facing stage-success commands
   - operator-only recovery/inspection paths
