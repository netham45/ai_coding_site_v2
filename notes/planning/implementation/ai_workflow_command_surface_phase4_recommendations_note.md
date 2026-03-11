# AI Workflow Command Surface Phase 4 Recommendations Note

## Purpose

This note records the Phase 4 design recommendations for `plan/tasks/2026-03-10_ai_workflow_command_surface_review_discovery.md`.

Phases 1 through 3 established:

- the transcript-backed workflow problems
- the current command inventory
- the ownership split between low-level cursor mutations and composite daemon-owned commands

This note translates those findings into explicit design recommendations without starting implementation.

Related documents:

- `plan/tasks/2026-03-10_ai_workflow_command_surface_review_discovery.md`
- `notes/planning/implementation/ai_workflow_command_surface_phase1_evidence_note.md`
- `notes/planning/implementation/ai_workflow_command_surface_phase2_inventory_note.md`
- `notes/planning/implementation/ai_workflow_command_surface_phase3_ownership_error_policy_note.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/cli/cli_surface_spec_v2.md`

---

## Recommendation 1: Split The Surface Explicitly Into AI-Facing Commands And Low-Level Operator Commands

The discovery result is not that the low-level commands are wrong. It is that they are doing two jobs at once.

Recommendation:

- preserve the current low-level mutation and inspection commands for operators, debugging, recovery, and tests
- introduce a clearly smaller AI-facing stage-outcome surface for ordinary success/failure/review completion
- document the distinction explicitly in runtime, CLI, and prompt notes

Reasoning:

- operators still need granular inspectability and control
- AI sessions should not need to choreograph several state-sensitive low-level mutations just to finish one ordinary stage

---

## Recommendation 2: Collapse Ordinary Stage Success Into Composite Daemon-Owned Commands

The current ordinary success path is over-fragmented.

Current common shape:

1. write artifact
2. `summary register`
3. `subtask complete`
4. `workflow advance`
5. `subtask current`
6. `subtask prompt`

Recommendation:

- replace the ordinary AI-facing happy path with composite stage-success commands that:
  - register required summary or result artifacts
  - complete the current subtask
  - advance when appropriate
  - return either:
    - the next stage handoff
    - a paused state
    - terminal run completion

Candidate examples:

- `subtask succeed --node <id> --summary-file <path> --summary-type subtask`
- `subtask report-command --node <id> --result-file <path>`
- `subtask fail-safe --node <id> --summary-file <path> --result-file <path>`

Discovery intent:

- names are provisional
- the important recommendation is ownership shape, not final command naming

---

## Recommendation 3: Treat `workflow advance` As A Low-Level Cursor Primitive, Not The Normal AI Happy Path

Phase 3 confirmed that `workflow advance` already behaves like a strict low-level cursor mutation.

Recommendation:

- keep `workflow advance` available
- stop making it the normal prompted success-path step for ordinary AI sessions
- reserve it for:
  - operator workflows
  - explicit recovery/manual continuation paths
  - advanced debugging and controlled remediation

Reasoning:

- the current races and sloppy retries are a predictable consequence of using a strict primitive as the normal AI-facing happy path

---

## Recommendation 4: Use Existing Composite Patterns As The Template

The repository already has examples of the desired command shape:

- `workflow start`
- `review run`
- `node quality-chain`
- `node register-layout`

Recommendation:

- later implementation should extend this existing daemon-owned pattern instead of introducing a separate command philosophy
- ordinary stage-success commands should behave more like `review run` than like `workflow advance`

Reasoning:

- that keeps the design consistent with already-working daemon-owned commands
- it preserves auditability because those commands already return durable, inspectable results

---

## Recommendation 5: Return Explicit Terminal Or Next-Stage Outcomes From Composite Commands

The transcript showed that the session learned terminal completion through `404 active node run not found`.

Recommendation:

- future AI-facing composite commands should return one authoritative outcome object such as:
  - `next_stage`
  - `paused`
  - `completed`
  - `failed`
- AI prompts should rely on that response shape rather than inferring state through another low-level mutation

Reasoning:

- it removes the need for post-success probing
- it gives the AI one clear transition contract
- it preserves low-level strictness in the underlying operator paths

---

## Recommendation 6: Keep Review As The First Enforced Composite-Only Success Path

Review already behaves closest to the desired model.

Recommendation:

- the future implementation should explicitly enforce that `review run` is terminal for review-stage routing
- prompts should stop carrying defensive prose like “do not call workflow advance after review run” once the runtime/UX makes that unnecessary

Reasoning:

- review already proves the daemon can own stage routing
- this is the cleanest place to tighten compliance first

---

## Recommendation 7: Preserve Auditability By Keeping Artifact Registration And Stage Outcomes Inspectable Separately

Composite commands should reduce AI ceremony, not erase audit detail.

Recommendation:

- even if stage success becomes one AI-facing command, the durable model should still preserve:
  - artifact history
  - summary history
  - result JSON history
  - attempt history
  - workflow-event history

Reasoning:

- operators still need to answer:
  - what file or summary was recorded
  - what result JSON was accepted
  - which stage transitioned and why

---

## Recommendation 8: Keep Parent Structural Commands Explicit Unless They Can Be Safely Embedded

Parent decomposition has a slightly different shape than ordinary leaf-stage completion.

Recommendation:

- keep `node register-layout` explicit
- treat `node materialize-children` as a separate design decision rather than automatically folding it into generic subtask success

Reasoning:

- `node register-layout` promotes a workspace artifact into authoritative durable state and should remain visible
- `node materialize-children` is a structural mutation, not just a stage-close event
- it may later be embedded behind a parent-specific composite command, but that should be decided separately

---

## Recommended Minimal Follow-On Implementation Sequence

The smallest sensible implementation ladder after discovery is:

### Phase A: Composite stage-success command design and daemon contract

Define:

- candidate AI-facing composite commands
- their request/response payloads
- their durable audit responsibilities
- their terminal/next-stage response model

### Phase B: Runtime and CLI implementation for ordinary stage completion

Implement:

- daemon-side composite success handling for ordinary non-review stages
- CLI surfaces for the new commands
- compatibility posture for existing low-level commands

### Phase C: Prompt migration and protocol tightening

Update:

- leaf prompts
- command-stage prompts
- parent layout prompts where needed
- review prompts after runtime enforcement makes the extra warnings obsolete

### Phase D: Misuse hardening and E2E enforcement

Add:

- stronger daemon/client error handling for clearly wrong follow-up commands
- E2E proof that the AI-facing happy path no longer relies on low-level retries or post-completion probing

---

## Phase 4 Conclusion

The design recommendation is not to remove the existing low-level surface.

The design recommendation is to stop making AI sessions use that low-level surface as the ordinary happy path.

The clean direction is:

- low-level commands remain for operators and recovery
- composite daemon-owned commands become the normal AI stage-outcome path
- prompt contracts shrink accordingly
- durable audit surfaces remain intact
