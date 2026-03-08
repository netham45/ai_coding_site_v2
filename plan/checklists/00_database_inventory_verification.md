# Checklist C00: Database Inventory Verification

## Goal

Verify that the implemented PostgreSQL schema covers the full orchestration model.

## Verify

- every required table/view/index implied by the notes exists
- lifecycle, runs, attempts, sessions, prompts, summaries, docs, provenance, merges, rebuilds, reviews, tests, validations, and conflicts are all represented
- migrations are reversible or safely forward-only by design
- hot read paths are indexed

## Tests

- exhaustive schema and migration tests
- performance checks for critical queries

## Notes

- update DB notes if implementation requires schema elaboration
