# Project Lifecycle Note Set

## Goal

Define the lifecycle notes that the generated repository should include so contributors know how to move the project from empty scaffold to mature system.

This note now works together with the fully written examples under:

- `plan/future_plans/project_skeleton_generator/lifecycle_note_examples/`

The current concrete starter-repo rendering of those ideas now lives under:

- `plan/future_plans/project_skeleton_generator/draft_repo/notes/lifecycle/`

## Lifecycle Folder

The generated repository or cloneable starter repo should contain:

- `notes/lifecycle/`

This folder should be operational guidance for the new project, not historical notes from this repository.

Those lifecycle notes should also be written so they can map onto workflow-overhaul profile variants later, rather than using one-off stage terminology that cannot be expressed in the future orchestration model.

The lifecycle notes should be the place where stage-specific operational doctrine lives.

The generated `AGENTS.md` should point to them rather than attempting to inline all of their rules.

## Proposed Lifecycle Files

### `00_project_lifecycle_overview.md`

Purpose:

- explain the overall operating model
- explain the relationship between plans, notes, logs, checklists, and tests
- explain the difference between bounded proof and real E2E proof
- explain that lifecycle stages contain detailed sub-steps
- explain that the operational-state checklist is the stage rollup surface

### `01_stage_00_genesis.md`

Purpose:

- define how to capture the original concept
- define how to identify the main systems
- define what invariants to write down first
- define what should exist before architecture work starts
- define the stage sub-steps that must be satisfied before architecture work begins

Expected outputs:

- original concept note
- rough system inventory
- first future-plan notes

Suggested future profile alignment:

- `phase.genesis`
- `plan.bootstrap`
- `task.note_authoring`

### `02_stage_01_architecture.md`

Purpose:

- define how to convert the concept into an architecture
- define the code versus config boundary
- define the main durable state and runtime boundaries
- define initial canonical verification commands
- define the stage sub-steps that move the project from concept to explicit architecture

Expected outputs:

- architecture notes
- system boundary notes
- verification command catalog draft

Suggested future profile alignment:

- `phase.architecture`
- `plan.authoring`
- `plan.verification`

### `03_stage_02_setup.md`

Purpose:

- define how to create the initial code, test, and runtime skeleton
- define setup plans
- define migration or persistence bootstrap expectations if a database exists
- define first bounded-test surfaces
- define the stage sub-steps that create a real scaffold without overclaiming maturity

Expected outputs:

- setup plans
- starter tests
- starter logs
- starter readiness checklist

Suggested future profile alignment:

- `phase.setup`
- `plan.bootstrap`
- `task.structure_bootstrap`

### `04_stage_03_feature_delivery.md`

Purpose:

- define how to open feature plans
- define checklist updates
- define development-log expectations
- define note-maintenance expectations
- define bounded-test expectations during implementation
- define the stage sub-steps that make feature work operationally disciplined

Expected outputs:

- feature plans
- task plans
- feature checklist entries
- feature logs

Suggested future profile alignment:

- `phase.discovery`
- `phase.implementation`
- `phase.documentation`
- `phase.e2e`
- `plan.execution`
- `plan.doc_alignment`
- `plan.verification`

### `05_stage_04_hardening_and_e2e.md`

Purpose:

- define when the project moves from implemented to verified
- define how real E2E proof is tracked
- define release-readiness expectations
- define audit and resilience review expectations
- define the stage sub-steps that justify stronger runtime claims

Expected outputs:

- E2E plans
- E2E execution policy updates
- release-readiness or flow-completion evidence

Suggested future profile alignment:

- `phase.e2e`
- `phase.review`
- `phase.remediation`
- `task.e2e`
- `task.checklist_alignment`

### `06_stage_05_post_v1_evolution.md`

Purpose:

- define how the repository behaves after the first proven release scope exists
- explain that post-v1 work is choice-driven and may reopen earlier lifecycle disciplines
- define workstream categories such as major feature expansion, overhaul, assurance, migration, and sunset
- define how to decide whether new work needs local feature handling or a larger re-baselining effort
- define the stage sub-steps that keep post-v1 work governed instead of ad hoc

Expected outputs:

- governing epic or batch-plan context for the selected workstream
- refreshed architectural or operational notes where the workstream reopens earlier assumptions
- explicit proof and rollout targets for the chosen workstream
- current operational-state updates showing both baseline maturity and active post-v1 workstream

Suggested future profile alignment:

- `epic.feature`
- `epic.review`
- `epic.documentation`
- `phase.discovery`
- `phase.architecture`
- `phase.implementation`
- `phase.e2e`
- `phase.review`
- `phase.remediation`
- `plan.execution`
- `plan.verification`
- `plan.doc_alignment`

## Stage Checklist Discipline

Each lifecycle stage note should end with:

- stage sub-steps
- entry conditions
- required artifacts
- required verification surfaces
- common failure modes
- exit conditions

Each stage sub-step should be written as a small gate with:

- why it exists
- required artifacts
- acceptance criteria
- proof required
- blocked claims
- advancement rule

That gives the generated repo a practical operating script.

## Relationship To Generated AGENTS

The lifecycle notes should be the detailed process body.

The generated `AGENTS.md` should be the contributor-facing doctrine summary that points to those lifecycle notes.

Recommended generated `AGENTS.md` instruction:

> Before meaningful work begins, read `notes/lifecycle/00_project_lifecycle_overview.md`, the current stage note, and the operational-state checklist. Use the current lifecycle stage and its sub-steps as the default process guide for required plans, notes, logs, checklists, and proof expectations.

Recommended generated `AGENTS.md` follow-up instruction:

> When the repository includes starter lifecycle notes derived from the skeleton generator, reference them explicitly instead of inventing alternate process rules from memory.

Recommended generated operational-state instruction:

> Use `plan/checklists/00_project_operational_state.md` as the rollup source for current stage, blocked stronger claims, and advancement readiness.

Recommended workflow-overhaul follow-up instruction:

> When lifecycle stages map to declared workflow profiles, use the profile-aligned node variants instead of inventing ad hoc task categories for genesis, architecture, setup, documentation, or E2E work.

## Important Constraint

The generator should not seed overly mature lifecycle doctrine that implies the new project has already earned stronger proving layers.

The lifecycle notes should explicitly tell the new repo:

- what to add now
- what to defer
- what cannot be claimed yet

That keeps the generated project honest about its actual maturity.

## Post-Release Continuation

The lifecycle model should not stop at first release.

The generator should not stop at placeholder continuation states.

The better model is:

- one explicit post-v1 lifecycle note
- several named post-v1 workstreams inside that note
- clear rules for when a chosen workstream reopens architecture, setup, documentation, migration, or E2E obligations

## Concrete Example Set

The future generator should be able to render or adapt these example files directly:

- `lifecycle_note_examples/00_project_lifecycle_overview.md`
- `lifecycle_note_examples/01_stage_00_genesis.md`
- `lifecycle_note_examples/02_stage_01_architecture.md`
- `lifecycle_note_examples/03_stage_02_setup.md`
- `lifecycle_note_examples/04_stage_03_feature_delivery.md`
- `lifecycle_note_examples/05_stage_04_hardening_and_e2e.md`
- `lifecycle_note_examples/06_stage_05_post_v1_evolution.md`

These examples should be treated as:

- starter templates for the generated repo
- process references that `AGENTS.md` explicitly points to
- examples of what “good lifecycle notes” look like in a fresh disciplined repository
