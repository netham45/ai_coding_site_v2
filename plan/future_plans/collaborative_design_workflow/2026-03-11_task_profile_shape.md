# Draft Task Profile Shape

## Purpose

Sketch the first plausible `task` workflow-profile shape for collaborative design so the idea is concrete enough to critique later.

This is still exploratory.

## Draft Profile ID

- `task.collaborative_design`

## Behavioral Intent

Use this profile when a task is expected to:

- create a first-pass UI implementation
- present that draft for human review
- gather structured design requirements from the human
- apply one or more revisions
- stop only when the result is approved or explicitly escalated

## Why This Profile Is Different From `task.implementation`

The existing draft `task.implementation` profile is essentially:

- change repository behavior or shipped assets for one bounded slice

Collaborative design would be stricter.

It would require:

- an explicit intermediate review gate
- durable requirement capture before claiming the task is done
- revision-aware prompts
- stronger proof that the operator actually accepted the direction

## Draft YAML Shape

```yaml
kind: workflow_profile_definition
id: task.collaborative_design
name: Collaborative Design Task
description: Create a UI draft, gather structured operator design feedback, and iterate before closure.
applies_to_kind: task
profile_family: task
status: draft
main_prompt_ref: prompts/task/collaborative_design.md
required_repository_updates:
  - development_log
required_artifacts:
  - implementation_diff
  - design_draft_summary
  - design_requirement_capture
  - effective_design_policy_summary
required_review_checkpoints:
  - initial_draft_review
  - post_revision_approval
required_verification:
  - bounded_tests
  - design_policy_checks
completion_restrictions:
  forbidden_statuses_until_requirements_met:
    - flow_complete
    - release_ready
  require_operator_approval_or_explicit_escalation: true
metadata:
  intent: design_iteration
  maturity: starter_builtin_candidate
```

This should remain declarative.

The daemon/runtime would still own:

- state transitions
- duplicate-submission handling
- legality of revision rounds
- audit-history persistence
- enforcement of approved overrides and required policy inputs

## Suggested Prompt Stack

The future prompt assembly should likely include:

1. Stable task-tier execution prompt
2. Collaborative-design profile prompt
3. Current implementation context
4. Latest approved design requirements
5. Any unresolved operator feedback from the last review round

The profile-specific prompt should tell the AI to avoid pretending the first draft is final.

## Suggested Operator Artifact Shape

The review artifact should probably store fields like:

- page_or_component_target
- required_sections
- required_fields
- required_actions
- tone_or_style_words
- references
- avoidances
- device_priority
- open_questions
- approval_state

This matters because later revisions should consume a structured artifact, not only free-form prose.

Separate but related artifacts may also be needed for:

- effective global design rules
- approved page-level overrides
- design-policy verification results

## Candidate User Experience

For an operator with little UI experience, the system should prefer guided requirement capture over open-ended critique.

Possible interaction pattern:

- show the draft
- show a short "what changed" summary
- ask 5-8 constrained review questions
- allow optional free-form notes
- synthesize a requirement summary
- ask the operator to confirm or correct that summary before revision begins

That confirmation step is important.

Otherwise the AI may revise against a misunderstood interpretation.

## Future UI Surface Options

Possible review surfaces later include:

- terminal-first review with screenshot links
- browser-based review in the future website UI
- optional external-design-reference upload or link attachment

The system should not depend on a full design platform to be useful.

## Exit Conditions For The Real Feature

A future implemented version should not claim success merely because a page exists.

It should require one of:

- operator approval of the revised design summary
- explicit operator decision to stop with known shortcomings
- explicit escalation to a broader redesign or multi-task effort

And if design-policy enforcement exists, it should also require:

- successful required design-policy verification
- or an explicit recorded exception path

## When To Introduce Plan-Level Support

Move beyond a pure task-level profile only if repeated real cases show that collaborative design often needs separate tasks for:

- discovery and reference collection
- draft implementation
- structured review intake
- accessibility or responsiveness verification
- visual-regression proof

Until then, task-level is the more disciplined first fit.
