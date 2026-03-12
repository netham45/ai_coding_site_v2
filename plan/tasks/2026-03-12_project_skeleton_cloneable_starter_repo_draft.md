# Task: Draft Cloneable Starter Repo For Project Skeleton

## Goal

Turn the `project_skeleton_generator` future-plan bundle into a concrete draft starter repository shape that can live as a separate repository users are encouraged to clone at project start.

## Rationale

- Rationale: The current future-plan bundle explains the skeleton-generator idea, but it still reads primarily like extraction-and-rendering theory. A concrete starter-repo draft makes the idea reviewable as an actual clone target.
- Reason for existence: This task exists to align the future plan with the newer direction that the starter experience should likely ship as its own repository, while still preserving generator-oriented notes for later automation if desired.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/28_F23_testing_framework_integration.md`: the starter repo must preserve the bounded-to-real-E2E proving doctrine and documented verification-command expectations.
- `plan/features/35_F36_auditable_history_and_reproducibility.md`: the starter repo needs development logs, audit-oriented note discipline, and reconstructible work history from the start.
- `plan/features/59_F04_builtin_runtime_policy_hook_prompt_library_authoring.md`: the starter repo needs prompt assets treated as first-class implementation surfaces when prompts are part of a project.
- `plan/features/65_F12_project_policy_extensibility.md`: the starter repo must preserve explicit policy surfaces rather than burying workflow or document expectations in ad hoc contributor behavior.
- `plan/features/73_F35_automation_of_all_user_visible_actions.md`: the starter repo needs operator-surface and proving expectations documented clearly rather than implied by internal helpers.

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `plan/future_plans/project_skeleton_generator/README.md`
- `plan/future_plans/project_skeleton_generator/2026-03-10_project_skeleton_generator_overview.md`
- `plan/future_plans/project_skeleton_generator/2026-03-10_generated_repository_shape.md`
- `plan/future_plans/project_skeleton_generator/2026-03-10_project_lifecycle_note_set.md`
- `plan/future_plans/project_skeleton_generator/2026-03-10_rendered_agents_template.md`
- `plan/future_plans/project_skeleton_generator/2026-03-10_rendered_operational_state_example.md`
- `notes/catalogs/checklists/authoritative_document_family_inventory.md`
- `notes/catalogs/checklists/document_schema_rulebook.md`
- `notes/catalogs/checklists/document_schema_test_policy.md`
- `notes/catalogs/checklists/verification_command_catalog.md`

## Scope

- Database: not applicable for the current product implementation; this task only drafts starter-repo guidance for how a future cloned repository should define its durable-state expectations.
- CLI: not applicable for the current product implementation; this task only drafts starter-repo guidance for a future repository's operator and AI command surfaces.
- Daemon: not applicable for the current product implementation; this task only drafts starter-repo guidance for a future repository's runtime authority.
- YAML: not applicable for the current product implementation; this task only drafts starter-repo guidance for a future repository's declarative structure and policy assets.
- Prompts: not applicable for the current product implementation; this task only drafts starter-repo guidance for prompt assets and prompt-contract expectations in a future repository.
- Notes: update the `project_skeleton_generator` future-plan bundle to reflect the cloneable-separate-repo direction, and add an actual starter-repo draft tree under that future-plan folder.
- Development logs: add a log for this doc-update batch and keep it current through completion.
- Tests: run the authoritative bounded document checks that cover changed task-plan and note surfaces.
- Performance: negligible for this task; this is documentation and starter-structure drafting work rather than a runtime behavior change.

## Verification

- `PYTHONPATH=src python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_notes_quickstart_docs.py -q`

## Exit Criteria

- The future-plan bundle explicitly records the separate cloneable starter-repo direction.
- A concrete draft starter repo exists under `plan/future_plans/project_skeleton_generator/`.
- The draft starter repo contains an `AGENTS.md` that carries forward the core concepts from the current repository-level `AGENTS.md`, adapted for a fresh repo.
- The draft starter repo contains a meaningfully fleshed out `notes/` tree rather than only placeholder top-level folders.
- The governing task plan and development log exist and cite the actual verification command used for this batch.
- The documented bounded verification command passes.
