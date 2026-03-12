# Route 09: Blocked Recovery And Resume

## Planned Test File

`tests/e2e/test_e2e_workflow_profile_blocked_recovery_resume_real.py`

## Goal

Prove that blocked-step state and current required step survive pause, restart, and resume.

## Main Path

- pause a workflow while it is blocked or waiting
- restart the daemon or recover the session
- inspect and resume through the intended surfaces

## Required Assertions

- blocked reason remains durable
- current required step is preserved
- resume does not silently bypass blocked legality

## Adversarial Checks

- attempt resume while the blocked predicate is still unsatisfied
- verify the same blocked reason survives restart

## Affected Systems

- Database
- CLI
- Daemon
- Prompts

## Proof Target

Restart-safe preservation of rigid workflow legality.
