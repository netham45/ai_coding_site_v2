# Task: Grouped Lineage Cutover Scope Real E2E

## Goal

Add a real daemon/CLI/database E2E proving that rebuild-backed manual cutover switches the full required cutover scope instead of making only the requested candidate version authoritative.

## Rationale

- Rationale: Grouped cutover now exists at the bounded/runtime layer, but FC-15 still lacks a real operator flow proving that a parent candidate cutover carries its rebuilt child scope with it.
- Reason for existence: This task exists to turn grouped lineage cutover from bounded plumbing into a real Flow 10 checkpoint without overstating the still-missing post-cutover rematerialization narrative.

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
- `notes/specs/git/git_rectification_spec_v2.md`
- `notes/planning/implementation/live_rebuild_cutover_coordination_decisions.md`
- `notes/catalogs/checklists/feature_checklist_backfill.md`

## Scope

- Database: inspect durable version status and authoritative selectors after real grouped cutover.
- CLI: drive the scenario through real `node regenerate`, `node versions`, `node version cutover-readiness`, `node version cutover`, and `node show` commands.
- Daemon: exercise the real grouped cutover authority-switch path through the daemon API rather than a direct helper call.
- YAML: use existing built-in node kinds only.
- Prompts: not applicable in this slice.
- Tests: extend the real Flow 10 suite with a grouped-cutover checkpoint for a stable rebuilt subtree.
- Performance: keep the real proof bounded to one parent and one child so it isolates grouped cutover semantics without expanding into a larger rebuild tree.
- Notes: update FC-15 and the E2E tracking docs to record that grouped lineage cutover now has a dedicated real checkpoint.

## Verification

Canonical verification commands for this task:

```bash
PYTHONPATH=src python3 -m pytest tests/e2e/test_flow_10_regenerate_and_rectify_real.py -q -k grouped_lineage_cutover
PYTHONPATH=src python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_feature_plan_docs.py tests/unit/test_feature_checklist_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_verification_command_docs.py -q
git diff --check
```

## Exit Criteria

- real Flow 10 proves a parent candidate cutover switches its rebuilt child scope together
- the real proof confirms both root and child authoritative selectors move to their candidate versions in one cutover action
- FC-15 no longer lists grouped lineage cutover as lacking a dedicated real E2E checkpoint
- docs and logs remain honest that the broader post-cutover fresh-rematerialization narrative is still outstanding
