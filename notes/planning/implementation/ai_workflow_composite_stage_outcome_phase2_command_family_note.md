# AI Workflow Composite Stage Outcome Phase 2 Command Family Note

## Purpose

This note records Phase 2 of `plan/tasks/2026-03-10_ai_workflow_composite_stage_outcome_design.md`.

Phase 1 froze which lifecycle stages are in scope for the composite AI-facing stage-outcome family. Phase 2 defines the candidate command family, the shared response model, and the compatibility posture with existing low-level commands.

This note is still design only. It does not implement the commands.

Related documents:

- `plan/tasks/2026-03-10_ai_workflow_composite_stage_outcome_design.md`
- `notes/planning/implementation/ai_workflow_composite_stage_outcome_phase1_stage_selection_note.md`
- `notes/planning/implementation/ai_command_lifecycle_structural_review_note.md`
- `notes/planning/implementation/ai_workflow_command_surface_phase4_recommendations_note.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/cli/cli_surface_spec_v2.md`

---

## Design Rule

The composite family should replace repeated low-level AI happy-path rituals, not erase the low-level primitives.

That means:

- low-level commands remain
- composite commands become the normal AI-facing stage-outcome path for in-scope stages
- composite commands must preserve durable artifact, summary, result, attempt, and workflow-event inspectability

---

## Candidate Command Family

## 1. `subtask succeed`

Purpose:

- ordinary non-command stage success for in-scope stages such as leaf implementation or similar parent work that is fundamentally “complete the current stage and route onward”

Candidate request shape:

- `subtask succeed --node <id> --compiled-subtask <id> --summary-file <path>`
- optional:
  - `--summary-type <type>`
  - `--summary "<short durable summary>"`
  - `--artifact-root <path>` only if later needed, not required for first design

Expected daemon-owned side effects:

1. validate that the referenced subtask is the current in-scope stage
2. register the provided durable summary artifact
3. mark the current attempt complete
4. evaluate any immediate post-stage routing that belongs to ordinary success
5. advance to the next lifecycle state when appropriate
6. return one authoritative outcome object

This command replaces the ordinary low-level ritual:

- `summary register`
- `subtask complete`
- `workflow advance`
- follow-up probing for next-stage existence

## 2. `subtask report-command`

Purpose:

- command-subtask success or failure for stages whose main outcome is a structured command result

Candidate request shape:

- success form:
  - `subtask report-command --node <id> --compiled-subtask <id> --result-file <path>`
- failure form:
  - `subtask report-command --node <id> --compiled-subtask <id> --result-file <path> --summary-file <path> --status failed`

Optional:

- `--summary "<short durable summary>"`
- `--status success|failed`

Expected daemon-owned side effects:

1. validate current stage identity
2. ingest `execution_result_json`
3. record failure summary too when the status is failing
4. complete or fail the current attempt appropriately
5. run the command-stage routing logic
6. return one authoritative outcome object

This command replaces the command-subtask mini ritual:

- `subtask start`
- run command
- write `command_result.json`
- `subtask complete --result-file ...` or `subtask fail ...`
- `workflow advance`

Note:

- the command still has to be run by the AI in the workspace
- what becomes composite is the reporting and routing step after that command has run

## 3. `review run`

Purpose:

- existing composite review-stage outcome command

Candidate posture:

- keep the current surface
- explicitly classify it as a member of the composite family

Reason:

- it already bundles:
  - attempt start
  - review completion
  - routing/advance

Phase 2 decision:

- `review run` remains the model and compatibility anchor rather than being renamed immediately

## 4. Possible later sibling commands

These are not frozen for the first implementation phase, but the family design should leave room for them:

- `subtask fail-safe`
- `validation run-and-route`
- `testing run-and-route`

Current Phase 2 posture:

- do not over-expand the first family
- ordinary success, command-result routing, and review are enough to define the command model

---

## Shared Response Shape

All composite AI-facing stage-outcome commands should return one response object with a stable top-level routing field.

Candidate top-level shape:

```json
{
  "outcome": "next_stage|paused|completed|failed",
  "node_id": "...",
  "node_run_id": "...",
  "compiled_subtask_id": "...",
  "summary_recorded": true,
  "attempt_status": "COMPLETE|FAILED",
  "routing": {
    "next_compiled_subtask_id": "...",
    "pause_flag": null,
    "reason": "..."
  }
}
```

Required semantics:

- `next_stage`
  - includes enough current-stage routing data that the session can continue cleanly
- `paused`
  - includes pause reason and pause flag data
- `completed`
  - indicates terminal run completion without requiring another low-level probing command
- `failed`
  - indicates the run or stage failed and why

Important boundary:

- this response shape is for AI-facing composite commands
- low-level operator commands may continue returning the lower-level run progress snapshot shape

---

## Compatibility Rules

## Rule 1: Low-level commands remain supported

The design does not remove:

- `summary register`
- `subtask complete`
- `subtask fail`
- `workflow advance`

Reason:

- operators, debugging flows, and controlled recovery still need them

## Rule 2: Prompts should stop requiring low-level happy-path choreography

For in-scope stages, later prompts should prefer the composite command family and stop teaching:

- separate summary registration
- separate completion mutation
- separate cursor advance mutation
- separate next-stage probing after success

## Rule 3: `workflow advance` remains a strict primitive

The design does not relax `workflow advance` into a generic AI-facing convenience path.

Instead:

- composite commands absorb the ordinary happy-path need for it
- `workflow advance` stays available where explicit low-level control is actually intended

## Rule 4: Review compatibility remains explicit

Because `review run` already behaves like the desired family:

- later implementation should treat it as the composite review-stage member
- prompts should not be forced into a transitional wrapper only for naming symmetry

---

## Lifecycle Mapping

The first command family maps to the lifecycle like this:

- Stage 4 ordinary execution:
  - `subtask succeed`
- Stage 5 command-subtask execution:
  - `subtask report-command`
- Stage 7 review routing:
  - `review run`
- selected Stage 7 validation/testing result-routing:
  - likely later variants of `subtask report-command` or explicit sibling commands

The family does not directly target:

- Stage 1 startup
- Stage 2 bootstrap
- Stage 3 read-side prompt/context retrieval
- Stage 8 pause/intervention
- Stage 9 corrective prompts
- Stage 10 recovery
- Stage 11 child-session push/pop
- Stage 6 parent structural mutation by default

---

## Open Decisions For Phase 3

Phase 3 should now decide:

1. whether `subtask succeed` should infer the current compiled subtask by node alone or always require `--compiled-subtask`
2. whether `subtask report-command` should encode failure through `--status failed` or separate success/failure commands
3. whether validation/testing should be absorbed into `subtask report-command` variants or get their own composite commands
4. how parent layout-generation success should relate to the family without hiding `node register-layout`

---

## Result

The composite family is now defined as a small staged command set:

- `subtask succeed`
- `subtask report-command`
- `review run`

with one shared AI-facing response model:

- `next_stage`
- `paused`
- `completed`
- `failed`

That is enough to continue into Phase 3 boundary and ownership review without prematurely fixing names or implementation details.
