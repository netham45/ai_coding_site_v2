# Review State Machine

## Purpose

Define the likely future state machine for collaborative-design execution so the review loop is not treated as vague chat behavior.

This is still a working note.

## Core Rule

The design-review flow should be runtime-visible and inspectable.

It should not exist only as prompt wording.

## Draft States

Recommended first-pass states:

- `drafting_initial`
- `awaiting_review_input`
- `synthesizing_requirements`
- `awaiting_requirement_confirmation`
- `revising_design`
- `awaiting_final_approval`
- `approved`
- `escalated`
- `stopped_with_known_gaps`

## Intended Flow

1. `drafting_initial`
2. `awaiting_review_input`
3. `synthesizing_requirements`
4. `awaiting_requirement_confirmation`
5. `revising_design`
6. `awaiting_final_approval`
7. either `approved`, loop back to `awaiting_review_input`, or move to `escalated`

## State Meanings

### `drafting_initial`

The AI is building the first coded draft and generating the first review summary.

Required outputs:

- implementation diff
- draft summary
- preview or screenshot artifact when available

### `awaiting_review_input`

The system has presented the draft and is waiting for operator answers.

Required outputs:

- review questionnaire
- current preview reference
- explicit pending-human-input flag

### `synthesizing_requirements`

The runtime or AI is translating operator answers into structured requirements.

Required outputs:

- candidate requirement capture artifact
- open-question list when ambiguity remains

### `awaiting_requirement_confirmation`

The operator confirms whether the synthesized requirements are accurate enough to drive revision.

Possible outcomes:

- confirm and continue
- correct and resynthesize
- stop
- escalate

### `revising_design`

The AI revises the implementation against the confirmed requirement capture and active design rules.

Required outputs:

- revision diff
- updated summary
- verification results for any immediate checks

### `awaiting_final_approval`

The revised design is ready for operator approval or another review cycle.

Possible outcomes:

- approve
- request another round
- stop with known gaps
- escalate

## Illegal Shortcuts

The real runtime should prevent:

- claiming approval without a stored approval decision
- revising against unconfirmed synthesized requirements unless explicitly allowed
- silently discarding earlier requirements
- hiding that human input is currently blocking progress

## Restart And Recovery Expectations

On restart, the operator should be able to inspect:

- current state
- current round number
- last questionnaire
- last requirement capture
- last approval decision
- next required action

## Escalation Path

Escalation should exist when a single-task design loop is no longer sufficient.

Triggers might include:

- too many revision rounds
- unresolved contradictions
- missing product direction
- design-policy conflicts that require project-level decisions

## Recommended Next Step

The next useful follow-on note is a tighter mapping from each state to CLI/API inspection and mutation surfaces.
