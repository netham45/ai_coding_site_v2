# Checklist C09: Workflow Compiler Stage Verification

## Goal

Verify the compiler as a staged pipeline rather than one opaque subsystem.

## Verify

- source discovery/loading is deterministic
- schema validation is a distinct enforced stage
- override resolution is a distinct enforced stage
- hook expansion and policy resolution are distinct enforced stages
- rendering/payload freeze is deterministic
- compiled workflow persistence and failure diagnostics are complete

## Tests

- exhaustive stage-by-stage compiler tests
- performance checks per compiler stage and across the full pipeline

## Notes

- update compile notes whenever stage boundaries or diagnostics change
