# E2E Task Profile Catalog

## Purpose

Document the concrete future `task.e2e.*` profile catalog implied by the repository's real-E2E flow inventory and suite matrix.

This note exists so real runtime journeys can be decomposed into explicit E2E task nodes instead of a single generic `task.e2e` bucket.

## Why The Current Base Profile Is Not Enough

The starter profile bundle currently includes one generic `task.e2e` profile:

- it defines the right leaf execution chain
- it defines the right proof posture
- it does not identify which runtime journey or suite the task is actually proving

That is not enough once E2E work becomes first-class decomposed work.

The system needs concrete E2E profile identities so:

- a plan can assign one E2E journey as its own child task
- prompts can say exactly which runtime surface is under proof
- completion predicates can be specific to the target journey
- operators can inspect which real-proof backlog item a task actually owns

## Proposed Catalog Shape

Keep `task.e2e` as the base profile.

Add concrete overlays in two groups:

1. canonical flow E2E profiles
2. specialized suite-family E2E profiles

Recommended directory:

- `e2e_task_profiles/canonical_flow_profiles.md`
- `e2e_task_profiles/specialized_suite_profiles.md`

## Canonical Flow Profiles

One concrete `task.e2e.*` profile should exist for each active canonical runtime flow:

- `task.e2e.flow_01_create_top_level_node`
- `task.e2e.flow_02_compile_or_recompile_workflow`
- `task.e2e.flow_03_materialize_and_schedule_children`
- `task.e2e.flow_04_manual_tree_edit_and_reconcile`
- `task.e2e.flow_05_admit_and_execute_node_run`
- `task.e2e.flow_06_inspect_state_and_blockers`
- `task.e2e.flow_07_pause_resume_and_recover`
- `task.e2e.flow_08_handle_failure_and_escalate`
- `task.e2e.flow_09_run_quality_gates`
- `task.e2e.flow_10_regenerate_and_rectify`
- `task.e2e.flow_11_finalize_and_merge`
- `task.e2e.flow_12_query_provenance_and_docs`
- `task.e2e.flow_13_human_gate_and_intervention`

These profiles should exist because the repo already treats those flows as the canonical runtime journeys that require real proof.

## Specialized Suite Profiles

Additional concrete `task.e2e.*` profiles should exist where one specialized suite spans multiple features or a broader runtime boundary:

- `task.e2e.compile_variants_and_diagnostics`
- `task.e2e.dependency_and_child_materialization`
- `task.e2e.child_merge_and_reconciliation`
- `task.e2e.session_binding_and_resume`
- `task.e2e.tmux_session_runtime`
- `task.e2e.provider_recovery`
- `task.e2e.failure_escalation_and_intervention`
- `task.e2e.quality_chain`
- `task.e2e.prompt_and_summary_history`
- `task.e2e.provenance_and_docs`
- `task.e2e.audit_and_reproducibility`
- `task.e2e.branch_identity_and_history`
- `task.e2e.merge_conflict_and_resolution`
- `task.e2e.live_git_merge_and_finalize`
- `task.e2e.regeneration_and_upstream_rectification`
- `task.e2e.rebuild_cutover_coordination`
- `task.e2e.incremental_parent_merge`
- `task.e2e.full_epic_tree_runtime`

## Shared Inheritance Contract

All concrete E2E task profiles should inherit the base `task.e2e` compiled chain:

1. `load_task_context`
2. `prepare_runtime_environment`
3. `run_real_e2e_commands`
4. `capture_real_runtime_evidence`
5. `register_outputs_and_summary`
6. `validate_completion_predicates`
7. `complete_or_block`

They should override only what is profile-specific:

- target journey or suite id
- canonical command family
- environment prerequisites
- evidence expectations
- special completion predicates

## Decomposition Guidance

Recommended parent usage:

- `plan.verification` should commonly spawn one or more `task.e2e.flow_*` tasks when the goal is to prove a specific canonical journey
- `phase.e2e` should commonly spawn one or more specialized `task.e2e.*` suite profiles when grouped runtime proof is required
- `epic.feature` should reserve E2E work for dedicated descendants rather than parent-owned implementation or parent-owned ad hoc test execution

## Future YAML Adoption Direction

When this moves from notes into real runtime assets, the likely order should be:

1. keep `task.e2e` as the real base profile
2. add concrete overlay assets for the canonical flow profiles first
3. add specialized suite profiles second
4. wire parent layouts and child-role mappings to those concrete ids

## Main Constraint

These concrete E2E profiles should remain evidence-specific, not implementation-owning.

They exist to prove runtime behavior honestly.

They should not become a backdoor for parent tiers or E2E tasks to absorb unrelated implementation work.
