# Flow C: Execute One Compiled Subtask

Sources:

- `notes/runtime_pseudocode_plan.md`
- `notes/runtime_command_loop_spec_v2.md`

## Scenario

The active compiled subtask is a `run_prompt` inside `generate_child_layout`.

## Full task flow

### Step 1: fetch current work

```text
ai-tool subtask current --node plan_v1
ai-tool subtask prompt --node plan_v1
ai-tool subtask context --node plan_v1
```

Simulated context:

```yaml
compiled_subtask_id: cst_plan_014
type: run_prompt
task: generate_child_layout
context:
  user_prompt: Create a greeting generator...
  prior_summaries:
    - plan_research_summary
```

### Step 2: create attempt

Durable write:

```yaml
subtask_attempts:
  compiled_subtask_id: cst_plan_014
  attempt_number: 1
  status: STARTED
```

### Step 3: mark started

```text
ai-tool subtask start --compiled-subtask cst_plan_014
```

### Step 4: perform work

Prompt:

```text
Generate a one-child layout for a greeting feature task. Write it to
.ai/layouts/plan_v1.yaml and return JSON status.
```

Simulated AI response:

```json
{
  "status": "OK",
  "written_file": ".ai/layouts/plan_v1.yaml"
}
```

### Step 5: capture outputs

Runtime records:

- changed files
- summary text if present
- output artifact paths

### Step 6: run required validations

Example inferred checks:

```yaml
checks:
  - type: file_exists
    path: .ai/layouts/plan_v1.yaml
  - type: yaml_schema
    schema: layout_definition
```

### Step 7: accept or reject completion

If checks pass:

```text
ai-tool subtask complete --compiled-subtask cst_plan_014
ai-tool workflow advance --node plan_v1
```

If checks fail:

- retry
- pause
- or fail to parent

## Logic issues exposed

1. The runtime loop says completion must be daemon-validated, but the exact semantics of `subtask complete` versus daemon-side acceptance are still not fully frozen.
2. Many built-in tasks are named, but their exact output contracts are still inferred rather than explicitly authored YAML.

