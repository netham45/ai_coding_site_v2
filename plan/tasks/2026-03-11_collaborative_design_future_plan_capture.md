# Task: Capture Collaborative Design Future Plan

## Goal

Capture a future-plan bundle for a collaborative-design workflow in which the AI produces an initial page/UI implementation, pauses for human review, asks for a structured list of design requirements and field-level constraints, and then iterates on the design with explicit review checkpoints.

## Rationale

- Rationale: The user wants a design-assistance mode that works even when the operator has very little UI-design experience, but the repository does not yet have a preserved plan for how that behavior should fit the workflow-overhaul profile model.
- Reason for existence: This task exists to review the current workflow-overhaul working notes, decide where this idea belongs in the future roadmap, preserve the original rough concept, make an explicit argument for task-level profile placement, record the future cross-system implications, and capture candidate operator loops and tooling options without overstating implementation readiness.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/14_F10_ai_facing_cli_command_loop.md`: the future collaborative loop would need review prompts and pause/resume behavior that stay aligned with the real AI-facing command surface.
- `plan/features/34_F32_automation_of_all_user_visible_actions.md`: the design-review loop should only expose review, regenerate, and update actions that are durable and inspectable.
- `plan/features/60_F05_builtin_node_task_layout_library_authoring.md`: if collaborative design becomes a built-in profile, it will need layout/profile-aware starter assets rather than ad hoc decomposition.
- `plan/features/62_F05_builtin_runtime_policy_hook_prompt_library_authoring.md`: the future behavior depends on prompt assets and runtime policies that encode review gates and required requirement capture.

## Required Notes

Read these note files before implementing or revising this phase:

- `plan/future_plans/README.md`
- `plan/future_plans/workflow_overhaul/2026-03-10_self_hosted_workflow_overhaul_notes.md`
- `plan/future_plans/workflow_overhaul/2026-03-10_workflow_profile_definition_schema_draft.md`
- `plan/future_plans/workflow_overhaul/starter_workflow_profiles/task.implementation.yaml`
- `notes/logs/doc_updates/2026-03-11_collaborative_design_future_plan_capture.md`
- `notes/catalogs/checklists/authoritative_document_family_inventory.md`
- `notes/catalogs/checklists/document_schema_rulebook.md`
- `notes/catalogs/checklists/document_schema_test_policy.md`
- `AGENTS.md`

## Scope

- Database: not applicable for this documentation task; the future-plan notes should still describe the durable review, prompt, and acceptance artifacts the real feature would likely require.
- CLI: not applicable for this documentation task; the notes should still explain how a future CLI- or operator-surface-driven review loop would work.
- Daemon: not applicable for this documentation task; the notes should still explain future pause/resume and review-gate behavior.
- YAML: not applicable for this documentation task; the notes should still sketch a future profile shape and why the idea belongs in the workflow-profile model.
- Prompts: not applicable for this documentation task; the notes should still describe the future prompt stack and requirement-gathering loop.
- Notes: add and expand a non-authoritative future-plan bundle under `plan/future_plans/` for the collaborative-design idea, including the original starting idea, a review-and-placement note tied to workflow-overhaul, a profile-shape note with rough operator-loop and tooling guidance, a design-rules-and-enforcement note covering global design policy, override handling, and strict verification expectations, plus follow-on notes for draft schema shapes, review-state flow, operator questionnaire design, inspection/API surfaces, verification mapping, a proposed implementation-plan sequence, deeper notes for local app startup/debug contracts, UI review scenarios, Playwright/mock-state review strategies, response-shape/runtime-reporting notes for scenario status, captured artifacts, and pending operator action, and lifecycle-matrix notes for per-state required artifacts, legal actions, and completion gates.
- Tests: run the authoritative document tests for the new task plan and development log after the bundle is added.
- Performance: negligible for this task; the future note should still call out preview-generation, screenshot, and iteration-latency concerns for later implementation.

## Verification

- Document-schema coverage: `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py`

## Exit Criteria

- `plan/future_plans/collaborative_design_workflow/` exists as a new future-plan bundle.
- The bundle contains a file preserving the original rough user idea.
- The bundle contains a review note that positions the idea after `workflow_overhaul` and explains why.
- The bundle contains an explicit argument for implementing the first version as a task-level workflow profile, with recorded conditions for introducing plan-level support later.
- The bundle captures the future operator loop for draft, review, requirement capture, revision, and approval.
- The bundle captures a future global-design-rules layer, including inheritance, explicit override policy, and enforcement expectations.
- The bundle captures the future implications across database, CLI, daemon, YAML, and prompts.
- The bundle contains deeper follow-on notes for schema shape, review-state transitions, operator question design, inspection surfaces, verification strategy, and a recommended implementation-plan sequence.
- The bundle contains deeper follow-on notes for how the system would start local apps, reach hard-to-open UI states, and remove repeated setup tedium through reusable review scenarios and Playwright-assisted state materialization.
- The bundle contains deeper follow-on notes for how a future daemon and CLI would report scenario readiness, current runtime mode, captured review artifacts, and pending operator action.
- The bundle contains deeper follow-on notes for lifecycle gating so a future runtime can tell which artifacts must exist, which actions are legal, and why completion is blocked at each review stage.
- The bundle records candidate design-collaboration tooling directions without treating any external tool as a required dependency.
- `plan/future_plans/README.md` lists the new bundle.
- `plan/tasks/README.md` lists the governing task plan.
- The governing task plan and development log exist and point to each other.
- The documented verification command passes.
