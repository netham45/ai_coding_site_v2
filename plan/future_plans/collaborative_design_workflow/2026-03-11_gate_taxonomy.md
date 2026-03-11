# Gate Taxonomy

## Purpose

Clarify the different kinds of gates the future collaborative-design runtime would need so "blocked" does not mean only one thing.

This is a working note.

## Core Recommendation

The future feature should distinguish at least three gate categories:

- progress gates
- verification gates
- completion-status gates

These should not be collapsed into one generic blocked flag.

## Gate Category 1: Progress Gates

Progress gates block the next step in the workflow loop.

Examples:

- no review answers submitted yet
- requirement capture not yet confirmed
- revised preview artifacts not yet generated

These gates answer:

- why can the task not advance to the next review state

## Gate Category 2: Verification Gates

Verification gates block approval or stronger status claims because required checks have not passed.

Examples:

- required fields render check failed
- accessibility check pending
- design-rule drift check failed

These gates answer:

- why can the task not be treated as sufficiently proven

## Gate Category 3: Completion-Status Gates

Completion-status gates restrict which state labels or summaries are legal.

Examples:

- approval exists but required verification is not complete
- stopped-with-known-gaps cannot be reported as fully approved
- escalation cannot be reported as resolved design completion

These gates answer:

- what the system is allowed to claim

## Recommended Reporting Shape

A future response could report:

- `progress_gate`
- `verification_gate`
- `completion_gate`

instead of one overloaded blocked value.

## Why This Matters

Different audiences need different clarity:

- operators need to know what they must do next
- AI workers need to know what to fix next
- auditors need to know what may or may not be claimed

## Recommended Next Step

The next useful note would be a decision record for how these gates should surface in CLI, daemon responses, and a future browser UI.
