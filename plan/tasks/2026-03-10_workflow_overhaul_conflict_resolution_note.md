# Task: Workflow Overhaul Conflict Resolution Note

## Goal

Extend the workflow-overhaul future-planning note so it captures merge-conflict handling as a workflow and rectification problem, not only as a raw git operation.

## Rationale

- Rationale: The current workflow-overhaul note explains profile-aware tiers, briefs, and decomposition, but it does not yet describe how future workflow profiles should respond when child mergeback produces conflicts that require code reconciliation, task/dependency revision, or upstream replan.
- Reason for existence: This task exists to preserve the conflict-handling idea in the future-plan bundle before implementation begins, while framing it in repository-native terms that match the existing rectification and profile-aware workflow direction.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/22_F20_conflict_detection_and_resolution.md`
- `plan/features/23_F18_child_merge_and_reconcile_pipeline.md`
- `plan/features/24_F19_regeneration_and_upstream_rectification.md`
- `plan/features/65_F04_layout_replacement_and_hybrid_reconciliation.md`
- `plan/features/71_F11_live_git_merge_and_finalize_execution.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `plan/future_plans/workflow_overhaul/2026-03-10_self_hosted_workflow_overhaul_notes.md`
- `notes/specs/git/git_rectification_spec_v2.md`
- `notes/contracts/runtime/cutover_policy_note.md`
- `notes/contracts/parent_child/child_session_mergeback_contract.md`
- `notes/pseudocode/modules/rectify_node_from_seed.md`
- `notes/planning/implementation/conflict_detection_and_resolution_decisions.md`
- `notes/planning/implementation/regeneration_and_upstream_rectification_decisions.md`
- `AGENTS.md`

## Scope

- Database: not applicable; this task only updates future-planning notes and logs.
- CLI: not applicable; this task does not change current CLI commands.
- Daemon: not applicable; this task does not change current runtime conflict behavior.
- YAML: document how future workflow profiles and layouts should declare conflict-handling and rectification obligations.
- Prompts: document how future prompts should distinguish mechanical merge repair from semantic/spec rectification.
- Tests: run the relevant document-schema tests for the task plan and development log.
- Performance: note only future-direction implications if conflict-driven rectification expands planning/rebuild loops.
- Notes: update the workflow-overhaul future note with staged conflict handling, conflict classes, and workflow-profile implications.

## Verification

- Document-schema coverage: `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py -q`

## Exit Criteria

- The workflow-overhaul future note explicitly frames merge conflict handling as a staged workflow decision problem.
- The note distinguishes mechanical conflict resolution from semantic conflict reconciliation and spec/dependency rectification.
- The note records how workflow profiles, prompts, and compiler/runtime boundaries should participate in future conflict handling.
- The governing task plan and development log exist and reference the updated future note.
