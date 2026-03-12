# Rendered Generated `AGENTS.md` Template

## Purpose

Show what a generated repository's starter `AGENTS.md` could look like under the lifecycle-stage-governance model.

This is an example output for the future generator design, not an authoritative `AGENTS.md` for this repository.

The current future-plan bundle also carries a richer concrete starter-repo version at:

- `plan/future_plans/project_skeleton_generator/draft_repo/AGENTS.md`

Treat that draft file as the primary review surface when evaluating what a cloneable starter repo should ship today.

## Design Goals

The generated `AGENTS.md` should:

- stay concise
- define the always-on doctrine
- point contributors to the lifecycle notes and operational-state checklist
- avoid inlining every stage-specific rule
- stay parameterized enough for different projects and system inventories

## Rendered Example

```md
# AGENTS.md

## Purpose

This repository is being built as:

- `<project_mission_summary>`

Work in this repo must stay aligned with the design and process notes under `notes/`.

Implementation is not allowed to drift away from the documented lifecycle stage, plans, notes, checklists, or verification commands silently.

If coding reveals a limitation, contradiction, missing behavior, missing proof surface, command mismatch, or checklist/status mismatch, update the relevant note, checklist, or lifecycle artifact in the same change or an immediately adjacent follow-up change.

## Lifecycle Governance

Before meaningful work begins, read:

- `notes/lifecycle/00_project_lifecycle_overview.md`
- the current lifecycle stage note under `notes/lifecycle/`
- `plan/checklists/00_project_operational_state.md`

Follow the rules for the lifecycle stage the repository is actually in.

Treat stage-specific requirements as belonging to the lifecycle notes and operational-state checklist, not as ad hoc process rules to invent from memory.

Do not claim statuses or proving levels that the current stage and its completed sub-stages do not justify.

## System Coverage Rule

Every meaningful feature or change must explicitly consider the repository's declared primary systems:

- `<system_1>`
- `<system_2>`
- `<system_3>`
- `<system_4>`
- `<system_5_or_variant>`

If a system is not affected, record that deliberately in the governing plan, checklist, or review context instead of omitting it silently.

## Task Plan Rule

No meaningful code or process change should happen without a governing task plan under `plan/tasks/`.

The governing task plan should:

- define the goal
- define the scope
- name the relevant notes
- name the canonical verification commands
- state the intended proof layer honestly

## Development Log Rule

All meaningful work must leave a durable development log under `notes/logs/`.

The log should record:

- what was attempted
- what changed
- what commands were run
- what passed or failed
- what remains blocked or partial

## Testing Progression Rule

Testing should progress in stages:

1. bounded or fixture-assisted proof for changing work
2. real end-to-end proof for runtime behavior that the repository intends to claim

Bounded proof is useful, but it is not the same as end-to-end completion proof.

## Verification Command Rule

Canonical verification commands must be written down in the appropriate authoritative surfaces.

Contributors should use:

- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`

Do not invent ad hoc proof commands when the repository already declares a canonical command surface.

## Completion Language Rule

Use completion language carefully:

- `implemented`: assets or code exist, but stronger proof may still be missing
- `verified`: the documented command for the claimed layer was actually run successfully
- `flow_complete`: the declared runtime flow passed end to end for the stated scope
- `release_ready`: the stronger readiness bar for the declared release scope is actually satisfied

Do not describe work as complete, verified, flow-complete, or release-ready unless the current stage and proof surface justify it.

## Stack Declaration Rule

This starter repository is intentionally stack-agnostic until genesis and architecture work record the real choices.

Once the repository chooses primary languages, frameworks, persistence layers, or test tools, record those decisions in the relevant notes and lifecycle surfaces instead of leaving them implicit.

## Practical Contributor Rule

When making a meaningful change, ask:

1. what lifecycle stage governs this work right now?
2. which declared systems are affected?
3. what notes need to change?
4. what checklist or log updates are required?
5. what command proves the current claimed layer?
6. what stronger claims are still blocked?

If those questions are not answered, the work is not ready to claim as done.
```

## Parameterization Notes

The generator should substitute at least:

- `<project_mission_summary>`
- declared primary systems

It may also optionally parameterize:

- declared stack decisions once known
- repository-specific forbidden shortcuts
- deployment or security posture
- external service expectations

## Why This Template Matters

This template is intentionally shorter than the current repository's `AGENTS.md`.

That is by design.

The generated repository should grow stronger stage-specific doctrine through:

- lifecycle notes
- operational-state checklist updates
- feature and task plans
- verification-command docs

not by turning the starter `AGENTS.md` into a giant maturity dump on day zero.
