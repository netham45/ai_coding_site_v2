# Project Lifecycle Overview

## Purpose

This repository uses staged development.

The project is expected to move through:

1. genesis
2. architecture
3. setup
4. feature delivery
5. hardening and end-to-end proof

The project should also reserve later continuation space for:

6. maintenance
7. evolution or migration

These stages exist to stop the repository from drifting into undocumented behavior or overstated completion claims.

## Core Rule

Contributors and AI agents must read the relevant lifecycle note before starting meaningful work in that stage.

When in doubt:

- start with this file
- then read the current stage note
- then read the operational-state checklist
- then read the governing task plan
- then update notes, logs, and checklists as required by that stage

## Relationship Between Artifacts

### `AGENTS.md`

`AGENTS.md` is the short operational doctrine.

It should tell contributors:

- what rules always apply
- what systems must be considered
- what completion language is allowed
- which lifecycle notes to read
- that stage-specific detail belongs in lifecycle sub-steps rather than inlined `AGENTS.md` growth

### `plan/checklists/00_project_operational_state.md`

The operational-state checklist is the maturity rollup.

It should record:

- the current stage
- which sub-steps are complete
- which stronger claims are still blocked
- what must happen before the repo can advance

### `notes/lifecycle/*.md`

The lifecycle notes are the detailed operating guide.

They explain:

- what stage the project is in
- what sub-steps exist inside that stage
- what artifacts must exist
- what proof is expected at that stage
- what must not be claimed yet

### `plan/tasks/*.md`

Task plans govern meaningful implementation or doc-alignment work.

No meaningful change should happen without a governing task plan.

### `notes/logs/**/*.md`

Development logs record what work was actually done, what commands were run, what passed or failed, and what the next step is.

### `plan/checklists/*.md`

Checklists track implementation and verification status.

They are not optional reminders.

They are part of the implementation surface.

## AI Instruction

AI contributors should be told to reference these lifecycle notes explicitly.

Suggested `AGENTS.md` instruction:

> Before meaningful work begins, read `notes/lifecycle/00_project_lifecycle_overview.md`, the current stage note, and `plan/checklists/00_project_operational_state.md`. Follow the rules for the current stage and its sub-steps.

## Stage Map

- `01_stage_00_genesis.md`: define the idea, systems, boundaries, and first invariants.
- `02_stage_01_architecture.md`: define architecture, durable state, system boundaries, and command surfaces.
- `03_stage_02_setup.md`: create the initial code and test skeleton plus the first bounded proof.
- `04_stage_03_feature_delivery.md`: deliver features with task plans, notes, logs, checklists, and bounded tests.
- `05_stage_04_hardening_and_e2e.md`: harden the system and prove real end-to-end behavior.
- later continuation stages should be added explicitly rather than assumed informally.

## Completion Language Rule

The repository should use completion language carefully.

- `implemented` means assets exist, but full real E2E proof may not exist yet.
- `verified` means the documented command for the claimed scope was actually run successfully.
- `flow_complete` means the declared flow passed end to end through real code.
- `release_ready` means the project satisfied its stronger proving, checklist, and readiness requirements.

Do not use stronger language than the current proof supports.

## Common Failure Modes

- Writing code before deciding what notes and plans govern the change.
- Treating notes as optional after code exists.
- Treating bounded tests as final completion proof.
- Forgetting to update logs and checklists when the work changes.
- Letting AI invent process rules instead of following documented ones.

## Exit Conditions For This Overview

This file is serving its purpose when:

- each later stage note exists
- `AGENTS.md` points here
- contributors can tell which file to read next for the current stage
