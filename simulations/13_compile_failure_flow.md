# Compile Failure Flow

Source:

- `notes/compile_failure_persistence.md`

## Scenario

An override targets a missing built-in task definition.

## Full task flow

Compilation stages:

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

Failure occurs at stage 4.

## Simulated result

```json
{
  "status": "FAIL",
  "failure_stage": "override_resolution",
  "failure_class": "override_missing_target",
  "summary": "Override target task_definition/review_node_old_name was not found."
}
```

Durable effect:

- node does not become `READY`
- compile failure record is persisted
- no run may start

## Logic issues exposed

1. Compile failure is now canonically visible through `COMPILE_FAILED`, but the exact event vocabulary around compile attempts still needs to be normalized across notes and simulations.
