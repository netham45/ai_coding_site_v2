# Workflow Overhaul Prompt Contract

## Purpose

Define the shared planning-stage contract that every prompt under `plan/future_plans/workflow_overhaul/prompts/` should follow.

This is a future-plan prompt-contract note.

It is not an active runtime prompt-pack contract yet.

## Why This Note Exists

The workflow-overhaul bundle needs prompts that are:

- structurally consistent
- reviewable across tiers
- explicit about lifecycle and legality
- aligned with the rigid workflow-enforcement model in the surrounding notes

Without a shared contract, prompt behavior can drift into:

- inconsistent section shape
- missing lifecycle or escalation instructions
- vague completion language
- soft prompt advice where the future runtime expects hard blocked mutations

## Core Rule

Every planning-stage prompt in this bundle should describe:

1. what this node is
2. what this prompt is trying to produce
3. where this prompt sits in the workflow lifecycle
4. what inputs the runtime must inject
5. what actions are allowed
6. what actions are forbidden
7. what result shape is required
8. what conditions must be satisfied before the step can be treated as complete
9. what should happen when the work cannot proceed legally

## Recommended Composition Model

The preferred design for this bundle is:

- one tier base prompt per node tier
- one profile overlay per workflow profile
- one briefing prompt per tier where briefing behavior is tier-specific rather than profile-specific

Recommended shape:

- `epic/base.md` plus profile overlays such as `epic/feature.md`
- `sub_epic/base.md` plus profile overlays such as `sub_epic/implementation.md`
- `plan/base.md` plus profile overlays such as `plan/execution.md`
- `task/base.md` plus profile overlays such as `task/review.md`

Reason:

- shared lifecycle and enforcement language should be centralized
- profile prompts should mostly describe deltas, not restate the entire contract
- drift is easier to detect when the non-profile-specific sections live in one file per tier

## Required Sections

### 1. `Role`

Must explain:

- the current node tier and profile style
- what this prompt is allowed to decide
- what this prompt must not decide

### 2. `Objective`

Must explain:

- the immediate goal of the prompt
- the expected result of a successful turn
- the narrow scope of success for this step

### 3. `Lifecycle Position`

Must explain:

- the current workflow stage
- prerequisite steps or current-state assumptions
- the next legal downstream step after success
- whether the prompt is decomposition, execution, verification, remediation, or briefing oriented

For decomposition-required tiers, this section should make clear that:

- higher tiers must create or reconcile children
- they must not skip directly to merge or completion

### 4. `Inputs`

Must list the runtime-provided inputs the prompt expects.

Typical inputs include:

- node identity and title
- selected workflow profile
- effective layout
- acceptance criteria
- required repository updates
- required verification
- policy constraints
- context bundle
- current child state
- blocked reasons
- available child kinds, roles, or profiles injected programmatically

### 5. `Allowed Actions`

Must state what the session may do in this step.

Examples:

- define child nodes
- execute one bounded task
- gather evidence
- run declared commands
- perform narrow merge or documentation reconciliation

### 6. `Forbidden Actions`

Must state what the session may not do.

This should include, where applicable:

- step skipping
- silent scope narrowing
- silent scope broadening
- parent-tier absorption of child-owned implementation
- undocumented behavior invention
- unsupported completion claims

### 7. `Expected Result`

Must state the output the prompt is trying to produce.

Examples:

- a child layout definition
- a bounded task-completion result
- a verification evidence package
- a remediation handoff
- a compiler-generated brief interpretation posture

### 8. `Completion Conditions`

Must state what must be true before the result can honestly count as complete for this step.

Examples:

- required roles are covered
- required outputs are explicit
- required commands ran
- required evidence exists
- required findings or summaries were produced

This section should not imply that prompt success alone overrides future daemon gating.

### 9. `Escalation Or Failure`

Must explain what to do when the step cannot legally or honestly finish.

Typical rules:

- fail clearly instead of guessing
- request replan when structure is wrong
- leave a blocked result when prerequisites are missing
- hand off to remediation rather than patching around the issue silently

### 10. `Response Contract`

Must define the structured response shape expected from the prompt.

For decomposition prompts this is usually JSON.

For execution prompts this is usually a structured status/result schema.

The response contract should use explicit status vocabulary and avoid free-form completion claims outside the schema.

## Base Prompt Rule

Each tier base prompt should include the full required section set.

The base prompt is the main source for:

- lifecycle position
- allowed and forbidden action rules
- enforcement posture
- general expected-result shape
- escalation posture
- response contract

## Overlay Prompt Rule

Each profile overlay may be thinner than a base prompt.

An overlay should usually provide:

- profile-specific role deltas
- profile-specific objective deltas
- profile-specific input expectations
- additional forbidden actions
- profile-specific expected results
- profile-specific completion conditions

An overlay should not restate the entire base prompt unless the profile is materially different enough to justify a standalone full prompt.

If a profile truly needs a fully different contract, that should be an explicit exception, not the default pattern.

## Tier-Specific Expectations

### Brief prompts

`global_brief` prompts should still follow the contract, but their expected result is different.

They should emphasize:

- briefing purpose
- lifecycle posture
- authoritative interpretation of compiled state
- how the receiving session should use the brief

### Decomposition prompts

`epic`, `sub_epic`, and `plan` decomposition prompts must explicitly include:

- delegation expectations
- required child role coverage
- prohibition on performing child-owned work at the current tier

### Task prompts

`task` prompts must explicitly include:

- bounded execution scope
- artifact and verification ownership
- structured completion or blocked result expectations

## Programmatic Inputs The Future Runtime Should Inject

The future runtime should be able to inject, where applicable:

- `workflow_profile`
- `selected_layout`
- `required_child_roles`
- `available_child_kinds`
- `available_child_profiles`
- `required_updates`
- `required_verification`
- `completion_restrictions`
- `blocked_actions`
- `current_step`
- `next_legal_steps`
- `context_bundle`

Not every prompt needs every field, but the contract should make those surfaces explicit.

## Relationship To Rigid Workflow Enforcement

This prompt contract is not a replacement for daemon enforcement.

The surrounding workflow-overhaul notes already require:

- rigid step order
- explicit subtask completion predicates
- blocked `4xx` responses for skipped required steps

Prompts should reinforce those rules, not invent a softer alternative.

## Practical Authoring Rule

When adding or revising a prompt in this bundle:

- preserve the required section order unless there is a strong reason not to
- keep shared tier behavior in the base prompt and profile-specific deltas in the overlay
- prefer explicit allowed/forbidden/completion language over tone-only guidance
