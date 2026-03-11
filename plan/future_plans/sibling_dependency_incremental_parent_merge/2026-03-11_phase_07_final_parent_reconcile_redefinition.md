# Phase 07 Draft: Final Parent Reconcile Redefinition

## Goal

Make final parent reconcile mean "perform remaining parent-local synthesis after child merges are already applied," not "first time child work reaches parent."

## Rationale

- Rationale: If final parent reconcile still owns the first child-to-parent merge step, the entire incremental merge design collapses back into the current flawed model.
- Reason for existence: This phase exists to rewrite final parent reconcile around already-applied incremental merges so the repository doctrine, prompts, and runtime behavior all agree on the new orchestration model.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/23_F18_child_merge_and_reconcile_pipeline.md`: this phase is the doctrinal rewrite of the existing merge-and-reconcile model after incremental merges already exist.
- `plan/features/69_F21_F22_F23_F29_turnkey_quality_gate_finalize_chain.md`: final parent reconcile must still hand off correctly into validation, review, testing, docs, and finalize stages.
- `plan/features/71_F11_live_git_merge_and_finalize_execution.md`: the final parent flow must avoid double-merging already-applied child work.
- `plan/features/33_F29_documentation_generation.md`: final reconcile still has to leave downstream docs/provenance/finalize behavior intact.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/git/git_rectification_spec_v2.md`
- `notes/specs/prompts/prompt_library_plan.md`
- `notes/pseudocode/modules/collect_child_results.md`
- `notes/pseudocode/modules/rectify_node_from_seed.md`
- `plan/future_plans/sibling_dependency_incremental_parent_merge/2026-03-11_overview.md`

## Scope

- Database: persist enough merged-upward child history, including actual applied incremental merge order, for final parent reconcile to know what is already applied.
- CLI: expose final parent reconcile readiness and merged-upward child history clearly enough for operator inspection.
- Daemon: redefine final reconcile-ready semantics and prevent duplicate merge execution during later parent-local synthesis.
- YAML: existing reconcile task and workflow assets may need declarative wording changes, but the merge legality remains code-owned.
- Prompts: redefine final parent reconcile prompts/context to assume child merges are already applied.
- Tests: bounded proof that final reconcile sees merged-upward child history without re-merging, plus real E2E proving final parent flow still succeeds after incremental merges.
- Performance: final reconcile should not have to re-scan or re-merge the full child set unnecessarily once incremental merge history is available.
- Notes: this phase requires broad doctrinal rewrites so the written model matches the new orchestration semantics.

## Verification

- Bounded proof:
  - final parent reconcile sees merged-upward child history
  - no duplicate child merge occurs in final reconcile
- Real proof:
  - full real E2E proves:
    - child A merges upward
    - child B unblocks after merge
    - final parent reconcile still succeeds afterward

## Exit Criteria

- repository doctrine and runtime behavior agree on the new parent flow
- final parent reconcile is explicitly post-merge synthesis, not the first child merge point
- this phase remains a future-plan draft and is not an implementation claim by itself
