# Rendered Operational State Checklist Example

## Purpose

Show what a generated repository's `plan/checklists/00_project_operational_state.md` could look like once the stage-governance model is rendered into an actual checklist artifact.

This is an example output for the future generator design, not an authoritative checklist for this repository.

## Suggested Header

```md
# Project Operational State

## Goal

Track the repository's current operational maturity honestly.

Use this checklist to:

- record the current lifecycle stage
- record which sub-stages are complete
- record what stronger claims are still blocked
- record what must pass before the repository can advance
```

## Suggested Current-State Summary

```md
## Current State

- Active stage: `setup`
- Current maturity status: `setup_bootstrapped`
- Next target stage: `feature_delivery_ready`
- Stronger claims currently blocked: `flow_complete`, `release_ready`
- Governing references:
  - `notes/lifecycle/00_project_lifecycle_overview.md`
  - `notes/lifecycle/03_stage_02_setup.md`
  - `notes/catalogs/checklists/verification_command_catalog.md`
```

## Example State Table

This example uses a repository that has completed setup cleanly, has bounded proof, but has not yet landed real E2E.

```md
| State | Status | Current stage? | Acceptance summary | Proof summary | Blocked stronger claims | Advance when |
| --- | --- | --- | --- | --- | --- | --- |
| `genesis` | complete | no | Mission, system inventory, initial invariants, and bootstrap governance exist. | Planning artifacts and operational-state checklist exist. | `verified`, `flow_complete`, `release_ready` were blocked until later stages. | Architecture inputs are explicit. |
| `architecture_defined` | complete | no | Boundaries, state model, code/config boundary, and real command surfaces are documented. | Architecture notes and command catalog exist. | `flow_complete`, `release_ready` were blocked until later stages. | Setup can begin without guessing boundaries. |
| `setup_bootstrapped` | complete | yes | Scaffold, lifecycle docs, governing artifacts, bounded proof, and first E2E intent exist. | Bounded scaffold command passes; doc checks pass. | Runtime `verified` beyond bounded scope, `flow_complete`, `release_ready`. | Feature work can proceed under task-plan governance. |
| `feature_delivery_ready` | in_progress | no | Task-plan, log, checklist, and note-maintenance processes are partly active. | At least one feature/task slice is governed; command surfaces exist. | `flow_complete`, `release_ready`. | Feature work can proceed repeatedly without ad hoc process invention. |
| `bounded_verified` | planned | no | Current bounded-proof discipline is not yet broadly established. | Additional bounded commands still need to pass for active feature families. | `flow_complete`, `release_ready`. | Active feature slices have passing bounded proof and current checklist status. |
| `e2e_ready` | planned | no | Real E2E target exists, but the repo is not yet ready to prove it. | E2E policy and mapping are incomplete or not yet current. | `release_ready`. | Real runtime proof target and boundaries are concrete enough to test. |
| `flow_complete` | blocked | no | No real end-to-end runtime narrative has passed yet. | No real E2E command has passed for the declared flow scope. | N/A | Declared real E2E command passes and docs are current. |
| `release_ready` | blocked | no | Stronger release bar not yet met. | Real E2E, resilience, and readiness evidence are incomplete. | N/A | Release-scope proving surfaces pass and readiness docs are current. |
```

## Example Stage Detail

### `setup_bootstrapped`

```md
## Stage: `setup_bootstrapped`

- Purpose: Establish the first runnable repository skeleton and bounded proof surface.
- Status: `complete`
- Current stage: `yes`
- Blocked stronger claims:
  - runtime `verified` beyond bounded scope
  - `flow_complete`
  - `release_ready`
```

#### `setup.seed_structure`

```md
- Status: `complete`
- Why it exists: Create the minimum file and directory surface the repo needs to operate coherently.
- Required artifacts:
  - top-level scaffold directories
  - starter `README.md`
  - starter `AGENTS.md`
- Acceptance criteria:
  - expected base directories exist
  - starter top-level docs exist
  - the scaffold makes next work discoverable
- Proof required:
  - `python3 -m pytest tests/unit/test_bootstrap_structure.py`
- Result:
  - Passed on 2026-03-10
- Advance when:
  - the repository has the minimum disciplined skeleton on disk
```

#### `setup.seed_governing_artifacts`

```md
- Status: `complete`
- Why it exists: Ensure setup work itself is governed and reconstructible.
- Required artifacts:
  - bootstrap task plan
  - bootstrap development log
  - bootstrap readiness checklist
- Acceptance criteria:
  - plan, log, and checklist all exist
  - the artifacts cite each other coherently
- Proof required:
  - `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py`
- Result:
  - Passed on 2026-03-10
- Advance when:
  - setup work is durably tracked instead of undocumented
```

#### `setup.seed_stage_governance`

```md
- Status: `complete`
- Why it exists: Make lifecycle-stage control active from the first runnable scaffold.
- Required artifacts:
  - lifecycle notes
  - operational-state checklist
- Acceptance criteria:
  - lifecycle notes exist
  - the operational-state checklist exists
  - the current stage is recorded honestly
  - blocked stronger claims are explicit
- Proof required:
  - artifact existence review
- Result:
  - Complete for current setup scope
- Advance when:
  - contributors can tell which stage rules govern the repo right now
```

#### `setup.establish_bounded_proof`

```md
- Status: `complete`
- Why it exists: Ensure setup has at least one real proving surface instead of empty structure.
- Required artifacts:
  - bounded verification command
  - doc-consistency or structure-check command
- Acceptance criteria:
  - at least one bounded command exists
  - the command is runnable from a clean shell
  - it passes
  - the command is documented in the relevant plan or note surface
- Proof required:
  - `python3 -m pytest tests/unit/test_bootstrap_docs.py`
  - `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py`
- Result:
  - Passed on 2026-03-10
- Blocked stronger claims:
  - runtime `verified`
  - `flow_complete`
  - `release_ready`
- Advance when:
  - the scaffold is backed by real bounded proof rather than placeholders
```

#### `setup.declare_e2e_intent`

```md
- Status: `complete`
- Why it exists: Keep the repository honest about the missing real proof layer.
- Required artifacts:
  - named future real E2E target
- Acceptance criteria:
  - at least one future real E2E target is named
  - current docs say honestly that it is still future work
  - stronger claims remain blocked explicitly
- Proof required:
  - checklist and note review
- Result:
  - E2E target declared; still not complete
- Advance when:
  - the repo has a declared real proof destination instead of pretending bounded proof is final
```

## Suggested Status Vocabulary

For a rendered checklist like this, a practical starting vocabulary would be:

- `planned`
- `in_progress`
- `complete`
- `blocked`

If the generated repository later wants stronger structural enforcement, it can adopt a stricter checklist schema through its lifecycle notes.

## Why This Example Matters

The important part is not the exact prose.

The important part is that the rendered checklist makes it obvious:

- what stage the repo is in
- what has actually passed
- what still blocks stronger claims
- what must happen next
