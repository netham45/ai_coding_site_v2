# Workflow Overhaul Corrective Feedback Loop Planning

## Entry 1

- Timestamp: 2026-03-14T02:27:07-06:00
- Task ID: 2026-03-14_workflow_overhaul_corrective_feedback_loop_planning
- Task title: Workflow overhaul corrective feedback loop planning
- Status: started
- Affected systems: notes, prompts planning context, daemon planning context, CLI planning context, database planning context, YAML planning context, website UI planning context, development logs
- Summary: Began updating the workflow-overhaul draft so verification-driven remediation is modeled as a deterministic corrective loop with runtime-owned chain extension or corrective child materialization rather than as a terminal pass/fail gate.
- Plans and notes consulted:
  - `plan/tasks/2026-03-14_workflow_overhaul_corrective_feedback_loop_planning.md`
  - `AGENTS.md`
  - `plan/future_plans/workflow_overhaul/draft/README.md`
  - `plan/future_plans/workflow_overhaul/draft/PLAN_PROGRESS_CHECKLIST.md`
  - `plan/future_plans/workflow_overhaul/draft/draft_setup_plans/02_runtime_surface_and_data_model_readiness.md`
  - `plan/future_plans/workflow_overhaul/draft/draft_feature_plans/04_compiled_profile_context_and_brief_generation.md`
  - `plan/future_plans/workflow_overhaul/draft/draft_feature_plans/22_workflow_profile_route_design_and_mutation_contracts.md`
  - `plan/future_plans/workflow_overhaul/draft/draft_feature_plans/24_workflow_profile_runtime_gap_closure_plans.md`
  - `plan/future_plans/workflow_overhaul/draft/draft_feature_plans/30_unified_command_lifecycle_contract.md`
  - `plan/future_plans/workflow_overhaul/draft/e2e_route_plans/01_planning_ladder.md`
  - `plan/future_plans/workflow_overhaul/draft/e2e_route_plans/02_feature_delivery_ladder.md`
  - `plan/future_plans/workflow_overhaul/draft/e2e_route_plans/04_documentation_ladder.md`
  - `plan/future_plans/workflow_overhaul/draft/e2e_route_plans/07_leaf_completion_predicates.md`
  - `plan/future_plans/workflow_overhaul/prompts/README.md`
  - `plan/future_plans/workflow_overhaul/prompts/epic/feature.md`
  - `plan/future_plans/workflow_overhaul/prompts/plan/verification.md`
  - `plan/future_plans/workflow_overhaul/prompts/task/base.md`
  - `plan/future_plans/workflow_overhaul/prompts/task/verification.md`
  - `plan/future_plans/workflow_overhaul/prompts/task/remediation.md`
  - `notes/specs/runtime/runtime_command_loop_spec_v2.md`
  - `src/aicoding/db/models.py`
  - `src/aicoding/daemon/workflows.py`
  - `src/aicoding/daemon/run_orchestration.py`
  - `src/aicoding/daemon/review_runtime.py`
- Commands and tests run:
  - `sed -n '1,260p' plan/future_plans/workflow_overhaul/draft/README.md`
  - `sed -n '1,260p' plan/future_plans/workflow_overhaul/draft/PLAN_PROGRESS_CHECKLIST.md`
  - `sed -n '1,260p' plan/future_plans/workflow_overhaul/draft/draft_feature_plans/24_workflow_profile_runtime_gap_closure_plans.md`
  - `sed -n '1,260p' plan/future_plans/workflow_overhaul/draft/draft_setup_plans/02_runtime_surface_and_data_model_readiness.md`
  - `rg -n "compiled_subtask|compiled_subtasks|workflow advance|review_results|revise_action|current_subtask|append.*subtask|materialize.*children|immutable compile|frozen rendered|compiled workflow" src/aicoding notes/specs/runtime tests/unit tests/integration`
  - `sed -n '1,260p' src/aicoding/db/models.py`
  - `sed -n '1,260p' src/aicoding/daemon/workflows.py`
  - `sed -n '1,260p' src/aicoding/daemon/run_orchestration.py`
  - `rg -n "revise_action|rerun_task|review run|evaluate_review_subtask|current_compiled_subtask_id|execution_cursor_json|current_task_id" src/aicoding/daemon src/aicoding/resources/yaml/builtin/system-yaml notes/specs/runtime`
  - `sed -n '1,220p' src/aicoding/daemon/review_runtime.py`
- Result: In progress. The current runtime already supports review-driven rewind through `revise_action`, but the compiled chain and run cursor are still fundamentally frozen rather than appendable, so the future draft needs explicit runtime and persistence work for deterministic corrective expansion.
- Next step: Patch the draft queue, command subfeature breakdown, E2E route expectations, and prompt contracts with concrete steps for corrective expansion, loop caps, and tier-specific remediation/reverification behavior.

## Entry 2

- Timestamp: 2026-03-14T02:27:07-06:00
- Task ID: 2026-03-14_workflow_overhaul_corrective_feedback_loop_planning
- Task title: Workflow overhaul corrective feedback loop planning
- Status: complete
- Affected systems: notes, prompts planning context, daemon planning context, CLI planning context, database planning context, YAML planning context, website UI planning context, development logs
- Summary: Updated the workflow-overhaul draft queue, lifecycle feature slices, command-subfeature breakdown, E2E route plans, and prompt contracts so verification-driven remediation is modeled as deterministic corrective expansion with mandatory reverification and a hard remediation-turn cap.
- Plans and notes consulted:
  - `plan/tasks/2026-03-14_workflow_overhaul_corrective_feedback_loop_planning.md`
  - `AGENTS.md`
  - `plan/future_plans/workflow_overhaul/draft/README.md`
  - `plan/future_plans/workflow_overhaul/draft/PLAN_PROGRESS_CHECKLIST.md`
  - `plan/future_plans/workflow_overhaul/draft/draft_setup_plans/02_runtime_surface_and_data_model_readiness.md`
  - `plan/future_plans/workflow_overhaul/draft/draft_feature_plans/04_compiled_profile_context_and_brief_generation.md`
  - `plan/future_plans/workflow_overhaul/draft/draft_feature_plans/22_workflow_profile_route_design_and_mutation_contracts.md`
  - `plan/future_plans/workflow_overhaul/draft/draft_feature_plans/24_workflow_profile_runtime_gap_closure_plans.md`
  - `plan/future_plans/workflow_overhaul/draft/draft_feature_plans/30_unified_command_lifecycle_contract.md`
  - `plan/future_plans/workflow_overhaul/draft/e2e_route_plans/01_planning_ladder.md`
  - `plan/future_plans/workflow_overhaul/draft/e2e_route_plans/02_feature_delivery_ladder.md`
  - `plan/future_plans/workflow_overhaul/draft/e2e_route_plans/04_documentation_ladder.md`
  - `plan/future_plans/workflow_overhaul/draft/e2e_route_plans/07_leaf_completion_predicates.md`
  - `plan/future_plans/workflow_overhaul/draft/2026-03-13_command_subfeature_plan_index.md`
  - `plan/future_plans/workflow_overhaul/draft/command_subfeature_plans/README.md`
  - `plan/future_plans/workflow_overhaul/prompts/README.md`
  - `plan/future_plans/workflow_overhaul/prompts/epic/feature.md`
  - `plan/future_plans/workflow_overhaul/prompts/plan/verification.md`
  - `plan/future_plans/workflow_overhaul/prompts/task/base.md`
  - `plan/future_plans/workflow_overhaul/prompts/task/verification.md`
  - `plan/future_plans/workflow_overhaul/prompts/task/remediation.md`
  - `notes/specs/runtime/runtime_command_loop_spec_v2.md`
  - `src/aicoding/db/models.py`
  - `src/aicoding/daemon/run_orchestration.py`
  - `src/aicoding/daemon/review_runtime.py`
- Commands and tests run:
  - `sed -n '1,260p' plan/future_plans/workflow_overhaul/draft/README.md`
  - `sed -n '1,260p' plan/future_plans/workflow_overhaul/draft/PLAN_PROGRESS_CHECKLIST.md`
  - `sed -n '1,260p' plan/future_plans/workflow_overhaul/draft/draft_feature_plans/24_workflow_profile_runtime_gap_closure_plans.md`
  - `sed -n '1,260p' plan/future_plans/workflow_overhaul/draft/draft_setup_plans/02_runtime_surface_and_data_model_readiness.md`
  - `rg -n "compiled_subtask|compiled_subtasks|workflow advance|review_results|revise_action|current_subtask|append.*subtask|materialize.*children|immutable compile|frozen rendered|compiled workflow" src/aicoding notes/specs/runtime tests/unit tests/integration`
  - `sed -n '1,260p' src/aicoding/db/models.py`
  - `sed -n '1,260p' src/aicoding/daemon/workflows.py`
  - `sed -n '1,260p' src/aicoding/daemon/run_orchestration.py`
  - `rg -n "revise_action|rerun_task|review run|evaluate_review_subtask|current_compiled_subtask_id|execution_cursor_json|current_task_id" src/aicoding/daemon src/aicoding/resources/yaml/builtin/system-yaml notes/specs/runtime`
  - `sed -n '1,220p' src/aicoding/daemon/review_runtime.py`
  - `PYTHONPATH=src python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_feature_plan_docs.py -q`
  - `PYTHONPATH=src python3 -m pytest tests/unit/test_logging.py -q`
- Result: The future-plan bundle now has concrete implementation steps for corrective expansion:

  - runtime/data-model readiness now calls out append-only leaf chain extension, non-leaf corrective child materialization, loop budgets, and inspection surfaces
  - the compile-context slice now freezes corrective-expansion policy and remediation-turn-cap metadata
  - route and command lifecycle slices now explicitly require `needs_remediation`, deterministic remediation plus reverification, and tier-aware corrective expansion
  - the command-subfeature family now includes a dedicated foundation plan for corrective expansion and reverification
  - planning, feature-delivery, documentation, and leaf E2E routes now require proof of bounded corrective loops
  - prompt drafts now include a plan-level remediation overlay and task-level `needs_remediation` behavior

Verification status:

  - `PYTHONPATH=src python3 -m pytest tests/unit/test_logging.py -q` passed
  - `PYTHONPATH=src python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_feature_plan_docs.py -q` failed for a pre-existing unrelated development-log schema issue in `notes/logs/doc_updates/2026-03-13_ai_project_skeleton_milestone_gate_hardening.md`, which still does not cite a governing `plan/tasks/...` entry as required by the current test

- Next step: If this future-plan direction is accepted, the next implementation-planning pass should add the concrete persistence objects, daemon mutation API, and inspection payload shapes needed to make corrective expansion real code rather than draft-only scope.
