# Stage 04: Hardening And End-To-End Proof

## Purpose

Hardening and E2E is where the repository proves the real runtime behavior it intends to claim.

This stage exists to move the project beyond:

- partial implementation
- bounded-only proof
- optimistic completion language

and into:

- real runtime validation
- flow-based proof
- resilience and audit review
- honest readiness claims

## Stage Sub-Steps

### `hardening.map_real_scope`

Why it exists:

- define exactly which runtime narrative is being proven

Required artifacts:

- E2E plan
- mapped flow or feature target

Acceptance criteria:

- the target flow or feature family is named explicitly
- the intended runtime boundaries are named explicitly
- the claimed scope is narrow enough to prove honestly

Proof required:

- artifact existence check

Blocked claims:

- broad completion claims for undefined scope

Advance when:

- the repo can say exactly what runtime story it is attempting to prove

### `hardening.run_real_proof`

Why it exists:

- move from bounded confidence to real runtime evidence

Required artifacts:

- real E2E command
- E2E log entry

Acceptance criteria:

- the real command exists
- it runs through the intended runtime boundary
- pass or fail is recorded honestly

Proof required:

- actual command execution

Blocked claims:

- `flow_complete`
- `release_ready`

Advance when:

- the intended runtime flow has been exercised for real, not just described

### `hardening.align_policy_and_coverage`

Why it exists:

- keep execution-policy and coverage surfaces consistent with what really happened

Required artifacts:

- execution policy updates
- flow coverage updates
- checklist updates

Acceptance criteria:

- policy docs cite the real command surface
- coverage docs match the strongest actual proof
- checklist language matches the proven scope

Proof required:

- authoritative doc checks where adopted

Blocked claims:

- trustworthy readiness language

Advance when:

- policy, coverage, and checklist docs all tell the same truth about the runtime proof

### `hardening.record_residual_gaps`

Why it exists:

- stop successful narrow proof from hiding nearby missing proof

Required artifacts:

- explicit residual-gap note or checklist language
- operational-state checklist update

Acceptance criteria:

- remaining gaps outside the proven scope are stated explicitly
- blocked stronger claims remain visible
- the operational-state checklist reflects the current proving level honestly

Proof required:

- artifact existence check

Blocked claims:

- `release_ready` if remaining gaps still block it

Advance when:

- the repository distinguishes clearly between what is proven and what is still open

### `hardening.decide_maturity_claim`

Why it exists:

- ensure the resulting status language matches the actual proof level

Required artifacts:

- final claimed status in checklist or readiness surface

Acceptance criteria:

- the claimed status is no stronger than the proof
- `flow_complete` is used only for the declared proven flow scope
- `release_ready` is used only when the stronger readiness bar is actually met

Proof required:

- review of claim against the proving command and current docs

Blocked claims:

- any status above the actual proof

Advance when:

- the repository's maturity language is defensible for the declared scope

The operational-state checklist should only advance beyond this stage when those sub-steps are complete for the declared scope.

## What This Stage Should Produce

Minimum expected artifacts:

- E2E plans
- concrete E2E suites or commands
- execution policy updates
- flow coverage tracking
- hardening notes
- honest readiness status
- operational-state advancement notes

## Recommended Files

- `plan/e2e_tests/<flow>.md`
- `plan/checklists/00_project_operational_state.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`
- `notes/catalogs/audit/flow_coverage_checklist.md`
- `notes/logs/e2e/<date>_<task>.md`
- hardening notes under `notes/planning/implementation/`

## Questions This Stage Must Answer

- Which real flows are now proven through real runtime boundaries?
- Which flows are still only bounded or simulated?
- What commands prove the real E2E layer?
- What resilience, recovery, concurrency, or audit checks are required?
- What language is the repository now justified in using?
- Does the operational-state checklist block stronger claims that are still unjustified?

## AI Instruction

If the repository is in hardening and E2E stage, AI contributors should:

- prefer real runtime proof over additional mock-heavy proof
- tighten status claims to match actual E2E coverage
- update flow coverage and execution policy docs as suites land or fail
- update the operational-state checklist when the proving level actually changes
- document residual gaps instead of hiding them

Suggested `AGENTS.md` line:

> During hardening and E2E work, favor real runtime proof through the intended system boundaries. Do not describe a flow as complete, verified, or release-ready unless the documented E2E commands were actually run successfully for that scope.

## Entry Conditions

- The repository already has implemented feature slices.
- Bounded proof exists for meaningful behavior.
- Real runtime flow proof is now the limiting factor.

## Required Artifacts

- E2E plan coverage
- E2E command catalog entries
- flow coverage status
- E2E logs
- hardening or remediation notes where needed
- operational-state checklist updates

## Required Verification Surface

This stage should prove:

- declared E2E commands pass
- documented flow coverage is current
- readiness language matches the actual proof level
- any new authoritative docs still pass doc-consistency tests

## Common Failure Modes

- Calling the product complete because unit and integration tests pass.
- Letting the E2E plan and actual commands drift apart.
- Hiding failing or missing flows behind vague status language.
- Ignoring audit, recovery, or operator-inspection gaps.
- Advancing the maturity stage without updating the operational-state checklist.

## Exit Conditions

This stage is complete enough for a claimed scope when:

- the target flows pass end to end
- the E2E execution policy is current
- the flow coverage surface is current
- remaining gaps are stated explicitly
- the repository's status language matches the actual proof
- the operational-state checklist records the justified maturity level for the declared scope

## Example Deliverable

Example flow coverage snippet:

```md
| Flow | Strongest proof | Status | Canonical command |
| --- | --- | --- | --- |
| Create project | real E2E | verified | `pytest tests/e2e/test_create_project.py` |
| Resume interrupted run | integration | partial | Real E2E still pending |
```
