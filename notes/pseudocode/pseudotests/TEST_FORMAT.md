# Pseudotest Format

## Purpose

Define a canonical structure for pseudotests so AI and human reviewers can evaluate the pseudocode package consistently.

This is not an executable runner format yet. It is the normalized review format that the current markdown pseudotests should follow.

---

## Canonical case structure

Each pseudotest case should contain:

1. `Scenario`
2. `Applies to`
3. `Preconditions`
4. `Action`
5. `Expected durable effects`
6. `Expected forbidden effects`
7. `Expected operator-visible results`
8. `Pass rule`

`Expected forbidden effects` is important. Many of these tests are checking that the system does *not* silently advance, mutate authority, or guess.

---

## Review method

To "run" a pseudotest against the current package:

1. identify the target module or state machine
2. trace the relevant happy path and failure branches
3. confirm each expected durable effect is explicitly represented
4. confirm each forbidden effect is explicitly prevented or contradicted by guards
5. confirm CLI/operator visibility is described
6. mark the case:
   - `pass`
   - `partial`
   - `fail`
7. capture the missing branch, state write, or guard if not `pass`

---

## Pass criteria

### `pass`

- the module or state machine explicitly supports the expected behavior
- required durable effects are present
- forbidden effects are clearly blocked

### `partial`

- the design direction is clear
- one or more required writes, guards, or inspection surfaces are still implied rather than explicit

### `fail`

- the artifact contradicts the expected behavior
- or the behavior is missing enough detail that the case cannot be evaluated honestly

---

## Minimal example

### `example_case_name`

Scenario:

- a node is paused on a user gate

Applies to:

- `modules/run_node_loop.md`
- `state_machines/node_lifecycle.md`

Preconditions:

- run is active
- current subtask returns `pause`

Action:

- evaluate one loop iteration

Expected durable effects:

- pause summary is registered
- run is transitioned to paused state

Expected forbidden effects:

- cursor must not advance
- run must not silently resume

Expected operator-visible results:

- pause reason is queryable

Pass rule:

- pass only if all three behavior classes above are explicit in the artifacts
