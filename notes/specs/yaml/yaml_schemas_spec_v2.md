# YAML Schemas Spec V2

## Purpose

This document defines the canonical declarative configuration model for the system.

V2 expands the prior YAML spec by:

- formalizing the full YAML family inventory
- clarifying built-in versus project-local YAML
- defining the workflow compilation boundary
- adding first-class review, testing, and documentation families
- clarifying how overrides, hooks, and policies affect compiled workflows

Vocabulary:

- **node**: the durable execution context
- **task**: a named execution phase owned by a node definition
- **subtask**: one executable stage inside a task
- **compiled workflow**: the immutable runtime artifact produced from YAML sources

Avoid treating `worker` as a separate runtime concept. A node is the execution unit.

---

## 1. Core rules

### Rule 1: YAML is source input, not runtime truth

Mutable YAML definitions are source inputs. Execution must occur from compiled immutable workflow snapshots.

### Rule 2: All YAML must validate against an explicit family schema

No generated or edited YAML should be trusted without validation.

### Rule 3: Built-in and project-local YAML must remain distinct

The system must preserve which definitions came from:

- built-in system files
- project-local extension files
- project-local override files

### Rule 4: Generic canonical forms must exist

The model must support configurable tiers and kinds rather than hardcoding one ladder.

Projects may still use semantic defaults such as:

- epic
- phase
- plan
- task

but those are defaults, not runtime restrictions.

### Rule 5: Workflow-affecting YAML must preserve lineage

If a YAML file can affect compiled workflow behavior, its path, role, hash, and resolved contribution must be preserved.

---

## 2. Resolution and compilation order

When compiling YAML for a node version:

1. load built-in source definitions required for the node kind
2. load project-local extension files
3. load applicable override files
4. resolve overrides according to family merge rules
5. validate resolved YAML against family schemas
6. resolve project policies that affect workflow structure
7. resolve hook insertions
8. compile immutable workflow snapshot
9. persist source lineage and resolved YAML

Recommended project-local override directory:

```text
.ai/overrides/
  nodes/
  tasks/
  layouts/
  hooks/
  reviews/
  testing/
  docs/
  runtime/
```

Recommended project-local extension directory families:

```text
.ai/
  policies/
  nodes/
  tasks/
  subtasks/
  layouts/
  hooks/
  validations/
  reviews/
  testing/
  docs/
  provenance/
  rectification/
  runtime/
  environments/
```

Each compiled workflow snapshot must preserve:

- source file paths
- source roles
- content hashes
- resolved merged YAML
- inserted hook lineage
- compile timestamp and workflow hash

Recommended canonical source roles:

- `base_definition`
- `extension_definition`
- `override_definition`
- `policy_definition`
- `hook_definition`
- `review_definition`
- `testing_definition`
- `docs_definition`
- `rectification_definition`
- `prompt_template`

Implementation staging note:

- the current implementation persists source lineage for built-in node creation/versioning using:
  - built-in node/task/layout YAML
  - built-in runtime-policy and prompt-reference YAML
  - the node definition's referenced prompt template
- the current implementation now also validates `override_definition` YAML from the packaged project-local override root and persists those override documents in node-version source lineage
- the current implementation now compiles those captured inputs into immutable workflow snapshots and durable compile-failure records
- the current implementation now performs deterministic override resolution during compilation for node, task, layout, runtime-policy, project-policy, prompt-reference, review, testing, docs, hook, and rectification YAML families
- the current implementation persists the applied override chain, compatibility warnings, and resolved per-document YAML payloads into the compiled workflow snapshot for daemon and CLI inspection
- the current built-in library now uses authored non-node family documents instead of `status: scaffold` placeholders across tasks, subtasks, layouts, validations, reviews, testing, docs, rectification, runtime, hooks, and policies
- the current default built-in node workflows now include `review_node` after `validate_node`, and source-lineage capture now includes referenced built-in review definitions plus their prompt templates when a compiled task declares `uses_reviews`
- the current implementation now also captures referenced testing definitions in node-version source lineage and compiled workflow source backfill when a task declares `uses_testing`
- the current implementation now treats `run_tests` as a first-class durable gate with `test_results` persistence and cached `subtask_attempts.testing_json`, but the packaged default node workflows still stage testing as opt-in through explicit task selection, policy, or override rather than silently inserting `test_node` into every built-in node kind
- current override merging is bounded to top-level family fields with explicit field-level merge modes; nested path-addressed patch semantics remain deferred
- the current override source set is the packaged project-local override root as a deterministic compile input boundary; narrower node-scoped applicability rules remain deferred
- the current compiler now performs deterministic compile-time hook selection and expansion for policy and node hook refs, persists hook diagnostics in `compiled_workflows.resolved_yaml.hook_expansion`, and records inserted subtasks with `inserted_by_hook` metadata
- the current compile-time hook boundary is intentionally limited to explicit workflow insertion triggers; runtime-only triggers such as `on_node_created` and `on_merge_conflict`, plus conditional `if` matching, remain deferred
- the current implementation now validates `environment_policy_definition` YAML from `environments/*.yaml`, allows `subtask_definition.environment_policy_ref`, freezes resolved environment requests into compiled subtasks, and records referenced environment policy documents in source lineage
- the current implementation now also validates optional `render_context` blocks on `subtask_definition` and hook run steps; compile-time rendering supports canonical `{{variable}}` syntax with legacy `<variable>` compatibility, freezes rendered prompt/command text into compiled subtasks, and rejects render syntax in unsupported fields such as `args`, `env`, `checks`, `outputs`, and `retry_policy`
- the current implementation now treats validation, review, testing, docs, and rectification YAML as rigid higher-order families with explicit field validation instead of permissive catch-all payloads
- schema validation now also checks prompt-bearing review and hook definitions against the packaged prompt catalog so broken prompt refs fail at YAML validation time instead of surfacing later during runtime use
- the current implementation now also treats `runtime_definition`, `runtime_policy_definition`, and `prompt_reference_definition` as rigid schema families with catalog-backed reference validation
- runtime definitions now validate declared action refs against packaged subtask assets, runtime-policy docs validate referenced runtime/hook/review/testing/docs YAML assets, and prompt-reference docs validate dotted keys plus prompt-pack-relative markdown targets

---

## 3. YAML family inventory

The system should support the following YAML families.

### Required core families

- `node_definition`
- `task_definition`
- `subtask_definition`
- `validation_check`
- `output_definition`
- `layout_definition`
- `hook_definition`
- `override_definition`

### Required or strongly recommended support families

- `project_policy_definition`
- `review_definition`
- `testing_definition`
- `documentation_definition`
- `rectification_definition`

### Optional or advanced families

- `provenance_definition`
- `runtime_policy_definition`
- `environment_policy_definition`
- `action_automation_definition`

Open rule:

- optional families may be omitted in an implementation phase, but the design must still explicitly classify them as deferred rather than leaving them implied.

Implementation staging note:

- the current implementation validates `node_definition` with full field coverage
- the currently authored built-in and project-policy families are validated with explicit family models
- `override_definition` is now a first-class validated family for the packaged project-local override root

---

## 4. Built-in versus project-local YAML

### Built-in system YAML

These define the default orchestration system behavior and ship with the platform.

Examples:

- built-in node kinds
- built-in task catalog
- built-in subtask templates
- built-in validation, review, testing, docs, and rectification definitions

### Project-local extension YAML

These add new definitions without replacing built-ins.

Examples:

- new node kinds
- new task definitions
- project-specific test suites
- project-specific hooks

### Project-local override YAML

These modify the behavior of existing built-in or extension definitions.

Examples:

- changing node policy defaults
- inserting additional validations
- disabling auto-merge
- altering review/testing/docs requirements

---

## 5. Expandable hierarchy model

The hierarchy must not be hardcoded to `epic|phase|plan|task`.

Instead:

- node definitions declare `tier`
- node definitions declare `kind`
- node definitions may declare allowed parent/child constraints

The runtime and schema layers must allow:

- future custom tiers
- multiple kinds at the same tier
- project-defined ladders through YAML

The default built-in library may still include:

- `epic`
- `phase`
- `plan`
- `task`

Those defaults must sit on top of the generic substrate rather than replacing it.

---

## 6. Node definition schema

A node definition describes a node kind and the tasks it may run.

```yaml
node_definition:
  id: string
  kind: string
  tier: integer|string
  description: string
  main_prompt: string
  entry_task: string
  available_tasks:
    - string
  parent_constraints:
    allowed_kinds:
      - string
    allowed_tiers:
      - integer|string
    allow_parentless: boolean
  child_constraints:
    allowed_kinds:
      - string
    allowed_tiers:
      - integer|string
    min_children: integer
    max_children: integer
  policies:
    max_node_regenerations: integer
    max_subtask_retries: integer
    child_failure_threshold_total: integer
    child_failure_threshold_consecutive: integer
    child_failure_threshold_per_child: integer
    require_review_before_finalize: boolean
    require_testing_before_finalize: boolean
    require_docs_before_finalize: boolean
    auto_run_children: boolean
    auto_rectify_upstream: boolean
    auto_merge_to_parent: boolean
    auto_merge_to_base: boolean
  hooks:
    - string
```

### Clarifications

- `entry_task` identifies the first task in the node execution plan
- `available_tasks` lists the task definitions the node kind may use
- parent/child constraints define valid structural relationships, not runtime dependencies

---

## 7. Task definition schema

A task is a named execution phase inside a node. It runs an ordered list of subtasks.

```yaml
task_definition:
  id: string
  name: string
  description: string
  applies_to_kinds:
    - string
  policy:
    max_subtask_retries: integer
    on_failure: fail_to_parent|pause_for_user
  uses_reviews:
    - string
  uses_testing:
    - string
  uses_docs:
    - string
  subtasks:
    - subtask_definition
```

### Clarifications

- nodes have tasks
- tasks have subtasks
- tasks do not call tasks
- subtasks do not call tasks
- tasks may reference review/testing/docs definitions used during compilation

---

## 8. Subtask definition schema

Recommended subtask types:

- `run_prompt`
- `run_command`
- `build_context`
- `wait_for_children`
- `wait_for_sibling_dependency`
- `reset_to_seed`
- `merge_children`
- `validate`
- `review`
- `run_tests`
- `build_docs`
- `write_summary`
- `finalize_node`
- `spawn_child_session`
- `spawn_child_node`
- `update_provenance`

```yaml
subtask_definition:
  id: string
  type: run_prompt|run_command|build_context|wait_for_children|wait_for_sibling_dependency|reset_to_seed|merge_children|validate|review|run_tests|build_docs|write_summary|finalize_node|spawn_child_session|spawn_child_node|update_provenance
  title: string
  description: string
  requires:
    - subtask_complete: string
  prompt: string
  command: string
  args:
    key: value
  env:
    KEY: value
  checks:
    - validation_check
  outputs:
    - output_definition
  retry_policy:
    max_attempts: integer
    backoff_seconds: integer
  block_on_user_flag: string
  pause_summary_prompt: string
  on_failure:
    action: fail_to_parent|pause_for_user
```

### Clarifications

- a `search` operation is modeled as either a bounded child session or a prompt-driven research subtask
- review/testing/docs/provenance execution may compile into concrete subtasks using this family

---

## 9. Validation check schema

```yaml
validation_check:
  type: file_exists|file_updated|command_exit_code|json_schema|yaml_schema|ai_json_status|file_contains|git_clean|git_dirty|summary_written|docs_built|provenance_updated|dependencies_satisfied|session_bound
  path: string
  command: string
  exit_code: integer
  schema: string
  value: string
  pattern: string
```

Dependencies and required-state checks must be enforced. A task or subtask should not be considered complete if required validations are unsatisfied.

---

## 10. Output definition schema

```yaml
output_definition:
  type: file_updated|working_tree_dirty|summary_written|entity_index_updated|docs_built|provenance_updated|ai_json_status|test_results_written|review_results_written
  path: string
  value: string
```

---

## 11. Layout definition schema

Layout files define child nodes to create.

```yaml
layout_definition:
  children:
    - id: string
      kind: string
      tier: integer|string
      name: string
      goal: string
      rationale: string
      dependencies:
        - string
      acceptance:
        - string
      ordinal: integer
```

Projects may still provide convenience aliases such as `phases`, `plans`, or `tasks`, but the generic child form should remain canonical.

---

## 12. Hook definition schema

Hooks are policy-driven insertions at predefined lifecycle points.

### Recommended hook points

Node-level:

- `on_node_created`
- `before_node_compile`
- `after_node_compile`
- `before_node_run`
- `after_node_run`
- `before_node_complete`
- `after_node_complete`
- `before_node_rectify`
- `after_node_rectify`
- `before_upstream_rectify`
- `after_upstream_rectify`

Task/subtask-level:

- `before_task`
- `after_task`
- `before_subtask`
- `after_subtask`
- `on_subtask_failure`

Review/validation/testing-level:

- `before_validation`
- `after_validation`
- `before_review`
- `after_review`
- `before_testing`
- `after_testing`

Merge-level:

- `before_merge_children`
- `after_merge_children`
- `on_merge_conflict`

```yaml
hook_definition:
  id: string
  when: on_node_created|before_node_compile|after_node_compile|before_node_run|after_node_run|before_node_complete|after_node_complete|before_node_rectify|after_node_rectify|before_upstream_rectify|after_upstream_rectify|before_task|after_task|before_subtask|after_subtask|on_subtask_failure|before_validation|after_validation|before_review|after_review|before_testing|after_testing|before_merge_children|after_merge_children|on_merge_conflict
  applies_to:
    tiers:
      - integer|string
    node_kinds:
      - string
    task_ids:
      - string
    subtask_types:
      - string
  if:
    changed_entity_types:
      - file|module|class|function|method|variable|type|endpoint|test
    paths_match:
      - string
  run:
    - type: run_command|run_prompt|validate|review|run_tests|build_docs
      command: string
      prompt: string
      checks:
        - validation_check
```

### Hook rule

Hooks must compile into explicit durable workflow stages or checks. They must not remain implicit runtime side effects.

---

## 13. Override definition schema

Override files define how project-local YAML modifies existing source definitions.

```yaml
override_definition:
  target_family: node_definition|task_definition|layout_definition|hook_definition|review_definition|testing_definition|documentation_definition|rectification_definition|project_policy_definition
  target_id: string
  compatibility:
    min_schema_version: integer|string
    built_in_version: string
  merge_mode: replace|deep_merge|append_list|replace_list
  value:
    key: value
```

### Override rule

Each family should document which fields are:

- replace-only
- mergeable
- appendable

If an override creates an invalid merged document, compilation must fail.

Recommended compatibility direction:

- built-in YAML families should have explicit version identity
- compiled workflow lineage should preserve the exact built-in version used during compilation
- overrides should be able to declare compatibility intent against schema, runtime, or built-in library versions
- compilation should warn or fail clearly when an override appears stale or incompatible with its target base

---

## 14. Project policy schema

Project policy YAML defines cross-cutting defaults.

```yaml
project_policy_definition:
  id: string
  description: string
  defaults:
    auto_run_children: boolean
    auto_merge_to_parent: boolean
    auto_merge_to_base: boolean
    require_review_before_finalize: boolean
    require_testing_before_finalize: boolean
    require_docs_before_finalize: boolean
  runtime_policy_refs:
    - string
  hook_refs:
    - string
  review_refs:
    - string
  testing_refs:
    - string
  docs_refs:
    - string
```

### Compile boundary note

If a project policy changes workflow structure or quality gates, it must contribute to compiled workflow lineage. Purely operational runtime settings may remain outside compiled workflow if intentionally classified that way.

The same principle applies to override compatibility metadata when it affects whether an override is valid, stale, or warning-worthy during compilation.

Implementation staging note:

- the current implementation now validates and loads project policy YAML from `yaml/project/project-policies/*.yaml`
- effective project policy is merged deterministically over the built-in default runtime policy and is embedded into compiled workflow payloads for auditability
- the current slice now also allows `project_policy_definition` and `runtime_policy_definition` to participate in the compiler override-resolution stage
- prompt-template selection can now be changed through resolved node or project-policy override inputs, and the chosen prompt asset is preserved in source lineage

---

## 15. Review definition schema

Review is a first-class YAML family.

```yaml
review_definition:
  id: string
  name: string
  applies_to:
    node_kinds:
      - string
    task_ids:
      - string
    lifecycle_points:
      - string
  scope: layout|node_output|merge_result|docs|policy_compliance|custom
  description: string
  inputs:
    include_parent_requirements: boolean
    include_child_summaries: boolean
    include_acceptance_criteria: boolean
    include_changed_files: boolean
    include_validation_results: boolean
    include_test_results: boolean
  prompt: string
  criteria:
    - string
  on_result:
    pass_action: continue
    revise_action: rerun_subtask|rerun_task|pause_for_user
    fail_action: fail_to_parent|pause_for_user
```

---

## 16. Testing definition schema

Testing is a first-class YAML family.

```yaml
testing_definition:
  id: string
  name: string
  applies_to:
    node_kinds:
      - string
    task_ids:
      - string
    lifecycle_points:
      - string
  scope: unit|integration|smoke|project_custom
  description: string
  commands:
    - command: string
      working_directory: string
      env:
        KEY: value
  retry_policy:
    max_attempts: integer
    rerun_failed_only: boolean
  pass_rules:
    require_exit_code_zero: boolean
    max_failed_tests: integer
  on_result:
    pass_action: continue
    fail_action: fail_to_parent|pause_for_user|allow_override
```

---

## 17. Documentation definition schema

Documentation generation is a first-class YAML family.

```yaml
documentation_definition:
  id: string
  name: string
  applies_to:
    node_kinds:
      - string
    lifecycle_points:
      - string
  scope: local|merged|entity_history|rationale_view|custom
  description: string
  inputs:
    include_static_analysis: boolean
    include_entity_relations: boolean
    include_node_summaries: boolean
    include_prompt_history: boolean
    include_review_results: boolean
    include_test_results: boolean
  outputs:
    - path: string
      format: markdown|html|json|yaml
  rebuild_policy:
    on_finalize: boolean
    on_rectify: boolean
    on_docs_request: boolean
```

Implementation staging note:

- the current packaged family name is `docs_definition`
- the current validator and built-in library support `scope`, `inputs`, and `outputs` with `path` plus `view`
- rebuild-policy fields remain deferred, and docs generation is currently triggered through explicit daemon/CLI build requests rather than implicit automatic rebuild hooks

---

## 18. Rectification definition schema

Rectification should be a first-class configurable family where policy-driven behavior is needed.

```yaml
rectification_definition:
  id: string
  name: string
  applies_to:
    node_kinds:
      - string
  reset_policy:
    reset_to_seed: boolean
  merge_policy:
    deterministic_order: dependency_then_ordinal_then_created_at_then_id
  stages:
    - string
  require_review: boolean
  require_testing: boolean
  require_docs: boolean
```

---

## 19. Runtime and environment policy schemas

These families are optional in V2 but should be explicitly classified if used.

### Runtime policy

```yaml
runtime_policy_definition:
  id: string
  heartbeat_seconds: integer
  idle_nudge_seconds: integer
  max_idle_nudges: integer
  child_session_limit: integer
```

### Environment policy

```yaml
environment_policy_definition:
  id: string
  isolation_mode: none|container|namespace|custom_profile
  allow_network: boolean
  runtime_profile: string
  mandatory: boolean
```

Implementation staging note:

- the current built-in library ships `environments/local_default.yaml` and `environments/isolated_test_profile.yaml`
- `custom_profile` requests are compile-time validated against project policy `environment_profiles`
- infrastructure-specific launcher details remain outside YAML and are resolved at daemon runtime

---

## 20. Default built-in YAML library

The built-in system should ship with default files covering at minimum:

### Nodes

- `nodes/epic.yaml`
- `nodes/phase.yaml`
- `nodes/plan.yaml`
- `nodes/task.yaml`

### Tasks

- `tasks/research_context.yaml`
- `tasks/generate_child_layout.yaml`
- `tasks/review_child_layout.yaml`
- `tasks/spawn_children.yaml`
- `tasks/wait_for_children.yaml`
- `tasks/reconcile_children.yaml`
- `tasks/validate_node.yaml`
- `tasks/review_node.yaml`
- `tasks/test_node.yaml`
- `tasks/build_node_docs.yaml`
- `tasks/update_provenance.yaml`
- `tasks/finalize_node.yaml`
- `tasks/rectify_node_from_seed.yaml`
- `tasks/rectify_upstream.yaml`

### Reviews

- `reviews/layout_against_prompt.yaml`
- `reviews/node_against_requirements.yaml`
- `reviews/reconcile_output.yaml`
- `reviews/pre_finalize.yaml`

### Testing

- `testing/default_unit_test_gate.yaml`
- `testing/default_integration_test_gate.yaml`
- `testing/default_smoke_test_gate.yaml`

### Docs

- `docs/build_local_node_docs.yaml`
- `docs/build_merged_tree_docs.yaml`
- `docs/default_doc_views.yaml`

### Rectification

- `rectification/rectify_node_from_seed.yaml`
- `rectification/rectify_upstream.yaml`
- `rectification/merge_current_children.yaml`
- `rectification/reconcile_conflict.yaml`

---

## 21. Canonical default quality-gate ordering

The default built-in ordering should be:

1. reconcile node-local output
2. validation
3. review
4. testing
5. provenance update
6. docs build
7. finalize node

Projects may override this only where the runtime and policy model explicitly allows it.

---

## 22. Example task: rectify from seed

```yaml
task_definition:
  id: rectify_node_from_seed
  name: Rectify node from seed and current children
  applies_to_kinds:
    - plan
    - task
  policy:
    max_subtask_retries: 2
    on_failure: fail_to_parent
  uses_reviews:
    - pre_finalize
  uses_testing:
    - default_smoke_test_gate
  uses_docs:
    - build_local_node_docs
  subtasks:
    - id: gather_context
      type: build_context
      title: Gather rectification inputs
      prompt: |
        Gather this node's seed commit, current child finals, child summaries,
        parent requirements, active hooks, and resolved overrides.
        Write results to .ai/rectify_context.yaml
      outputs:
        - type: file_updated
          path: .ai/rectify_context.yaml

    - id: reset_to_seed
      type: reset_to_seed
      title: Reset branch to seed
      requires:
        - subtask_complete: gather_context
      command: ai-tool git reset-node-to-seed --node ${node_id}

    - id: merge_children
      type: merge_children
      title: Merge current child finals
      requires:
        - subtask_complete: reset_to_seed
      command: ai-tool git merge-current-children --node ${node_id} --ordered

    - id: reconcile
      type: run_prompt
      title: Reconcile merged output
      requires:
        - subtask_complete: merge_children
      prompt: |
        Reconcile this node after child merges.
        Resolve inconsistencies while preserving parent requirements.

    - id: maybe_pause_for_user
      type: write_summary
      title: Pause if user-gated
      requires:
        - subtask_complete: reconcile
      block_on_user_flag: review_before_merge
      pause_summary_prompt: |
        Summarize the rebuilt node for the user before continuing.

    - id: validate
      type: validate
      title: Validate node output
      requires:
        - subtask_complete: maybe_pause_for_user
      checks:
        - type: command_exit_code
          command: ai-tool node validate --node ${node_id}
          exit_code: 0

    - id: update_provenance
      type: update_provenance
      title: Refresh code provenance
      requires:
        - subtask_complete: validate

    - id: build_docs
      type: build_docs
      title: Build node docs
      requires:
        - subtask_complete: update_provenance
      command: ai-tool docs build-node-view --node ${node_id}

    - id: finalize
      type: finalize_node
      title: Commit final state
      requires:
        - subtask_complete: build_docs
      command: ai-tool git finalize-node --node ${node_id}
```

---

## 23. Compilation requirement

At node creation or supersession time, the system must compile:

- fully merged YAML after overrides
- fully expanded hook-inserted stage list
- all selected review/testing/docs definitions
- durable compiled task and subtask IDs
- explicit dependency graph between compiled subtasks

Execution must occur from the compiled artifact, not from mutable source YAML.

---

## 24. V2 closure notes

This V2 YAML spec resolves or reduces the following prior gaps:

- missing YAML family inventory
- unclear review/testing/docs modeling
- incomplete built-in YAML library scope
- unclear override and policy families
- unclear quality-gate ordering at the YAML layer

Remaining follow-on work still needed:

- write the actual built-in YAML documents
- finalize which optional families are included in the first implementation phase
- align the DB, runtime, CLI, and git v2 specs to this document
- decide whether child-set authority metadata for manual/layout hybrid trees is represented directly in YAML-driven metadata or only in runtime/DB state
