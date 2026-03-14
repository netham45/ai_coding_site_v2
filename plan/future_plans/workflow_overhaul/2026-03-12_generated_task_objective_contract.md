# Generated Task Objective Contract

## Purpose

Define the future prompt and objective contract for tasks generated from a reusable task-sequence template.

This replaces the checklist-item prompt concept.

It is not an active runtime prompt-pack contract yet.

## Core Rule

A generated task is still just a task.

Its prompt should follow the normal task-profile contract for its semantic role.

The template contributes structured objective context, expected outputs, proving targets, and dependency lineage.

## Required Additions Beyond Normal Task Prompts

Generated tasks should receive:

- the originating template id
- the originating step id
- the step objective
- the step dependencies and upstream generated siblings
- any template-defined expected outputs
- any template-defined proving targets

## What Should Not Exist

The runtime should not need:

- a checklist-item prompt family
- active-item-only mutations
- checklist-specific allowed options
- checklist-specific terminal item results

Generated tasks should complete through the same result-registration path as other tasks.

## Suggested Injected Context

```yaml
template_context:
  template_id: e2e_route_v1
  step_id: prove_real_e2e
  generated_from_owner_node_id: uuid
  depends_on_step_ids:
    - inspect_contract
  expected_outputs:
    - real_e2e_test
  proving_targets:
    - tests/e2e/test_flow_02_compile_or_recompile_workflow_real.py
```

## Prompt Safety Rule

Template provenance should help clarify why the task exists.

It should not weaken daemon authority over:

- task legality
- dependency readiness
- completion validation
- blocker registration
- result persistence
