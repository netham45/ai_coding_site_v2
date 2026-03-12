# Route 11: Operator Inspection

## Planned Test File

`tests/e2e/test_e2e_workflow_profile_operator_inspection_real.py`

## Goal

Prove the read surfaces for profile-aware runtime state.

## Main Path

- call `workflow brief`, `node types`, `node profiles`, workflow inspection, and blocker inspection surfaces
- compare reported state across surfaces

## Required Assertions

- selected profile, effective layout, role expectations, next legal step, and blocked reasons are visible
- operator reads agree with daemon-owned state
- child-profile recommendations are inspectable without opening raw YAML

## Adversarial Checks

- inspect a blocked workflow
- inspect a partially progressed workflow
- ensure read surfaces agree across those states

## Affected Systems

- Database
- CLI
- Daemon
- Prompts

## Proof Target

Accurate operator visibility into profile-aware workflow state.
