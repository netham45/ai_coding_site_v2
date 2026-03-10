# Stage 03: Feature Delivery

## Purpose

Feature delivery is where the repository starts implementing actual product behavior under the documented process.

This stage exists to ensure that each meaningful feature is handled across:

- the affected systems
- the relevant notes
- the checklist layer
- the development-log layer
- bounded proof
- planned real E2E proof

## Stage Sub-Steps

### `feature_delivery.open_governing_context`

Why it exists:

- prevent meaningful changes from being made without a governing plan boundary

Required artifacts:

- governing feature-plan context
- governing task plan

Acceptance criteria:

- a task plan exists for the meaningful change
- adjacent feature context is named
- the plan includes the intended verification surface

Proof required:

- artifact existence check

Blocked claims:

- the change is properly governed

Advance when:

- the change can be explained through its plan context rather than only through code

### `feature_delivery.implement_across_systems`

Why it exists:

- force explicit accounting for affected systems rather than coding the convenient slice only

Required artifacts:

- implementation changes
- system-impact notes where needed

Acceptance criteria:

- affected systems are named explicitly
- implementation aligns with the stated system impact
- missing affected-system work is marked honestly if still pending

Proof required:

- review against task plan scope

Blocked claims:

- the feature is fully implemented across scope

Advance when:

- the intended affected systems are either handled or explicitly marked as still open

### `feature_delivery.update_operational_docs`

Why it exists:

- keep notes, logs, and checklists from drifting behind code

Required artifacts:

- note updates
- development-log updates
- checklist updates

Acceptance criteria:

- changed behavior is reflected in notes if required
- the development log records start, transition, or completion honestly
- checklist status matches actual proof and limitations

Proof required:

- doc-consistency checks where authoritative docs changed

Blocked claims:

- the feature state is inspectable

Advance when:

- an operator or contributor can reconstruct what changed and what is still missing

### `feature_delivery.run_bounded_proof`

Why it exists:

- prove the changed slice at the currently appropriate layer

Required artifacts:

- bounded tests
- task verification section

Acceptance criteria:

- the documented bounded command exists
- the command was actually run
- it passes for the claimed scope

Proof required:

- actual command execution

Blocked claims:

- `flow_complete`
- `release_ready`

Advance when:

- the feature has real bounded proof for the current slice

### `feature_delivery.record_e2e_gap_or_target`

Why it exists:

- stop bounded proof from being mistaken for final runtime proof

Required artifacts:

- named E2E target or explicit E2E gap statement
- operational-state checklist update if maturity language changes

Acceptance criteria:

- the real E2E target is named or the missing target is stated explicitly
- blocked stronger claims are still visible
- no stronger status is implied without the corresponding runtime proof

Proof required:

- artifact existence check

Blocked claims:

- `flow_complete` without real E2E proof
- `release_ready`

Advance when:

- the feature's runtime-proof story is explicit, even if still incomplete

## What This Stage Should Produce

Minimum expected artifacts:

- feature plans
- task plans
- implementation changes
- note updates
- checklist updates
- development-log updates
- bounded tests
- operational-state checklist updates when the repo's maturity meaningfully changes

## Recommended Files

- `plan/features/<feature>.md`
- `plan/tasks/<date>_<task>.md`
- `plan/checklists/<family>.md`
- `plan/checklists/00_project_operational_state.md`
- `notes/logs/features/<date>_<task>.md`
- affected notes under `notes/specs/`, `notes/contracts/`, or `notes/catalogs/`

## Questions This Stage Must Answer

- Which systems are affected?
- What invariants are introduced or defended?
- What notes must be updated?
- What bounded tests prove the behavior now?
- What real E2E target will eventually prove the behavior in runtime?
- Does the operational-state checklist still block stronger claims that this feature work does not yet justify?

## AI Instruction

If the repository is in feature-delivery stage, AI contributors should:

- open or follow a task plan before changing meaningful behavior
- update notes when implementation exposes missing behavior or assumptions
- update logs at start, major transitions, and completion
- update checklists honestly when proof is partial
- keep the operational-state checklist honest when the repo is still bounded-proof-only

Suggested `AGENTS.md` line:

> During feature delivery, no meaningful behavior change is complete without updated notes, a governing task plan, current development-log entries, checklist status updates, bounded tests, and a named real-E2E target.

## Entry Conditions

- Setup scaffold exists and its bootstrap proof passes.
- The project is ready to add real behavior.
- Feature and task plan families exist.

## Required Artifacts

- governing feature plan or adjacent feature-plan context
- governing task plan
- development log
- affected note updates
- checklist updates
- bounded tests
- named E2E target or explicit E2E gap statement
- operational-state checklist updates where maturity claims changed

## Required Verification Surface

Feature delivery should prove:

- the bounded tests for the changed behavior pass
- the relevant doc-consistency tests pass if authoritative docs changed
- the task's canonical verification commands were actually run

It does not automatically prove release readiness.

## Common Failure Modes

- Updating code without updating the notes it depends on.
- Marking features as complete without real E2E proof.
- Treating the checklist as optional bookkeeping.
- Forgetting to record the commands and results in the development log.
- Letting feature work imply maturity-stage advancement without updating the rollup checklist.

## Exit Conditions

A feature-delivery slice is complete enough to exit when:

- the intended implementation exists
- bounded proof exists
- notes, logs, and checklists are current
- the E2E target is named clearly
- the operational-state checklist still reflects the actual proving level honestly

## Example Deliverable

Example task verification section:

```md
## Verification

- Unit coverage: `pytest tests/unit/test_feature_x.py`
- Integration coverage: `pytest tests/integration/test_feature_x_cli.py`
- Docs coverage: `pytest tests/unit/test_feature_checklist_docs.py`
```
