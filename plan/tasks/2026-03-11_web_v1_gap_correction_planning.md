# Task: Web V1 Gap Correction Planning

## Goal

Add the missing authoritative corrective plans for the remaining website v1 gaps so the repo no longer treats those misses as informal follow-up work.

## Rationale

- Rationale: After reconciling the current website implementation against the v1 scope freeze, several required behaviors remain incomplete beyond repo-backed project start.
- Reason for existence: This task exists to turn those remaining gaps into explicit feature and verification phases instead of leaving them as audit bullets or implied future cleanup.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/web/features/00_project_bootstrap_and_selection.md`
- `plan/web/features/01_explorer_shell_and_hierarchy_tree.md`
- `plan/web/features/04_bounded_action_surface.md`
- `plan/web/features/05_repo_backed_project_start_and_top_level_bootstrap.md`
- `plan/features/37_F10_top_level_workflow_creation_commands.md`
- `plan/features/15_F11_operator_cli_and_introspection.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_v1_scope_freeze.md`
- `notes/planning/implementation/frontend_website_project_bootstrap_selection_decisions.md`
- `notes/planning/implementation/frontend_website_explorer_tree_decisions.md`
- `notes/planning/implementation/frontend_website_final_verification_audit.md`

## Scope

- Database: no direct schema work is planned in this planning pass, but the corrective plans must name any existing durable artifacts they depend on.
- CLI: no direct CLI change is planned in this planning pass, but the corrective plans must keep browser behavior aligned with existing operator semantics.
- Daemon: define the remaining missing daemon-facing project bootstrap-readiness and project-context behavior required by the website v1 scope.
- YAML: not applicable.
- Prompts: no new prompt system work is planned in this pass.
- Tests: define the remaining bounded, browser, and real-E2E proof required to close the outstanding v1 gaps honestly.
- Performance: note where additional filters, project checks, or action proof could create operator-visible latency.
- Notes: update existing implementation and scope notes so they point to the new corrective phases.

## Planned Changes

1. Add a corrective web feature plan for project bootstrap readiness and project-selector daemon context.
2. Add a corrective web feature plan for the remaining required tree filters.
3. Add a corrective web verification plan for full v1 browser execution proof of the remaining agreed action flows and shared loading/error states.
4. Update the existing feature and audit notes to point to those corrective plans explicitly.
5. Add the governing development log and update the task-plan index.

## Verification

Canonical verification commands for this task:

```bash
python3 -m pytest tests/unit/test_task_plan_docs.py -q
python3 -m pytest tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- Authoritative corrective plans exist for the remaining website v1 gaps beyond repo-backed project start.
- Existing implementation and audit notes point to those corrective phases explicitly.
- The governing task plan and development log reference each other.
- The documented verification commands are run and their result is recorded honestly.
