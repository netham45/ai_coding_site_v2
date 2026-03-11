# Sibling Dependency Incremental Parent Merge

This bundle captures a future implementation plan for one specific orchestration gap:

- when child B depends on sibling child A
- and child repos clone from the parent
- child B must not start from stale parent state after child A completes

These notes are non-authoritative working plans under `plan/future_plans/`.

Current documents:

- `2026-03-11_overview.md`
