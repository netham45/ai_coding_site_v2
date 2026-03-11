# Task: Incremental Parent Merge Phase 06 Conflict Handoff And Prompt Context

## Goal

Persist daemon-assembled incremental merge conflict context into the parent runtime cursor so parent AI and operators can inspect the exceptional path without reconstructing state from raw conflict tables.

## Rationale

- Rationale: Successful incremental merges are now daemon-owned, but merge conflicts still need a clear parent-facing handoff surface.
- Reason for existence: This task exists as a separate slice so the repository can prove conflict-context assembly and parent prompt/context visibility before attempting broader conflict-resolution automation.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/74_F08_F18_incremental_parent_merge_overview.md`
- `plan/features/80_F20_incremental_parent_merge_phase_06_conflict_handoff_and_prompt_context.md`
- `plan/features/22_F20_conflict_detection_and_resolution.md`
- `plan/features/14_F10_ai_facing_cli_command_loop.md`
- `plan/features/31_F28_prompt_history_and_summary_history.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/specs/prompts/prompt_library_plan.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/git/git_rectification_spec_v2.md`
- `notes/contracts/runtime/session_recovery_appendix.md`
- `plan/features/74_F08_F18_incremental_parent_merge_overview.md`

## Scope

- Database: reuse durable merge events, merge conflicts, lane state, and run cursor persistence rather than introducing a second conflict ledger.
- CLI: existing `subtask context`, `subtask prompt`, `node reconcile`, `git merge-conflicts show`, and interventions surfaces should expose enough context for diagnosis without adding a new command in this slice.
- Daemon: on incremental merge conflict, assemble and persist parent-facing conflict context; on durable conflict resolution, update that context to reflect current status.
- YAML: not affected directly in this slice.
- Prompts: conflict handoff stays daemon-assembled through `stage_context_json` / `parent_reconcile_context`; no new prompt asset is required in this slice because the existing reconcile prompt path remains authoritative.
- Tests: add bounded proof for conflict-context persistence and update-after-resolution behavior.
- Performance: conflict-context assembly should be local to the conflicted parent lineage and avoid full-tree scans.
- Notes: document that parent AI involvement on this path comes from daemon-persisted context rather than ad hoc merge-conflict table reconstruction.

## Plan

### Phase 6A: Task scaffolding and context review

1. Add the authoritative task plan and development log entry for this phase.
2. Review current merge-conflict persistence, parent reconcile context persistence, and stage-context assembly.
3. Confirm the smallest repo-native surface for parent conflict handoff.

Exit criteria:

- the task/log artifacts exist and the handoff path is tied to the existing run-cursor and `stage_context_json` contract

### Phase 6B: Conflict-context persistence

1. Add a daemon helper that writes incremental merge conflict context into the active parent run cursor when the merge lane blocks on conflict.
2. Update merge-conflict resolution to refresh that same context so parent-facing inspection shows current resolution state.
3. Reuse the existing parent reconcile context channel rather than adding a parallel prompt payload.

Exit criteria:

- parent subtask context and reconcile-style reads can see daemon-assembled incremental merge conflict details

### Phase 6C: Bounded proof

1. Add bounded proof that conflicted incremental merges persist parent-facing conflict context.
2. Add bounded proof that conflict resolution updates the persisted context status and summary.
3. Run the affected code and authoritative document verification commands.

Exit criteria:

- the exceptional merge-conflict handoff is proven at the bounded layer and documented honestly as not yet full E2E-complete

## Verification

- `python3 -m pytest tests/unit/test_incremental_parent_merge.py tests/unit/test_interventions.py tests/unit/test_child_reconcile.py -q`
- `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_feature_plan_docs.py tests/unit/test_feature_checklist_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_verification_command_docs.py -q`
- `git diff --check`

## Exit Criteria

- conflicted incremental merges persist daemon-assembled parent-facing conflict context
- resolving a durable conflict updates the same persisted parent context surface
- the parent AI conflict path relies on existing `stage_context_json` / `parent_reconcile_context` delivery rather than ad hoc table reconstruction
- full real conflicted incremental-merge E2E remains explicitly deferred
