# Development Log: Workflow Overhaul Verification Feedback Loop Review

## Entry 1

- Timestamp: 2026-03-14T02:27:07-06:00
- Task ID: workflow_overhaul_verification_feedback_loop_review
- Task title: Review workflow-overhaul verification feedback-loop gap
- Status: started
- Affected systems: notes, prompts, daemon, cli, database, yaml, website_ui
- Summary: Began a review of the future workflow-overhaul draft and the implemented runtime/notes to check whether verification stages have a legal path to send work back for remediation when they discover incomplete implementation or missing outputs.
- Plans and notes consulted:
  - `plan/tasks/2026-03-14_workflow_overhaul_verification_feedback_loop_review.md`
  - `AGENTS.md`
  - `plan/future_plans/workflow_overhaul/draft/draft_feature_plans/22_workflow_profile_route_design_and_mutation_contracts.md`
  - `plan/future_plans/workflow_overhaul/draft/e2e_route_plans/02_feature_delivery_ladder.md`
  - `plan/future_plans/workflow_overhaul/draft/e2e_route_plans/03_review_and_remediation_ladder.md`
  - `plan/future_plans/workflow_overhaul/draft/e2e_route_plans/04_documentation_ladder.md`
  - `plan/future_plans/workflow_overhaul/prompts/epic/base.md`
  - `plan/future_plans/workflow_overhaul/prompts/epic/feature.md`
  - `plan/future_plans/workflow_overhaul/prompts/epic/review.md`
  - `plan/future_plans/workflow_overhaul/prompts/epic/documentation.md`
  - `plan/future_plans/workflow_overhaul/prompts/plan/base.md`
  - `plan/future_plans/workflow_overhaul/prompts/plan/verification.md`
  - `plan/future_plans/workflow_overhaul/prompts/task/base.md`
  - `plan/future_plans/workflow_overhaul/prompts/task/verification.md`
  - `notes/specs/runtime/runtime_command_loop_spec_v2.md`
  - `flows/09_run_quality_gates_flow.md`
  - `flows/10_regenerate_and_rectify_flow.md`
- Commands and tests run:
  - `rg -n "verification|verify|stage|workflow overhaul|future plans|plan stage|task stage|return to|feedback loop|reopen|regress|back to" notes docs flows src tests .`
  - `rg --files notes docs flows src tests .`
  - `sed -n '1,220p' plan/future_plans/workflow_overhaul/draft/draft_feature_plans/22_workflow_profile_route_design_and_mutation_contracts.md`
  - `sed -n '1,220p' plan/future_plans/workflow_overhaul/draft/e2e_route_plans/02_feature_delivery_ladder.md`
  - `sed -n '1,220p' plan/future_plans/workflow_overhaul/draft/e2e_route_plans/03_review_and_remediation_ladder.md`
  - `sed -n '1,220p' plan/future_plans/workflow_overhaul/draft/e2e_route_plans/04_documentation_ladder.md`
  - `sed -n '1,260p' plan/future_plans/workflow_overhaul/draft/draft_feature_plans/12_generated_task_completion_and_blocker_enforcement.md`
  - `sed -n '1,260p' plan/future_plans/workflow_overhaul/draft/draft_feature_plans/11_generated_task_prompt_objective_and_result_contract.md`
  - `sed -n '1,220p' plan/future_plans/workflow_overhaul/prompts/epic/review.md`
  - `sed -n '1,220p' plan/future_plans/workflow_overhaul/prompts/epic/documentation.md`
  - `sed -n '1,220p' plan/future_plans/workflow_overhaul/prompts/epic/planning.md`
  - `sed -n '1,220p' plan/future_plans/workflow_overhaul/prompts/epic/feature.md`
  - `sed -n '1,240p' plan/future_plans/workflow_overhaul/prompts/epic/base.md`
  - `sed -n '1,260p' plan/future_plans/workflow_overhaul/draft/draft_feature_plans/30_unified_command_lifecycle_contract.md`
  - `sed -n '1,260p' plan/future_plans/workflow_overhaul/draft/draft_feature_plans/04_compiled_profile_context_and_brief_generation.md`
  - `sed -n '1,240p' plan/future_plans/workflow_overhaul/draft/e2e_route_plans/01_planning_ladder.md`
  - `sed -n '1,240p' plan/future_plans/workflow_overhaul/draft/e2e_route_plans/07_leaf_completion_predicates.md`
  - `rg -n "task\\.verification|task\\.remediation|verification_mapping|required_child_roles|verification obligations|remediation" plan/future_plans/workflow_overhaul/draft plan/future_plans/workflow_overhaul/e2e_task_profiles plan/future_plans/workflow_overhaul/prompts`
  - `sed -n '1,220p' plan/future_plans/workflow_overhaul/e2e_task_profiles/canonical_flow_profiles.md`
  - `sed -n '1,220p' plan/future_plans/workflow_overhaul/e2e_task_profiles/specialized_suite_profiles.md`
  - `rg -n "remediation|re-review|verification|quality gate|run_quality|review run|rectify|regenerate|return to previous|previous stage|reopen|failure findings|blocked reason" notes/specs/runtime notes/planning/implementation src/aicoding tests/unit tests/integration | head -n 400`
  - `sed -n '430,520p' notes/specs/runtime/runtime_command_loop_spec_v2.md`
  - `sed -n '1,220p' flows/09_run_quality_gates_flow.md`
  - `sed -n '1,220p' flows/10_regenerate_and_rectify_flow.md`
- Result: Review in progress; the draft appears to preserve remediation for review and documentation profiles but not as a generalized verification-to-remediation-to-reverification loop across feature-delivery and lower-tier verification plans/tasks.
- Next step: record the concrete findings and propose the route-contract changes needed to make verification outcomes capable of spawning remediation and re-entry.

## Entry 2

- Timestamp: 2026-03-14T02:27:07-06:00
- Task ID: workflow_overhaul_verification_feedback_loop_review
- Task title: Review workflow-overhaul verification feedback-loop gap
- Status: complete
- Affected systems: notes, prompts, daemon, cli, database, yaml, website_ui
- Summary: Completed the review and identified the main gap: verification is represented as a proving band, but most of the future workflow-overhaul draft does not yet define a reusable remediation loop that routes incomplete or failed verification results back into bounded remediation and then back into re-verification.
- Plans and notes consulted:
  - `plan/tasks/2026-03-14_workflow_overhaul_verification_feedback_loop_review.md`
  - `AGENTS.md`
  - `plan/future_plans/workflow_overhaul/draft/e2e_route_plans/02_feature_delivery_ladder.md`
  - `plan/future_plans/workflow_overhaul/draft/e2e_route_plans/03_review_and_remediation_ladder.md`
  - `plan/future_plans/workflow_overhaul/draft/e2e_route_plans/04_documentation_ladder.md`
  - `plan/future_plans/workflow_overhaul/prompts/epic/feature.md`
  - `plan/future_plans/workflow_overhaul/prompts/epic/documentation.md`
  - `plan/future_plans/workflow_overhaul/prompts/epic/review.md`
  - `plan/future_plans/workflow_overhaul/prompts/plan/verification.md`
  - `plan/future_plans/workflow_overhaul/prompts/task/base.md`
  - `plan/future_plans/workflow_overhaul/prompts/task/verification.md`
  - `notes/specs/runtime/runtime_command_loop_spec_v2.md`
  - `flows/09_run_quality_gates_flow.md`
  - `flows/10_regenerate_and_rectify_flow.md`
- Commands and tests run:
  - `nl -ba plan/future_plans/workflow_overhaul/prompts/epic/feature.md | sed -n '1,120p'`
  - `nl -ba plan/future_plans/workflow_overhaul/prompts/epic/documentation.md | sed -n '1,120p'`
  - `nl -ba plan/future_plans/workflow_overhaul/prompts/epic/review.md | sed -n '1,120p'`
  - `nl -ba plan/future_plans/workflow_overhaul/prompts/plan/verification.md | sed -n '1,160p'`
  - `nl -ba plan/future_plans/workflow_overhaul/prompts/task/base.md | sed -n '1,220p'`
  - `nl -ba notes/specs/runtime/runtime_command_loop_spec_v2.md | sed -n '438,470p'`
  - `nl -ba flows/09_run_quality_gates_flow.md | sed -n '1,120p'`
  - `nl -ba plan/future_plans/workflow_overhaul/draft/e2e_route_plans/02_feature_delivery_ladder.md | sed -n '1,120p'`
  - `nl -ba plan/future_plans/workflow_overhaul/draft/e2e_route_plans/03_review_and_remediation_ladder.md | sed -n '1,120p'`
  - `nl -ba plan/future_plans/workflow_overhaul/draft/e2e_route_plans/04_documentation_ladder.md | sed -n '1,120p'`
  - `ls plan/future_plans/workflow_overhaul/prompts/plan`
- Result: The review found three concrete problems.

1. `epic.feature` requires only `discovery`, `implementation`, `documentation`, and `e2e`, so the general feature-delivery ladder has no explicit remediation or reverification band even though docs and E2E can surface incompleteness.
2. `plan/verification.md` requires defect classification for downstream remediation, but the draft prompt family does not include a sibling `plan/remediation.md` contract, so the loop breaks at the exact tier where verification findings become actionable work.
3. `task/base.md` only allows `complete`, `blocked`, `failed`, and `escalate`, which forces verification-discovered incompleteness into generic failure instead of a first-class “needs remediation/reverify” route.

The implemented runtime already shows the missing concept: review can return `revise` and daemon-owned routing rewinds to the last non-gate implementation subtask so validation and review run again naturally.

- Next step: update the workflow-overhaul draft so verification is modeled as a route-producing stage outcome with explicit remediation and reverification contracts, then add E2E coverage that proves the loop for feature, docs, and generic verification plans/tasks.
