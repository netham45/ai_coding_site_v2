# Task: Web Repo-Backed Project Start Planning

## Goal

Add the missing authoritative plans and note corrections for the website repo-backed top-level bootstrap gap so the current partial project-selector behavior is no longer treated as an acceptable v1 endpoint.

## Rationale

- Rationale: The website currently exposes project selection and top-level creation, but the selected project does not yet bootstrap the chosen source repo into the created top-level node's worker repo.
- Reason for existence: This task exists to turn that gap into explicit authoritative planning, fix the misleading deferred-language in the current notes, and define the exact corrective implementation slice required to make project selection materially start work from the chosen repo.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/web/features/00_project_bootstrap_and_selection.md`
- `plan/features/37_F10_top_level_workflow_creation_commands.md`
- `plan/features/12_F17_deterministic_branch_model.md`
- `plan/features/71_F11_live_git_merge_and_finalize_execution.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_top_level_creation_contract.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_top_level_node_creation_flow.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_v1_scope_freeze.md`
- `notes/planning/implementation/frontend_website_project_bootstrap_selection_decisions.md`
- `notes/planning/implementation/live_git_merge_and_finalize_execution_decisions.md`
- `notes/planning/implementation/top_level_workflow_creation_commands_decisions.md`

## Scope

- Database: no schema change is planned in this planning pass, but the corrective plan must state which existing durable git and version records are relied on and where new persistence would be required if current artifacts are insufficient.
- CLI: no website-specific CLI change is planned in this planning pass, but the corrective plan must keep website project-start semantics aligned with the existing top-level workflow and git-inspection doctrine.
- Daemon: define the missing repo-backed top-level bootstrap sequence for `POST /api/projects/{project_id}/top-level-nodes` using the existing live-git substrate instead of the current deferred placeholder.
- YAML: not applicable; the corrective plan should keep repo bootstrap authority in code rather than inventing YAML-driven git execution rules.
- Prompts: preserve the existing operator-entered top-level prompt behavior and make clear that repo bootstrap does not replace prompt-driven workflow creation.
- Tests: define the required daemon integration, bounded browser, and real git E2E proving layers for the corrective feature.
- Performance: record that local repo clone plus branch bootstrap must remain responsive enough for operator creation flows.
- Notes: update the existing future-plan and implementation notes so they describe the current implementation honestly as partial and point to the corrective feature plan.

## Planned Changes

1. Review the existing web feature, future-plan, and live-git notes that describe project selection, top-level creation, and live repo bootstrap.
2. Add a new authoritative web feature plan for repo-backed project start and top-level bootstrap.
3. Add a paired web verification plan for real repo-backed project-start proof.
4. Update the current website project-bootstrap implementation note to mark the shipped slice as partial and to point to the corrective feature plan.
5. Update the current future-plan creation notes so repo-backed project bootstrap is recorded as a required v1 correction rather than a casual later deferral.
6. Update the task-plan index and add a development log for this planning batch.

## Verification

Canonical verification commands for this task:

```bash
python3 -m pytest tests/unit/test_task_plan_docs.py -q
python3 -m pytest tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- A new authoritative web feature plan exists for repo-backed project start and top-level bootstrap.
- A paired authoritative web verification plan exists for real repo-backed project-start proof.
- The current implementation note explicitly says the shipped project-selector feature is partial until repo-backed bootstrap lands.
- The future-plan notes no longer treat repo-backed project start as an acceptable vague deferral for v1.
- The governing task plan and development log reference each other.
- The documented verification commands are run and their result is recorded honestly.
