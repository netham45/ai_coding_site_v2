# Phase F25: Failure Escalation And Parent Decision Logic

## Goal

Handle child and subtask failures compositionally through durable parent decisions.

## Rationale

- Rationale: Failures in child work need structured parent-level decisions so retries, replans, pauses, and escalation are consistent across the tree.
- Reason for existence: This phase exists to turn failure handling into durable orchestration logic rather than scattered one-off reactions to errors.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/11_F08_dependency_graph_and_admission_control.md`: F08 shapes some of the failure classes and blocked-parent states.
- `plan/features/13_F09_node_run_orchestration.md`: F09 invokes failure handling when execution cannot advance normally.
- `plan/features/29_F24_user_gating_and_pause_flags.md`: F24 provides the pause and user-deferment states failure handling can enter.
- `plan/features/23_F18_child_merge_and_reconcile_pipeline.md`: F18 is one major source of parent-visible child failure outcomes.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/catalogs/inventory/major_feature_inventory.md`
- `notes/catalogs/traceability/spec_traceability_matrix.md`
- `notes/contracts/parent_child/parent_failure_decision_spec.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/prompts/prompt_library_plan.md`
- `notes/pseudocode/modules/handle_child_failure_at_parent.md`
- `notes/pseudocode/modules/handle_subtask_failure.md`

## Scope

- Database: failure classes, summaries, parent counters, parent decisions.
- CLI: failure history and parent-decision inspection.
- Daemon: child-failure classification plus retry/replan/pause behavior.
- YAML: declarative retry/pause thresholds only; decisions remain code-owned.
- Prompts: parent pause-for-user and parent-local replan prompts.
- Tests: exhaustive coverage for every failure class and parent-decision outcome.
- Performance: benchmark repeated failure-handling and counter-update paths.
- Notes: update parent-failure notes if the taxonomy expands.
