# Project Skeleton Generator Overview

## Purpose

Define a future direction for a starter repository and, optionally later, a tool or function that can inspect this repository's operational framework and produce a new, empty project that follows the same broad discipline.

This is not a proposal to clone the current product.

It is a proposal to clone the repository's operating model:

- planning-first development
- explicit system boundaries
- notes as implementation assets
- required development logs
- bounded-test to real-E2E progression
- explicit verification commands
- checklist-based status discipline
- lifecycle-stage guidance
- profile-aware workflow decomposition

The current best delivery direction is to expose that operating model first as a separate repository users are encouraged to clone.

Automation can follow later if it still provides enough value after the starter repository shape has stabilized.

## Desired Outcome

The starter project should start life with enough structure that an AI or human contributor can build a new system without rediscovering the process doctrine from scratch.

The starter project should already contain:

- `AGENTS.md`
- `plan/`
- `notes/`
- `simulations/`
- `code/`
- starter test directories
- starter verification command notes
- starter lifecycle notes
- an operational-state checklist
- starter checklists
- a starter inventory of primary systems

## Main Idea

Treat this repository as two layers:

1. Product layer
2. Operational layer

The future starter repo and any later generator should extract only the operational layer by default.

That means the generator should carry forward:

- document families
- status vocabulary
- plan/checklist/log workflow
- lifecycle-stage doctrine
- lifecycle-stage sub-step doctrine
- verification doctrine
- folder topology
- scaffolded note prompts
- system-coverage expectations

It should not blindly copy:

- current feature inventory
- repo-specific orchestration semantics
- repo-specific YAML assets
- repo-specific database schema
- repo-specific runtime contracts

## Working Thesis

The safest way to build this is to define a concrete cloneable starter repository first, then, if still useful, model the current repository's operational state as a structured export that can render that same repository shape automatically.

That gives the future implementation two separable jobs:

1. Define and stabilize the target starter repository.
2. Optionally extract and normalize operational doctrine from the source repository so it can render that target repository from a template pack plus project-specific answers.

This should align with the workflow-overhaul direction already captured in:

- `plan/future_plans/workflow_overhaul/2026-03-10_self_hosted_workflow_overhaul_notes.md`

The starter repository should ideally be bootstrapped in a way that can later map onto the same `epic -> phase -> plan -> task` substrate with profile-aware variants.

## Current Review Surface

The concrete starter-repo draft now lives under:

- `plan/future_plans/project_skeleton_generator/draft_repo/`

Review and refine that tree as the primary artifact.

## Proposed Capabilities

The future implementation should eventually be able to:

- read the source repository's doctrinal files
- identify canonical document families
- identify required folder structure
- identify required status vocabularies
- identify lifecycle stages and stage artifacts
- identify stage-local sub-steps and advancement rules
- identify reusable workflow profiles and stage-to-profile mappings
- identify checklist categories
- identify development-log requirements
- identify canonical verification command surfaces
- identify the declared primary systems for the new project
- emit or publish a clean starter repository with placeholders instead of copied product logic
- emit a concise `AGENTS.md` that points contributors at the active lifecycle stage instead of expanding every stage rule inline
- emit a reviewable starter `AGENTS.md` template that shows how global doctrine and stage-local doctrine are split
- emit starter workflow-profile guidance for planning, setup, delivery, docs, and E2E
- emit starter post-v1 workstream guidance so the generated repo does not stop at first release

## Non-Goals

The first version should not try to:

- infer arbitrary product architecture from code
- copy all notes wholesale into the new repo
- preserve every single source-repo document family
- auto-generate a finished feature inventory
- claim that the generated project is release-ready
- infer strong process rules from tests alone

## Working Questions

- Which parts of the current doctrine are truly reusable versus only meaningful for this repository?
- Which document families should be seeded immediately versus adopted later?
- How much of `AGENTS.md` should be parameterized versus static?
- Should the generated project always start with five core systems, or should system count be configurable while still encouraging explicit system coverage?
- How strict should the starting checklist layer be in a fresh repo before real features exist?

## Current Direction

The current best direction is:

- publish a separate starter repo users can clone
- keep a concrete draft starter tree in this future-plan bundle until that repo exists
- let lifecycle notes carry detailed stage-specific doctrine
- keep an operational-state checklist that records which stage and sub-steps are active
- allow stronger claims only when the repo reaches the corresponding proving level

## Post-V1 Gap

The current bundle is strongest from empty scaffold through first hardening.

The next gap is what happens after that.

Once a generated repository reaches a first `flow_complete` or `release_ready` scope, the lifecycle becomes choice-driven. The repository may need to:

- add a new major feature family
- introduce a new subsystem or platform surface
- perform a security, compliance, or resilience audit
- replace or heavily refactor an existing architecture slice
- migrate data, traffic, or ownership to another service
- deprecate or sunset behavior deliberately

The future generator therefore needs to seed a post-v1 operating model that tells contributors how to reopen discovery, architecture, setup, delivery, and E2E work intentionally for the chosen kind of change.
