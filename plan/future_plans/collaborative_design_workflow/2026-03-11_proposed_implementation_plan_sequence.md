# Proposed Implementation Plan Sequence

## Purpose

Freeze a first recommended set of authoritative plan units that should exist if collaborative design moves from future planning into real implementation planning.

This is a working note, not an implementation plan.

## Proposed Plan List

1. workflow-profile and schema foundation
2. design-rule policy and inheritance foundation
3. review-state and artifact persistence foundation
4. CLI and daemon design-inspection surfaces
5. first collaborative-design task execution flow
6. design verification and enforcement suite
7. browser review surface integration
8. E2E hardening and adversarial-flow proof

## Plan 1: workflow-profile and schema foundation

Scope:

- add collaborative-design profile support
- adopt draft schema families for design rules, requirement captures, overrides, and verification definitions
- extend profile-aware inspection surfaces where required

Required proof:

- schema tests
- profile applicability tests
- document-consistency updates

## Plan 2: design-rule policy and inheritance foundation

Scope:

- define effective design-rule resolution
- define override legality
- freeze effective design context into compiled state

Required proof:

- inheritance tests
- override legality tests
- compile-context tests

## Plan 3: review-state and artifact persistence foundation

Scope:

- persist review states and rounds
- persist questionnaires, requirement captures, approvals, and escalation decisions
- define restart and resume behavior

Required proof:

- database persistence tests
- daemon state-transition tests
- recovery tests

## Plan 4: CLI and daemon design-inspection surfaces

Scope:

- add status, rules, requirements, overrides, and verification surfaces
- add mutations for review submission, confirmation, approval, stop, and escalation

Required proof:

- CLI contract tests
- daemon route tests
- operator inspection proof

## Plan 5: first collaborative-design task execution flow

Scope:

- initial draft generation
- review questionnaire
- requirement synthesis and confirmation
- revision loop
- final approval flow

Required proof:

- bounded prompt/artifact tests
- integration tests through real runtime boundaries

## Plan 6: design verification and enforcement suite

Scope:

- static policy checks
- rendered checks
- accessibility checks
- completion gating

Required proof:

- enforcement tests
- rendered UI tests
- failed-verification gating tests

## Plan 7: browser review surface integration

Scope:

- connect the future browser UI to collaborative-design inspection and action surfaces
- expose review rounds, rule summaries, verification failures, and approval controls

Required proof:

- frontend component tests
- daemon integration tests
- browser narrative tests

## Plan 8: E2E hardening and adversarial-flow proof

Scope:

- full review loop
- interruption and restart
- contradictory feedback
- escalation path
- explicit untested-flow audit

Required proof:

- real E2E suite
- resilience coverage
- residual-gap inventory if anything remains deferred
