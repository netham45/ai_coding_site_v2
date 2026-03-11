# AI Workflow Composite Stage Outcome Phase 1 Stage Selection Note

## Purpose

This note records Phase 1 of `plan/tasks/2026-03-10_ai_workflow_composite_stage_outcome_design.md`.

The purpose of this phase is to decide which lifecycle stages should use the future composite AI-facing stage-outcome command family and which stages should remain outside that family.

This note does not define final command names yet. It freezes the lifecycle boundary first.

Related documents:

- `plan/tasks/2026-03-10_ai_workflow_composite_stage_outcome_design.md`
- `notes/planning/implementation/ai_command_lifecycle_structural_review_note.md`
- `notes/planning/implementation/full_ai_prompt_command_surface_review_note.md`
- `notes/planning/implementation/ai_workflow_command_surface_phase4_recommendations_note.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/runtime/tmux_session_lifecycle_spec_v1.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/specs/prompts/prompt_library_plan.md`

---

## Selection Rule

The composite AI-facing stage-outcome family should be used only for lifecycle stages where all of the following are true:

1. the AI is finishing one bounded stage of work
2. the daemon can accept that stage outcome authoritatively
3. the stage usually needs the same cluster of low-level actions:
   - record artifact or result
   - mark current subtask outcome
   - route to the next daemon-owned lifecycle state
4. the stage is part of the ordinary AI happy path rather than operator-only diagnosis or transport-level recovery

The composite family should not be used merely because a command exists. It should only cover stages where collapsing the low-level ritual makes the lifecycle clearer without hiding structural or recovery boundaries.

---

## In-Scope Lifecycle Stages

## 1. Ordinary execution

Lifecycle source:

- Stage 4 in `ai_command_lifecycle_structural_review_note.md`

Current shape:

- `subtask start`
- do work
- `summary register`
- `subtask complete`
- `workflow advance`
- `subtask current`
- `subtask prompt`

Decision:

- in scope

Reason:

- this is the clearest ordinary AI happy-path stage
- the current ritual is fragmented
- this is the primary target for a composite success outcome

## 2. Command-subtask execution

Lifecycle source:

- Stage 5 in `ai_command_lifecycle_structural_review_note.md`

Current shape:

- `subtask current`
- `subtask start`
- `subtask context`
- run command
- write `command_result.json`
- `subtask complete --result-file ...` or `subtask fail ...`
- `workflow advance`

Decision:

- in scope

Reason:

- this is another ordinary AI stage-outcome family
- it differs from ordinary execution mainly by result-file semantics
- it should be a first-class composite variant rather than a separate mini DSL forever

## 3. Review routing

Lifecycle source:

- Stage 7 in `ai_command_lifecycle_structural_review_note.md`

Current shape:

- already uses `review run`

Decision:

- in scope, but as the model/template rather than the first rewrite target

Reason:

- review already behaves like the desired composite command family
- the design must treat it as a member of the family so the lifecycle becomes consistent
- the design should preserve its special review semantics rather than forcing it back down to low-level commands

## 4. Selected quality-gate stages

Lifecycle source:

- Stage 7 in `ai_command_lifecycle_structural_review_note.md`

Current shape:

- mixed:
  - review is composite
  - validation/testing often still follow command-subtask or low-level rituals

Decision:

- partially in scope

Reason:

- validation and testing are likely candidates for composite stage-outcome handling where the stage is fundamentally “record result and route”
- docs/provenance should not be assumed to fit automatically until Phase 2 defines their command semantics more precisely

---

## Out-Of-Scope Lifecycle Stages

## 1. Top-level startup

Lifecycle source:

- Stage 1

Decision:

- out of scope

Reason:

- `workflow start` is already a daemon-owned composite creation/admission command
- it is not a subtask stage-outcome problem

## 2. Primary session bind and bootstrap

Lifecycle source:

- Stage 2

Decision:

- out of scope

Reason:

- this is transport/bootstrap behavior, not stage completion
- session binding, prompt bootstrap, and tmux/Codex launch are separate lifecycle concerns

## 3. Stage bootstrap and context loading

Lifecycle source:

- Stage 3

Decision:

- out of scope for the composite outcome family itself

Reason:

- `subtask current`, `subtask prompt`, `subtask context`, and `subtask environment` remain necessary read-side surfaces
- these may become less frequent in the happy path, but they should not be collapsed into a generic write/outcome command family

## 4. Pause and intervention

Lifecycle source:

- Stage 8

Decision:

- out of scope

Reason:

- pause and intervention are not ordinary success/outcome transitions
- they need explicit operator-facing and policy-facing semantics

## 5. Idle, missed-step, and corrective guidance

Lifecycle source:

- Stage 9

Decision:

- out of scope

Reason:

- these are corrective prompts and runtime interventions
- they may eventually call into composite commands, but they are not themselves part of the stage-outcome family

## 6. Recovery, resume, and replacement

Lifecycle source:

- Stage 10

Decision:

- out of scope

Reason:

- recovery is transport/session lifecycle behavior
- it requires its own explicit session and provider semantics

## 7. Child-session delegation and merge-back

Lifecycle source:

- Stage 11

Decision:

- out of scope for the first composite command family

Reason:

- child-session push/pop is a specialized branch with separate merge-back semantics
- it should not be forced into the same contract as ordinary subtask success without a dedicated design pass

## 8. Parent structural mutations

Lifecycle source:

- Stage 6

Decision:

- mostly out of scope for the first composite family

Explicit exception:

- parent layout-generation subtasks may eventually use a parent-specific composite success command

Reason:

- `node register-layout` promotes a workspace artifact into durable authoritative state and should remain explicit
- `node materialize-children` and child-structure coordination are structural mutations, not generic subtask completion
- parent stages need a separate decision about whether any structural step gets embedded later

## 9. Terminal completion as a standalone stage

Lifecycle source:

- Stage 12

Decision:

- not a separate composite command target
- instead it must be a possible response shape from in-scope composite commands

Reason:

- the design goal is that an in-scope composite stage command can return `completed` cleanly
- terminal completion should not require a separate follow-up command

---

## Phase 1 Boundary Decisions

The first composite AI-facing stage-outcome family should cover:

1. ordinary execution success or failure
2. command-subtask result reporting
3. review routing as the already-existing composite example
4. selected validation/testing-style result-routing stages where the lifecycle shape matches

The first composite family should not try to absorb:

1. bootstrap and binding
2. prompt/context read surfaces
3. pause/intervention
4. idle/recovery/corrective flows
5. child-session push/pop
6. parent structural mutations by default

---

## Implications For Phase 2

Phase 2 should now design the composite command family as a staged set, not one universal command.

At minimum it likely needs:

1. an ordinary execution outcome command
2. a command-result outcome command
3. a review-aligned outcome contract
4. a shared response shape for:
   - `next_stage`
   - `paused`
   - `completed`
   - `failed`

Phase 2 should also explicitly decide whether validation/testing become:

- thin variants of the command-result outcome command
- or separate stage-outcome commands

---

## Result

The lifecycle boundary is now frozen.

The composite AI-facing stage-outcome family is a design for ordinary stage completion and selected quality/result-routing stages, not a redesign of the entire runtime transport, recovery, or structural orchestration surface.
