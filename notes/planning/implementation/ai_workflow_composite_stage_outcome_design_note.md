# AI Workflow Composite Stage Outcome Design Note

## Purpose

This note is the rolled-up design output for `plan/tasks/2026-03-10_ai_workflow_composite_stage_outcome_design.md`.

It consolidates:

- lifecycle-stage selection
- candidate composite command family
- ownership boundaries
- retained low-level command posture
- parent and quality-gate special cases

This note is design only. It does not implement the commands.

Related documents:

- `plan/tasks/2026-03-10_ai_workflow_composite_stage_outcome_design.md`
- `notes/planning/implementation/ai_workflow_composite_stage_outcome_phase1_stage_selection_note.md`
- `notes/planning/implementation/ai_workflow_composite_stage_outcome_phase2_command_family_note.md`
- `notes/planning/implementation/ai_command_lifecycle_structural_review_note.md`
- `notes/planning/implementation/ai_workflow_command_surface_phase3_ownership_error_policy_note.md`
- `notes/planning/implementation/ai_workflow_command_surface_phase4_recommendations_note.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/specs/prompts/prompt_library_plan.md`

---

## Design Goal

The design goal is not to remove the low-level command surface.

The design goal is to stop making ordinary AI happy-path stages depend on repeated low-level rituals such as:

1. `summary register`
2. `subtask complete`
3. `workflow advance`
4. `subtask current`
5. `subtask prompt`

For the in-scope lifecycle stages, the AI should instead have one stage-outcome command that returns a clear routed outcome.

---

## Final Lifecycle Scope

## In scope

The first composite command family covers:

1. ordinary execution stages
2. command-subtask execution stages
3. review routing
4. selected validation/testing-style result-routing stages where the semantics match the same “record result and route” shape

## Out of scope

The first composite family does not cover:

1. top-level startup
2. primary-session bind/bootstrap
3. prompt/context read-side retrieval
4. pause/intervention handling
5. idle, missed-step, and corrective prompts
6. recovery/resume/replacement flows
7. child-session push/pop
8. parent structural mutations by default

Important exception:

- parent layout-generation stages may later use a parent-specific composite success command, but only without hiding `node register-layout`

---

## Command Family

## 1. `subtask succeed`

Role:

- ordinary execution-stage success for in-scope non-command stages

Expected inputs:

- current node identity
- current compiled subtask identity or daemon-resolved current stage
- durable summary artifact

Expected daemon-owned actions:

1. validate stage identity
2. record the summary artifact durably
3. complete the current attempt
4. route the lifecycle onward
5. return an AI-facing outcome object

## 2. `subtask report-command`

Role:

- command-subtask reporting for stages whose primary outcome is a structured command result

Expected inputs:

- current node identity
- current compiled subtask identity or daemon-resolved current stage
- result JSON artifact
- optional failure summary

Expected daemon-owned actions:

1. validate stage identity
2. record the result JSON durably
3. complete or fail the current attempt
4. route the lifecycle onward
5. return an AI-facing outcome object

## 3. `review run`

Role:

- existing composite review-stage outcome command

Design posture:

- keep the current command
- explicitly treat it as a first-class member of the composite family

Reason:

- it already proves the desired daemon-owned shape

## Deferred siblings

Possible later members:

- validation-specific composite routing command
- testing-specific composite routing command
- parent-stage composite success command

Current posture:

- defer these until the first family is implemented or the boundary pressure becomes clearer

---

## Shared Outcome Model

All AI-facing composite stage-outcome commands should return one routed outcome.

Required outcome values:

- `next_stage`
- `paused`
- `completed`
- `failed`

Minimum response responsibilities:

- identify the current node and run
- identify the current stage that was accepted
- indicate whether required summary/result artifacts were recorded
- include the lifecycle routing result

Important rule:

- terminal run completion must be represented as `completed`
- AI sessions should not have to detect terminal success by issuing another low-level command and seeing `404 active node run not found`

---

## Ownership Boundary

## Retained low-level commands

These remain valid and important:

- `summary register`
- `subtask complete`
- `subtask fail`
- `workflow advance`
- `subtask current`
- `subtask prompt`
- `subtask context`
- `node register-layout`
- `node materialize-children`
- recovery, pause, and intervention commands

They remain because:

- operators need them
- debugging and recovery need them
- some structural mutations are not ordinary stage outcomes

## AI-facing normal path

For in-scope stages, later prompts should prefer:

- `subtask succeed`
- `subtask report-command`
- `review run`

and stop teaching:

- separate success-path summary registration
- separate success-path completion mutation
- separate success-path cursor advance
- separate post-success next-stage probing

## `workflow advance` boundary

`workflow advance` remains:

- strict
- low-level
- state-sensitive

It should not remain the normal AI happy-path step for in-scope stages.

## `review run` boundary

`review run` remains:

- composite
- terminal for review-stage routing
- the compatibility anchor for the new family

Later prompts should not teach redundant advancement after it.

---

## Parent And Structural Special Cases

Parent lifecycle stages need a narrower rule.

### Keep explicit

- `node register-layout`

Reason:

- it turns a workspace artifact into authoritative durable state

### Do not absorb by default

- `node materialize-children`
- structural child scheduling logic
- child-materialization inspection loops

Reason:

- these are structural mutations or structural orchestration surfaces, not generic stage-completion behavior

### Allowed future extension

- a parent-stage composite command may later bundle ordinary parent subtask success around these structural steps
- but it should do so explicitly and not by pretending structural mutations are ordinary generic subtask outcomes

---

## Quality-Gate Special Cases

Quality gates are not fully uniform yet.

### Review

- already composite
- keep as-is

### Validation and testing

- likely candidates for the same family when the stage is fundamentally “record result and route”
- may be implemented either as:
  - variants of `subtask report-command`
  - or later sibling commands if the semantics diverge too far

### Docs and provenance

- do not force into the first family automatically
- their lifecycle semantics need a separate decision if they are to become composite later

---

## Prompt-Migration Consequences

When implementation begins later, the first prompt-migration targets should be:

1. `execution/implement_leaf_task.md`
2. synthesized command-subtask prompts in `run_orchestration.py`
3. workflow-rendered parent ordinary-success guidance in `workflows.py`
4. review prompts only to remove obsolete defensive warnings, not to change the review command itself

The corrective and recovery families should remain separate follow-on work:

- `runtime/*`
- `recovery/*`
- `pause/*`

Those families should adopt the new normal-path commands only where they explicitly resume or correct in-scope stages.

---

## Implementation-Handoff Summary

The first implementation phase after this design should do exactly this:

1. implement `subtask succeed`
2. implement `subtask report-command`
3. preserve `review run` as the review-stage composite member
4. return a routed outcome model of:
   - `next_stage`
   - `paused`
   - `completed`
   - `failed`
5. keep low-level commands intact for operator/debug/recovery use

That is the narrowest implementation slice that meaningfully changes the AI-facing happy path without trying to redesign the entire runtime in one pass.
