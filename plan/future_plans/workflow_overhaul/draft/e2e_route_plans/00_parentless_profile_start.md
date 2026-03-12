# Route 00: Parentless Profile Start

## Planned Test File

`tests/e2e/test_e2e_workflow_profile_parentless_start_real.py`

## Goal

Prove that any shipped parentless-capable kind can start top-level with a selected workflow profile.

## Main Path

- start top-level `epic`, `phase`, `plan`, and `task` nodes through the real startup surface
- compile each workflow
- inspect selected profile and compiled context

## Required Assertions

- top-level legality is structural, not epic-only
- selected profile is visible on the created version
- selected profile is frozen into compiled workflow context
- startup remains inspectable through CLI and daemon surfaces

## Adversarial Checks

- reject a profile that does not apply to the chosen kind
- reject top-level start for a kind that is not parentless-capable

## Affected Systems

- Database
- CLI
- Daemon
- YAML
- Prompts

## Proof Target

Parentless profile-aware startup legality and inspectability.
