# Workflow Overhaul Integration

## Purpose

Tie the project-skeleton-generator concept directly to the workflow-overhaul concept so the generated repository is not only a folder-and-doc scaffold, but also a natural target for the future profile-aware orchestration model.

## Main Decision

The skeleton-generator concept should not invent a separate task taxonomy.

It should align with the workflow-overhaul direction:

- stable node kinds: `epic`, `phase`, `plan`, `task`
- behavior differences expressed as workflow profiles and role-bearing layout children
- generated repository lifecycle stages expressed as reusable planning and delivery profiles

## Why This Matters

Without this integration, the future generator would create one operational model while the workflow-overhaul effort creates another.

That would cause drift in:

- lifecycle terminology
- prompt selection
- plan decomposition
- required updates
- verification posture
- closure expectations

The better direction is:

- one workflow substrate
- multiple profile-driven node variants

## Node Variants: Recommended Interpretation

For this future direction, "node variants" should usually mean:

- profile variants on stable node kinds

not:

- many new node kinds

Examples:

- `epic.planning`
- `epic.feature`
- `epic.documentation`
- `phase.genesis`
- `phase.architecture`
- `phase.setup`
- `phase.discovery`
- `phase.implementation`
- `phase.documentation`
- `phase.e2e`
- `phase.review`
- `phase.remediation`
- `plan.bootstrap`
- `plan.authoring`
- `plan.execution`
- `plan.verification`
- `plan.doc_alignment`
- `task.note_authoring`
- `task.structure_bootstrap`
- `task.implementation`
- `task.docs`
- `task.checklist_alignment`
- `task.log_update`
- `task.e2e`

These names are draft vocabulary.

The important point is that the generated repository should be decomposable using the same profile-aware model the workflow-overhaul notes are already moving toward.

## Lifecycle Stage To Workflow Profile Mapping

The generated repository lifecycle notes should map cleanly onto workflow profiles.

### Genesis

Recommended profile mapping:

- `epic.planning`
- `phase.genesis`
- `plan.bootstrap`
- `task.note_authoring`

Typical outputs:

- concept notes
- system inventory
- invariants draft
- future plans
- operational-state checklist initialized to genesis

### Architecture

Recommended profile mapping:

- `epic.planning`
- `phase.architecture`
- `plan.authoring`
- `plan.verification`
- `task.note_authoring`

Typical outputs:

- architecture notes
- boundary notes
- command catalog draft
- setup-plan set
- operational-state advancement rules for setup

### Setup

Recommended profile mapping:

- `epic.feature`
- `phase.setup`
- `phase.documentation`
- `plan.bootstrap`
- `plan.verification`
- `task.structure_bootstrap`
- `task.docs`

Typical outputs:

- scaffold directories
- starter code
- starter tests
- bootstrap checklist
- bootstrap log
- operational-state checklist advanced to setup

### Feature Delivery

Recommended profile mapping:

- `epic.feature`
- `phase.discovery`
- `phase.implementation`
- `phase.documentation`
- `phase.e2e`
- `plan.execution`
- `plan.doc_alignment`
- `plan.verification`

Typical outputs:

- feature plans
- task plans
- implementation changes
- note and checklist updates
- bounded proof
- named E2E targets
- lifecycle sub-step completion updates

### Hardening And E2E

Recommended profile mapping:

- `epic.review` or `epic.feature`
- `phase.e2e`
- `phase.review`
- `phase.remediation`
- `plan.verification`
- `task.e2e`
- `task.checklist_alignment`

Typical outputs:

- real E2E suites
- flow coverage updates
- execution policy updates
- remediation loops
- operational-state advancement toward flow-complete or release-ready scope

## Generated Repo As A Self-Hosting Target

The long-term value is that the generated repository should be able to describe its own development using the same orchestration concepts it was bootstrapped with.

That means a future generated project could eventually say:

- this bootstrap work is a planning epic
- this feature delivery effort is a feature epic
- this documentation cleanup is a documentation epic
- this hardening pass is a review epic

This is a much better self-hosting story than treating the generated repository's process docs as static prose disconnected from the workflow engine.

## Generator Responsibilities

The future generator should eventually be able to seed:

- lifecycle notes
- starter `AGENTS.md`
- starter operational-state checklist
- starter workflow-profile suggestions
- starter layout suggestions for planning and feature-delivery epics
- examples of which profile families correspond to which lifecycle stages

The first implementation does not need to create working runtime YAML for all of this.

But the design should reserve space for it.

## Suggested Starter Profile Families For Generated Repos

If the future generator adopts workflow-overhaul integration, the most useful starter profile families are:

- planning profiles
- bootstrap/setup profiles
- feature-delivery profiles
- documentation-alignment profiles
- E2E and hardening profiles

That is enough to cover the lifecycle notes without forcing a brand-new project to adopt the full mature profile catalog immediately.

## Constraints

- Do not silently require the full workflow-overhaul implementation before the generator is useful.
- Do not fork lifecycle terminology away from the workflow-overhaul terminology.
- Do not let profile selection live only in prompts; the future operational export should be able to carry profile and role expectations structurally.

## Recommended Follow-On Planning

After this integration note, the next useful future-planning artifacts would be:

- an `operational_profile` schema revision that includes workflow profiles and role expectations
- a starter generated `AGENTS.md` template that references lifecycle stages and workflow profiles together
- a draft starter `workflow_profiles/` family for generated repositories
