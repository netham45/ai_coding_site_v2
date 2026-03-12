# Task: Website Spec Gap Remediation Planning

## Goal

Turn the current website review findings into explicit corrective implementation plans for the major remaining spec gaps, with testing and real E2E coverage defined up front.

## Rationale

- Rationale: The current website implementation is materially narrower than the published website plans in project routing, tree navigation, execution detail, and regeneration semantics.
- Reason for existence: This task exists to prevent those gaps from remaining informal complaints or ad hoc follow-up work by converting them into authoritative feature slices with concrete proof requirements.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/web/features/00_project_bootstrap_and_selection.md`
- `plan/web/features/01_explorer_shell_and_hierarchy_tree.md`
- `plan/web/features/02_detail_tabs.md`
- `plan/web/features/03_prompts_and_regeneration_flow.md`
- `plan/web/features/04_bounded_action_surface.md`
- `plan/web/features/05_repo_backed_project_start_and_top_level_bootstrap.md`
- `plan/features/02_F01_configurable_node_hierarchy.md`
- `plan/features/24_F19_regeneration_and_upstream_rectification.md`
- `plan/features/70_F19_live_rebuild_cutover_coordination.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_v1_scope_freeze.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_top_level_node_creation_flow.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_review_and_expansion.md`
- `plan/future_plans/frontend_website_ui/2026-03-11_v1_action_table.md`
- `notes/logs/reviews/2026-03-11_website_spec_gap_review.md`

## Scope

- Database: no direct schema changes in this planning pass, but each corrective plan must call out any durable-state implications honestly.
- CLI: no direct CLI change in this planning pass, but the corrective plans must preserve browser and CLI semantic alignment.
- Daemon: define the missing read and mutation contracts needed for multi-root project flows, real tree navigation, execution detail, and cancel-and-regenerate behavior.
- Website: define the corrective React route, shell, and detail-surface changes needed to match the website plans.
- YAML: not applicable.
- Prompts: define prompt/regeneration corrections where existing candidate reuse and save-and-regenerate behavior are currently too narrow.
- Tests: define bounded, integration, browser, and real E2E proof for each corrective slice.
- Performance: note where tree loading, project bootstrap, attempt inspection, or cancellation orchestration could become operator-visible bottlenecks.
- Notes: add authoritative corrective plans and record the governing development log.

## Planned Changes

1. Add a feature plan for project multi-root navigation and persistent top-level creation access.
2. Add a feature plan for real expandable tree navigation, ancestor visibility, and subtree focus.
3. Add a feature plan for workflow and subtask execution detail expansion.
4. Add a feature plan for cancel-and-regenerate live subtree orchestration and prompt-flow reentry.
5. Add the governing development log for this planning batch.
6. Run the authoritative document-family tests after adding the new planning documents.

## Verification

Canonical verification commands for this task:

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py -q
PYTHONPATH=src python3 -m pytest tests/unit/test_feature_plan_docs.py -q
PYTHONPATH=src python3 -m pytest tests/unit/test_document_schema_docs.py -q
```

## Exit Criteria

- each major website spec gap from the review is mapped to an explicit corrective feature plan
- the corrective plans include testing and real E2E expectations rather than deferring proof silently
- the governing task plan and development log reference each other
- the documented verification commands are run and their result is recorded honestly
