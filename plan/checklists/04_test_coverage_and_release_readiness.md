# Checklist C04: Test Coverage And Release Readiness

## Goal

Refuse `verified`, `flow_complete`, or `release_ready` claims until testing, performance, note updates, and the documented proving ladder are actually satisfied.

## Required References

- `notes/catalogs/checklists/feature_checklist_standard.md`
- `notes/catalogs/checklists/feature_checklist_backfill.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`

## Verify

- every feature has exhaustive unit coverage
- all meaningful branches and failure paths are tested
- no known limitation discovered during coding is undocumented
- performance-sensitive paths have benchmarks or regression tests
- all setup, feature, and checklist phases have been satisfied
- any `verified`, `flow_complete`, or `release_ready` claim is backed by the correct canonical command layer
- release-readiness claims distinguish bounded proof from gated real-E2E proof

## Tests

- aggregate test-suite review
- performance regression review
- coverage-gap review

## Canonical Review Rule

- use `notes/catalogs/checklists/verification_command_catalog.md` for the canonical command set
- use `notes/catalogs/checklists/e2e_execution_policy.md` for local, CI, gated/manual, and release-readiness execution expectations
- do not treat bounded or integration proof alone as `release_ready`

## Notes

- update `notes/` whenever verification reveals missing detail or incorrect assumptions
