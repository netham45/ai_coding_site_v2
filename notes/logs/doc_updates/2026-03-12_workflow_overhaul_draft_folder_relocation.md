# Workflow Overhaul Draft Folder Relocation

## Entry 1

- Timestamp: 2026-03-12T21:55:00-06:00
- Task ID: 2026-03-12_workflow_overhaul_draft_folder_relocation
- Task title: Workflow-overhaul draft folder relocation
- Status: started
- Affected systems: notes, YAML planning context, prompts planning context, CLI planning context, daemon planning context, website planning context, development logs, document consistency tests
- Summary: Began relocating the workflow-overhaul draft-plan bundle into a dedicated `draft/` subtree under the same future-plan family.
- Plans and notes consulted:
  - `plan/tasks/2026-03-12_workflow_overhaul_draft_folder_relocation.md`
  - `AGENTS.md`
  - `plan/future_plans/workflow_overhaul/2026-03-10_self_hosted_workflow_overhaul_notes.md`
  - `plan/future_plans/workflow_overhaul/draft/2026-03-12_draft_setup_and_feature_plan_index.md`
- Commands and tests run:
  - `find plan/future_plans/workflow_overhaul -maxdepth 2 -mindepth 1 | sort`
  - `rg -n "plan/future_plans/workflow_overhaul/" plan/future_plans/workflow_overhaul plan/tasks notes/logs/doc_updates`
- Result: In progress. The workflow-overhaul bundle still needs to be moved under `draft/`, and many notes/tasks/logs reference the pre-move paths directly.
- Next step: Move the draft bundle into `draft/`, update references, rerun document tests, and record the final result.

## Entry 2

- Timestamp: 2026-03-12T22:04:00-06:00
- Task ID: 2026-03-12_workflow_overhaul_draft_folder_relocation
- Task title: Workflow-overhaul draft folder relocation
- Status: complete
- Affected systems: notes, YAML planning context, prompts planning context, CLI planning context, daemon planning context, website planning context, development logs, document consistency tests
- Summary: Moved the current workflow-overhaul draft-plan bundle into `plan/future_plans/workflow_overhaul/draft/` and updated the affected path references.
- Plans and notes consulted:
  - `plan/tasks/2026-03-12_workflow_overhaul_draft_folder_relocation.md`
  - `AGENTS.md`
  - `plan/future_plans/workflow_overhaul/2026-03-10_self_hosted_workflow_overhaul_notes.md`
  - `plan/future_plans/workflow_overhaul/draft/2026-03-12_draft_setup_and_feature_plan_index.md`
- Commands and tests run:
  - `mkdir -p plan/future_plans/workflow_overhaul/draft && for item in plan/future_plans/workflow_overhaul/*; do base=$(basename "$item"); if [ "$base" != "draft" ]; then mv "$item" plan/future_plans/workflow_overhaul/draft/; fi; done`
  - `rg -l 'plan/future_plans/workflow_overhaul/' plan/future_plans/workflow_overhaul/draft plan/tasks notes/logs/doc_updates | grep -v '2026-03-12_workflow_overhaul_draft_folder_relocation.md' | while read -r file; do perl -0pi -e 's#plan/future_plans/workflow_overhaul/#plan/future_plans/workflow_overhaul/draft/#g' "$file"; done`
  - `rg -n "plan/future_plans/workflow_overhaul/(?!draft/)" -P .`
  - `PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_document_schema_docs.py -q`
- Result:
  - The `workflow_overhaul` top level now contains the `draft/` subtree.
  - Existing workflow-overhaul draft-plan notes, examples, prompts, catalogs, and subplan directories now live under `plan/future_plans/workflow_overhaul/draft/`.
  - Affected task/log/future-plan references were updated to the new `draft/` paths.
  - Verification passed: `13 passed in 2.87s`
- Next step: If desired, add a small top-level redirect note under `plan/future_plans/workflow_overhaul/` so operators landing in the folder are pointed straight to `draft/`.

## Entry 3

- Timestamp: 2026-03-12T22:18:00-06:00
- Task ID: 2026-03-12_workflow_overhaul_draft_folder_relocation
- Task title: Workflow-overhaul draft folder relocation
- Status: changed_plan
- Affected systems: notes, YAML planning context, prompts planning context, CLI planning context, daemon planning context, website planning context, development logs, document consistency tests
- Summary: Corrected the relocation scope after realizing the first pass moved the entire workflow-overhaul note bundle instead of only the executable implementation-plan assets.
- Plans and notes consulted:
  - `plan/tasks/2026-03-12_workflow_overhaul_draft_folder_relocation.md`
  - `plan/future_plans/workflow_overhaul/2026-03-10_self_hosted_workflow_overhaul_notes.md`
  - `plan/future_plans/workflow_overhaul/draft/2026-03-12_draft_setup_and_feature_plan_index.md`
- Commands and tests run:
  - `find plan/future_plans/workflow_overhaul/draft -maxdepth 1 -mindepth 1 | sort`
  - `find plan/future_plans/workflow_overhaul -maxdepth 1 -mindepth 1 | sort`
- Result: The first relocation was too broad. The draft folder should contain only implementation plans, while notes, prompts, starter assets, examples, and schema/support drafts should stay at the workflow-overhaul top level.
- Next step: Move the non-plan assets back out of `draft/`, keep the actual plan directories and plan indexes there, rerun document checks, and record the corrected final state.

## Entry 4

- Timestamp: 2026-03-12T22:24:00-06:00
- Task ID: 2026-03-12_workflow_overhaul_draft_folder_relocation
- Task title: Workflow-overhaul draft folder relocation
- Status: complete
- Affected systems: notes, YAML planning context, prompts planning context, CLI planning context, daemon planning context, website planning context, development logs, document consistency tests
- Summary: Narrowed the `draft/` subtree so it now contains only the executable workflow-overhaul plan assets, with supporting notes and draft inputs restored to the top level.
- Plans and notes consulted:
  - `plan/tasks/2026-03-12_workflow_overhaul_draft_folder_relocation.md`
  - `plan/future_plans/workflow_overhaul/2026-03-10_self_hosted_workflow_overhaul_notes.md`
  - `plan/future_plans/workflow_overhaul/draft/2026-03-12_draft_setup_and_feature_plan_index.md`
- Commands and tests run:
  - `find plan/future_plans/workflow_overhaul/draft -maxdepth 1 -mindepth 1 | sort`
  - `find plan/future_plans/workflow_overhaul -maxdepth 1 -mindepth 1 | sort`
  - `PYTHONPATH=src python3 -m pytest tests/unit/test_task_plan_docs.py tests/unit/test_document_schema_docs.py -q`
- Result:
  - `draft/` now contains only:
    - `draft_setup_plans/`
    - `draft_feature_plans/`
    - `workflow_profile_subfeature_plans/`
    - `checklist_feature_plans/`
    - `e2e_route_plans/`
    - `2026-03-12_draft_setup_and_feature_plan_index.md`
    - `2026-03-12_workflow_profile_subfeature_plan_index.md`
    - `2026-03-12_workflow_overhaul_e2e_route_plan.md`
  - Supporting notes, prompts, starter profiles, schema drafts, examples, simulations, and auxiliary draft inputs were restored to `plan/future_plans/workflow_overhaul/`.
  - Verification passed: `13 passed`
- Next step: If desired, the remaining plan-like support assets such as `checklist_future_flows/` can be explicitly classified as either executable plans or reference inputs.
