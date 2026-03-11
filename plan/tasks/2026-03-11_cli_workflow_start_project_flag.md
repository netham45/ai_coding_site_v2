# Task: CLI Workflow Start Project Flag

## Goal

Add a `--project` flag to `workflow start` so the CLI can start a top-level workflow from a selected repo under `repos/` through the same repo-backed project-start path now used by the website.

## Rationale

- Rationale: Repo-backed project start now exists at the daemon level, but it is currently only reachable through the website-facing route rather than through the canonical CLI workflow-start surface.
- Reason for existence: This task exists to restore CLI parity for repo-backed project start and prevent a required runtime flow from remaining website-only.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/37_F10_top_level_workflow_creation_commands.md`
- `plan/web/features/05_repo_backed_project_start_and_top_level_bootstrap.md`
- `plan/features/12_F17_deterministic_branch_model.md`
- `plan/features/71_F11_live_git_merge_and_finalize_execution.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/planning/implementation/top_level_workflow_creation_commands_decisions.md`
- `notes/planning/implementation/frontend_website_repo_backed_project_start_decisions.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_top_level_creation_contract.md`

## Scope

- Database: no new schema is planned; reuse the existing durable node-version and live-git metadata written by the repo-backed project-start path.
- CLI: extend `workflow start` with a `--project` flag that routes to the project-scoped repo-backed startup path while preserving existing `workflow start` behavior when the flag is omitted.
- Daemon: allow the project-scoped create request to accept an optional title so CLI startup can preserve the current derived-title behavior when the operator omits `--title`.
- YAML: not applicable.
- Prompts: preserve existing prompt-driven startup semantics and title derivation behavior.
- Tests: add parser, CLI integration, and real git E2E coverage for `workflow start --project ...`.
- Performance: keep CLI project-start overhead aligned with the existing repo-backed daemon route.
- Notes: update the top-level workflow creation and repo-backed project-start notes so the new CLI surface is described honestly.

## Planned Changes

1. Add this governing task plan and paired development log.
2. Extend the daemon project-scoped top-level create request to allow an omitted title while preserving current website behavior.
3. Add `--project` to the `workflow start` CLI parser.
4. Update the workflow-start handler so:
   - without `--project`, it still calls `/api/workflows/start`
   - with `--project`, it calls `/api/projects/{project_id}/top-level-nodes`
5. Add unit/parser coverage and CLI integration coverage for the new flag.
6. Add a real git E2E test for `workflow start --project ...`.
7. Update the implementation notes to document the new CLI path and title-resolution behavior.

## Verification

Canonical verification commands for this task:

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_cli.py tests/integration/test_workflow_start_flow.py -q
PYTHONPATH=src python3 -m pytest tests/e2e/test_cli_workflow_start_project_real.py -q -m e2e_real
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py -q
PYTHONPATH=src python3 -m pytest tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- `workflow start --project <repo>` exists and starts work from the selected repo-backed project-start path.
- Omitting `--project` preserves the prior `workflow start` behavior.
- `workflow start --project ...` works with and without explicit `--title`.
- CLI integration and real git E2E proof exist for the new flag.
- The implementation notes describe the new CLI surface honestly.
- The governing task plan and development log reference each other.
