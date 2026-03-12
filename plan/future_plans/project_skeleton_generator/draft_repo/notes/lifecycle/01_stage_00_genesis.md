# Stage 00: Genesis

## Purpose

Genesis forces the repository to define what it is trying to become before implementation races ahead of understanding.

## Required Outcomes

- mission is captured
- systems are explicit
- stack choices are either explicitly undecided or explicitly proposed
- initial invariants and unknowns are recorded
- bootstrap governance is active
- operational state is initialized honestly

## Stage Sub-Steps

### `genesis.capture_mission`

- Why it exists: stop the purpose of the repo from living only in chat history.
- Required artifacts:
  - `notes/explorations/original_concept.md`
- Acceptance criteria:
  - the problem is stated plainly
  - intended users or operators are named
  - desired outcome is explicit

### `genesis.define_system_inventory`

- Why it exists: force explicit system thinking before code starts.
- Required artifacts:
  - `notes/catalogs/inventory/system_inventory.md`
- Acceptance criteria:
  - primary systems are named
  - each system has a clear responsibility
  - provisional systems are labeled honestly
  - chosen or still-open stack decisions are recorded explicitly instead of implied

### `genesis.record_invariants_and_unknowns`

- Why it exists: make first constraints and risks explicit before they are buried later.
- Required artifacts:
  - `notes/explorations/initial_risks_and_unknowns.md`
- Acceptance criteria:
  - at least one invariant is written down
  - unknowns are distinguished from firm rules

### `genesis.record_stack_direction`

- Why it exists: keep language, framework, persistence, and tooling choices explicit from the moment they start to matter.
- Required artifacts:
  - `notes/specs/architecture/stack_decision_record.md`
- Acceptance criteria:
  - the stack is either explicitly undecided or explicitly proposed
  - open questions are listed honestly
  - no later docs assume a settled stack that this note does not record

### `genesis.seed_bootstrap_governance`

- Why it exists: ensure the first meaningful work is governed rather than ad hoc.
- Required artifacts:
  - bootstrap task plan
  - bootstrap development log
  - bootstrap readiness checklist

### `genesis.initialize_operational_state`

- Why it exists: create a durable stage rollup before later work starts.
- Required artifacts:
  - `plan/checklists/00_project_operational_state.md`

## Blocked Claims

Until genesis is complete, do not claim:

- architecture is settled
- setup is complete
- runtime behavior is verified
- anything is flow-complete or release-ready
