# Route 06: Blocked Step Skip

## Planned Test File

`tests/e2e/test_e2e_workflow_profile_step_order_enforcement_real.py`

## Goal

Prove rigid step order for non-leaf compiled chains.

## Main Path

- create a profile-aware non-leaf node
- attempt illegal step jumps
- inspect current required step and blocked reason

## Required Assertions

- skipped-step mutations fail rather than warn
- blocked responses identify the missing prior step or predicate
- inspect surfaces show the current legal step

## Adversarial Checks

- attempt `merge_children` before `wait_for_children`
- attempt `wait_for_children` before materialization where illegal
- attempt `complete` after only partial progress

## Affected Systems

- Database
- CLI
- Daemon
- YAML

## Proof Target

Rigid step-order enforcement for compiled non-leaf workflows.
