# Task: Grouped Lineage Cutover Scope Implementation

## Goal

Make manual candidate cutover consume the enumerated required cutover scope so rebuild-backed parent, sibling, and ancestor candidates move authority together instead of cutting over one candidate version in isolation.

## Rationale

- Rationale: The runtime now exposes required cutover-scope enumeration and scope-aware readiness blockers, but `node version cutover` still only flips one logical node's authoritative selector.
- Reason for existence: This task exists to close the gap between the F19 cutover doctrine and the actual authority-switch path so rebuild-backed lineage cutover stops leaving required sibling or ancestor candidates behind.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/24_F19_regeneration_and_upstream_rectification.md`
- `plan/features/70_F19_live_rebuild_cutover_coordination.md`
- `plan/features/83_F19_dependency_aware_regeneration_scope.md`
- `plan/features/85_F19_version_consistent_live_runtime_authority.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/contracts/runtime/cutover_policy_note.md`
- `notes/pseudocode/modules/finalize_lineage_cutover.md`
- `notes/specs/git/git_rectification_spec_v2.md`
- `notes/planning/implementation/live_rebuild_cutover_coordination_decisions.md`

## Scope

- Database: reuse existing version selectors and lifecycle rows, but switch all required candidate versions in the enumerated cutover scope inside one authority mutation path.
- CLI: no new command family; `node version cutover` should now apply grouped cutover semantics for rebuild-backed candidates.
- Daemon: require every candidate in the enumerated scope to be cutover-ready before switching authority, then supersede old authoritative versions and rebind lifecycle ownership across the whole scope.
- YAML: not applicable.
- Prompts: not applicable in this slice.
- Tests: add bounded proof for grouped authority switching and blocked grouped cutover when any required scope member is not ready.
- Performance: keep grouped cutover bounded to the already enumerated scope so authority switching does not fan out into unrelated lineage scans.
- Notes: update cutover doctrine and implementation notes to state that manual candidate cutover now consumes the required scope rather than only the requested candidate version.

## Verification

Canonical verification commands for this task:

```bash
python3 -m py_compile src/aicoding/daemon/versioning.py
PYTHONPATH=src python3 -m pytest tests/unit/test_node_versioning.py tests/unit/test_regeneration.py tests/integration/test_node_versioning_flow.py -q -k "cutover"
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_feature_plan_docs.py tests/unit/test_feature_checklist_docs.py tests/unit/test_document_schema_docs.py tests/unit/test_verification_command_docs.py -q
git diff --check
```

## Exit Criteria

- rebuild-backed candidate cutover switches authority for every candidate version in the enumerated required scope
- grouped cutover fails if any required scope member is not cutover-ready
- lifecycle version binding is rebound consistently for the switched scope
- notes and development logs describe grouped cutover as implemented for rebuild-backed scope even if broader live git replay/cutover narratives remain partial
