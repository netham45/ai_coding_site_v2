# Generated Repository Shape

## Goal

Describe the target skeleton that the future generator should render for a fresh project.

## Top-Level Structure

Suggested initial tree:

```text
AGENTS.md
README.md
code/
notes/
notes/logs/
notes/logs/setup/
notes/logs/features/
notes/logs/doc_updates/
notes/lifecycle/
notes/catalogs/
notes/catalogs/checklists/
notes/catalogs/inventory/
notes/catalogs/audit/
plan/
plan/tasks/
plan/checklists/
plan/features/
plan/future_plans/
simulations/
tests/
tests/unit/
tests/e2e/
```

This should be the minimal disciplined layout, not the final mature layout.

## Seed Files

The generator should create these files on day zero:

- `AGENTS.md`
- `README.md`
- `plan/README.md`
- `plan/tasks/README.md`
- `plan/checklists/README.md`
- `plan/features/README.md`
- `plan/future_plans/README.md`
- `notes/lifecycle/00_project_lifecycle_overview.md`
- `notes/lifecycle/01_stage_00_genesis.md`
- `notes/lifecycle/02_stage_01_architecture.md`
- `notes/lifecycle/03_stage_02_setup.md`
- `notes/lifecycle/04_stage_03_feature_delivery.md`
- `notes/lifecycle/05_stage_04_hardening_and_e2e.md`
- `notes/lifecycle/06_stage_05_post_v1_evolution.md`
- `plan/checklists/00_project_operational_state.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/catalogs/checklists/feature_checklist_standard.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`
- `notes/catalogs/inventory/system_inventory.md`
- `notes/catalogs/audit/flow_coverage_checklist.md`
- `plan/tasks/<date>_project_bootstrap.md`
- `notes/logs/setup/<date>_project_bootstrap.md`
- `plan/checklists/00_project_bootstrap_readiness.md`

## Generated AGENTS Shape

The generated `AGENTS.md` should be assembled from reusable blocks.

The future-plan bundle should also carry a rendered example of the starter `AGENTS.md` so the intended balance between global doctrine and stage-specific delegation is reviewable before implementation. See `2026-03-10_rendered_agents_template.md`.

### Base required blocks

- repository purpose
- system-coverage rule
- lifecycle-governance rule
- stage-adherence rule
- testing progression rule
- completion vocabulary
- stack defaults

### Parameterized blocks

- project name
- project mission
- declared primary systems
- language and framework defaults
- any project-specific forbidden shortcuts

### Optional blocks

- deployment rules
- security posture
- provider or external-service posture
- UI-specific expectations

### Suggested stage-governance block

Suggested generated `AGENTS.md` language:

> Before meaningful work begins, read `notes/lifecycle/00_project_lifecycle_overview.md`, the current lifecycle stage note, and `plan/checklists/00_project_operational_state.md`.
>
> Follow the rules for the lifecycle stage the repository is actually in. Treat stage-specific requirements as belonging to the lifecycle notes and operational-state checklist, not as ad hoc process rules to invent from memory.
>
> Do not claim statuses or proving levels that the current stage and its completed sub-steps do not justify.

## Starter Systems

The default skeleton should support explicit system declarations like:

- database
- cli
- daemon or backend
- yaml or config
- prompts

The future generator should allow alternatives, but it should still require explicit systems rather than letting a new repo stay vague.

## Placeholder Content Strategy

Each starter file should contain:

- why the file exists
- what it governs
- what is still a placeholder
- what the next real upgrade path is

This matters because an empty but unexplained folder tree will drift immediately.

## Checklist Model

The generated repository should start with two distinct checklist ideas:

- one operational-state checklist that tracks stage advancement
- one or more stage-local or feature-local checklists as the repository matures

The operational-state checklist should be the top-level maturity control surface.

The future-plan bundle should also carry a rendered example of that file so the intended output shape is reviewable before implementation. See `2026-03-10_rendered_operational_state_example.md`.

## Scaffold Philosophy

The generated project should feel like:

- a disciplined empty workshop

not like:

- a half-copied clone of this repo

That means:

- keep starter docs short
- leave obvious placeholders
- seed only the minimum command set needed to begin
- keep later adoption steps explicit in the lifecycle notes

## Post-V1 Starter Intent

The generated repository should include a visible reminder that first release is not the end of its process model.

The starter lifecycle set should therefore seed one explicit post-v1 note that tells future contributors how to handle:

- new major feature programs
- architecture or subsystem overhauls
- assurance and audit passes
- migrations and offloads
- deprecation and sunset work

The note can stay lightweight on day zero, but the category names and governing questions should already exist so a later repository does not regress into vague maintenance language for materially different kinds of work.
