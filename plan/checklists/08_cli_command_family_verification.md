# Checklist C08: CLI Command Family Verification

## Goal

Verify CLI implementation by command family rather than as one monolith.

## Verify

- top-level workflow creation commands are implemented
- AI work-retrieval commands are implemented
- AI progress/transition commands are implemented
- operator structure/state commands are implemented
- operator history/artifact commands are implemented
- session attach/resume/control commands are implemented

## Tests

- exhaustive command-family coverage with malformed input and authority/error cases
- performance checks for each hot command family

## Notes

- update CLI notes if any family requires additional commands or different grouping
