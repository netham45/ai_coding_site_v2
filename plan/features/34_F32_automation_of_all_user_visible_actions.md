# Phase F32: Automation Of All User-Visible Actions

## Goal

Ensure every user-visible operation is scriptable, durable, and testable.

## Rationale

- Rationale: A spec-driven orchestration system cannot rely on invisible manual steps for actions the user thinks the product supports.
- Reason for existence: This phase exists to ensure every visible operation has a real command/runtime path with durable auditability and test coverage.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/14_F10_ai_facing_cli_command_loop.md`: F10 covers automatable AI-facing actions.
- `plan/features/15_F11_operator_cli_and_introspection.md`: F11 covers automatable operator-facing actions.
- `plan/features/01_F31_daemon_authority_and_durable_orchestration_record.md`: F31 ensures automatable actions still route through safe authority boundaries.
- `plan/features/37_F10_top_level_workflow_creation_commands.md`: F10-S1 is one concrete user-visible command family.
- `plan/features/48_F11_operator_structure_and_state_commands.md`: F11-S1 is another command family that should be covered in the automation matrix.
- `plan/features/49_F11_operator_history_and_artifact_commands.md`: F11-S2 rounds out the historical and artifact inspection actions.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/catalogs/inventory/major_feature_inventory.md`
- `notes/catalogs/traceability/spec_traceability_matrix.md`
- `notes/catalogs/traceability/action_automation_matrix.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/planning/implementation/implementation_slicing_plan.md`
- `notes/catalogs/audit/auditability_checklist.md`

## Scope

- Database: audit trail for every mutating action.
- CLI: close remaining gaps between conceptual actions and real command surfaces.
- Daemon: route every supported action through safe orchestration logic.
- YAML: optional action metadata only if truly needed.
- Prompts: ensure prompt-linked actions are automatable and inspectable.
- Tests: exhaustive coverage for every action in the automation matrix.
- Performance: benchmark high-frequency action paths.
- Notes: update the action automation matrix whenever actions are added or changed.
