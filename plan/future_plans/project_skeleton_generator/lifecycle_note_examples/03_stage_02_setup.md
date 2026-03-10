# Stage 02: Setup

## Purpose

Setup creates the initial runnable repository skeleton.

This stage should establish:

- base code layout
- starter tests
- starter plans
- starter logs
- starter checklists
- bootstrap verification

## Stage Sub-Steps

### `setup.seed_structure`

Why it exists:

- create the minimum file and directory surface the repo needs to operate coherently

Required artifacts:

- scaffolded folder tree
- starter README
- starter `AGENTS.md`

Acceptance criteria:

- the expected base directories exist
- starter top-level docs exist
- the scaffold makes the next work discoverable instead of implicit

Proof required:

- structure or artifact existence check

Blocked claims:

- the repo is feature-ready

Advance when:

- the repository has the minimum disciplined skeleton on disk

### `setup.seed_governing_artifacts`

Why it exists:

- ensure setup work itself is governed and reconstructible

Required artifacts:

- bootstrap task plan
- bootstrap development log
- bootstrap readiness checklist

Acceptance criteria:

- the plan exists
- the log exists
- the checklist exists
- the artifacts cite each other coherently where appropriate

Proof required:

- document-schema or doc-linkage check where adopted

Blocked claims:

- setup is governed cleanly

Advance when:

- setup work is durably tracked instead of being an undocumented bootstrap burst

### `setup.seed_stage_governance`

Why it exists:

- make lifecycle-stage control active from the first runnable scaffold

Required artifacts:

- lifecycle notes
- operational-state checklist

Acceptance criteria:

- lifecycle notes exist
- the operational-state checklist exists
- the current stage is recorded honestly
- blocked stronger claims are explicit

Proof required:

- artifact existence check

Blocked claims:

- stage advancement is trustworthy

Advance when:

- contributors can tell which stage rules govern the repo right now

### `setup.establish_bounded_proof`

Why it exists:

- ensure setup has at least one real proving surface instead of empty structure

Required artifacts:

- bounded verification command
- doc-consistency or structure-check command

Acceptance criteria:

- at least one bounded command exists
- the command is runnable from a clean shell
- it passes
- the command is documented in the relevant plan or note surface

Proof required:

- actual command execution

Blocked claims:

- runtime behavior is verified
- `flow_complete`
- `release_ready`

Advance when:

- the scaffold is backed by real bounded proof rather than placeholders

### `setup.declare_e2e_intent`

Why it exists:

- keep the repository honest about the missing real proof layer

Required artifacts:

- named real E2E target

Acceptance criteria:

- at least one future real E2E target is named
- current docs say honestly that the target is still future work if it is not yet implemented
- stronger claims remain blocked explicitly

Proof required:

- artifact existence check

Blocked claims:

- `flow_complete`
- `release_ready`

Advance when:

- the repo has a declared real proof destination instead of pretending bounded proof is final

The operational-state checklist should only advance setup once the required sub-steps are actually satisfied.

## What This Stage Should Produce

Minimum expected artifacts:

- top-level folder structure
- runtime or application skeleton
- test skeleton
- operational-state checklist
- first bootstrap checklist
- first successful bounded proof command

## Recommended Files

- `plan/setup/00_project_bootstrap.md`
- `plan/checklists/00_project_operational_state.md`
- `plan/checklists/00_project_bootstrap_readiness.md`
- `notes/logs/setup/<date>_project_bootstrap.md`
- `tests/unit/test_bootstrap_docs.py`
- `tests/unit/test_bootstrap_structure.py`

## Questions This Stage Must Answer

- Does the repository have the expected base structure?
- Can contributors run the bootstrap verification commands from a clean shell?
- Are the first planning, logging, and checklist surfaces already in place?
- Does the operational-state checklist record setup as the current stage honestly?
- Is there at least one bounded proof path for the scaffold?

## AI Instruction

If the repository is in setup stage, AI contributors should:

- create the minimum viable structure cleanly
- keep placeholder docs explicit about what is not done yet
- add tests for the scaffold and doctrine surfaces
- update the operational-state checklist as setup sub-steps are completed
- avoid pretending the project is already feature-complete

Suggested `AGENTS.md` line:

> During setup, create the minimum disciplined scaffold and bounded-proof surface first. Seed notes, plans, logs, and checklists before claiming the repository is ready for feature delivery.

## Entry Conditions

- Architecture notes and command catalog exist.
- The repository is ready to create actual code and test folders.
- Bootstrap artifact expectations are clear.

## Required Artifacts

- scaffolded folder tree
- bootstrap task plan
- bootstrap development log
- operational-state checklist
- bootstrap readiness checklist
- starter tests
- starter README and AGENTS

## Required Verification Surface

Setup should have at least:

- one bounded command that validates the scaffold
- one doc-consistency or structure check
- one smoke test for the starter code surface if code exists

Real E2E proof is usually still future work.

## Common Failure Modes

- Creating code folders without any doctrine files.
- Creating doctrine files without any verification commands.
- Treating placeholder commands as if they were real proof.
- Failing to leave placeholders that explain what the scaffold does not yet prove.
- Confusing scaffold presence with runtime readiness.

## Exit Conditions

Setup is complete enough to exit when:

- the scaffold exists
- the bootstrap proving command passes
- the repository has starter notes, plans, logs, and checklists
- the operational-state checklist can honestly mark setup as satisfied for the current scope
- feature work can begin without inventing the process from scratch

## Example Deliverable

Example bootstrap checklist row:

```md
| Area | Status | Notes |
| --- | --- | --- |
| AGENTS and lifecycle docs | implemented | Starter doctrine exists and points contributors at the stage notes. |
| Bootstrap verification command | implemented | `pytest tests/unit/test_bootstrap_docs.py` |
```
