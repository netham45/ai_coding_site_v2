# Post-V1 Lifecycle Model

## Purpose

Define how a generated repository should behave after it has a first real `v1`, `flow_complete`, or `release_ready` scope.

The key point is that the lifecycle does not end there.

It also does not stay purely linear.

After first release, work becomes choice-driven. Different kinds of change should reopen different parts of the lifecycle deliberately.

## Main Decision

Post-v1 governance should be modeled as:

- a retained baseline maturity claim for the scope already proven
- a named active workstream for the new kind of work
- reopened lifecycle gates only where the new work actually changes assumptions

This is better than either extreme:

- pretending all post-v1 work is just routine maintenance
- pretending every new program throws the whole repository back to genesis

## Why The Existing Model Needs Expansion

The current skeleton bundle already explains how to move from:

- concept
- architecture
- setup
- feature delivery
- hardening and E2E

But real projects do not stop once the first user-visible slice ships.

At that point, contributors need explicit guidance for questions like:

- Is this a local enhancement or a new feature program?
- Does this change reopen architecture and migration work?
- Is this primarily an audit or assurance pass rather than feature delivery?
- Are we moving behavior elsewhere instead of adding more behavior here?
- Are we deprecating and sunsetting instead of building forward?

## Workstream Categories

### `feature_expansion`

Use when:

- the user wants a new major feature or product area
- the work may need its own define, setup, implementation, documentation, and E2E path
- the repository can keep prior baseline claims for already-proven scope

Typical lifecycle reopening:

- discovery
- architecture for the new slice
- setup if new tooling, services, or data paths are required
- feature delivery
- hardening and E2E for the new slice

### `system_overhaul`

Use when:

- the user wants a major refactor, platform change, subsystem replacement, or deep design correction
- old assumptions are no longer reliable enough to treat the work as incremental delivery

Typical lifecycle reopening:

- architecture
- invariants
- migration planning
- implementation
- remediation
- E2E requalification for affected flows

### `assurance_audit`

Use when:

- the user wants a security audit, compliance pass, resilience hardening pass, privacy review, or performance requalification
- the central goal is risk reduction and proof quality, not net-new feature breadth

Typical lifecycle reopening:

- review
- verification
- remediation
- hardening and E2E

### `migration_offload`

Use when:

- the user wants to move data, traffic, ownership, workloads, or integrations elsewhere
- the repository must manage coexistence, cutover, rollback, or export rather than only local behavior changes

Typical lifecycle reopening:

- architecture
- migration planning
- implementation
- documentation
- cutover E2E
- recovery and rollback proof

### `sunset_archive`

Use when:

- the user wants to retire a feature, integration, environment, or the full project
- success means controlled deprecation and explainable shutdown, not additional capability

Typical lifecycle reopening:

- documentation
- operator guidance
- migration or export planning where needed
- final verification and archive proof

## Selection Heuristic

A generated repository should teach contributors to classify post-v1 work with a simple rule:

### Local enhancement

If the change fits inside an existing feature boundary, preserves existing architecture assumptions, and does not need its own rollout narrative, keep it inside normal feature-delivery handling.

### New program

If the change introduces a new major product area, new system boundary, new migration path, new audit burden, or a controlled retirement path, open a named post-v1 workstream instead of hiding it under routine feature work.

## Required Cross-System Questions

Every post-v1 workstream should still force the repository to ask:

1. What changes in durable state or migration posture?
2. What changes in operator or CLI surfaces?
3. What changes in live runtime or daemon authority?
4. What YAML or policy structure changes?
5. What prompts or review guidance change?
6. Which notes, checklists, and logs must be reopened?
7. Which prior E2E narratives must be rerun?
8. Which new failure, rollback, or sunset invariants now exist?

## Operational-State Implication

The generated `plan/checklists/00_project_operational_state.md` should track:

- the strongest baseline maturity already earned
- the active post-v1 workstream name
- the scope of that workstream
- the reopened lifecycle gates
- the blocked stronger claims for the new workstream

That model lets a repository say something precise like:

- baseline product scope remains `flow_complete`
- active workstream is `system_overhaul`
- architecture and migration gates are reopened for the overhaul scope
- prior release-readiness language does not automatically extend to the changed runtime path

## Relationship To Workflow Profiles

This model should align with the workflow-overhaul direction.

The workstream label identifies the kind of program.

The actual orchestration still uses stable node kinds with profile-aware variants such as:

- `epic.feature`
- `epic.review`
- `phase.architecture`
- `phase.implementation`
- `phase.e2e`
- `phase.remediation`
- `plan.execution`
- `plan.verification`
- `plan.doc_alignment`

In other words:

- the workstream explains why the program exists
- the profiles explain how it is decomposed

## Key Invariants

- Post-v1 work must not silently borrow stale proof from pre-change runtime behavior.
- Already-proven baseline scope should remain visible instead of being erased.
- Major change programs must be named explicitly rather than hidden under generic maintenance language.
- Migration and sunset work must be treated as first-class product-lifecycle outcomes, not as accidental leftovers.
- Audit and assurance work must produce evidence and closure language, not only remediation code.
