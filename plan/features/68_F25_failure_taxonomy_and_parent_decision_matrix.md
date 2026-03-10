# Phase F25-S1: Failure Taxonomy And Parent Decision Matrix

## Goal

Expand child-failure handling into a richer, explicit failure taxonomy with a broader parent decision matrix.

## Rationale

- Rationale: Current failure escalation already persists child failure counters and decision history, but it still exercises only a narrow subset of the possible failure classes and parent responses.
- Reason for existence: This phase exists to make failure handling comprehensive, inspectable, and predictable instead of depending on a small number of heuristics and one primary tested branch.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/30_F25_failure_escalation_and_parent_decision_logic.md`: F25 established the current parent-decision loop.
- `plan/features/29_F24_user_gating_and_pause_flags.md`: F24 may be required when failures escalate to explicit user intervention.
- `plan/features/24_F19_regeneration_and_upstream_rectification.md`: F19 is one downstream destination for regenerate-child decisions.
- `plan/features/23_F18_child_merge_and_reconcile_pipeline.md`: F18 can surface merge- or reconcile-derived child failures that the parent must classify.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/contracts/parent_child/parent_failure_decision_spec.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/database/database_schema_spec_v2.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/planning/implementation/per_flow_gap_remediation_plan.md`

## Scope

- Database: persist richer failure class metadata, decision reasoning, repeated-failure thresholds, and any additional parent-decision audit state required.
- CLI: expose broader failure classification, parent-decision inspection, and override surfaces.
- Daemon: implement a fuller failure taxonomy and route each class through explicit parent decision rules.
- YAML: keep failure classification and parent-decision authority in code; YAML may contribute policy thresholds only where appropriate.
- Prompts: ensure parent-failure and escalation prompts align with the expanded decision matrix.
- Tests: exhaustively cover retry-child, regenerate-child, replan-parent, pause-for-user, repeated-failure thresholds, and override-versus-auto decisions.
- Performance: benchmark child-failure inspection and parent-decision history reads under repeated failure scenarios.
- Notes: update failure taxonomy, escalation, and intervention notes to match the final decision matrix.
