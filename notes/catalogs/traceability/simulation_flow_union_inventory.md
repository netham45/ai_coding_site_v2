# Simulation And Flow Union Inventory

## Purpose

This note compares the older simulation sets in:

- `simulations/`
- `simulations2/`
- `simulations/db/`

against the current explicit flow docs in:

- `flows/`

The goal is to build one deduplicated list of runtime flows implied by both sets and identify:

- which current `flows/` are clearly represented by the simulations
- which current `flows/` are not directly represented by the simulations
- which behaviors are proposed by the simulations but still do not have a dedicated `flows/` document

Interpretation rule:

- simulations and simulation-derived YAML flow assets are planning and bounded-proof artifacts
- they do not count as real-E2E completion by themselves
- real-E2E target assignment and completion state live in:
  - `plan/e2e_tests/06_e2e_feature_matrix.md`
  - `notes/catalogs/audit/flow_coverage_checklist.md`
  - `notes/catalogs/checklists/feature_checklist_backfill.md`

## Deduplicated union

### Shared with an existing `flows/` doc

1. Create and compile a new top-level node
   - Existing flow: `flows/01_create_top_level_node_flow.md`
   - Simulation sources:
     - `simulations/01_flow_a_create_and_compile_top_level_node.md`
     - `simulations/db/01_top_level_node_creation.md`

2. Compile or recompile workflow state, including hook/policy expansion and compile-failure persistence
   - Existing flow: `flows/02_compile_or_recompile_workflow_flow.md`
   - Simulation sources:
     - `simulations/01_flow_a_create_and_compile_top_level_node.md`
     - `simulations/12_project_bootstrap_flow.md`
     - `simulations/13_compile_failure_flow.md`
     - `simulations/14_hook_expansion_flow.md`
     - `simulations2/05_compile_failure_and_reattempt_flow.md`
     - `simulations/db/07_compile_failure_pause_and_events.md`

3. Admit a ready node and execute the command loop
   - Existing flow: `flows/05_admit_and_execute_node_run_flow.md`
   - Simulation sources:
     - `simulations/02_flow_b_admit_and_run_ready_node.md`
     - `simulations/03_flow_c_execute_one_compiled_subtask.md`
     - `simulations/db/02_run_admission_and_subtask_execution.md`

4. Materialize children and classify scheduling/blocking state
   - Existing flow: `flows/03_materialize_and_schedule_children_flow.md`
   - Simulation sources:
     - `simulations/04_flow_d_spawn_and_reconcile_children.md`
     - `simulations/15_invalid_dependency_graph_flow.md`
     - `simulations2/01_dependency_blocked_sibling_flow.md`
     - `simulations2/02_invalid_dependency_graph_flow.md`
     - `simulations/db/03_child_materialization_and_scheduling.md`

5. Manual-versus-layout tree reconciliation
   - Existing flow: `flows/04_manual_tree_edit_and_reconcile_flow.md`
   - Simulation sources:
     - `simulations/18_manual_vs_auto_tree_reconciliation_flow.md`

6. Inspect state, blockers, and current execution state
   - Existing flow: `flows/06_inspect_state_and_blockers_flow.md`
   - Simulation sources:
     - `simulations2/01_dependency_blocked_sibling_flow.md`
     - `simulations2/03_parent_child_failure_decision_flow.md`
     - `simulations2/04_child_session_round_trip_flow.md`
     - `simulations2/06_resume_after_interruption_flow.md`
     - `simulations2/07_rectification_stateful_flow.md`
   - Note:
     - The simulations use inspection heavily, but usually as embedded read steps rather than as a standalone “inspection-first” scenario.

7. Pause, resume, and recover interrupted work
   - Existing flow: `flows/07_pause_resume_and_recover_flow.md`
   - Simulation sources:
     - `simulations/05_flow_e_pause_or_fail.md`
     - `simulations/06_flow_f_recover_interrupted_work.md`
     - `simulations/17_child_session_mergeback_flow.md`
     - `simulations2/04_child_session_round_trip_flow.md`
     - `simulations2/06_resume_after_interruption_flow.md`
     - `simulations/db/05_session_recovery_and_child_sessions.md`

8. Handle failure, escalation, and impossible waits
   - Existing flow: `flows/08_handle_failure_and_escalate_flow.md`
   - Simulation sources:
     - `simulations/05_flow_e_pause_or_fail.md`
     - `simulations/13_compile_failure_flow.md`
     - `simulations/15_invalid_dependency_graph_flow.md`
     - `simulations/16_parent_child_failure_decision_flow.md`
     - `simulations2/02_invalid_dependency_graph_flow.md`
     - `simulations2/03_parent_child_failure_decision_flow.md`
     - `simulations2/05_compile_failure_and_reattempt_flow.md`
     - `simulations/db/07_compile_failure_pause_and_events.md`

9. Run quality gates and persist their results
   - Existing flow: `flows/09_run_quality_gates_flow.md`
   - Simulation sources:
     - `simulations/05_flow_e_pause_or_fail.md`
     - `simulations/08_epic_default_flow.md`
     - `simulations/09_phase_default_flow.md`
     - `simulations/10_plan_default_flow.md`
     - `simulations/11_task_default_flow.md`
     - `simulations/db/04_quality_gate_and_summary_persistence.md`

10. Regenerate, rectify, rebuild, and rematerialize
    - Existing flow: `flows/10_regenerate_and_rectify_flow.md`
    - Simulation sources:
      - `simulations/07_flow_g_rectify_after_change.md`
      - `simulations2/07_rectification_stateful_flow.md`
      - `simulations/db/06_rectification_merge_and_cutover.md`

11. Finalize, merge, and cut over authoritative lineage
    - Existing flow: `flows/11_finalize_and_merge_flow.md`
    - Simulation sources:
      - `simulations/04_flow_d_spawn_and_reconcile_children.md`
      - `simulations/07_flow_g_rectify_after_change.md`
      - `simulations/19_cutover_flow.md`
      - `simulations2/07_rectification_stateful_flow.md`
      - `simulations/db/06_rectification_merge_and_cutover.md`

12. Human gate and intervention handling
    - Existing flow: `flows/13_human_gate_and_intervention_flow.md`
    - Simulation sources:
      - `simulations/05_flow_e_pause_or_fail.md`
      - `simulations/18_manual_vs_auto_tree_reconciliation_flow.md`
      - `simulations/19_cutover_flow.md`
    - Note:
      - The simulations show intervention points, but not a fully unified intervention catalog surface.

### Current `flows/` doc not directly represented by the simulations

13. Query provenance, rationale, entity history, and docs as an operator read flow
   - Existing flow: `flows/12_query_provenance_and_docs_flow.md`
   - Closest simulation material:
     - `simulations/08_epic_default_flow.md`
     - `simulations/09_phase_default_flow.md`
     - `simulations/10_plan_default_flow.md`
     - `simulations/11_task_default_flow.md`
     - `simulations/db/04_quality_gate_and_summary_persistence.md`
   - Why this is not a direct match:
     - The simulations exercise provenance refresh and docs generation as pipeline stages.
     - They do not provide a dedicated operator scenario for `rationale show`, `entity show`, `entity history`, `entity relations`, or docs query/readback as the main purpose of the flow.

### Proposed by the simulations and now represented by dedicated YAML flow assets

14. Project bootstrap and local YAML onboarding
   - Simulation sources:
     - `simulations/12_project_bootstrap_flow.md`
   - Scope:
     - create local `.ai/` structure
     - author project policy/testing/docs/override YAML
     - validate project-local YAML
     - perform the first compile in a new project
   - YAML flow asset:
     - `flows/14_project_bootstrap_and_yaml_onboarding_flow.yaml`

15. Default node-kind workflow blueprints
   - Simulation sources:
     - `simulations/08_epic_default_flow.md`
     - `simulations/09_phase_default_flow.md`
     - `simulations/10_plan_default_flow.md`
     - `simulations/11_task_default_flow.md`
   - Scope:
     - explicit default stage ladders for each built-in node kind
   - Note:
     - These are workflow blueprints rather than operational flows, but they are still represented as distinct simulations.
   - YAML flow assets:
     - `flows/15_epic_default_workflow_blueprint_flow.yaml`
     - `flows/16_phase_default_workflow_blueprint_flow.yaml`
     - `flows/17_plan_default_workflow_blueprint_flow.yaml`
     - `flows/18_task_default_workflow_blueprint_flow.yaml`

16. Hook expansion as a standalone compile-stage walkthrough
   - Simulation sources:
     - `simulations/14_hook_expansion_flow.md`
   - Scope:
     - collect hooks
     - order hooks
     - insert hooks
     - validate the expanded workflow
   - YAML flow asset:
     - `flows/19_hook_expansion_compile_stage_flow.yaml`

17. Compile failure and reattempt as a first-class operator loop
   - Simulation sources:
     - `simulations/13_compile_failure_flow.md`
     - `simulations2/05_compile_failure_and_reattempt_flow.md`
     - `simulations/db/07_compile_failure_pause_and_events.md`
   - Scope:
     - fail compilation
     - inspect durable compile failure
     - fix the source or override
     - reattempt compile successfully
   - YAML flow asset:
     - `flows/20_compile_failure_and_reattempt_flow.yaml`

18. Child-session round-trip and merge-back as a standalone bounded-work loop
   - Simulation sources:
     - `simulations/17_child_session_mergeback_flow.md`
     - `simulations2/04_child_session_round_trip_flow.md`
     - `simulations/db/05_session_recovery_and_child_sessions.md`
   - YAML flow asset:
     - `flows/21_child_session_round_trip_and_mergeback_flow.yaml`

19. Dependency-blocked sibling wait as a standalone scheduling flow
   - Simulation sources:
     - `simulations2/01_dependency_blocked_sibling_flow.md`
   - Scope:
     - one child runs
     - one sibling stays blocked on the dependency
     - runtime surfaces explain the wait
   - YAML flow asset:
     - `flows/22_dependency_blocked_sibling_wait_flow.yaml`

## Bottom line

- The simulations do map to almost all of the current `flows/` set.
- The clearest current `flows/` doc that the simulations do **not** directly represent is:
  - `flows/12_query_provenance_and_docs_flow.md`
- The simulation-proposed gaps that were previously missing now have dedicated executable YAML flow assets under `flows/14` through `flows/22`.
