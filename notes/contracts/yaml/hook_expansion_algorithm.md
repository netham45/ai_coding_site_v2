# Hook Expansion Algorithm

## Purpose

This document defines how hooks should be resolved and expanded into concrete workflow stages during compilation.

Hooks are already part of the architecture, but without a clear expansion algorithm they remain a source of ambiguity:

- multiple hooks may target the same lifecycle point
- hooks may overlap with explicit task/subtask stages
- hook ordering may affect correctness
- hook expansion may change quality-gate behavior

This document turns hooks into a deterministic compilation mechanism rather than a vague extension concept.

Related documents:

- `notes/specs/yaml/yaml_schemas_spec_v2.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/planning/expansion/review_testing_docs_yaml_plan.md`
- `notes/contracts/yaml/override_conflict_semantics.md`
- `notes/catalogs/traceability/cross_spec_gap_matrix.md`

---

## Core Rule

Hooks must compile into explicit durable workflow stages or checks.

That means:

- hooks are not hidden runtime side effects
- hooks do not run “magically” at execution time without compiled representation
- hook expansion is part of workflow compilation
- the result of hook expansion must be inspectable in the compiled workflow

Implementation staging note:

- the current implementation performs compile-time expansion for policy and node hook refs and persists the result in `compiled_workflows.resolved_yaml.hook_expansion`
- hook-backed compiled subtasks are marked with `inserted_by_hook = true` plus a deterministic `inserted_by_hook_id`
- this first slice intentionally skips conditional `if` matching and runtime-only triggers such as `on_node_created` and `on_merge_conflict`; those hooks are reported as skipped rather than executed implicitly

---

## Hook Expansion Inputs

Hook expansion should consider:

- node kind and tier
- current task ID
- current subtask type
- lifecycle insertion point
- project policy refs
- explicit hook refs on the node/task
- hook applicability filters
- changed entity conditions if used

Hooks should be resolved against the same source-lineage model as other workflow-affecting YAML.

---

## Hook Selection Rule

At a given insertion point, a hook is selected only if:

- its `when` matches the insertion point
- its `applies_to` filters match current context
- its conditional `if` clauses match current context if present

If a hook does not match all required conditions:

- it is not expanded

The compiler should be able to explain why a hook was selected or not selected.

---

## Hook Insertion Points

The hook system currently assumes insertion points such as:

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
- `before_task`
- `after_task`
- `before_subtask`
- `after_subtask`
- `on_subtask_failure`
- `before_validation`
- `after_validation`
- `before_review`
- `after_review`
- `before_testing`
- `after_testing`
- `before_merge_children`
- `after_merge_children`
- `on_merge_conflict`

The algorithm should treat each insertion point as its own expansion context.

---

## Hook Expansion Output

The result of hook expansion should be:

- concrete inserted compiled stages
- explicit inserted checks
- durable metadata showing which hook inserted them
- deterministic ordering at each insertion point

Compiled subtasks should preserve:

- `inserted_by_hook = true`
- `inserted_by_hook_id`

---

## Ordering Rule

Multiple hooks at the same insertion point need deterministic ordering.

Recommended precedence:

1. explicit hook priority if the system later supports it
2. source precedence order
3. hook ID as deterministic final tiebreaker

Because explicit priority is not yet formalized, recommended current default is:

1. built-in hooks first
2. project extension hooks second
3. project override-produced hook changes resolved before insertion
4. final deterministic ordering by hook ID within each source precedence layer

Implementation staging note:

- the current implementation sorts hook expansion by insertion phase, then source precedence (`yaml_builtin_system` before `yaml_project`), then relative path and hook ID

This makes ordering predictable even before a richer priority model exists.

---

## Composition Rule

Hooks should compose by insertion, not by mutating each other at runtime.

That means:

- each matching hook expands into its own concrete stage(s)
- the compiler produces the final ordered list
- runtime executes only the compiled result

This avoids hidden dynamic hook chaining behavior.

---

## Hook vs Explicit Stage Rule

If a workflow already contains an explicit stage semantically equivalent to a hook-generated stage, the system must avoid accidental duplication.

Recommended default:

- hooks should not silently deduplicate against explicit stages unless the family defines a clear equivalence rule

Safer default behavior:

- expand hooks explicitly
- let duplicate or conflicting stage patterns fail validation if dangerous

Reason:

- silent deduplication can hide why a stage is missing
- explicit duplication is easier to diagnose than invisible suppression

---

## Hook Families Most Likely To Need Careful Handling

These hook classes are the most semantically sensitive:

### Validation hooks

Risk:

- duplicate validation insertion
- validation ordering drift

### Review hooks

Risk:

- review stages appearing before required prerequisites

### Testing hooks

Risk:

- testing inserted in the wrong position relative to review or finalize

### Docs/provenance hooks

Risk:

- docs or provenance stages duplicated or placed too early

### Merge/rectification hooks

Risk:

- merge conflict handling becoming non-deterministic

---

## Canonical Ordering Relative To Quality Gates

The hook system must not violate the built-in canonical order unless policy explicitly allows it.

Default order remains:

1. reconcile
2. validation
3. review
4. testing
5. provenance
6. docs
7. finalize

So for example:

- `before_review` hooks must occur after validation context is available
- `before_testing` hooks must occur after review
- docs hooks should not sneak docs generation ahead of testing unless explicitly allowed

---

## Expansion Strategy

The compiler should expand hooks in phases.

## Phase 1: Collect candidate hooks

Gather all hooks from:

- built-in definitions
- project extensions
- project overrides
- project policy refs
- node/task explicit refs

## Phase 2: Filter by applicability

Keep only hooks matching current node/task/subtask/lifecycle context.

## Phase 3: Order hooks deterministically

Sort matching hooks according to the ordering rule.

## Phase 4: Expand hooks into concrete units

Convert each hook’s `run` entries into:

- concrete inserted subtasks
- inserted checks
- inserted review/testing/docs stages where appropriate

## Phase 5: Validate resulting structure

Check for:

- invalid stage order
- invalid duplicate-sensitive patterns
- dependency graph issues
- schema violations after insertion

If invalid:

- compilation fails

---

## Pseudocode

```python
def expand_hooks(workflow_context):
    candidates = collect_hook_candidates(workflow_context)
    matching = [
        hook for hook in candidates
        if hook_matches_context(hook, workflow_context)
    ]

    ordered = order_hooks(matching)
    inserted = []

    for hook in ordered:
        units = compile_hook_run_units(hook, workflow_context)
        inserted.extend(tag_units_with_hook_metadata(units, hook.id))

    expanded = insert_units_into_workflow(workflow_context, inserted)
    validate_expanded_workflow(expanded)
    return expanded
```

---

## Failure Conditions

Hook expansion should fail compilation if:

- hook ordering would violate required stage order
- a hook targets an invalid insertion point for the current context
- expanded units create an invalid dependency graph
- hook-generated output violates schema
- hook expansion causes unresolvable duplicate-sensitive behavior

These should be treated as compile failures, not runtime surprises.

---

## Duplicate-Sensitive Patterns

Certain patterns should be treated as especially risky.

Examples:

- two hooks both insert the same finalize stage
- multiple hooks inject incompatible review stages at one point
- multiple testing hooks create contradictory gate semantics
- a hook injects child-spawn logic into a task that already has explicit child materialization

Recommended default:

- detect and fail on risky duplicates rather than trying to guess user intent

---

## DB Implications

The current DB model already supports key parts of hook auditability through:

- `compiled_subtasks.inserted_by_hook`
- `compiled_subtasks.inserted_by_hook_id`
- `compiled_workflow_sources`

Possible future improvement:

- preserve hook expansion summaries or compile-time expansion diagnostics if debugging proves difficult

For a first implementation, the current compiled-workflow lineage fields may be enough.

---

## CLI Implications

The CLI should let operators inspect:

- which hooks are in effect
- which hooks matched a node/workflow
- which compiled subtasks were inserted by which hooks

Current and likely useful surfaces:

- `ai-tool hooks list --node <id>`
- `ai-tool hooks show --node <id>`
- `ai-tool workflow show --node <id>`

Potential useful addition:

- `ai-tool hooks explain --node <id>`

If names differ, the capability should still exist.

---

## Interaction With Overrides

Overrides may affect hook behavior by:

- changing hook definitions
- changing node/task applicability
- changing policy refs

Therefore:

- override resolution must happen before hook expansion
- hook expansion must use the fully resolved YAML model

This order must remain stable.

---

## Interaction With Manual Node Definitions

Manual or project-defined node/task structures may still use hooks.

The algorithm should not assume only the built-in semantic ladder exists.

It should care only about:

- the current resolved workflow context
- the insertion point
- hook applicability rules

---

## Open Decisions Still Remaining

### D01. Explicit hook priority

Recommended current direction:

- optional future enhancement
- use deterministic source precedence plus hook ID now

### D02. Duplicate-equivalence detection

Recommended current direction:

- keep this narrow
- fail on risky duplicates rather than attempting broad semantic deduplication

### D03. Hook expansion diagnostics

Recommended current direction:

- optional future improvement unless debugging needs prove it necessary

---

## Recommended Next Follow-On Work

The next docs that should absorb this logic are:

1. `notes/specs/yaml/yaml_schemas_spec_v2.md`
2. `notes/specs/runtime/runtime_command_loop_spec_v2.md`
3. `notes/catalogs/traceability/cross_spec_gap_matrix.md`

Then reduce the severity of the hook-expansion gap.

---

## Exit Criteria

This note is complete enough when:

- hook selection is explicit
- ordering is explicit
- composition is explicit
- duplicate-sensitive behavior is explicit
- compile-failure conditions are explicit

At that point, hooks are deterministic enough to be safe as part of the orchestration system.
