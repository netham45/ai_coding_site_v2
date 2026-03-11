# Collaborative Design Workflow Working Notes

This folder captures a future idea for a collaborative UI-design workflow where the AI produces an initial implementation, asks the operator to review it, gathers structured design requirements, and iterates until the result is acceptable.

This is a working-note bundle, not an implementation plan.

Nothing in this folder should be read as an implementation, verification, or completion claim for the current repository.

## Bundle Contents

- `2026-03-11_original_starting_idea.md`
- `2026-03-11_review_and_profile_placement.md`
- `2026-03-11_task_profile_shape.md`
- `2026-03-11_design_rules_and_enforcement.md`
- `2026-03-11_design_schema_draft.md`
- `2026-03-11_review_state_machine.md`
- `2026-03-11_operator_questionnaire_and_requirement_capture.md`
- `2026-03-11_cli_api_and_inspection_surfaces.md`
- `2026-03-11_verification_and_enforcement_matrix.md`
- `2026-03-11_proposed_implementation_plan_sequence.md`
- `2026-03-11_local_app_startup_and_debug_contract.md`
- `2026-03-11_ui_review_scenarios.md`
- `2026-03-11_playwright_and_mock_state_strategy.md`
- `2026-03-11_scenario_response_shapes.md`
- `2026-03-11_action_request_shapes.md`
- `2026-03-11_artifact_taxonomy.md`
- `2026-03-11_lifecycle_matrix.md`
- `2026-03-11_gate_taxonomy.md`
- `2026-03-11_runtime_reporting_surface.md`

## Working Intent

The main questions in this bundle are:

- where this idea belongs relative to `workflow_overhaul/`
- whether collaborative design should be expressed first as a task-level workflow profile
- how the AI should gather useful design feedback from an operator with little UI-design experience
- which review artifacts should be durable rather than transient chat
- which design tools or preview surfaces should be optional inputs instead of hard dependencies

This bundle is deliberately exploratory.

It assumes this idea would only make sense after the repository has much stronger support for:

- profile-aware workflow decomposition from `plan/future_plans/workflow_overhaul/`
- prompt packs and task-profile behavior that can encode explicit review gates
- durable pause/resume and operator-inspection surfaces for interactive iteration loops

The goal here is to preserve and sharpen the idea without pretending it is implementation-ready.
