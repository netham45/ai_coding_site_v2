# Checklist C00: Database Inventory Verification

## Goal

Verify that the implemented PostgreSQL schema covers the full orchestration model.

## Verify

- every required table/view/index implied by the notes exists
- lifecycle, runs, attempts, sessions, prompts, summaries, docs, provenance, merges, rebuilds, reviews, tests, validations, and conflicts are all represented
- migrations are reversible or safely forward-only by design
- hot read paths are indexed
- the implementation still aligns with the SQLAlchemy + Alembic assumption unless the notes are updated deliberately

## Tests

- exhaustive schema and migration tests
- performance checks for critical queries and synchronous DB access under expected concurrency

## Notes

- update DB notes if implementation requires schema elaboration
