# Phase 06 Draft: Conflict Handoff And Prompt Context

## Goal

On incremental merge conflict, block dependents, surface conflict context clearly, and hand control to the parent AI session only for the exceptional path.

## Rationale

- Rationale: Ordinary successful incremental merges should be daemon-owned, but merge conflicts still require semantic resolution that the daemon cannot safely invent.
- Reason for existence: This phase exists to define the clean boundary where the daemon pauses the merge lane, blocks dependents, and hands a well-formed conflict context to the parent AI session.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/22_F20_conflict_detection_and_resolution.md`: conflict persistence and resolution behavior remains the nearest existing architectural anchor.
- `plan/features/23_F18_child_merge_and_reconcile_pipeline.md`: parent-visible merge state and reconcile context should remain coherent when conflict handoff is introduced.
- `plan/features/14_F10_ai_facing_cli_command_loop.md`: parent AI prompt/context delivery must remain aligned with the daemon-owned command loop.
- `plan/features/31_F28_prompt_history_and_summary_history.md`: conflict prompts and summaries should remain durably inspectable.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/specs/prompts/prompt_library_plan.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/git/git_rectification_spec_v2.md`
- `notes/contracts/runtime/session_recovery_appendix.md`
- `plan/future_plans/sibling_dependency_incremental_parent_merge/2026-03-11_overview.md`

## Scope

- Database: persist conflict-lane state, blocked dependents, and resume-safe conflict metadata.
- CLI: expose conflict inspection and lane status clearly enough for operators and AI sessions to diagnose what is blocked.
- Daemon: pause the merge lane on conflict, keep dependents blocked, assemble conflict context, and resume only after durable resolution.
- YAML: no free-form YAML-owned merge resolution logic; conflict handling remains code-owned with prompts as assets.
- Prompts: define daemon-built conflict-resolution context and final-resume context for the parent AI session.
- Tests: bounded conflict-context assembly and resume logic, plus real conflicted incremental merge proof once the runtime is stable enough.
- Performance: conflict detection and lane pausing should not leave the background loop in a hot-spin state.
- Notes: update prompt/runtime/conflict doctrine so parent AI involvement is explicitly exceptional rather than part of the happy path, and keep pause/cancel semantics aligned with the broader parent merge-lane contract.

## Verification

- Bounded proof:
  - conflict context payload shape
  - blocked dependents remain blocked during conflict
  - resume-after-resolution transitions lane back to active processing
- Real proof:
  - real conflicted incremental merge routes to parent AI handling and later resumes correctly

## Exit Criteria

- conflict path is daemon-owned until human/AI semantic intervention is actually required
- conflict context is daemon-assembled rather than reconstructed ad hoc by the AI
- this phase remains a future-plan draft and is not an implementation claim by itself
