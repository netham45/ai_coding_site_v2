# Project Operational State Checklist

## Purpose

Define the canonical stage-tracking artifact that a generated repository should use to record its current operational maturity.

This checklist is the bridge between:

- a concise generated `AGENTS.md`
- detailed lifecycle-stage notes
- honest completion and proving claims

The generated repository should use this checklist to answer:

- what lifecycle stage the repo is currently in
- which stage sub-steps are already satisfied
- which stronger rules are active now
- which claims are still forbidden

## Core Model

The generated repository should not pretend all mature-repo rules are active on day zero.

Instead, it should adopt stage-gated rigor:

- each lifecycle stage has explicit sub-steps
- each sub-step has proof expectations
- later-stage requirements do not become mandatory until the repo reaches that stage
- stronger status claims are forbidden until the current stage's sub-steps justify them

`AGENTS.md` should point contributors to this checklist and the current lifecycle note rather than attempting to inline every stage-specific rule.

## Suggested File Location

- `plan/checklists/00_project_operational_state.md`

This should be the generated repository's top-level operational maturity checklist.

Stage-local checklists may still exist, but they should roll up into this file rather than replacing it.

For a concrete example of the rendered output shape, see:

- `plan/future_plans/project_skeleton_generator/2026-03-10_rendered_operational_state_example.md`

## Suggested Checklist Shape

Each state row or section should include:

- state name
- purpose
- current status
- required sub-steps
- sub-step acceptance criteria
- proof surface
- blocked stronger claims
- advancement rule

Each sub-step should be written as an enforceable gate with:

- sub-stage name
- why it exists
- required artifacts
- acceptance criteria
- proof required
- blocked claims
- advancement rule

## Suggested States

### `genesis`

Purpose:

- capture the project idea
- identify the primary systems
- define first invariants and boundaries

Required sub-steps:

- concept note exists
- initial system inventory exists
- first lifecycle notes exist
- first future-plan or architecture direction note exists

Proof surface:

- artifact existence checks
- note-structure or doc-consistency checks where adopted
- explicit confirmation that the operational-state checklist records genesis honestly

Blocked stronger claims:

- `verified`
- `flow_complete`
- `release_ready`

### `architecture_defined`

Purpose:

- convert the idea into an explicit architecture and operating model

Required sub-steps:

- architecture notes exist
- code/config or code/YAML boundary is documented
- initial verification command catalog exists
- initial document-family expectations are named
- initial invariants are written down

Proof surface:

- architecture and boundary notes exist
- initial command catalog exists
- setup plans cite the intended proving commands

Blocked stronger claims:

- `flow_complete`
- `release_ready`

### `setup_bootstrapped`

Purpose:

- establish the first runnable repository skeleton and bounded proof surface

Required sub-steps:

- bootstrap task plan exists
- bootstrap development log exists
- starter `AGENTS.md` exists and points to lifecycle governance
- operational-state checklist exists
- bounded verification command is real and runnable
- document-consistency command is real and runnable
- first real E2E target is named, even if still `planned`

Proof surface:

- bounded command passes from a clean shell
- doc-consistency command passes from a clean shell
- starter plan, log, and checklist surfaces cite each other coherently

Blocked stronger claims:

- runtime `verified` claims not backed by real commands
- `flow_complete`
- `release_ready`

### `feature_delivery_ready`

Purpose:

- allow feature work to proceed without inventing process rules ad hoc

Required sub-steps:

- task-plan process is active
- development-log process is active
- feature checklist process is active
- note-maintenance expectations are explicit
- canonical command surfaces are documented for current work

Proof surface:

- at least one feature/task slice can be opened without inventing process rules
- current task plans cite verification commands
- current logs and checklists reflect actual work state

Blocked stronger claims:

- `flow_complete` for unproven runtime behavior
- `release_ready`

### `bounded_verified`

Purpose:

- confirm the repository has real bounded-proof discipline for its current scope

Required sub-steps:

- bounded commands pass
- current authoritative document tests pass
- current checklist statuses match actual proof
- known limitations are stated explicitly

Proof surface:

- bounded verification command passes
- current document-family consistency tests pass for changed authoritative surfaces
- checklist status language matches the documented proof level

Blocked stronger claims:

- `flow_complete` for flows without real E2E proof
- `release_ready`

### `e2e_ready`

Purpose:

- move the repository into real runtime proving mode

Required sub-steps:

- at least one real E2E target is mapped explicitly
- E2E execution policy exists
- flow or feature mapping to E2E exists
- real runtime boundaries are identified for the next proof layer

Proof surface:

- E2E targets are named in authoritative docs
- execution policy and mapping docs agree on the intended real proof surface
- next runtime boundary is concrete enough to test

Blocked stronger claims:

- `release_ready` until required real E2E passes

### `flow_complete`

Purpose:

- record that a declared runtime narrative passes end to end for the stated scope

Required sub-steps:

- declared real E2E command passes
- related checklist and mapping docs are current
- remaining gaps outside the declared scope are stated explicitly

Proof surface:

- real E2E command passes
- coverage and checklist docs cite that command consistently
- scope caveats are written down explicitly

### `release_ready`

Purpose:

- record that the repository meets its stated release-scope proving bar

Required sub-steps:

- required bounded and real E2E proof passes
- relevant notes, logs, and checklists are current
- readiness caveats are explicit
- required resilience, audit, and performance expectations are satisfied for the declared scope

Proof surface:

- release-scope proving commands pass
- readiness docs and checklists are current
- resilience, audit, and performance expectations are documented and met for the declared release scope

## Post-Release Continuation States

The generator should reserve lifecycle space beyond `release_ready`.

These later states do not need full criteria yet, but the generated repository should know they exist:

- `maintenance`
- `hardening`
- `evolution`
- `deprecation`
- `migration`

The lifecycle notes should define them later rather than leaving the process to end at first release.

## Relationship To `AGENTS.md`

The generated `AGENTS.md` should not grow by copying every stage-specific rule inline.

Instead, it should say, in effect:

> Follow the current lifecycle stage and the operational-state checklist. Apply the sub-step rules for the stage the repository is actually in. Do not enforce or claim later-stage maturity early.

## Relationship To Stage Notes

Each lifecycle note should contain the detailed sub-steps for that stage.

Each sub-step should define:

- requirement
- expected artifacts
- proving command or proof type
- common shortcuts to avoid
- advancement condition

That keeps the detail in the lifecycle notes while letting the operational-state checklist remain the rollup surface.
