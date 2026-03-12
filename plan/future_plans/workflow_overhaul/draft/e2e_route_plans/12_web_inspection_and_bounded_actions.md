# Route 12: Web Inspection And Bounded Actions

## Planned Test File

`tests/e2e/test_e2e_workflow_profile_web_inspection_real.py`

## Goal

Prove website rendering of profile-aware workflow state and bounded action legality.

## Main Path

- open profile-aware nodes in the web UI
- inspect blocked reasons, required steps, and legal actions
- trigger bounded legal and illegal actions

## Required Assertions

- web UI reflects daemon-owned legality
- blocked actions show the same reasons as CLI and API
- browser-visible state stays consistent after route-changing mutations

## Adversarial Checks

- trigger an illegal blocked action from the UI
- confirm the UI surfaces the same blocked code and reason as the daemon

## Affected Systems

- Database
- Daemon
- Website UI
- CLI/API comparison surfaces

## Proof Target

Website parity with daemon-owned legality and inspection state.
