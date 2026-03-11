You are generating a plan layout for node `{{node_id}}`.

Inputs:
- phase goal: `{{node.title}}`
- acceptance criteria: `{{acceptance_criteria}}`
- user request: `{{user_request}}`

Your job:
- create the minimum coherent set of `plan` children needed to deliver the phase

Requirements:
- each child must have a clear execution boundary
- dependencies must be explicit and minimal
- outputs and acceptance criteria must be concrete
- do not create children that merely restate the phase title

Layout schema:
- the file must be valid YAML with top-level keys:
  - `kind: layout_definition`
  - `id`
  - `name`
  - `description`
  - `children`
- each `children` entry must include:
  - `id`
  - `kind: plan`
  - `tier: 2`
  - `name`
  - `goal`
  - `rationale`
  - `dependencies`
  - `acceptance`
  - `ordinal`

Minimal example:
```yaml
kind: layout_definition
id: phase_to_single_plan
name: Phase To Single Plan
description: Minimal generated plan layout.
children:
  - id: implementation_plan
    kind: plan
    tier: 2
    name: Implementation Plan
    goal: Execute the requested delivery path.
    rationale: Keep the decomposition minimal and directly executable.
    dependencies: []
    acceptance:
      - The requested delivery path is concrete.
    ordinal: 1
```

Output contract:
- produce a valid `layout_definition`
- keep the structure executable, reviewable, and small
- write the approved layout to `layouts/generated_layout.yaml`
- immediately register that file with `python3 -m aicoding.cli.main node register-layout --node {{node_id}} --file layouts/generated_layout.yaml`
- do not assume the daemon will discover `layouts/generated_layout.yaml` unless it has been registered explicitly

Required CLI workflow:
1. Resolve the live compiled subtask UUID:
   - `python3 -m aicoding.cli.main subtask current --node {{node_id}}`
   - read `state.current_compiled_subtask_id` from that output and use that UUID in later `--compiled-subtask` flags
2. Mark the subtask attempt started:
   - `python3 -m aicoding.cli.main subtask start --node {{node_id}} --compiled-subtask CURRENT_COMPILED_SUBTASK_ID`
3. Inspect the current context before writing the layout:
   - `python3 -m aicoding.cli.main subtask context --node {{node_id}}`
4. Generate `layouts/generated_layout.yaml` and register it immediately.
5. When the layout is registered successfully:
   - write a concise summary to `summaries/layout_generation.md`
   - record success and let the daemon route the workflow with:
     `python3 -m aicoding.cli.main subtask succeed --node {{node_id}} --compiled-subtask CURRENT_COMPILED_SUBTASK_ID --summary-file summaries/layout_generation.md`
6. If blocked or unable to produce a valid registered layout:
   - write the blocker summary to `summaries/layout_generation_failure.md`
   - fail the subtask with:
     `python3 -m aicoding.cli.main subtask fail --node {{node_id}} --compiled-subtask CURRENT_COMPILED_SUBTASK_ID --summary-file summaries/layout_generation_failure.md`

Completion contract:
- after `subtask succeed`, follow the routed daemon outcome instead of manually chaining `summary register`, `subtask complete`, or `workflow advance`
- if the routed outcome is `next_stage`, fetch the next stage prompt with `python3 -m aicoding.cli.main subtask prompt --node {{node_id}}` and continue in the same session
- if the routed outcome is `completed`, stop and do not probe the closed parent run with additional low-level workflow commands
