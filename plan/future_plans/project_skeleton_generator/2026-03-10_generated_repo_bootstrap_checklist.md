# Generated Repo Bootstrap Checklist

## Purpose

Provide a draft checklist that the generated repository can ship with and attempt to follow during its first setup and planning stages.

This is a working-note checklist for the future generator design, not an authoritative checklist for this repository.

This should be treated as a stage-local bootstrap checklist, not as the generated repository's only maturity control surface.

The generated repository should also have a separate operational-state checklist that tracks lifecycle advancement.

## Checklist Shape

The generated repository should probably start with one compact bootstrap checklist rather than a large mature checklist matrix.

That compact bootstrap checklist should sit underneath the top-level operational-state checklist.

Suggested sections:

- repository foundation
- doctrine adoption
- system definition
- planning surfaces
- testing surfaces
- logging surfaces
- early E2E intent

## Draft Checklist

### Repository Foundation

- [ ] `AGENTS.md` exists and states the repo purpose, system-coverage rule, testing progression rule, and completion vocabulary.
- [ ] `README.md` explains the project mission and points to the planning and lifecycle docs.
- [ ] Base directories exist for `code/`, `notes/`, `plan/`, `simulations/`, and `tests/`.

### Doctrine Adoption

- [ ] `notes/lifecycle/` exists and contains the stage notes for genesis, architecture, setup, feature delivery, and hardening/E2E.
- [ ] `notes/catalogs/checklists/verification_command_catalog.md` exists, even if some commands are placeholders.
- [ ] `notes/catalogs/checklists/e2e_execution_policy.md` exists and distinguishes bounded proof from real E2E proof.
- [ ] `notes/catalogs/checklists/feature_checklist_standard.md` exists and defines the local status vocabulary.

### System Definition

- [ ] The repository has an explicit primary system inventory.
- [ ] Each declared system has a short statement of responsibility.
- [ ] The project has stated whether it uses the default five-system model or a deliberate variant.

### Planning Surfaces

- [ ] `plan/tasks/README.md`, `plan/checklists/README.md`, and `plan/features/README.md` exist.
- [ ] The first bootstrap task plan exists.
- [ ] The first development log exists and cites the governing task plan.
- [ ] The first readiness checklist exists.
- [ ] The operational-state checklist exists and marks bootstrap as the active maturity stage.

### Testing Surfaces

- [ ] The repository defines a bounded-test command.
- [ ] The bounded-test command is real and runnable from a clean shell rather than a placeholder.
- [ ] The repository defines a future real-E2E target, even if not yet implemented.
- [ ] The repository states what cannot yet be called `verified`, `flow_complete`, or `release_ready`.

### Logging Surfaces

- [ ] `notes/logs/setup/` exists.
- [ ] The initial setup task recorded a start state, commands run, result, and next step.
- [ ] The generated repo's process docs explain when new logs are required.

### Early E2E Intent

- [ ] The generated repo has at least one documented end-to-end narrative target.
- [ ] The repo does not overclaim completion before the real E2E layer exists.
- [ ] The lifecycle notes explain how to graduate from setup proof to real runtime proof.

## Working Recommendation

The generated repository should treat this checklist as:

- a bootstrap discipline aid

not as:

- proof that the project is already mature

The point is to stage the project into rigor, not to pretend rigor already happened.
