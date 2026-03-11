# Lifecycle Matrix

## Purpose

Tie the collaborative-design review states to required artifacts, legal actions, and completion gates so the future runtime contract is explicit.

This is a working note.

## Core Rule

Every meaningful review state should answer three questions:

- what artifacts must already exist
- what actions are currently legal
- what blocks completion or forward progress

## Matrix

### State: `drafting_initial`

Required artifacts:

- runtime contract reference
- selected review scenario
- effective design policy summary

Legal actions:

- stop
- escalate

Illegal actions:

- approve
- confirm requirements
- request revision

Forward-progress gate:

- initial coded draft must exist

### State: `awaiting_review_input`

Required artifacts:

- design_draft_summary
- implementation_diff
- at least one preview artifact
- review_questionnaire

Legal actions:

- submit review
- stop
- escalate

Illegal actions:

- approve
- confirm requirements

Forward-progress gate:

- operator review answers are required

### State: `synthesizing_requirements`

Required artifacts:

- review_answers
- latest preview artifacts

Legal actions:

- stop
- escalate

Illegal actions:

- approve
- request revision

Forward-progress gate:

- requirement_capture artifact must be produced

### State: `awaiting_requirement_confirmation`

Required artifacts:

- requirement_capture
- synthesized requirement summary

Legal actions:

- confirm requirements
- stop
- escalate

Illegal actions:

- approve
- request revision

Forward-progress gate:

- confirmed or corrected requirement capture is required

### State: `revising_design`

Required artifacts:

- confirmed requirement_capture
- effective design policy summary
- approved overrides if any

Legal actions:

- stop
- escalate

Illegal actions:

- approve
- submit review

Forward-progress gate:

- revised implementation and updated preview artifacts must exist

### State: `awaiting_final_approval`

Required artifacts:

- revision_summary
- updated preview artifacts
- current verification results

Legal actions:

- approve
- request revision
- stop with known gaps
- escalate

Illegal actions:

- submit review for an earlier round

Forward-progress gate:

- operator decision is required

### State: `approved`

Required artifacts:

- approval_decision
- final requirement capture
- final verification results

Legal actions:

- inspect only

Completion gate:

- all required verification must have passed or an explicit exception path must exist

### State: `stopped_with_known_gaps`

Required artifacts:

- stop_with_known_gaps_decision
- remaining gap list

Legal actions:

- inspect only
- escalate later

Completion gate:

- task cannot claim stronger status than the recorded limitations allow

### State: `escalated`

Required artifacts:

- escalation_decision
- escalation reason

Legal actions:

- inspect only
- hand off to broader planning

Completion gate:

- task exits the simple collaborative loop without pretending the design is settled

## Why This Matrix Matters

Without a lifecycle matrix, the future runtime is likely to drift into:

- missing artifacts
- inconsistent action legality
- approval without proof
- unclear blocked states

## Recommended Next Step

The next useful companion note is a gate taxonomy that distinguishes:

- progress gates
- verification gates
- completion-status gates
