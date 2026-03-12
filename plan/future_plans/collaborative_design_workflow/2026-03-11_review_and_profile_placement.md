# Collaborative Design Review And Profile Placement

## Purpose

Review the collaborative-design idea against the current workflow-overhaul notes and decide where it most naturally belongs in the future roadmap.

This is still a working note, not an implementation plan.

## Position In The Roadmap

This idea should come after `plan/future_plans/workflow_overhaul/draft/`.

Reason:

- the workflow-overhaul bundle is where profile-aware behavior, tier contracts, prompt stacking, and completion obligations are being introduced
- collaborative design needs an execution mode with explicit human review gates, not just different decomposition wording
- without workflow-profile support, the idea would degrade into a brittle custom prompt or an ad hoc side conversation

It may also later integrate with:

- `plan/future_plans/frontend_website_ui/` for browser-based review surfaces

But browser UI is not the primary prerequisite.

The primary prerequisite is profile-aware workflow behavior.

The stronger version of the idea also depends on profile-aware enforcement of design policy, not only profile-aware prompting.

## Core Recommendation

The first version should be modeled primarily as a `task` workflow profile.

Recommended draft vocabulary:

- `task.collaborative_design`

Why `task` first:

- the defining behavior is a bounded execution packet with a draft -> review -> revise loop
- the human interaction is about refining one concrete page or UI slice, not decomposing a larger tree
- the operator should be able to invoke it where implementation already happens rather than requiring a whole new tier
- the loop needs different prompts, review gates, and durable artifacts, but not necessarily different child-node structure

## Why Not A New Node Kind

This idea does not justify a new structural kind such as `design_task` or `design_phase` as a first move.

That would repeat the same mistake the workflow-overhaul notes are already trying to avoid:

- kind proliferation for behavior that is really profile variation

The stable node kind can remain `task`.

The workflow profile would change:

- prompts
- review-gate expectations
- required artifacts
- required operator confirmations
- completion restrictions
- required design-policy inputs and verification

## Why Not Plan-Level First

A plan-level profile is not the right first anchor.

A plan-level profile would make sense only if the repository later wants a multi-task design program such as:

- one task to create references
- one task to build a draft UI
- one task to collect review feedback
- one task to execute design revisions
- one task to verify accessibility, responsiveness, and visual regression

That is plausible later.

But the original idea is narrower:

- let the AI make a basic page
- get feedback
- turn that feedback into explicit requirements
- revise the page

That is one execution loop more than it is a decomposition strategy.

## Suggested Human-AI Loop

The future operator loop should look like this:

1. The operator asks for a page or screen.
2. The AI creates a minimal but real first draft in code.
3. The AI presents a review summary in structured language rather than "what do you think?"
4. The AI asks a bounded requirement form such as:
   - required sections
   - required fields
   - labels or terminology that must appear
   - preferred tone or visual direction
   - examples or reference sites
   - must-avoid patterns
   - device priorities
5. The operator answers in plain language.
6. The runtime stores the resulting requirement set as a durable design-review artifact.
7. The AI revises the implementation against that artifact.
8. The operator either approves, requests another revision, or escalates to a broader redesign.

The key product value is requirement extraction for non-designers.

The workflow should help the operator produce useful input, not assume they already know design vocabulary.

## What The Workflow Should Ask For

A first-pass requirement form should probably bias toward concrete prompts the operator can answer.

Examples:

- "What must this page let the user do?"
- "Which fields must exist exactly?"
- "Which actions or buttons are required?"
- "What information should be visible without scrolling?"
- "Do you want this to feel more professional, playful, technical, minimal, or bold?"
- "Are there any sites or screenshots that feel close to what you want?"
- "What do you dislike about the current draft?"

That is more realistic than asking a novice operator for a full design brief.

## Five-System Impact For A Real Implementation

### Database

The real feature would likely need durable records for:

- draft-preview lineage
- design-review rounds
- structured requirement captures
- approval or rejection decisions
- final accepted design intent summary

### CLI

The CLI would need inspectable surfaces for:

- current collaborative-design status
- latest review questions
- recorded requirements
- pending approval gates
- accepted or rejected revisions

### Daemon

The daemon would need to own:

- pause/resume semantics for review-required tasks
- legality rules for when another revision may start
- artifact linkage between preview outputs and review feedback
- idempotent handling of repeated review submissions

### YAML

The workflow-profile definition would likely need declarative fields for:

- required review checkpoint categories
- required design-requirement capture sections
- allowed revision count or escalation policy
- whether screenshots, references, or coded previews are mandatory inputs

It may also later need design-policy-linked fields such as:

- required design-rule inputs
- allowed override categories
- required design verification targets

### Prompts

Prompt assets would need to cover:

- first-draft generation
- review request phrasing for non-designers
- requirement extraction from vague feedback
- revision planning
- approval or escalation summaries
- design-rule compliance guidance

## Design Rules Should Be First-Class

This future feature becomes much stronger if it also has:

- project-level design rules
- inherited page-level defaults
- explicit override handling
- strict tests that catch drift

That means the design workflow should not depend on the AI having strong visual instincts by itself.

It should instead let the operator approve or refine a design inside a constrained design-policy system.

## Tooling Direction

The future feature should not require a specific external design tool in order to be useful.

Recommended posture:

- default to code-first previews and screenshots generated from the real application
- allow optional reference inputs from external tools or links
- treat external design tools as supplements, not the source of truth

Useful tooling categories to evaluate later:

- collaborative mockup tools such as Figma-like or Penpot-like editors
- lightweight sketch/reference surfaces such as Excalidraw-like boards
- code-first component preview surfaces such as Storybook-style review environments
- browser screenshots and visual-diff tooling tied to the real repo

The repository's strongest advantage is likely coded preview plus structured review, not pixel-perfect design-tool parity.

## Risks And Failure Modes

- The operator may give vague feedback such as "make it nicer," which means the prompt and requirement form need to translate ambiguity into concrete follow-up questions.
- The AI may overfit to aesthetics and miss required fields or flows, so requirement capture has to stay grounded in concrete UI obligations.
- Review loops can stall if the runtime does not make pending human input obvious and durable.
- Screenshot-only review may hide interaction problems, so later versions may need richer local preview or browser-driven flows.
- If the loop remains chat-only, auditability will be weak and repeated revisions will drift.

## Recommended Next Planning Step

If this idea stays interesting after workflow-overhaul work advances, the next useful artifact would be a more explicit draft profile spec:

- prompt stack
- required artifacts
- review-state machine
- operator question set
- completion restrictions
- design-rule and override model

That draft is captured next in this bundle.
