# Flow 09: Run Quality Gates

## Purpose

Run the canonical non-implementation gates that determine whether work may proceed to finalization.

## Covers journeys

- run validation gates
- run review gates
- run testing hooks
- block or pass finalization

## Entry conditions

- a subtask, node, or parent reconciliation stage produced candidate outputs that must be checked

## Task flow

1. determine applicable gate policy for the node version
2. run validation checks
3. run review checks
4. run testing checks
5. run provenance and docs stages if required by policy
6. persist results, findings, artifacts, and summaries
7. compute overall gate verdict
8. either allow advancement, request fixes, or pause for user

## Required subtasks

- `resolve_gate_policy`
- `run_validations`
- `run_reviews`
- `run_tests`
- `run_provenance_stage_if_required`
- `run_docs_stage_if_required`
- `persist_gate_results`
- `compute_gate_verdict`

## Required capabilities

- validation result persistence
- review result persistence
- test result persistence
- gate ordering
- CLI surfaces to inspect and optionally trigger gate execution

## Durable outputs

- validation results
- review results
- test results
- optional provenance/docs artifacts
- gate verdict summary

## Failure cases that must be supported

- validation failure
- review rejection
- flaky or missing test command
- gate-order conflict with project overrides

## Completion rule

The node has a durable gate verdict that clearly explains why finalization may continue or why fixes are required first.
