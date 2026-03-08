# YAML Schemas Spec

## Purpose

This document defines the declarative configuration model for the system.

Vocabulary:

- **node**: the durable execution context
- **task**: a named execution phase owned by a node definition
- **subtask**: one executable stage inside a task

Avoid using `worker` as a separate concept. A node is the execution unit.

---

## 1. Resolution order

When loading YAML for a node:

1. load the base built-in definition
2. load project-local override files that match by path and filename
3. apply override merge rules
4. validate merged YAML against schema
5. compile immutable workflow snapshot

Recommended override directory:

```text
.ai/overrides/
  nodes/
  tasks/
  layouts/
  hooks/
```

Each compiled workflow snapshot must persist:

- base source file path
- override source file paths
- content hashes of all applied files
- resolved merged YAML

---

## 2. Expandable tier model

The hierarchy must not be hardcoded to `epic|phase|plan|task`.

Instead, node definitions declare:

- `tier`
- `kind`
- optional parent/child constraints

A default project may still use:

- epic
- phase
- plan
- task

but the runtime and schema layer must allow:

- future custom tiers
- multiple kinds at the same tier
- projects redefining concept ladders through YAML

---

## 3. Root schema families

The system should have distinct schema families:

- `node_definition`
- `task_definition`
- `subtask_definition`
- `validation_check`
- `hook_definition`
- `layout_definition`

Generated YAML should never be trusted without schema validation.

---

## 4. Node definition schema

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
  policies:
    max_node_regenerations: integer
    max_subtask_retries: integer
    child_failure_threshold_total: integer
    child_failure_threshold_consecutive: integer
    require_review_before_finalize: boolean
    auto_run_children: boolean
    auto_rectify_upstream: boolean
    auto_merge_to_parent: boolean
    auto_merge_to_base: boolean
  hooks:
    - string
```

---

## 5. Task definition schema

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
  subtasks:
    - subtask_definition
```

### Clarification

- nodes have tasks
- tasks have subtasks
- tasks do not call tasks
- subtasks do not call tasks
- tasks may call subtasks
- subtasks may call subtasks

---

## 6. Subtask definition schema

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
- `build_docs`
- `write_summary`
- `finalize_node`
- `spawn_child_session`

A `search` operation is modeled as a bounded child session or prompt-driven subtask that performs research and returns a summary to context, rather than as a full child node.

```yaml
subtask_definition:
  id: string
  type: run_prompt|run_command|build_context|wait_for_children|wait_for_sibling_dependency|reset_to_seed|merge_children|validate|review|build_docs|write_summary|finalize_node|spawn_child_session
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

---

## 7. Validation check schema

```yaml
validation_check:
  type: file_exists|file_updated|command_exit_code|json_schema|yaml_schema|ai_json_status|file_contains|git_clean|git_dirty
  path: string
  command: string
  exit_code: integer
  schema: string
  value: string
  pattern: string
```

Dependencies and required-state checks must be strictly enforced. A task or subtask should not be considered complete if its required checks are unsatisfied.

---

## 8. Output definition schema

```yaml
output_definition:
  type: file_updated|working_tree_dirty|summary_written|entity_index_updated|docs_built|ai_json_status
  path: string
  value: string
```

---

## 9. Layout schemas

Layout files define child nodes to create. The schema should be generic rather than tied to fixed names.

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
```

Projects may still provide convenience aliases such as `phases`, `plans`, or `tasks`, but the generic form should be canonical.

---

## 10. Hook system

Hooks are policy-driven subtask insertions at predefined lifecycle points.

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

- `before_review`
- `after_review`
- `before_validation`
- `after_validation`
- `before_testing`
- `after_testing`

Merge-level:

- `before_merge_children`
- `after_merge_children`
- `on_merge_conflict`

### Hook definition schema

```yaml
hook_definition:
  id: string
  when: on_node_created|before_node_compile|after_node_compile|before_node_run|after_node_run|before_node_complete|after_node_complete|before_node_rectify|after_node_rectify|before_upstream_rectify|after_upstream_rectify|before_task|after_task|before_subtask|after_subtask|on_subtask_failure|before_review|after_review|before_validation|after_validation|before_testing|after_testing|before_merge_children|after_merge_children|on_merge_conflict
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
    - type: run_command|run_prompt|validate
      command: string
      prompt: string
      checks:
        - validation_check
```

---

## 11. Example task: rectify from seed

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

    - id: review
      type: review
      title: Review node output
      requires:
        - subtask_complete: validate
      prompt: |
        Review the node against parent requirements, child summaries,
        acceptance criteria, and project overrides.

    - id: build_docs
      type: build_docs
      title: Build node docs
      requires:
        - subtask_complete: review
      command: ai-tool docs build-node-view --node ${node_id}

    - id: finalize
      type: finalize_node
      title: Commit final state
      requires:
        - subtask_complete: build_docs
      command: ai-tool git finalize-node --node ${node_id}
```

---

## 12. Compilation requirement

At node creation time, the system must compile:

- fully merged YAML after overrides
- fully expanded hook-inserted subtask list
- durable compiled subtask IDs
- explicit dependency graph between compiled subtasks

Execution must occur from this compiled artifact, not from mutable source YAML.

