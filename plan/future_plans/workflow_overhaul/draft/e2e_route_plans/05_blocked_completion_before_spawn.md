# Route 05: Blocked Completion Before Spawn

## Planned Test File

`tests/e2e/test_e2e_workflow_profile_children_required_before_completion_real.py`

## Goal

Prove that decomposition-required non-leaf profiles cannot merge or complete before spawning required children.

## Main Path

- start a decomposition-required non-leaf node
- attempt merge or completion before child materialization
- inspect blocked state

## Required Assertions

- daemon returns concrete `4xx`
- machine code is `children_required_before_completion` or equivalent
- blocked reason is visible through CLI and API reads

## Adversarial Checks

- attempt `complete`
- attempt `merge_children`
- attempt equivalent parent-local closure actions

## Affected Systems

- Database
- CLI
- Daemon
- YAML

## Proof Target

Hard enforcement of child-spawn requirements before merge or completion.
