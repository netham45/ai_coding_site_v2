# Route 08: Parent Merge Narrowness

## Planned Test File

`tests/e2e/test_e2e_workflow_profile_parent_merge_narrowness_real.py`

## Goal

Prove that parents may reconcile, perform basic bug checks, and do documentation alignment, but may not absorb child-owned implementation work.

## Main Path

- drive a non-leaf node to merge time
- exercise allowed parent-local merge behavior
- attempt prohibited parent-owned implementation behavior

## Required Assertions

- parent merge/docs work remains bounded
- prohibited parent-owned implementation is rejected or blocked
- documentation alignment remains legal when parent-owned

## Adversarial Checks

- attempt to treat new implementation as merge-time parent-local work
- verify the blocked reason is inspectable

## Affected Systems

- Database
- CLI
- Daemon
- YAML
- Prompts

## Proof Target

Narrow parent merge scope with no backdoor implementation absorption.
