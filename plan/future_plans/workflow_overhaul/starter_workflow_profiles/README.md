# Starter Workflow Profiles

These YAML files are draft built-in examples for the future `workflow_profile_definition` family.

They are examples for the workflow-overhaul bundle only.

They are not active runtime assets.

## Contents

- `epic.planning.yaml`
- `epic.feature.yaml`
- `epic.review.yaml`
- `epic.documentation.yaml`
- `phase.discovery.yaml`
- `phase.implementation.yaml`
- `phase.documentation.yaml`
- `phase.e2e.yaml`
- `phase.review.yaml`
- `phase.remediation.yaml`
- `plan.authoring.yaml`
- `plan.execution.yaml`
- `plan.verification.yaml`
- `task.implementation.yaml`
- `task.review.yaml`
- `task.verification.yaml`
- `task.docs.yaml`
- `task.e2e.yaml`
- `task.remediation.yaml`

## Purpose

The goal of this folder is to make the workflow-overhaul idea concrete enough that later implementation can:

- compare profile shapes directly
- test naming and vocabulary consistency
- design the future schema around real examples instead of abstract bullets

These draft examples do not imply that only `epic` may be top-level.

The intended rule remains:

- top-ness is structural, not semantic
- any node kind may be top-level when its hierarchy definition allows `allow_parentless: true`
- the current draft profile catalog happens to be richer at the `epic` tier because that is where the self-hosted examples currently begin, not because lower tiers are forbidden from being parentless starts
- the intended future built-in posture is that `epic`, `phase`, `plan`, and `task` are all parentless-capable top-level kinds
- every draft profile in this folder should be startable as a top-level profile through its own `applies_to_kind` when that kind is allowed to be parentless

## Usage In This Bundle

Read these files together with:

- `2026-03-10_self_hosted_workflow_overhaul_notes.md`
- `2026-03-10_workflow_profile_definition_schema_draft.md`
- `2026-03-10_proposed_note_and_code_updates.md`

The intended future runtime interpretation for these examples is rigid:

- non-leaf profiles are decomposition-required unless a later authoritative contract says otherwise
- skipped required steps should fail with concrete blocked mutations
- higher tiers should not silently absorb child-owned implementation work
