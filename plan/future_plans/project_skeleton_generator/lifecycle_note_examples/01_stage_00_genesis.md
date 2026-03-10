# Stage 00: Genesis

## Purpose

Genesis is where the repository records what it is trying to become before implementation starts.

This stage exists to force the project to define:

- the product mission
- the major systems
- the rough stack
- the first invariants
- the first obvious risks and unknowns

## Stage Sub-Steps

### `genesis.capture_mission`

Why it exists:

- prevent the repository purpose from living only in chat history

Required artifacts:

- mission or concept note

Acceptance criteria:

- the project problem is stated plainly
- the intended users or operators are named
- the note is stored durably in the repository

Proof required:

- artifact existence check

Blocked claims:

- architecture is defined
- implementation is ready

Advance when:

- the mission note exists and answers the basic "what is this repo for?" question

### `genesis.define_system_inventory`

Why it exists:

- force explicit system thinking before code starts

Required artifacts:

- initial system inventory note

Acceptance criteria:

- the primary systems are named
- each system has a short responsibility statement
- unknown or provisional systems are labeled honestly

Proof required:

- artifact existence check
- review that system responsibilities are explicit rather than implied

Blocked claims:

- full architecture readiness

Advance when:

- contributors can identify the repo's major systems without guessing

### `genesis.record_invariants_and_unknowns`

Why it exists:

- make first constraints and risks explicit before they are buried later

Required artifacts:

- initial invariants and unknowns note

Acceptance criteria:

- at least one meaningful invariant is written down
- obvious unknowns or risks are recorded explicitly
- the note distinguishes invariant from open question

Proof required:

- artifact existence check

Blocked claims:

- mature completion language

Advance when:

- the repo has a written starting point for constraints and uncertainty

### `genesis.seed_bootstrap_governance`

Why it exists:

- ensure the first meaningful work is governed rather than ad hoc

Required artifacts:

- bootstrap task plan
- bootstrap development log

Acceptance criteria:

- the bootstrap task plan exists
- the bootstrap development log exists
- the plan and log cite each other coherently

Proof required:

- document-schema checks for authoritative plan/log surfaces where adopted

Blocked claims:

- setup has started cleanly

Advance when:

- the first bootstrap work is durably governed and logged

### `genesis.initialize_operational_state`

Why it exists:

- create the rollup maturity surface before later stage advancement

Required artifacts:

- operational-state checklist

Acceptance criteria:

- the checklist exists
- genesis is marked as the current active stage
- stronger claims are explicitly blocked

Proof required:

- artifact existence check

Blocked claims:

- advancement into architecture without a durable stage record

Advance when:

- the operational-state checklist records genesis honestly

## What This Stage Should Produce

Minimum expected artifacts:

- a concept note
- a system inventory
- a rough stack note
- one or more future-plan notes
- an initial project bootstrap task plan
- an operational-state checklist initialized to genesis

## Recommended Files

- `notes/explorations/original_concept.md`
- `notes/catalogs/inventory/system_inventory.md`
- `notes/explorations/initial_risks_and_unknowns.md`
- `plan/future_plans/<topic>/README.md`
- `plan/tasks/<date>_project_bootstrap.md`
- `plan/checklists/00_project_operational_state.md`

## Questions This Stage Must Answer

- What problem is this repository solving?
- Who operates or uses the system?
- What are the primary systems?
- What must never happen?
- What data or records must always exist?
- What parts of the design are still unknown?
- Does the operational-state checklist reflect genesis honestly?

## AI Instruction

If the repository is still in genesis, AI contributors should:

- prefer note creation over code creation
- identify missing system boundaries
- identify missing invariants
- initialize or update the operational-state checklist before pretending the repo has advanced
- avoid pretending architecture decisions are already settled

Suggested `AGENTS.md` line:

> If the repository is in genesis, do not jump straight to implementation. First update the concept, system inventory, and future-plan notes until the basic architecture questions are explicit.

## Entry Conditions

- The repository exists but does not yet have a settled architecture.
- Primary systems or stack choices are still unclear.
- Completion and verification language would be premature.

## Required Artifacts

- mission statement
- primary system inventory
- rough stack statement
- initial invariant list
- bootstrap task plan
- bootstrap development log
- operational-state checklist

## Required Verification Surface

Genesis usually does not require product runtime proof yet.

It does require proof that:

- the planning artifacts exist
- the repository has a declared structure
- contributors know what to read next

## Common Failure Modes

- Starting implementation while the primary systems are still vague.
- Choosing stack components without writing them down.
- Letting the project mission live only in chat history.
- Acting as if all systems are affected equally without thinking through them.
- Advancing out of genesis without recording that state transition anywhere durable.

## Exit Conditions

Genesis is complete enough to exit when:

- the repository mission is written down
- the primary systems are named
- the initial stack direction is written down
- the operational-state checklist can honestly mark genesis complete for the current scope
- the next architecture stage has a clear starting point

## Example Deliverable

Example system inventory snippet:

```md
# System Inventory

- Database: durable truth for application state and history.
- CLI: operator and AI command surface.
- Daemon: authoritative runtime behavior.
- Config: declarative project structure and policy.
- Prompts: first-class execution and review assets.
```
