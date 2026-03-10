# Project Skeleton Generator Working Notes

This folder captures a future idea for generating a new repository from the operational framework used here.

This is a working-note bundle, not an implementation plan.

Nothing in this folder should be read as an implementation, verification, or completion claim for the current repository.

## Bundle Contents

- `2026-03-10_project_skeleton_generator_overview.md`
- `2026-03-10_operational_state_extraction_strategy.md`
- `2026-03-10_generated_repository_shape.md`
- `2026-03-10_project_lifecycle_note_set.md`
- `2026-03-10_project_operational_state_checklist.md`
- `2026-03-10_rendered_operational_state_example.md`
- `2026-03-10_rendered_agents_template.md`
- `2026-03-10_generated_repo_bootstrap_checklist.md`
- `2026-03-10_workflow_overhaul_integration.md`
- `lifecycle_note_examples/`

## Working Intent

The main question in this bundle is:

How do we take the operational doctrine of this repository and turn it into a bootstrapable empty project that starts with:

- a sane `AGENTS.md`
- a staged planning and verification doctrine
- starter `notes/`, `logs/`, `plans/`, `simulations/`, and `code/` directories
- explicit system definitions
- lifecycle guidance for how the new project should evolve

The notes here assume the eventual implementation could be either:

- a Python CLI tool
- a Python library entry point
- a template-rendering function inside the orchestrator

That choice is intentionally left open for later authoritative planning.

The lifecycle examples under `lifecycle_note_examples/` are intentionally written as concrete starter-note bodies for a future generated repository, not just as abstract guidance.

The bundle assumes a generated repository will keep `AGENTS.md` concise and put stage-specific rigor in:

- lifecycle stage notes with sub-steps
- an operational-state checklist that tracks which stage is currently active
