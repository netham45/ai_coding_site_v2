# Hypothetical Operational Simulations (Latest Notes)

## Purpose

This document rebuilds the prior simulations from the current note set.

It now covers three scenarios:

1. starting a first prompt-driven plan run
2. adding a new project to the system
3. rebuilding from a specific node and re-merging parents

This is based on the current direction in:

- `notes/default_yaml_library_plan.md`
- `notes/runtime_pseudocode_plan.md`
- `notes/child_materialization_and_scheduling.md`
- `notes/git_rectification_spec_v2.md`
- `notes/cutover_policy_note.md`
- `notes/compile_failure_persistence.md`
- `notes/override_conflict_semantics.md`
- `notes/session_recovery_appendix.md`
- `notes/invalid_dependency_graph_handling.md`
- `notes/yaml_schemas_spec_v2.md`
- `notes/node_lifecycle_spec_v2.md`
- `notes/runtime_command_loop_spec_v2.md`
- `notes/cli_surface_spec_v2.md`
- `notes/database_schema_spec_v2.md`

All outputs below are simulated.

---

## Shared assumptions

The current notes imply these baseline rules:

- node creation compiles immutable workflows from built-in YAML plus project-local extensions and overrides
- default built-in tasks include:
  - `research_context`
  - `generate_child_layout`
  - `review_child_layout`
  - `revise_child_layout`
  - `spawn_children`
  - `wait_for_children`
  - `reconcile_children`
  - `validate_node`
  - `review_node`
  - `test_node`
  - `update_provenance`
  - `build_node_docs`
  - `finalize_node`
  - `respond_to_child_failure`
  - `rectify_node_from_seed`
  - `rectify_upstream`
- child materialization and scheduling are separate
- quality-gate order is:
  1. reconcile
  2. validation
  3. review
  4. testing
  5. provenance
  6. docs
  7. finalize
- compilation failure is durable state
- cutover is conservative: candidate lineages do not become authoritative until the rebuilt path is stable

---

## Simulation 1: First prompt-driven run

### User intent

The operator wants a minimal but real first task:

> Create a small config-driven greeting generator. Add `greetings.yaml`, generate `greeting.txt`, verify it with a repeatable command, and summarize the work.

### Entry surface

The current CLI notes are file-based for node creation, so prompt-invocation is best modeled as a thin wrapper that writes a request file and then calls `node create`.

#### Request file

```yaml
request:
  title: Getting started greeting example
  prompt: >
    Create a small config-driven greeting generator. Add greetings.yaml,
    generate greeting.txt, verify it with a repeatable command, and summarize
    the work.
  target_kind: plan
```

#### Operator action

```text
ai-tool node create \
  --kind plan \
  --title "Getting started greeting example" \
  --file .ai/requests/getting_started_greeting.yaml
```

#### Simulated response

```json
{
  "status": "OK",
  "node_version_id": "plan_v1",
  "compiled_workflow_id": "cw_plan_v1",
  "lifecycle_state": "READY",
  "branch": "tier/plan/plan/getting-started-greeting__plan_v1"
}
```

### Compiled plan task graph

The latest notes imply this default plan-style flow:

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

### Plan run admission

#### Operator action

```text
ai-tool node run start --node plan_v1
```

#### Simulated response

```json
{
  "status": "OK",
  "run_id": "run_plan_v1_1",
  "session_id": "sess_plan_v1_1",
  "lifecycle_state": "RUNNING",
  "current_task_id": "research_context",
  "current_compiled_subtask_id": "plan_cst_001"
}
```

### Stage A: research and info gathering

Task:

- `research_context`

Compiled subtasks:

1. `build_context`
2. `spawn_child_session`
3. `write_summary`

#### Subtask `build_context`

Simulated commands:

```text
ai-tool session bind --node plan_v1
ai-tool workflow current --node plan_v1
ai-tool subtask current --node plan_v1
ai-tool subtask context --node plan_v1
```

Simulated response:

```yaml
node_version_id: plan_v1
run_id: run_plan_v1_1
task: research_context
subtask: build_context
user_prompt: >
  Create a small config-driven greeting generator. Add greetings.yaml,
  generate greeting.txt, verify it with a repeatable command, and summarize
  the work.
policy:
  auto_run_children: true
  require_review_before_finalize: true
  require_testing_before_finalize: true
  require_docs_before_finalize: true
repo_state:
  branch: main
  working_tree_state: clean
```

#### Subtask `spawn_child_session`

Delegated prompt:

```text
Inspect the repository and return:
- likely implementation file
- likely test path
- obvious scope constraints
- whether one child task is enough
```

Simulated runtime action:

```text
push_child_session(node=plan_v1, reason="research_context")
```

Simulated child-session output:

```md
# Repo Research Summary

- The sample repo is a small Python project.
- `src/app.py` is the natural implementation file.
- `tests/test_app.py` is the natural test path.
- One child task node is sufficient.
```

#### Subtask `write_summary`

Simulated summary registration:

```text
ai-tool summary register --node plan_v1 --file .ai/summaries/plan_research.md --type subtask
```

Summary:

```md
# Plan Research Summary

- Use one child `task` node.
- Implement in `src/app.py`.
- Validate with `tests/test_app.py`.
```

### Stage B: plan creation

Task:

- `generate_child_layout`

Compiled subtasks:

1. `build_context`
2. `run_prompt`
3. `validate`
4. `write_summary`

#### Subtask `run_prompt`

Prompt:

```text
Generate a layout_definition for this plan node.

Requirements:
- exactly one child
- child kind must be task
- child must implement the greeting feature
- acceptance criteria must include file outputs, validation, and summary

Write to .ai/layouts/plan_v1.yaml and return JSON status.
```

Simulated response:

```json
{
  "status": "OK",
  "written_file": ".ai/layouts/plan_v1.yaml"
}
```

Simulated layout:

```yaml
layout_definition:
  children:
    - id: greeting_task
      kind: task
      tier: task
      name: Greeting generator task
      goal: >
        Add a config-driven greeting generator that reads greetings.yaml and
        writes greeting.txt.
      rationale: >
        This is the smallest useful child for exercising planning, execution,
        validation, review, testing, docs, and finalize behavior.
      dependencies: []
      acceptance:
        - greetings.yaml exists
        - greeting.txt exists
        - tests pass
        - summary exists
```

#### Subtask `validate`

Action:

```text
ai-tool layout validate --node plan_v1
```

Response:

```json
{
  "status": "OK",
  "schema_family": "layout_definition",
  "dependency_validation": "valid",
  "errors": []
}
```

### Stage C: verification of the plan

Task:

- `review_child_layout`

Compiled subtasks:

1. `build_context`
2. `review`
3. `write_summary`

#### Subtask `review`

Prompt:

```text
Review the generated child layout against the request.

Check:
- correct child kind
- minimal child count
- complete acceptance criteria
- no missing dependency references

Return:
{"status":"PASS"|"REVISE"|"FAIL","summary":"...","findings":[...]}
```

Simulated response:

```json
{
  "status": "PASS",
  "summary": "The child layout is minimal, valid, and aligned with the request.",
  "findings": []
}
```

### Stage D: child creation and scheduling

Task:

- `spawn_children`

Compiled subtasks:

1. `spawn_child_node`
2. `write_summary`

#### Subtask `spawn_child_node`

Runtime function:

```text
materialize_layout_children(parent=plan_v1, layout=.ai/layouts/plan_v1.yaml)
```

Simulated response:

```json
{
  "status": "OK",
  "children_created": [
    {
      "node_version_id": "task_v1",
      "kind": "task",
      "compiled_workflow_id": "cw_task_v1",
      "initial_state": "COMPILED"
    }
  ],
  "dependency_edges_created": []
}
```

The latest scheduling note matters here:

- materialization succeeded
- scheduling happens next
- because there are no dependencies, `task_v1` is immediately `ready`

#### Simulated scheduling classification

```yaml
task_v1: ready
```

#### Simulated child run start

```text
ai-tool node run start --node task_v1
```

```json
{
  "status": "OK",
  "run_id": "run_task_v1_1",
  "session_id": "sess_task_v1_1",
  "lifecycle_state": "RUNNING"
}
```

### Stage E: child execution

Child compiled tasks:

1. `research_context`
2. `execute_node`
3. `validate_node`
4. `review_node`
5. `test_node`
6. `update_provenance`
7. `build_node_docs`
8. `finalize_node`

#### Child `research_context`

Key subtool:

```text
rg --files .
```

Simulated response:

```text
README.md
src/app.py
tests/test_app.py
scripts/run-app.sh
```

#### Child `execute_node`

Prompt:

```text
Implement the greeting feature.

Requirements:
- create greetings.yaml
- update the app to read greetings.yaml
- generate greeting.txt
- update tests so later validation and testing stages pass

Return JSON with changed files and a concise summary.
```

Simulated response:

```json
{
  "status": "OK",
  "changed_files": [
    "greetings.yaml",
    "src/app.py",
    "greeting.txt",
    "tests/test_app.py"
  ],
  "summary": "Implemented YAML-driven greeting generation and updated the focused test."
}
```

#### Child `validate_node`

Subtools:

- `validate` file existence
- `validate` file contents

Simulated response:

```json
{
  "status": "PASS",
  "checks": [
    "file_exists:greetings.yaml",
    "file_exists:greeting.txt",
    "file_contains:greeting.txt:Hello, Nathan!"
  ]
}
```

#### Child `review_node`

Simulated response:

```json
{
  "status": "PASS",
  "summary": "Implementation is small, aligned with the child goal, and produced expected outputs.",
  "findings": []
}
```

#### Child `test_node`

Subtool:

```text
python -m pytest tests/test_app.py
```

Simulated response:

```text
============================= test session starts =============================
collected 1 item

tests/test_app.py .                                                     [100%]

============================== 1 passed in 0.08s ==============================
```

#### Child `update_provenance`

Simulated response:

```json
{
  "status": "OK",
  "entities_indexed": 3,
  "relations_updated": 2
}
```

#### Child `build_node_docs`

Simulated response:

```json
{
  "status": "OK",
  "outputs": [
    ".ai/docs/task_v1/local.md"
  ]
}
```

#### Child `finalize_node`

Simulated response:

```json
{
  "status": "OK",
  "node_version_id": "task_v1",
  "lifecycle_state": "COMPLETE",
  "final_commit_sha": "taskfinal123"
}
```

### Stage F: parent wait, reconcile, review, merge

Task:

- `wait_for_children`

Simulated response:

```yaml
children:
  - node_version_id: task_v1
    state: COMPLETE
overall_ready: true
```

Task:

- `reconcile_children`

Compiled subtasks:

1. `reset_to_seed`
2. `merge_children`
3. `record_merge_metadata`
4. `write_summary`

#### `reset_to_seed`

```json
{
  "status": "OK",
  "seed_commit_sha": "planseed001",
  "head_after_reset": "planseed001"
}
```

#### `merge_children`

```json
{
  "status": "OK",
  "merged_children": [
    {
      "node_version_id": "task_v1",
      "final_commit_sha": "taskfinal123",
      "merge_order": 1
    }
  ],
  "head_after_merge": "planmerge456"
}
```

Task:

- `validate_node`

```json
{
  "status": "PASS",
  "summary": "Merged parent branch contains required outputs and summaries."
}
```

Task:

- `review_node`

```json
{
  "status": "PASS",
  "summary": "Merged parent output still matches the original request."
}
```

Task:

- `test_node`

```json
{
  "status": "PASS",
  "summary": "Plan-level testing requirements are satisfied."
}
```

Task:

- `update_provenance`

```json
{
  "status": "OK",
  "entities_indexed": 4,
  "relations_updated": 3
}
```

Task:

- `build_node_docs`

```json
{
  "status": "OK",
  "outputs": [
    ".ai/docs/plan_v1/local.md"
  ]
}
```

Task:

- `finalize_node`

```json
{
  "status": "OK",
  "node_version_id": "plan_v1",
  "lifecycle_state": "COMPLETE",
  "final_commit_sha": "planfinal789",
  "merge_to_base": "not_performed"
}
```

### Final inspectable state

```text
ai-tool tree show --node plan_v1
```

```text
plan_v1  COMPLETE  Getting started greeting example
└── task_v1  COMPLETE  Greeting generator task
```

---

## Simulation 2: Adding a new project

### Goal

Bring a new repository under orchestration control with project-local policy, YAML extensions, and overrides.

### Important note from the current docs

The notes do not yet define one frozen `project create` command.

So the current best simulation is a bootstrap flow built from:

- project-local `.ai/` files
- YAML validation
- override compatibility checks
- first node compilation in that project

### Step 1: bootstrap project-local YAML

The operator adds a local `.ai/` tree:

```text
.ai/
  policies/
    project.yaml
  testing/
    python_default.yaml
  docs/
    local_node_docs.yaml
  overrides/
    nodes/
      plan.yaml
    tasks/
      review_node.yaml
```

### Example project policy

```yaml
project_policy_definition:
  id: project_defaults
  defaults:
    auto_run_children: true
    require_review_before_finalize: true
    require_testing_before_finalize: true
    require_docs_before_finalize: true
    auto_merge_to_base: false
```

### Example testing definition

```yaml
testing_definition:
  id: project_python_tests
  name: Python default node tests
  applies_to:
    node_kinds:
      - task
    lifecycle_points:
      - before_finalize
  scope: unit
  description: Run focused pytest for project work.
  commands:
    - command: python -m pytest
      working_directory: .
  retry_policy:
    max_attempts: 1
    rerun_failed_only: false
  pass_rules:
    require_exit_code_zero: true
    max_failed_tests: 0
  on_result:
    pass_action: continue
    fail_action: fail_to_parent
```

### Example node override

```yaml
override_definition:
  id: project.plan.override
  target:
    family: node_definition
    document_id: plan
  compatibility:
    min_schema_version: 2
    built_in_version: "2.x"
  merge_mode: deep_merge
  changes:
    policies:
      auto_run_children: true
      auto_merge_to_base: false
```

### Step 2: validate project YAML

Simulated operator actions:

```text
ai-tool yaml validate --path .ai/policies/project.yaml
ai-tool yaml validate --path .ai/testing/python_default.yaml
ai-tool yaml validate --path .ai/overrides/nodes/plan.yaml
```

Simulated responses:

```json
{"status":"OK","family":"project_policy_definition"}
{"status":"OK","family":"testing_definition"}
{"status":"OK","family":"override_definition"}
```

### Step 3: first compile attempt

The operator creates the first top-level node in the new project:

```text
ai-tool node create \
  --kind plan \
  --title "Bootstrap greeting feature" \
  --file .ai/requests/bootstrap.yaml
```

Compilation stages from the latest notes:

1. source discovery
2. source loading
3. extension resolution
4. override resolution
5. schema validation
6. policy resolution
7. hook expansion
8. workflow compilation
9. compiled graph validation
10. workflow persistence

### Successful compile simulation

```json
{
  "status": "OK",
  "node_version_id": "proj_plan_v1",
  "compiled_workflow_id": "cw_proj_plan_v1",
  "built_in_version": "2.3.0",
  "override_warnings": []
}
```

### What the system should have persisted

- `source_documents` rows for:
  - built-in `nodes/plan.yaml`
  - built-in task documents
  - local policy YAML
  - local testing definition
  - local node override
- `compiled_workflow_sources` rows linking all of those to `cw_proj_plan_v1`
- resolved merged YAML

### Compile failure variant

If the project shipped an override targeting a non-existent built-in task:

```yaml
target:
  family: task_definition
  document_id: review_node_old_name
```

the latest notes say this should fail compilation visibly and durably.

#### Simulated failed compile response

```json
{
  "status": "FAIL",
  "failure_stage": "override_resolution",
  "failure_class": "override_missing_target",
  "summary": "Override target task_definition/review_node_old_name was not found."
}
```

#### Expected durable record

```yaml
compile_failure:
  node_version_id: proj_plan_v1
  failure_stage: override_resolution
  failure_class: override_missing_target
  target_family: task_definition
  target_id: review_node_old_name
```

That matters for onboarding because the current docs explicitly reject hidden or transient compile errors.

### Step 4: inspect the project’s resolved workflow

Simulated operator actions:

```text
ai-tool workflow show --node proj_plan_v1
ai-tool yaml resolved --node proj_plan_v1
```

Simulated response summary:

```yaml
workflow:
  built_in_version: 2.3.0
  local_policy_applied: true
  overrides_applied:
    - project.plan.override
  testing_definitions_applied:
    - project_python_tests
```

### Step 5: start the first real run

At this point, the new project behaves like any other project in the system:

- it has its own policy
- it has its own testing definition
- it may have project-local docs/review overrides
- future nodes compile against built-in YAML plus those project-local layers

The operator can now run:

```text
ai-tool node run start --node proj_plan_v1
```

That is the practical meaning of “adding a new project” under the current notes.

---

## Simulation 3: Rebuild from a specific node and re-merge parents

### Goal

Start from one changed node, create a candidate rebuilt lineage, re-merge parents from seed, and cut over only after the rebuilt path is stable.

### Starting authoritative tree

Assume the current authoritative tree is:

```text
plan_v1
├── task_parser_v1
└── task_greeting_v1
```

Assume both child tasks and the parent are `COMPLETE`.

Final commits:

- `task_parser_v1.final = parser111`
- `task_greeting_v1.final = greet111`
- `plan_v1.final = plan111`

### Change request

The user wants to change the greeting task so it also supports an optional sign-off line.

The operator targets the specific node:

```text
ai-tool node regenerate --node task_greeting_v1
```

### Step 1: create a candidate superseding node version

This follows the latest rectification and cutover notes:

- the old lineage stays authoritative
- the new lineage is a candidate until the rebuilt path is stable

#### Simulated response

```json
{
  "status": "OK",
  "supersedes": "task_greeting_v1",
  "new_node_version_id": "task_greeting_v2",
  "authoritative_cutover": "pending_upstream"
}
```

### Step 2: compile the candidate workflow

Simulated response:

```json
{
  "status": "OK",
  "node_version_id": "task_greeting_v2",
  "compiled_workflow_id": "cw_task_greeting_v2",
  "candidate_lineage": true
}
```

At this point:

- `task_greeting_v1` remains authoritative
- `task_greeting_v2` exists as a non-authoritative candidate

### Step 3: run the regenerated node

The changed node is a leaf task, so there are no descendants to regenerate.

Its candidate run executes its own workflow:

1. `research_context`
2. `execute_node`
3. `validate_node`
4. `review_node`
5. `test_node`
6. `update_provenance`
7. `build_node_docs`
8. `finalize_node`

#### Simulated execution prompt

```text
Update the greeting feature to support an optional sign-off line in the config.
Maintain existing behavior when sign-off is absent.
Update tests accordingly.
```

#### Simulated finalization response

```json
{
  "status": "OK",
  "node_version_id": "task_greeting_v2",
  "lifecycle_state": "COMPLETE",
  "final_commit_sha": "greet222",
  "authoritative": false
}
```

### Step 4: create candidate parent lineage

The latest notes imply upstream lineage cutover, not local-only cutover.

So the system now creates a candidate parent version:

```json
{
  "status": "OK",
  "supersedes": "plan_v1",
  "new_node_version_id": "plan_v2",
  "reason": "upstream_rectification_from_task_greeting_v2"
}
```

Now the system rectifies `plan_v2` from seed.

### Step 5: parent re-merge from seed

This is the important part.

The latest rectification notes say the parent should:

1. reset to seed
2. merge current child finals in deterministic order
3. run reconcile
4. run validation
5. run review
6. run testing
7. refresh provenance
8. build docs
9. finalize

### Deterministic merge inputs

Child finals selected:

- reuse current authoritative sibling final:
  - `task_parser_v1.final = parser111`
- use candidate rebuilt child final:
  - `task_greeting_v2.final = greet222`

Because only `task_greeting` changed, the unchanged sibling is reused.

### Simulated parent rectify task

Task:

- `rectify_node_from_seed`

Compiled subtasks:

1. `reset_to_seed`
2. `merge_children`
3. `record_merge_metadata`
4. `run_prompt` for parent-local reconcile
5. `validate`
6. `review`
7. `run_tests`
8. `update_provenance`
9. `build_docs`
10. `finalize_node`

#### `reset_to_seed`

```json
{
  "status": "OK",
  "node_version_id": "plan_v2",
  "seed_commit_sha": "planseed001",
  "head_after_reset": "planseed001"
}
```

#### `merge_children`

```json
{
  "status": "OK",
  "merge_order": [
    "task_parser_v1",
    "task_greeting_v2"
  ],
  "merged_commits": [
    "parser111",
    "greet222"
  ],
  "head_after_merge": "planmerge222"
}
```

#### `record_merge_metadata`

```json
{
  "status": "OK",
  "merge_event_id": "merge_evt_plan_v2_1"
}
```

#### Parent-local reconcile prompt

```text
Reconcile the parent output after merging the rebuilt greeting child.
Ensure summaries, acceptance status, and parent-local artifacts remain correct.
Return JSON status and any required parent-local changes.
```

#### Simulated response

```json
{
  "status": "OK",
  "summary": "Parent reconcile completed with no additional code changes required beyond metadata and summaries."
}
```

#### Validation

```json
{
  "status": "PASS",
  "summary": "Merged parent state is structurally valid."
}
```

#### Review

```json
{
  "status": "PASS",
  "summary": "Parent output remains aligned with the updated request."
}
```

#### Testing

```json
{
  "status": "PASS",
  "summary": "Merged tree tests pass."
}
```

#### Provenance

```json
{
  "status": "OK",
  "entities_indexed": 5,
  "relations_updated": 4
}
```

#### Docs

```json
{
  "status": "OK",
  "outputs": [
    ".ai/docs/plan_v2/local.md"
  ]
}
```

#### Finalize candidate parent

```json
{
  "status": "OK",
  "node_version_id": "plan_v2",
  "lifecycle_state": "COMPLETE",
  "final_commit_sha": "plan222",
  "authoritative": false
}
```

### Step 6: conservative cutover

The latest cutover note changes the simulation here.

The system should not mark `task_greeting_v2` or `plan_v2` authoritative too early.

Only after the required rebuilt path is stable does cutover happen.

#### Simulated cutover decision

```json
{
  "status": "OK",
  "cutover_scope": "upstream_lineage",
  "replaced_versions": [
    "task_greeting_v1",
    "plan_v1"
  ],
  "new_authoritative_versions": [
    "task_greeting_v2",
    "plan_v2"
  ]
}
```

After cutover:

- `task_parser_v1` remains authoritative and unchanged
- `task_greeting_v2` becomes authoritative
- `plan_v2` becomes authoritative
- `task_greeting_v1` and `plan_v1` become superseded historical versions

### Final authoritative tree

```text
plan_v2
├── task_parser_v1
└── task_greeting_v2
```

### Inspectable lineage

Operator actions:

```text
ai-tool node lineage --node task_greeting_v2
ai-tool node lineage --node plan_v2
ai-tool tree show --node plan_v2
```

Simulated responses:

```yaml
task_greeting_lineage:
  supersedes: task_greeting_v1
  authoritative: true

plan_lineage:
  supersedes: plan_v1
  authoritative: true
```

### Failure variant: parent merge conflict

If `plan_v2` hit a merge conflict during `merge_children`:

#### Simulated response

```json
{
  "status": "FAIL",
  "failure_class": "merge_conflict_unresolved",
  "merge_event_id": "merge_evt_plan_v2_1",
  "conflict_record_id": "merge_conflict_1"
}
```

The latest notes imply:

- persist the conflict
- do not cut over
- old authoritative lineage remains active
- route into reconcile/conflict-resolution or pause/fail policy

So the safe state would be:

- `plan_v1` stays authoritative
- `task_greeting_v2` remains only a candidate success below a failed upstream rebuild
- operator can inspect conflict history and decide next action

---

## Why these simulations changed

Compared with the earlier version, the current notes now make several things much clearer:

- adding a project is mainly a YAML/bootstrap plus first-compile story, not just “start running nodes”
- child materialization must be validated and idempotent before scheduling
- compile failures are first-class durable events
- subtree rebuilds produce candidate lineages, not instant replacements
- parent re-merge should explicitly reuse unchanged sibling finals and only cut over after the rebuilt upstream path is stable

That produces simulations that are stricter, safer, and closer to the intended system behavior.
