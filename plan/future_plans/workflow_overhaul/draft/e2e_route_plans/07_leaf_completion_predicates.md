# Route 07: Leaf Completion Predicates

## Planned Test File

`tests/e2e/test_e2e_workflow_profile_leaf_completion_predicates_real.py`

## Goal

Prove that `task.*` profiles cannot complete without their declared outputs, summaries, proof, and corrective-loop closure where required.

## Main Path

- run representative `task.implementation`, `task.review`, `task.verification`, `task.docs`, `task.e2e`, and `task.remediation` cases
- attempt completion before the declared evidence exists
- force a representative verification failure that appends remediation plus reverification on the same leaf chain
- complete after the evidence is durably written

## Required Assertions

- completion is blocked until declared predicates are satisfied
- blocked reason is task-specific
- successful completion records the required evidence honestly
- `needs_remediation` appends exactly one remediation subtask and one follow-up verification or re-review subtask
- remediation-turn counts are durable and inspectable

## Adversarial Checks

- missing outputs
- missing summary
- missing declared verification or E2E evidence
- remediation-turn budget exhaustion forces escalation instead of infinite corrective-chain growth

## Affected Systems

- Database
- CLI
- Daemon
- YAML
- Prompts

## Proof Target

Rigid leaf completion gating by durable predicates plus bounded append-only corrective expansion.
