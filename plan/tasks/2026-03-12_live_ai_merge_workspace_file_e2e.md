# Task: Live AI Merge Workspace File E2E

## Goal

Extend the real E2E merge proving surface so at least one hierarchy-wide merge narrative verifies actual files inside node workspace repos after a live tmux/Codex leaf edit, not only after test-authored git commits.

## Rationale

- Rationale: The repo already has strong real git merge assertions for clean merge, rerun/replay, and conflict-abort scenarios, but those file assertions are still mostly driven by test-authored child commits rather than a live AI session editing the node workspace repo.
- Reason for existence: This task exists to add a stronger end-to-end checkpoint that combines real tmux/Codex execution with real git merge propagation and on-disk repo-content verification across the hierarchy.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/13_F09_node_run_orchestration.md`
- `plan/features/39_F12_tmux_session_manager.md`
- `plan/features/71_F11_live_git_merge_and_finalize_execution.md`
- `plan/features/82_F08_F18_incremental_parent_merge_full_e2e.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `plan/checklists/16_e2e_real_runtime_gap_closure.md`
- `notes/logs/e2e/2026-03-10_refactor_e2e_tests_to_real_runtime_only.md`

## Scope

- Database: keep durable merge events and final-commit records authoritative for the hierarchy-wide merge narrative.
- CLI: use real CLI commands for hierarchy creation, git status/finalize, merge-events, and finalize/cutover inspection.
- Daemon: rely on the daemon-owned bootstrap, finalize, lifecycle transition, and incremental merge propagation path after the AI-authored task repo commit exists.
- Website UI: not directly changed in this slice.
- YAML: not directly changed in this slice.
- Prompts: the live task instruction handed to the tmux/Codex edit path must explicitly mutate files inside the current repo workspace and commit the result.
- Tests: add a real tmux/Codex plus real git E2E that proves workspace file contents at task, plan, phase, and epic scope after merge propagation; update note/checklist surfaces that currently overstate the absence of runtime shortcuts elsewhere.
- Performance: keep the live workspace narrative scoped to one hierarchy path so the stronger real-runtime proof does not create avoidable long-tail E2E time growth.
- Notes: record the new stronger merge proof and correct the current E2E gap checklist so it no longer implies that every remaining `tests/e2e/` narrative is already free of manual runtime advancement shortcuts.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/e2e/test_e2e_full_epic_tree_runtime_real.py -q -k live_ai_workspace
PYTHONPATH=src python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_e2e_execution_policy_docs.py tests/unit/test_feature_checklist_docs.py -q
```

## Exit Criteria

- a real tmux/Codex execution edits files inside the authoritative task repo workspace
- the resulting committed task-repo files are verified on disk before merge propagation
- plan, phase, and epic repos are verified on disk after the real merge propagation path
- the E2E execution checklist and command catalog explicitly describe the new proof and the remaining operator-driven shortcut gap
