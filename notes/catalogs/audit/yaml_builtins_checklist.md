# YAML Built-Ins Checklist

## Purpose

This document is a consolidated checklist of the built-in YAML definitions implied by the current notes, journeys, flows, simulations, and pseudocode.

It is narrower and more execution-focused than:

- `notes/catalogs/inventory/yaml_inventory_v2.md`
- `notes/catalogs/inventory/default_yaml_library_plan.md`

Those notes describe the YAML surface conceptually.
This note answers a more implementation-facing question:

- what built-in YAML definitions do we actually need to author to make the default system coherent end to end

---

## Review Scope

This checklist was synthesized from:

- `notes/scenarios/journeys/common_user_journeys_analysis.md`
- `flows/README.md` and the flow files
- `simulations/README.md` and the simulation files
- `notes/pseudocode/README.md`
- `notes/pseudocode/modules/*.md`
- `notes/catalogs/inventory/default_yaml_library_plan.md`
- `notes/catalogs/inventory/yaml_inventory_v2.md`
- `notes/specs/yaml/yaml_schemas_spec_v2.md`

This is not a proof that every listed file must exist as a separate physical YAML file.
Some items may end up inlined, generated, or folded into another family.
But if an item is checked here, the behavior still needs an explicit YAML home or a deliberate documented exception.

---

## Summary Findings

### 1. The core default ladder is now stable enough to enumerate

Across the default epic/phase/plan/task simulations, the same task sequence appears repeatedly:

- `research_context`
- `generate_child_layout`
- `review_child_layout`
- `spawn_children`
- `wait_for_children`
- `reconcile_children`
- `validate_node`
- `review_node`
- `test_node`
- `update_provenance`
- `build_node_docs`
- `finalize_node`

Leaf `task` nodes now also clearly require:

- `execute_node`

### 2. The subtask surface is also stable enough to enumerate

The pseudocode and simulations repeatedly exercise:

- prompt execution
- command execution
- waiting
- child node/session spawning
- validation/review/testing
- rectification/merge helpers
- summaries, docs, provenance, and recovery helpers

### 3. The remaining gaps are mostly about placement, not discovery

The main unresolved issues are:

- where `respond_to_child_failure` is inserted relative to `wait_for_children`
- whether some waiting/recovery/finalization behaviors should remain loop-owned rather than task-owned
- whether every listed subtask needs a standalone YAML file versus canonical inline templates

---

## Checklist Conventions

- `[x]` means the definition is clearly required by the current reviewed docs
- `[ ]` means the definition is not yet justified strongly enough as a built-in default, but is a plausible extension

Interpretation rule:

- this checklist is an audit and authoring-scope surface for built-in YAML coverage, not the canonical implementation or proving surface
- `[x]` here means the built-in definition has an explicit required home in the note set; it does not by itself mean the family is implemented, verified, flow-complete, or release-ready
- implementation and proving status live in:
  - `notes/catalogs/checklists/feature_checklist_backfill.md`
  - `notes/catalogs/checklists/verification_command_catalog.md`

## Scaffold Status

The current repository setup phase includes a placeholder packaged scaffold under:

- `src/aicoding/resources/yaml/builtin/system-yaml/`

That scaffold has now been replaced by authored built-ins for the currently implemented families. A checked item below should still be read as "must remain authored meaningfully", not merely "path exists".

---

## 1. Required Node Definitions

These are the minimum built-in node kinds directly exercised by the default journeys and simulations.

- [x] `nodes/epic.yaml`
- [x] `nodes/phase.yaml`
- [x] `nodes/plan.yaml`
- [x] `nodes/task.yaml`

### Optional or still-open node definitions

- [ ] `nodes/root.yaml`
- [ ] `nodes/research_only.yaml`
- [ ] `nodes/review_only.yaml`

---

## 2. Required Task Definitions

These task definitions are directly implied by the default flows, simulations, and pseudocode.

### Core planning and decomposition

- [x] `tasks/research_context.yaml`
- [x] `tasks/generate_child_layout.yaml`
- [x] `tasks/review_child_layout.yaml`

### Core execution and orchestration

- [x] `tasks/execute_node.yaml`
- [x] `tasks/spawn_children.yaml`
- [x] `tasks/wait_for_children.yaml`
- [x] `tasks/reconcile_children.yaml`

### Core quality gates and completion

- [x] `tasks/validate_node.yaml`
- [x] `tasks/review_node.yaml`
- [x] `tasks/test_node.yaml`
- [x] `tasks/update_provenance.yaml`
- [x] `tasks/build_node_docs.yaml`
- [x] `tasks/finalize_node.yaml`

### Failure, pause, and parent-decision path

- [x] `tasks/pause_for_user.yaml`
- [x] `tasks/respond_to_child_failure.yaml`
- [x] `tasks/summarize_failure.yaml`

### Rectification and rebuild

- [x] `tasks/rectify_node_from_seed.yaml`
- [x] `tasks/rectify_upstream.yaml`
- [x] `tasks/reconcile_merge_conflict.yaml`

### Runtime recovery and operator-control tasks if YAML-owned

- [x] `tasks/recover_interrupted_run.yaml`
- [x] `tasks/nudge_idle_session.yaml`

### Strong candidates but still placement-open

- [x] `tasks/wait_for_dependencies.yaml`
- [x] `tasks/revise_child_layout.yaml`

These are justified by the notes, but the exact default insertion points are still less frozen than the list above.

---

## 3. Required Subtask Definitions

These are the reusable subtask types most clearly exercised by the pseudocode dispatcher, simulations, and task plans.

### Core execution

- [x] `subtasks/build_context.yaml`
- [x] `subtasks/run_prompt.yaml`
- [x] `subtasks/run_command.yaml`
- [x] `subtasks/validate.yaml`
- [x] `subtasks/review.yaml`
- [x] `subtasks/run_tests.yaml`

### Coordination and waiting

- [x] `subtasks/wait_for_children.yaml`
- [x] `subtasks/wait_for_sibling_dependency.yaml`
- [x] `subtasks/spawn_child_node.yaml`
- [x] `subtasks/spawn_child_session.yaml`
- [x] `subtasks/collect_child_summaries.yaml`

### Rectification and git support

- [x] `subtasks/reset_to_seed.yaml`
- [x] `subtasks/merge_children.yaml`
- [x] `subtasks/record_merge_metadata.yaml`
- [x] `subtasks/finalize_git_state.yaml`

### Output, docs, provenance, and summaries

- [x] `subtasks/write_summary.yaml`
- [x] `subtasks/build_docs.yaml`
- [x] `subtasks/update_provenance.yaml`
- [x] `subtasks/pause_on_user_flag.yaml`
- [x] `subtasks/finalize_node.yaml`

### Recovery helpers

- [x] `subtasks/rebind_session.yaml`
- [x] `subtasks/nudge_session.yaml`
- [x] `subtasks/recover_cursor.yaml`

Packaging note:

- the current implementation now treats these standalone subtask YAML files as the canonical authored built-in subtask catalog even though the live compiler still materializes inline subtask payloads from task definitions
- the enforced standard for this slice is therefore: every built-in subtask file must remain schema-valid, prompt-bound where required, non-destructive by default, and synthetically compileable/startable against the current runtime

---

## 4. Required Layout Definitions

These layout templates are the built-in decomposition defaults repeatedly assumed by the journeys and simulations.

- [x] `layouts/epic_to_phases.yaml`
- [x] `layouts/phase_to_plans.yaml`
- [x] `layouts/plan_to_tasks.yaml`

### Optional or project-shaping layouts

- [x] `layouts/manual_top_node.yaml`
- [x] `layouts/research_only_breakdown.yaml`
- [x] `layouts/replan_after_failure.yaml`

---

## 5. Required Validation Definitions

Packaging note:

- the current implementation now validates these built-in validation, review, testing, and docs families together as one quality-library contract
- a checked item here therefore means more than "file exists": the built-in file must remain schema-valid, prompt-bound where required, task-bound where required, and compatible with the canonical built-in gate ordering enforced before workflow compilation

These are the validation checks most directly exercised by the simulations and task contracts.

- [x] `validations/file_exists.yaml`
- [x] `validations/file_updated.yaml`
- [x] `validations/command_exit_code.yaml`
- [x] `validations/json_schema.yaml`
- [x] `validations/yaml_schema.yaml`
- [x] `validations/ai_json_status.yaml`
- [x] `validations/file_contains.yaml`
- [x] `validations/git_clean.yaml`
- [x] `validations/git_dirty.yaml`

### Strongly recommended support validations

- [x] `validations/summary_written.yaml`
- [x] `validations/docs_built.yaml`
- [x] `validations/provenance_updated.yaml`
- [x] `validations/session_bound.yaml`
- [x] `validations/dependencies_satisfied.yaml`

---

## 6. Required Review Definitions

These are the review-stage definitions clearly implied by the quality-gate notes and default flows.

- [x] `reviews/layout_against_prompt.yaml`
- [x] `reviews/node_against_requirements.yaml`
- [x] `reviews/reconcile_output.yaml`
- [x] `reviews/pre_finalize.yaml`

### Strongly recommended review definitions

- [x] `reviews/merge_result_review.yaml`
- [x] `reviews/docs_quality_review.yaml`
- [x] `reviews/policy_compliance_review.yaml`

---

## 7. Required Testing Definitions

- [x] `testing/default_unit_test_gate.yaml`
- [x] `testing/default_integration_test_gate.yaml`
- [x] `testing/default_smoke_test_gate.yaml`

### Strongly recommended testing support

- [x] `testing/test_retry_policy.yaml`
- [x] `testing/test_failure_summary.yaml`
- [x] `testing/project_command_suite.yaml`

---

## 8. Required Documentation Definitions

- [x] `docs/build_local_node_docs.yaml`
- [x] `docs/build_merged_tree_docs.yaml`
- [x] `docs/default_doc_views.yaml`

### Strongly recommended documentation support

- [x] `docs/static_analysis_scope.yaml`
- [x] `docs/rationale_merge_rules.yaml`
- [x] `docs/entity_history_view.yaml`

---

## 9. Required Rectification Definitions

- [x] `rectification/rectify_node_from_seed.yaml`
- [x] `rectification/rectify_upstream.yaml`
- [x] `rectification/merge_current_children.yaml`
- [x] `rectification/reconcile_conflict.yaml`

### Strongly recommended rectification support

- [x] `rectification/regenerate_subtree.yaml`
- [x] `rectification/rebuild_review.yaml`
- [x] `rectification/rebuild_docs.yaml`

---

## 10. Required Runtime Policy Definitions

These are needed if the default runtime policy is YAML-owned rather than entirely code-owned.

Packaging note:

- the current implementation now validates the built-in runtime definitions, runtime policies, hooks, environments, prompt references, and required prompt assets together as one operational-library contract
- a checked item in these operational sections should therefore be read as "schema-valid and reference-valid within the shipped control plane", not merely "file exists"

- [x] `runtime/session_defaults.yaml`
- [x] `runtime/heartbeat_policy.yaml`
- [x] `runtime/idle_nudge_policy.yaml`
- [x] `runtime/child_session_policy.yaml`
- [x] `runtime/recovery_policy.yaml`

### Possible collapsed form

- [x] `runtime/default_runtime_policy.yaml`

This is an either/or packaging choice, not an additional semantic requirement.

---

## 11. Required Prompt Definitions

These are now tracked explicitly because the reviewed docs clearly require authored prompts for execution, correction, recovery, and decomposition.

- [x] `prompts/layouts/generate_phase_layout.md`
- [x] `prompts/layouts/generate_plan_layout.md`
- [x] `prompts/layouts/generate_task_layout.md`
- [x] `prompts/execution/implement_leaf_task.md`
- [x] `prompts/execution/reconcile_parent_after_merge.md`
- [x] `prompts/review/review_layout_against_request.md`
- [x] `prompts/review/review_node_output.md`
- [x] `prompts/testing/interpret_test_results.md`
- [x] `prompts/docs/build_node_docs.md`
- [x] `prompts/runtime/session_bootstrap.md`
- [x] `prompts/runtime/missed_step.md`
- [x] `prompts/runtime/command_failed.md`
- [x] `prompts/runtime/missing_required_output.md`
- [x] `prompts/runtime/idle_nudge.md`
- [x] `prompts/runtime/pause_for_user.md`
- [x] `prompts/runtime/resume_existing_session.md`
- [x] `prompts/runtime/replacement_session_bootstrap.md`
- [x] `prompts/runtime/delegated_child_session.md`
- [x] `prompts/runtime/parent_pause_for_user.md`
- [x] `prompts/runtime/parent_local_replan.md`

---

## 12. Required Hook Definitions

The reviewed docs still leave exact hook composition somewhat open, but these defaults are consistently implied enough to keep on the checklist.

- [x] `hooks/before_validation_default.yaml`
- [x] `hooks/after_validation_default.yaml`
- [x] `hooks/before_review_default.yaml`
- [x] `hooks/after_review_default.yaml`
- [x] `hooks/before_testing_default.yaml`
- [x] `hooks/after_testing_default.yaml`
- [x] `hooks/before_merge_children_default.yaml`
- [x] `hooks/after_merge_children_default.yaml`
- [x] `hooks/on_merge_conflict_default.yaml`
- [x] `hooks/before_upstream_rectify_default.yaml`
- [x] `hooks/after_upstream_rectify_default.yaml`
- [x] `hooks/on_node_created_default.yaml`
- [x] `hooks/before_node_complete_default.yaml`
- [x] `hooks/after_node_complete_default.yaml`
- [x] `hooks/after_subtask_default_summary.yaml`
- [x] `hooks/after_node_complete_build_docs.yaml`
- [x] `hooks/after_node_complete_update_provenance.yaml`

---

## 13. Global Policy Definitions

- [x] `policies/default_node_policy.yaml`
- [x] `policies/default_failure_policy.yaml`
- [x] `policies/default_merge_policy.yaml`
- [x] `policies/default_review_policy.yaml`
- [x] `policies/default_testing_policy.yaml`

---

## 14. High-Priority Definition Gaps Still Exposed By The Review

These are the main places where the docs still leave YAML authoring ambiguity.

### Gap 1. `respond_to_child_failure` insertion point

The docs clearly require a parent-facing failure decision path, but they do not yet freeze exactly where `tasks/respond_to_child_failure.yaml` sits relative to:

- `wait_for_children`
- `reconcile_children`
- parent-local retry/replan transitions

### Gap 2. Waiting semantics versus pause semantics

The pseudocode still leaves some ambiguity around whether waiting behavior is represented as:

- dedicated waiting subtasks
- loop-owned waiting states
- pause-like outcomes with different semantics

This especially affects:

- `subtasks/wait_for_children.yaml`
- `subtasks/wait_for_sibling_dependency.yaml`
- `tasks/wait_for_dependencies.yaml`

### Gap 3. Finalization ownership

The docs still leave open whether `finalize_node` should always be:

- a normal task/subtask in YAML
- a loop-owned terminal behavior
- or a hybrid where the YAML stage exists but the runtime owns final acceptance

### Gap 4. Recovery/nudge as tasks versus runtime-only helpers

The system clearly needs recovery/nudge behavior, but the exact packaging is still open:

- `tasks/recover_interrupted_run.yaml`
- `tasks/nudge_idle_session.yaml`
- `subtasks/rebind_session.yaml`
- `subtasks/nudge_session.yaml`
- `subtasks/recover_cursor.yaml`

### Gap 5. Standalone subtask documents versus canonical inline templates

The reviewed docs consistently require the subtask behaviors, but not yet the final packaging choice:

- physical `subtasks/*.yaml`
- inlined task-local definitions
- compile-time expansion from templates

---

## 15. Minimum Authoring Order

If the goal is to make the default built-in YAML library implementable as fast as possible, author the files in roughly this order.

### Phase 1: unblock default execution

- [x] `nodes/epic.yaml`
- [x] `nodes/phase.yaml`
- [x] `nodes/plan.yaml`
- [x] `nodes/task.yaml`
- [x] `tasks/research_context.yaml`
- [x] `tasks/generate_child_layout.yaml`
- [x] `tasks/review_child_layout.yaml`
- [x] `tasks/execute_node.yaml`
- [x] `tasks/spawn_children.yaml`
- [x] `tasks/wait_for_children.yaml`
- [x] `tasks/reconcile_children.yaml`
- [x] `tasks/validate_node.yaml`
- [x] `tasks/review_node.yaml`
- [x] `tasks/test_node.yaml`
- [x] `tasks/update_provenance.yaml`
- [x] `tasks/build_node_docs.yaml`
- [x] `tasks/finalize_node.yaml`
- [x] core `subtasks/*.yaml` used by those tasks

### Phase 2: unblock failure, pause, and recovery

- [x] `tasks/pause_for_user.yaml`
- [x] `tasks/summarize_failure.yaml`
- [x] `tasks/respond_to_child_failure.yaml`
- [x] recovery/nudge task and subtask definitions
- [x] pause/recovery prompt definitions

### Phase 3: unblock rectification and upstream rebuild

- [x] rectification definitions
- [x] reconcile/merge subtasks
- [x] merge-conflict handling definitions

### Phase 4: complete quality/support surface

- [x] review definitions
- [x] testing definitions
- [x] docs definitions
- [x] prompts
- [x] hooks
- [x] runtime and global policies

---

## Bottom Line

If the question is only "what built-in YAML node/task/subtask definitions do we need," the minimum coherent default answer from the reviewed docs is:

- 4 required node definitions
- 20 required or near-required task definitions
- 22 required subtask definitions

If the question is "what YAML library do we need to make the whole default system coherent," the answer is larger:

- nodes
- tasks
- subtasks
- layouts
- validations
- reviews
- testing
- docs
- rectification
- runtime policies
- prompts
- hooks
- global policies

That larger list is what the current journeys, simulations, pseudocode, and supporting notes actually imply.
