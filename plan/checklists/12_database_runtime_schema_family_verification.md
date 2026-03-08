# Checklist C12: Database Runtime Schema Family Verification

## Goal

Verify that the implemented runtime-state PostgreSQL schema family is complete and internally consistent.

## Verify

- node, dependency, lifecycle, run, pause, and rebuild-related tables and indexes exist
- runtime state names and legal transitions match daemon behavior
- hot runtime query paths are indexed and exercised
- CLI/runtime inspection surfaces can retrieve the full live state model without hidden joins or missing records

## Tests

- exhaustive runtime-state schema, migration, and transition tests
- performance checks for hot admission, state-transition, and dependency-inspection paths

## Notes

- update runtime/database notes immediately if runtime state families expand or normalize differently than planned
