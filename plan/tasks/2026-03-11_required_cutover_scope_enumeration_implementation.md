# Task: Required Cutover Scope Enumeration Implementation

## Goal

Implement explicit required-cutover-scope enumeration for rebuild-backed candidate lineages so the runtime can identify which candidate versions belong to one subtree or upstream lineage cutover unit instead of reasoning about one candidate version in isolation.

## Rationale

- Rationale: The current runtime can assess one candidate version for cutover readiness, but the dependency-invalidated fresh-restart model now needs a durable notion of sibling and ancestor candidates that must move together.
- Reason for existence: This task exists to lay the implementation foundation for grouped rebuild cutover and candidate-side replay completion without weakening the current cutover blockers.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/24_F19_regeneration_and_upstream_rectification.md`
- `plan/features/70_F19_live_rebuild_cutover_coordination.md`
- `plan/features/84_F19_dependency_invalidated_node_fresh_rematerialization.md`
- `plan/features/85_F19_version_consistent_live_runtime_authority.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/contracts/runtime/cutover_policy_note.md`
- `notes/pseudocode/modules/finalize_lineage_cutover.md`
- `notes/specs/git/git_rectification_spec_v2.md`
- `notes/planning/implementation/regeneration_and_upstream_rectification_decisions.md`

## Scope

- Database: derive cutover scope strictly from durable rebuild and version lineage records.
- CLI: no new command family in this slice.
- Daemon: add a reusable scope-enumeration helper for rebuild-backed candidates and keep cutover-readiness semantics coherent.
- YAML: not applicable in this slice.
- Prompts: not applicable in this slice.
- Tests: add bounded proof for subtree/upstream scope enumeration around rebuild-backed candidates.
- Performance: keep scope enumeration bounded to rebuild-linked candidates rather than scanning unrelated lineage history broadly.
- Notes: update cutover doctrine to reflect the new implemented enumeration helper and its current limits.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_regeneration.py -q
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_feature_plan_docs.py tests/unit/test_feature_checklist_docs.py tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- rebuild-backed candidates can enumerate their required subtree or upstream cutover scope from durable records
- bounded tests prove scope membership for regenerated descendants, dependency-invalidated siblings, and rebuilt ancestors
- notes and development logs are updated honestly for the implemented slice
