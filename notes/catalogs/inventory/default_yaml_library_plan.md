# Default YAML Library Plan

## Purpose

This document defines the built-in YAML file library that the system should ship with by default.

The goal is to move from abstract YAML family definitions into a concrete default file set that can support the default orchestration model end to end.

This is not yet the final YAML content. It is the file-level library plan for what should exist.

Implementation staging note:

- the current implementation now ships a real authored built-in library across node, task, subtask, layout, validation, review, testing, docs, rectification, runtime, hook, and policy families
- the default node kinds intentionally still bind to the smaller runtime task set already exercised by the current compiler and orchestration slices, while the broader authored library remains packaged and validation-ready for later runtime-flow phases
- the packaged default prompt pack is now authored as a concrete implementation asset set with explicit prompt-reference inventory, render compatibility checks, and prompt-to-YAML binding tests

Related documents:

- `notes/catalogs/inventory/yaml_inventory_v2.md`
- `notes/archive/superseded/yaml_schemas_spec_revised.md`
- `notes/planning/expansion/full_spec_expansion_plan.md`
- `notes/catalogs/inventory/major_feature_inventory.md`
- `notes/specs/prompts/prompt_library_plan.md`

---

## Goals

This document should answer:

- what built-in YAML files should exist
- how those files are grouped
- which files are essential for a minimal working default system
- which files are optional or advanced
- which files are still missing conceptually

---

## Default Library Philosophy

The built-in YAML library should satisfy the following.

### 1. It should be minimal but complete

The library should be small enough to reason about, but complete enough to execute the default system end to end.

### 2. It should separate generic mechanics from semantic defaults

The library should avoid hardcoding semantic assumptions more than necessary, but it should still provide a usable semantic default ladder such as:

- epic
- phase
- plan
- task

### 3. It should prefer composable building blocks

The default file set should avoid creating one-off task files where reusable patterns are more maintainable.

### 4. It should expose quality gates explicitly

Validation, review, testing, docs, and provenance refresh should not remain implicit side effects.

### 5. It should be override-friendly

Projects should be able to replace or adjust individual files without forking the entire built-in library.

---

## Recommended Built-In Library Families

The built-in library should likely include the following top-level groups.

```text
system-yaml/
  nodes/
  tasks/
  subtasks/
  layouts/
  prompts/
  hooks/
  validations/
  reviews/
  testing/
  docs/
  rectification/
  runtime/
  policies/
```

If provenance extraction and environment isolation become YAML-managed, add:

```text
  provenance/
  environments/
```

---

## Minimum Viable Built-In YAML Library

The following built-in files appear to be required for a minimally complete default system.

## 1. Node definition files

### Required

- `nodes/epic.yaml`
- `nodes/phase.yaml`
- `nodes/plan.yaml`
- `nodes/task.yaml`

### Optional but likely useful

- `nodes/root.yaml`
- `nodes/research_only.yaml`
- `nodes/review_only.yaml`

### Purpose

These files define:

- node kind metadata
- tier
- entry task
- available tasks
- policies
- child constraints
- hook defaults

### Open question

- whether `root.yaml` is a distinct built-in node kind or whether top-level `epic` is sufficient

---

## 2. Core task definition files

These are built-in task definitions used by the semantic defaults above.

### Planning and decomposition tasks

- `tasks/research_context.yaml`
- `tasks/generate_child_layout.yaml`
- `tasks/review_child_layout.yaml`
- `tasks/revise_child_layout.yaml`

### Execution and dependency tasks

- `tasks/wait_for_dependencies.yaml`
- `tasks/execute_node.yaml`
- `tasks/spawn_children.yaml`
- `tasks/wait_for_children.yaml`
- `tasks/reconcile_children.yaml`

### Quality and completion tasks

- `tasks/validate_node.yaml`
- `tasks/review_node.yaml`
- `tasks/test_node.yaml`
- `tasks/build_node_docs.yaml`
- `tasks/update_provenance.yaml`
- `tasks/finalize_node.yaml`

### Failure and pause tasks

- `tasks/summarize_failure.yaml`
- `tasks/pause_for_user.yaml`
- `tasks/respond_to_child_failure.yaml`

### Rectification tasks

- `tasks/rectify_node_from_seed.yaml`
- `tasks/rectify_upstream.yaml`
- `tasks/reconcile_merge_conflict.yaml`

### Runtime/control tasks if modeled as tasks

- `tasks/recover_interrupted_run.yaml`
- `tasks/nudge_idle_session.yaml`

---

## 3. Reusable subtask definition files

These represent the built-in subtask building blocks or canonical named subtask definitions.

### Core execution subtasks

- `subtasks/build_context.yaml`
- `subtasks/run_prompt.yaml`
- `subtasks/run_command.yaml`
- `subtasks/validate.yaml`
- `subtasks/review.yaml`
- `subtasks/run_tests.yaml`

### Coordination subtasks

- `subtasks/wait_for_children.yaml`
- `subtasks/wait_for_sibling_dependency.yaml`
- `subtasks/spawn_child_node.yaml`
- `subtasks/spawn_child_session.yaml`
- `subtasks/collect_child_summaries.yaml`

### Git/rebuild subtasks

- `subtasks/reset_to_seed.yaml`
- `subtasks/merge_children.yaml`
- `subtasks/record_merge_metadata.yaml`
- `subtasks/finalize_git_state.yaml`

### Output/support subtasks

- `subtasks/write_summary.yaml`
- `subtasks/build_docs.yaml`
- `subtasks/update_provenance.yaml`
- `subtasks/pause_on_user_flag.yaml`
- `subtasks/finalize_node.yaml`

### Recovery subtasks

- `subtasks/rebind_session.yaml`
- `subtasks/nudge_session.yaml`
- `subtasks/recover_cursor.yaml`

### Open question

- whether these should be referenced as reusable named subtask definitions, copied inline during compilation, or treated as canonical templates for task authors

Implementation staging note:

- the current implementation now freezes the packaging choice explicitly: built-in `subtasks/*.yaml` files are the canonical authored subtask catalog, while the active compiler still consumes inline subtask payloads from task definitions
- that means standalone subtask files must remain schema-valid, prompt-bound, and synthetically compileable against the current runtime vocabulary even though task definitions are not yet rewritten to reference them by id

---

## 4. Default layout definition files

The system likely needs built-in layout templates or patterns for default semantic decomposition.

### Required

- `layouts/epic_to_phases.yaml`
- `layouts/phase_to_plans.yaml`
- `layouts/plan_to_tasks.yaml`

### Useful optional files

- `layouts/manual_top_node.yaml`
- `layouts/research_only_breakdown.yaml`
- `layouts/replan_after_failure.yaml`

Implementation note:

- the built-in structural pack now ships these optional layouts as authored assets
- they remain additive and are not silently wired into the default active decomposition ladder
- workflow compilation now performs a built-in structural-library integrity check first so missing required node/task/subtask/layout assets fail as explicit compile errors instead of surfacing later as indirect missing-source errors

### Purpose

These files define:

- child kinds
- goals and rationale expectations
- dependencies
- acceptance fields
- ordering hints

---

## 5. Hook definition files

The built-in system should likely include default hooks for quality and consistency behavior.

Implementation note:

- the current implementation now treats the built-in runtime, hook, policy, environment, and prompt-reference assets as one inspectable operational-library contract
- workflow compilation now performs a dedicated built-in operational-library integrity check so missing required runtime/hook/policy files, broken prompt assets, or broken policy references fail as explicit compile errors before source resolution continues

### Validation/review/testing hooks

- `hooks/before_validation_default.yaml`
- `hooks/after_validation_default.yaml`
- `hooks/before_review_default.yaml`
- `hooks/after_review_default.yaml`
- `hooks/before_testing_default.yaml`
- `hooks/after_testing_default.yaml`

### Merge/rebuild hooks

- `hooks/before_merge_children_default.yaml`
- `hooks/after_merge_children_default.yaml`
- `hooks/on_merge_conflict_default.yaml`
- `hooks/before_upstream_rectify_default.yaml`
- `hooks/after_upstream_rectify_default.yaml`

### Node lifecycle hooks

- `hooks/on_node_created_default.yaml`
- `hooks/before_node_complete_default.yaml`
- `hooks/after_node_complete_default.yaml`

### Support hooks

- `hooks/after_subtask_default_summary.yaml`
- `hooks/after_node_complete_build_docs.yaml`
- `hooks/after_node_complete_update_provenance.yaml`

### Open question

- which of these behaviors should be explicit tasks versus default hooks

---

## 6. Validation definition files

The system should have a built-in validation library.

Implementation note:

- the current implementation now treats the built-in validation, review, testing, and docs families as one inspectable quality-library contract
- workflow compilation now performs a dedicated built-in quality-library integrity check so missing required gate/docs definitions, broken prompt bindings, or invalid built-in gate ordering fail as explicit compile errors instead of surfacing later as indirect runtime confusion

### Required validation definitions

- `validations/file_exists.yaml`
- `validations/file_updated.yaml`
- `validations/command_exit_code.yaml`
- `validations/json_schema.yaml`
- `validations/yaml_schema.yaml`
- `validations/ai_json_status.yaml`
- `validations/file_contains.yaml`
- `validations/git_clean.yaml`
- `validations/git_dirty.yaml`

### Likely additional validation definitions

- `validations/summary_written.yaml`
- `validations/docs_built.yaml`
- `validations/provenance_updated.yaml`
- `validations/session_bound.yaml`
- `validations/dependencies_satisfied.yaml`

---

## 7. Review definition files

Review should likely have its own built-in library rather than existing only as a generic subtask type.

### Required review definitions

- `reviews/layout_against_prompt.yaml`
- `reviews/node_against_requirements.yaml`
- `reviews/reconcile_output.yaml`
- `reviews/pre_finalize.yaml`

### Likely additional review definitions

- `reviews/merge_result_review.yaml`
- `reviews/docs_quality_review.yaml`
- `reviews/policy_compliance_review.yaml`

---

## 8. Testing definition files

Testing needs to become concrete in the built-in library.

### Required testing definitions

- `testing/default_unit_test_gate.yaml`
- `testing/default_integration_test_gate.yaml`
- `testing/default_smoke_test_gate.yaml`

### Likely additional testing definitions

- `testing/test_retry_policy.yaml`
- `testing/test_failure_summary.yaml`
- `testing/project_command_suite.yaml`

### Open question

- whether the system should ship only generic test gate templates or also specific default task/task-hook compositions

---

## 9. Documentation definition files

The built-in library should make docs generation explicit.

### Required documentation definitions

- `docs/build_local_node_docs.yaml`
- `docs/build_merged_tree_docs.yaml`
- `docs/default_doc_views.yaml`

### Likely additional documentation definitions

- `docs/static_analysis_scope.yaml`
- `docs/rationale_merge_rules.yaml`
- `docs/entity_history_view.yaml`

---

## 10. Rectification definition files

The git rebuild model needs explicit default YAML files.

### Required rectification definitions

- `rectification/rectify_node_from_seed.yaml`
- `rectification/rectify_upstream.yaml`
- `rectification/merge_current_children.yaml`
- `rectification/reconcile_conflict.yaml`

### Likely additional rectification definitions

- `rectification/regenerate_subtree.yaml`
- `rectification/rebuild_review.yaml`
- `rectification/rebuild_docs.yaml`

---

## 11. Runtime policy definition files

If runtime/session policy is YAML-managed, the default library should include:

- `runtime/session_defaults.yaml`
- `runtime/heartbeat_policy.yaml`
- `runtime/idle_nudge_policy.yaml`
- `runtime/child_session_policy.yaml`
- `runtime/recovery_policy.yaml`

These may also collapse into one `runtime/default_runtime_policy.yaml` if the system prefers fewer files.

---

## 12. Prompt definition files

The built-in library should ship authored prompt assets rather than relying on ad hoc prose embedded everywhere.

Concrete draft text for these lives in `notes/specs/prompts/prompt_library_plan.md`.

### Required prompt definitions

- `prompts/layouts/generate_phase_layout.md`
- `prompts/layouts/generate_plan_layout.md`
- `prompts/layouts/generate_task_layout.md`
- `prompts/execution/implement_leaf_task.md`
- `prompts/execution/reconcile_parent_after_merge.md`
- `prompts/review/review_layout_against_request.md`
- `prompts/review/review_node_output.md`
- `prompts/testing/interpret_test_results.md`
- `prompts/docs/build_node_docs.md`
- `prompts/runtime/session_bootstrap.md`
- `prompts/runtime/missed_step.md`
- `prompts/runtime/command_failed.md`
- `prompts/runtime/missing_required_output.md`
- `prompts/runtime/idle_nudge.md`
- `prompts/runtime/pause_for_user.md`
- `prompts/runtime/resume_existing_session.md`
- `prompts/runtime/replacement_session_bootstrap.md`
- `prompts/runtime/delegated_child_session.md`
- `prompts/runtime/parent_pause_for_user.md`
- `prompts/runtime/parent_local_replan.md`

### Purpose

These files should define:

- default prompt text
- required placeholders
- expected response contract
- whether the prompt is compile-time, runtime, or recovery-owned

---

## 13. Global/default policy definition files

The built-in library likely needs system-level defaults such as:

- `policies/default_node_policy.yaml`
- `policies/default_failure_policy.yaml`
- `policies/default_merge_policy.yaml`
- `policies/default_review_policy.yaml`
- `policies/default_testing_policy.yaml`

---

## 14. Minimal Default Flow By Node Kind

The following sections propose the minimum built-in task flow per default node kind.

## Epic node default flow

Likely built-in task sequence:

1. `research_context`
2. `generate_child_layout`
3. `review_child_layout`
4. `spawn_children`
5. `wait_for_children`
6. `reconcile_children`
7. `validate_node`
8. `review_node`
9. `test_node`
10. `update_provenance`
11. `build_node_docs`
12. `finalize_node`

## Phase node default flow

Likely built-in task sequence:

1. `research_context`
2. `generate_child_layout`
3. `review_child_layout`
4. `spawn_children`
5. `wait_for_children`
6. `reconcile_children`
7. `validate_node`
8. `review_node`
9. `test_node`
10. `update_provenance`
11. `build_node_docs`
12. `finalize_node`

## Plan node default flow

Likely built-in task sequence:

1. `research_context`
2. `generate_child_layout`
3. `review_child_layout`
4. `spawn_children`
5. `wait_for_children`
6. `reconcile_children`
7. `validate_node`
8. `review_node`
9. `test_node`
10. `update_provenance`
11. `build_node_docs`
12. `finalize_node`

## Task node default flow

Likely built-in task sequence:

1. `research_context`
2. `execute_node`
3. `validate_node`
4. `review_node`
5. `test_node`
6. `update_provenance`
7. `build_node_docs`
8. `finalize_node`

### Open question

- whether leaf task nodes should always have the same quality gates as higher nodes, or whether some of those should be hook-driven and project-specific

---

## Minimal Built-In Library Tiers

The file set should likely be delivered in tiers.

### Tier 1: essential

These are required for the default system to be coherent.

- semantic node definitions
- core task definitions
- core subtask definitions
- basic validation definitions
- basic review definitions
- core rectification definitions

### Tier 2: strongly recommended

These make the default system practically useful.

- testing definitions
- docs definitions
- runtime policy definitions
- default hooks
- default policies

### Tier 3: advanced/optional

These may be deferred if necessary.

- provenance extraction YAML
- isolated environment YAML
- specialized child-session YAML
- action automation mapping YAML

---

## Highest-Priority Missing Built-In Files

Based on current specs, the most important missing built-in file groups are:

1. concrete default node definition files
2. concrete default task definition files
3. review definition files
4. testing definition files
5. docs definition files
6. rectification/rebuild file library
7. runtime policy file set

---

## Key Design Decisions Still Needed

### D01. Generic vs semantic task library

Should built-in task files be semantic and node-kind-specific, or generic and selected through policy/entry-task composition?

### D02. How much should be hooks versus explicit tasks

Validation, review, testing, docs, and provenance updates can either be explicit tasks or inserted hooks. The system needs one canonical default model.

### D03. Leaf task quality gates

Should task nodes always run review/testing/docs/provenance, or should some be inherited conditionally?

### D04. Runtime policy granularity

Should runtime policy live in many small YAML files or one consolidated default file?

### D05. Provenance YAML ownership

Should provenance extraction behavior be part of docs or a standalone built-in family?

---

## Suggested Next Follow-On Docs

The next concrete follow-on documents after this should be:

- `notes/planning/expansion/database_schema_v2_expansion.md`
- `notes/planning/expansion/runtime_pseudocode_plan.md`
- `notes/planning/expansion/review_testing_docs_yaml_plan.md`

If the system wants to stay YAML-first for support systems, then also add:

- `notes/provenance_yaml_plan.md`
- `notes/runtime_policy_yaml_plan.md`

---

## Exit Criteria

This default YAML library planning phase should be considered complete when:

- the minimum built-in file set is enumerated
- each file group has a clear role
- the minimal node-kind flows are defined
- essential versus optional built-in YAML is classified
- the highest-priority missing built-in files are explicit

At that point, the system is ready to either:

1. write the actual built-in YAML documents, or
2. fold the library design into `yaml_schemas_spec_v2.md`
