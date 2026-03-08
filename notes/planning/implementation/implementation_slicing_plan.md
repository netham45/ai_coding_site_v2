# Implementation Slicing Plan

## Purpose

This document translates the current spec package into implementation slices.

The goal is to move from architecture/spec work into a build plan that:

- respects dependency order
- reduces risk early
- keeps the system inspectable as it grows
- avoids building high-level orchestration on top of unstable foundations

This is not a sprint plan with time estimates. It is a dependency-ordered implementation plan.

Related documents:

- `notes/planning/expansion/full_spec_expansion_plan.md`
- `notes/catalogs/inventory/major_feature_inventory.md`
- `notes/catalogs/traceability/spec_traceability_matrix.md`
- `notes/catalogs/traceability/cross_spec_gap_matrix.md`
- all `*_spec_v2.md` documents

---

## Implementation Strategy

The system should be built in layers.

Recommended strategy:

1. build durable core data and identity first
2. build workflow compilation second
3. build basic run execution third
4. add inspection and operator visibility early
5. add rectification and advanced recovery only after the base loop is reliable
6. treat support systems such as provenance/docs/isolation as bounded add-ons after the core runtime is stable

Reason:

- this architecture is highly stateful
- correctness depends more on durable orchestration than on UI polish or optional features
- hidden-state bugs will become expensive if the runtime loop is built before the data model and introspection surfaces are stable

---

## Slice 0: Spec Closure And Freeze

### Objective

Lock the minimum implementation-facing decisions that should not stay ambiguous during buildout.

### Required outputs

- freeze branch naming pattern
- freeze whether isolated environments are deferred or included as optional
- freeze whether compile failures get a dedicated table in first implementation
- freeze whether pause/workflow events get dedicated tables in first implementation
- freeze whether authoritative lineage gets explicit DB modeling in first implementation

### Why this comes first

These choices affect migrations, runtime ownership, and CLI behavior.

### Exit criteria

- no remaining critical design ambiguity blocks database or runtime work

---

## Slice 1: Core Database And Value Catalog

### Objective

Build the durable data backbone and bounded state vocabularies.

### Scope

- create core tables for node versions, hierarchy, dependencies
- create compiled workflow tables
- create runs, run state, attempts
- create sessions and session events
- create merge/rebuild lineage tables
- create prompts, summaries, docs, provenance tables
- create review/test/validation result tables if included in first implementation
- apply the state value catalog as enums/check constraints

### Features primarily covered

- F01
- F02
- F03
- F07
- F08
- F11
- F12
- F17
- F21
- F22
- F23
- F27
- F28
- F31
- F36

### Key risks

- under-modeled authority/current-version handling
- missing indexes for runtime-critical queries
- weak compile-failure or pause-event modeling

### Exit criteria

- migrations can represent the durable core model
- current-state and history views exist for core runtime inspection

---

## Slice 2: YAML Loader, Validator, And Compiler

### Objective

Build the source-loading and compilation layer that converts YAML into immutable workflows.

### Scope

- built-in YAML loading
- project extension loading
- override loading
- override merge semantics
- schema validation
- hook expansion
- workflow compilation
- compiled workflow persistence
- compile-failure persistence

### Features primarily covered

- F03
- F04
- F05
- F06
- F21
- F22
- F23
- F26
- F27
- F35
- F36

### Dependencies

- Slice 1

### Key risks

- bad override behavior making YAML unsafe
- hidden compile failure states
- hook expansion ambiguity

### Exit criteria

- a node version can compile into a stable workflow snapshot
- failure to compile is durably visible and inspectable

---

## Slice 3: Minimal Run Admission And Execution Loop

### Objective

Build the smallest end-to-end runnable orchestration loop for a single node with compiled subtasks.

### Scope

- run admission
- basic lifecycle transitions
- primary session binding
- current subtask retrieval
- subtask attempt creation and completion
- cursor advancement
- pause/failure recording
- basic summary registration

### Features primarily covered

- F07
- F09
- F10
- F11
- F12
- F24
- F25
- F31
- F36

### Dependencies

- Slice 1
- Slice 2

### Key risks

- unclear ownership between runtime and session
- cursor corruption
- invisible pause/failure state

### Exit criteria

- one compiled node can execute through a minimal workflow end to end
- state remains inspectable throughout execution

---

## Slice 4: Core CLI Introspection Surface

### Objective

Expose the durable model and execution state early so debugging is possible before advanced automation grows.

### Scope

- node show/tree/lineage/dependency commands
- run state commands
- workflow/task/subtask inspection commands
- prompt and summary inspection
- session inspection
- validation/review/testing result inspection
- merge/rebuild inspection

### Features primarily covered

- F10
- F11
- F15
- F17
- F18
- F21
- F22
- F23
- F28
- F30
- F31
- F36

### Dependencies

- Slice 1
- Slice 3

### Why this should come early

Without this, later failures in child orchestration, recovery, or rectification will be hard to diagnose.

### Exit criteria

- operators can inspect all important current runtime state
- AI sessions can retrieve current work through CLI

---

## Slice 5: Default YAML Library

### Objective

Author the built-in YAML files needed for the default semantic ladder and default task library.

### Scope

- default node YAMLs
- default task YAMLs
- default subtask templates or canonical shapes
- review/testing/docs YAMLs
- rectification YAMLs
- basic policies and hooks

### Features primarily covered

- F04
- F05
- F21
- F22
- F23
- F26
- F29
- F35

### Dependencies

- Slice 2

### Key risks

- a compiler with no usable built-in library
- divergence between YAML spec and actual built-in YAML set

### Exit criteria

- the default ladder can compile from real built-in YAML definitions

---

## Slice 6: Validation, Review, And Testing Execution

### Objective

Turn quality gates into real runtime behavior with real persistence.

### Scope

- validation execution and result recording
- review execution and result recording
- testing execution and result recording
- canonical default ordering enforcement
- gate-driven pass/revise/fail logic

### Features primarily covered

- F21
- F22
- F23
- F24
- F25
- F31
- F36

### Dependencies

- Slice 2
- Slice 3
- Slice 5

### Key risks

- quality gates staying superficial or implicit
- review/testing results not being durable enough for auditability

### Exit criteria

- quality gates are real execution stages with durable outputs

---

## Slice 7: Child Node Materialization And Scheduling

### Objective

Add decomposition and orchestration across multiple nodes.

### Scope

- layout materialization
- child node creation
- child dependency persistence
- ready-child scheduling
- wait-for-children behavior
- collect-child-summary behavior

### Features primarily covered

- F08
- F15
- F16
- F25
- F32

### Dependencies

- Slice 3
- Slice 4
- Slice 5

### Key risks

- child scheduling before introspection is mature
- dependency bugs causing deadlocks or invalid starts

### Exit criteria

- a parent can create child nodes, wait for them, and continue safely

---

## Slice 8: Parent Failure Logic And Replanning

### Objective

Implement the parent-side response model for child failures.

### Scope

- failure classification
- counters and thresholds
- retry child
- regenerate child
- parent replan path
- pause-for-user path
- parent decision summaries

### Features primarily covered

- F24
- F25

### Dependencies

- Slice 6
- Slice 7

### Key risks

- uncontrolled retries
- excessive tree churn
- poor user visibility into why the parent changed strategy

### Exit criteria

- child failure produces deterministic parent behavior with durable reasoning

---

## Slice 9: Session Recovery And Idle Handling

### Objective

Make the runtime robust against interruption and idleness.

### Scope

- resume existing session
- replacement primary session
- stale session detection
- nudge flow
- git mismatch handling during recovery
- duplicate-session ambiguity handling

### Features primarily covered

- F12
- F13
- F14
- F34

### Dependencies

- Slice 3
- Slice 4

### Key risks

- duplicate active sessions
- corrupted cursor recovery
- overreliance on tmux/provider state

### Exit criteria

- interrupted runs can be resumed or safely paused with clear reasoning

---

## Slice 10: Git Rectification And Upstream Rebuild

### Objective

Implement subtree regeneration and upstream rebuild mechanics.

### Scope

- superseding node versions
- reset-to-seed behavior
- deterministic merge order
- merge event recording
- conflict handling
- upstream rectification
- cutover policy

### Features primarily covered

- F02
- F17
- F18
- F19
- F20
- F36

### Dependencies

- Slice 6
- Slice 7
- Slice 8
- Slice 9

### Key risks

- premature cutover
- unresolved old-run conflicts
- opaque merge conflict handling

### Exit criteria

- changed subtrees can regenerate and rebuild upward deterministically

---

## Slice 11: Documentation And Provenance

### Objective

Add the support systems that explain and expose why the code looks the way it does.

### Scope

- entity extraction
- rationale mapping
- relation tracking
- provenance update step
- local docs build
- merged docs build
- provenance-aware doc generation

### Features primarily covered

- F28
- F29
- F30
- F36

### Dependencies

- Slice 6
- Slice 10

### Key risks

- provenance identity too weak to trust
- docs generated from stale or partial context

### Exit criteria

- node changes can be traced to code entities and surfaced in docs/rationale views

---

## Slice 12: Action Automation Completion Pass

### Objective

Close the gap between manual/operator-visible actions and CLI automation parity.

### Scope

- remaining planning/editing commands
- policy update flows
- blocker/pause diagnostics
- recovery-specific operator actions
- review/testing/docs explicit mutation commands where allowed

### Features primarily covered

- F11
- F32

### Dependencies

- all prior operational slices

### Exit criteria

- all meaningful user-visible actions have a reliable automation path

---

## Slice 13: Optional Isolated Environments

### Objective

Add bounded isolated execution if it remains in scope for first implementation.

### Scope

- environment policy references
- subtask-level isolated execution
- environment result metadata
- environment-related failure handling

### Features primarily covered

- F33

### Dependencies

- Slice 6
- Slice 9

### Recommended status

- optional
- defer if core orchestration needs stabilization first

### Exit criteria

- isolated execution is explicit, inspectable, and policy-driven

---

## Slice 14: Hardening And Audit Review

### Objective

Run the full auditability and no-hidden-state review against the implemented slices.

### Scope

- run the auditability checklist
- run the action automation matrix review
- confirm gap matrix reductions
- identify hidden-state leaks
- identify missing event histories or result models

### Features primarily covered

- F31
- F36

### Dependencies

- all core slices

### Exit criteria

- no critical hidden-state gaps remain
- the system is trustworthy enough for broader use

---

## Recommended Implementation Order Summary

If you want the shortest sensible critical path, the order should be:

1. Slice 0
2. Slice 1
3. Slice 2
4. Slice 3
5. Slice 4
6. Slice 5
7. Slice 6
8. Slice 7
9. Slice 8
10. Slice 9
11. Slice 10
12. Slice 11
13. Slice 12
14. Slice 13
15. Slice 14

---

## Recommended MVP Boundary

If you want a realistic first meaningful implementation boundary, stop after:

- Slice 6 for a single-node orchestrator with quality gates

If you want a realistic first multi-node orchestration boundary, stop after:

- Slice 10 for hierarchical orchestration with rebuilds

If you want the architecture vision with explanation surfaces, stop after:

- Slice 11 or Slice 12

---

## Highest-Risk Areas To De-Risk Early

These should get extra attention in implementation review:

1. current vs authoritative version handling
2. compile failure persistence and visibility
3. runtime ownership of cursor advancement
4. child scheduling and dependency deadlocks
5. parent failure decision loops
6. session replacement/recovery correctness
7. provenance identity confidence handling

---

## Suggested Next Planning Artifacts

If you want to go even further before coding, the next useful planning docs are:

- `notes/mvp_boundary_plan.md`
- `notes/migration_plan.md`
- `notes/test_strategy_plan.md`
- `notes/implementation_risk_register.md`

But this is optional. The current package is already strong enough to start slicing actual implementation work.

---

## Exit Criteria

This implementation slicing plan is complete enough when:

- the build order is dependency-aware
- risky foundations come before advanced features
- there is a clear MVP boundary
- optional features are clearly separated from critical path work

At that point, the project can move from spec expansion into staged implementation with much less ambiguity.
