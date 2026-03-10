# Task: Workflow Overhaul Epic Profiles And Tier Prompt Note

## Goal

Expand the workflow-overhaul future-planning note so it captures a concrete draft for epic-style profiles, YAML shape changes, tier contracts, and baseline tier prompts that can be reviewed before implementation begins.

## Rationale

- Rationale: The existing workflow-overhaul note preserves the high-level idea, but it does not yet define the actual YAML shapes, tier responsibilities, or prompt contracts needed to evaluate whether the direction is sound.
- Reason for existence: This task exists to convert the current vague future-plan note into a much more actionable design draft without prematurely promoting it into an implementation-ready feature plan family.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/02_F01_configurable_node_hierarchy.md`: profile-aware epic behavior must remain compatible with the current generic kind-and-tier hierarchy posture.
- `plan/features/09_F35_project_policy_extensibility.md`: workflow profiles will likely behave like declarative policy selections and should stay compatible with the current policy-selection direction.
- `plan/features/43_F05_prompt_pack_authoring.md`: the proposed per-tier prompts and prompt overlays would eventually extend the packaged prompt surface.
- `plan/features/60_F05_builtin_node_task_layout_library_authoring.md`: the current note must respect the deliberate freeze on the active built-in ladder while still proposing an evolution path.
- `plan/features/65_F04_layout_replacement_and_hybrid_reconciliation.md`: richer layout documents and role-bearing child definitions will interact with layout authority and replacement semantics later.

## Required Notes

Read these note files before implementing or revising this phase:

- `plan/future_plans/workflow_overhaul/2026-03-10_self_hosted_workflow_overhaul_notes.md`
- `notes/explorations/original_concept.md`
- `notes/planning/implementation/project_development_flow_doctrine.md`
- `notes/planning/implementation/implementation_slicing_plan.md`
- `notes/planning/implementation/configurable_node_hierarchy_decisions.md`
- `notes/planning/implementation/builtin_node_task_layout_library_authoring_decisions.md`
- `notes/specs/architecture/code_vs_yaml_delineation.md`
- `notes/specs/prompts/prompt_library_plan.md`
- `notes/catalogs/checklists/document_schema_rulebook.md`
- `notes/catalogs/checklists/document_schema_test_policy.md`
- `AGENTS.md`

## Scope

- Database: not applicable; this task only extends future-planning notes and does not change the durable runtime schema.
- CLI: not applicable; this task does not change the current CLI surface.
- Daemon: not applicable; this task does not change runtime orchestration logic.
- YAML: document the proposed future YAML family and field shapes for workflow profiles, richer layout children, and prompt references, but do not modify active runtime YAML assets.
- Prompts: document proposed baseline per-tier prompts and profile overlays, but do not modify active prompt-pack assets.
- Tests: run the relevant document-schema tests for the new task plan, log update, and note update.
- Performance: negligible for this documentation-only task; note any future performance implications of profile-aware layout validation.
- Notes: update the workflow-overhaul future-plan note with concrete tier definitions, YAML proposals, prompt proposals, and design guardrails.

## Verification

- Document-schema coverage: `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py`

## Exit Criteria

- The workflow-overhaul future-plan note contains explicit tier contracts for epic, phase, plan, and task.
- The workflow-overhaul future-plan note contains a concrete YAML proposal for profile-aware epics and richer layout children.
- The workflow-overhaul future-plan note contains baseline prompt proposals for the main tiers plus profile-specific overlays.
- The governing task plan and development log exist and point to each other.
- The documented verification command passes.
