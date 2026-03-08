# Getting Started: Running A First Prompt Through The System

## Purpose

This guide describes a spec-aligned "first real task" for this project.

It is intentionally more complex than a pure hello world, but still small enough to understand end to end. The goal is to exercise the system shape described in the notes:

- YAML-defined nodes, tasks, and subtasks
- immutable workflow compilation
- CLI-driven AI execution
- validation and review gates
- durable run state

This is a hypothetical guide. The repo currently contains design notes, not a finished runtime, so the commands below describe the intended operator experience.

---

## The starter scenario

The user enters a prompt at the command line asking the system to build a tiny "greeting generator" feature in a target codebase:

- read a config file such as `greetings.yaml`
- generate a `greeting.txt` artifact
- add a small test or verification command
- write a summary of what changed

Why this is a good first task:

- it produces a real file, not just terminal output
- it forces the task to satisfy checks
- it is small enough for one node tree
- it touches prompt work, command work, validation, and finalization

---

## The command-line entrypoint

The getting-started guide should begin with a command that feels like the real product surface.

Hypothetical command:

```text
ai-tool node create \
  --kind plan \
  --title "Getting started greeting example" \
  --prompt "Create a small config-driven greeting generator. Add greetings.yaml, generate greeting.txt, verify it with a repeatable command, and summarize the work."
```

If you want a more explicit workflow-oriented surface, it could instead look like:

```text
ai-tool workflow start \
  --kind plan \
  --prompt "Create a small config-driven greeting generator. Add greetings.yaml, generate greeting.txt, verify it with a repeatable command, and summarize the work."
```

The exact command name is less important than the behavior:

- the operator provides a freeform user prompt
- the runtime chooses or resolves the appropriate node definition
- a top-level plan node version is created
- YAML is resolved and compiled into an immutable workflow
- a node run is started

That is the right "hello world" entrypoint for this project.

---

## What to model behind that command

For a first pass, use the default ladder described in the notes even though the architecture is tier-agnostic:

- `plan` node as the top node
- one child `task` node that implements the greeting feature

That keeps the example simple while still exercising:

- manual tree construction
- child creation through a layout
- parent waiting on child completion
- final merge/reconcile behavior

---

## The example outcome

The child task should accomplish something like this in a sample repo:

1. create `greetings.yaml`
2. add a small script or program that reads it
3. generate `greeting.txt` containing a greeting for a named user
4. add a test or validation command that proves the output is correct
5. write a short summary artifact for the parent

That is "hello world, but more complex" because it is no longer just "print a string". It requires inputs, outputs, validation, and recorded completion state.

---

## What the CLI call should do

A successful first-run story should read like this:

1. the user runs one command with a prompt
2. the system creates a top-level `plan` node from that prompt
3. the plan node generates a layout with one child `task`
4. the child task implements the greeting feature
5. validations pass
6. summaries are written
7. the operator can inspect status, prompts, subtasks, and outputs through the CLI

This makes the project feel like an orchestration tool rather than a pile of YAML files.

---

## Minimal artifact set

The notes imply a starter task should need at least these artifact types:

- a node definition
- a task definition
- a child layout
- validation checks
- a compiled workflow snapshot
- a node run and subtask attempts

A plausible project-local layout behind that command would be:

```text
.ai/
  overrides/
    nodes/
    tasks/
    layouts/
  layouts/
    getting_started_plan.yaml
  summaries/
```

---

## Step 1: Resolve the prompt into a top node

The CLI prompt should map onto a top-level `plan` node whose job is to coordinate one child implementation task.

Conceptually, the system is doing something like:

- choose the `plan` node definition
- inject the user's prompt into node creation context
- create the node version
- compile the workflow snapshot

Example shape for that resolved node definition:

```yaml
node_definition:
  id: getting_started_plan
  kind: plan
  tier: plan
  description: Create a small greeting generator feature through one child task.
  main_prompt: >
    You are the plan node for a starter exercise. Create and supervise a single
    child task that adds a greeting generator feature, validates it, reviews it,
    and returns a concise implementation summary.
  entry_task: orchestrate_getting_started
  available_tasks:
    - orchestrate_getting_started
    - reconcile_and_finalize
  policies:
    max_node_regenerations: 2
    max_subtask_retries: 2
    child_failure_threshold_total: 1
    child_failure_threshold_consecutive: 1
    require_review_before_finalize: true
    auto_run_children: true
    auto_rectify_upstream: false
    auto_merge_to_parent: false
    auto_merge_to_base: false
  hooks: []
```

The user should not need to hand-write this to get started. The point is that the CLI entrypoint should create a node that behaves like this.

This matches the notes in three important ways:

- the node is declared by `kind` and `tier`
- execution starts from an `entry_task`
- policy is explicit rather than hidden in code

---

## Step 2: Run the parent task flow

The top node does not implement the feature itself. It turns the user's prompt into a child task, waits, then finalizes.

Example parent task:

```yaml
task_definition:
  id: orchestrate_getting_started
  name: Orchestrate starter task
  description: Spawn one child implementation task and wait for it to finish.
  applies_to_kinds:
    - plan
  policy:
    max_subtask_retries: 1
    on_failure: pause_for_user
  subtasks:
    - id: build_child_layout
      type: run_prompt
      title: Build child layout
      description: Create the layout for the single greeting task child.
      prompt: >
        Write a layout file describing one child task node named
        greeting_task. The child must create a config-driven greeting feature,
        verify it, and summarize its work.
      checks:
        - type: file_exists
          path: .ai/layouts/getting_started_plan.yaml
    - id: wait_for_child
      type: wait_for_children
      title: Wait for child completion
      description: Block until the greeting child task completes.
      requires:
        - subtask_complete: build_child_layout
    - id: finalize_parent
      type: finalize_node
      title: Finalize parent node
      description: Finalize the plan after child completion.
      requires:
        - subtask_complete: wait_for_child
```

This follows the lifecycle notes: tasks own ordered subtasks, and waiting is a first-class subtask type.

---

## Step 3: Generate the child layout

The layout is where the plan turns the user's prompt into a concrete child node to create.

Example:

```yaml
layout_definition:
  children:
    - id: greeting_task
      kind: task
      tier: task
      name: Greeting generator task
      goal: >
        Add a config-driven greeting generator that creates greeting.txt and
        prove it works with a repeatable validation command.
      rationale: >
        This is the smallest useful task that exercises file creation, command
        execution, validation, and summary reporting.
      dependencies: []
      acceptance:
        - greetings.yaml exists
        - greeting.txt is generated
        - validation command succeeds
        - summary artifact is written
```

This uses the generic `children` schema from the YAML notes rather than hardcoding `tasks:`.

---

## Step 4: Execute the child implementation task

This is the important piece. It should exercise the canonical subtask loop:

- gather context
- do the work
- validate
- review
- summarize
- finalize

Example:

```yaml
task_definition:
  id: implement_greeting_feature
  name: Implement greeting feature
  description: Create and verify a small greeting generator.
  applies_to_kinds:
    - task
  policy:
    max_subtask_retries: 2
    on_failure: fail_to_parent
  subtasks:
    - id: gather_context
      type: build_context
      title: Gather repo context
      description: Inspect the target repo and identify where the feature belongs.
    - id: write_feature
      type: run_prompt
      title: Implement the feature
      description: Create the config file, implementation, and output artifact.
      requires:
        - subtask_complete: gather_context
      prompt: >
        Add a minimal greeting generator. Create greetings.yaml, implement the
        code that reads it, generate greeting.txt, and keep the change small and
        consistent with the repo.
      checks:
        - type: file_exists
          path: greetings.yaml
        - type: file_exists
          path: greeting.txt
    - id: validate_feature
      type: validate
      title: Validate the feature
      description: Run the project command that proves the greeting output is correct.
      requires:
        - subtask_complete: write_feature
      command: ./scripts/validate-greeting.sh
      checks:
        - type: command_exit_code
          command: ./scripts/validate-greeting.sh
          exit_code: 0
    - id: review_feature
      type: review
      title: Review the change
      description: Review the implementation for correctness and gaps.
      requires:
        - subtask_complete: validate_feature
    - id: write_summary
      type: write_summary
      title: Write node summary
      description: Persist a concise summary for parent introspection.
      requires:
        - subtask_complete: review_feature
      outputs:
        - type: summary_written
          path: .ai/summaries/greeting_task.md
    - id: finalize_node
      type: finalize_node
      title: Finalize task node
      description: Mark the task complete and record final state.
      requires:
        - subtask_complete: write_summary
```

For a starter exercise, this is enough. It touches the main runtime ideas without requiring sibling dependencies, pushed child sessions, or rectification.

---

## Step 5: Walk the runtime flow

If the runtime described in the notes existed, the execution would look roughly like this:

1. The user runs `ai-tool workflow start ... --prompt "<user prompt>"`.
2. The system creates the `plan` node version for that prompt.
3. YAML plus overrides are resolved.
4. An immutable workflow snapshot is compiled.
5. A node run starts and binds a tmux-backed AI session.
6. The parent subtasks run until the child layout is produced.
7. The child `task` node is spawned from that layout.
8. The child runs through its compiled subtasks.
9. Subtask attempts, validations, summaries, and cursor movement are persisted.
10. The child finalizes, then the parent continues and finalizes.

The operator-facing and AI-facing loop together would look like:

```text
ai-tool workflow start --kind plan --prompt "<user prompt>"
ai-tool node show --node <plan-node-id>
ai-tool workflow show --node <plan-node-id>
ai-tool session bind --node <plan-node-id>
ai-tool subtask current --node <plan-node-id>
ai-tool subtask prompt --node <plan-node-id>
ai-tool subtask start --compiled-subtask <id>
ai-tool subtask complete --compiled-subtask <id>
ai-tool workflow advance --node <plan-node-id>
```

Then the same pattern repeats for the child task node, with `ai-tool node children --node <plan-node-id>` exposing the spawned child.

---

## What success should look like

A successful first task should leave evidence in all major system surfaces described by the notes.

### YAML / compilation

- source node/task/layout YAML exists
- overrides, if any, are traceable
- one compiled workflow snapshot exists per node version

### Runtime state

- a `node_run` exists for the parent and child
- `node_run_state` shows the current or final cursor state
- each subtask has at least one recorded attempt

### Files / repo state

- `greetings.yaml` exists
- `greeting.txt` exists
- the validation command passes
- a summary file exists for introspection

### Lifecycle

- child ends in `COMPLETE`
- parent ends in `COMPLETE` or a merge-approval pause state

If any one of those is missing, the system is not yet proving its full loop.

---

## What not to include in the first task

Do not make the first example too ambitious. Skip these initially:

- multiple sibling children
- sibling dependency waits
- pushed child research sessions
- subtree regeneration
- upstream rectification
- isolated containers
- documentation generation beyond a simple summary file

Those belong in later examples once the single-child flow is stable.

---

## Recommended next task after this one

Once this starter works, the next useful exercise is a two-child plan:

- child A implements a parser
- child B implements output formatting
- child B depends on child A

That would test:

- dependency admission
- deterministic child ordering
- parent merge/reconcile behavior
- richer CLI introspection

---

## Practical takeaway

If you want a "hello world" for this project, do not make it "print text".

Make it:

- one CLI command that accepts a user prompt
- one top node created from that prompt
- one child implementation node
- one real file output
- one real validation command
- one summary artifact

That is the smallest example that actually reflects the architecture described across the notes.
