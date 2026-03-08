# Pseudocode Workspace

## Purpose

This folder is the implementation-planning layer that sits between the prose specs in `notes/` and eventual code.

The goal is to convert the existing markdown specs into:

- explicit pseudocode modules
- explicit state transitions
- explicit branch/loop/failure behavior
- pseudotests that check logical soundness and coverage

This makes the design easier to validate with AI before committing to code.

---

## What belongs here

Each artifact in this folder should represent one of these:

- a canonical pseudocode module
- an end-to-end flow written in pseudocode
- a decision table or state machine extracted from prose specs
- a pseudotest suite for a module or flow
- a coverage map showing which notes have been compiled into pseudocode

This folder should not become a second prose-spec folder. Files here should prefer structured, testable representations over long narrative text.

---

## Proposed structure

- `README.md`
  - workspace purpose and operating rules
- `00_compilation_plan.md`
  - phased plan for converting notes into pseudocode artifacts
- `catalog/`
  - index files mapping source notes to pseudocode outputs
- `modules/`
  - one file per canonical runtime/compiler/orchestration module
- `flows/`
  - end-to-end user and system flows
- `state_machines/`
  - lifecycle, run-state, pause, recovery, merge, and failure machines
- `pseudotests/`
  - scenario-driven logical tests against modules and flows

---

## Canonical artifact format

Each pseudocode artifact should use the same shape:

1. `Purpose`
2. `Source notes`
3. `Inputs`
4. `Required state`
5. `Outputs`
6. `Durable writes`
7. `Happy path`
8. `Failure paths`
9. `Pause/recovery behavior`
10. `Open questions`
11. `Pseudotests`

This keeps artifacts evaluable by both humans and AI.

---

## Compilation workflow

For each source note:

1. identify whether it defines a module, flow, state machine, schema rule, or policy
2. extract normative rules from descriptive prose
3. convert those rules into ordered pseudocode or decision logic
4. list every durable state mutation explicitly
5. add failure and recovery branches
6. add pseudotests for success, invalid input, blocked dependency, contradiction, and recovery paths
7. link the artifact back to source notes and unresolved gaps

---

## Initial source clusters

The current notes already group naturally into the following compilation batches:

### Batch A: Runtime execution core

Primary sources:

- `notes/runtime_pseudocode_plan.md`
- `notes/runtime_command_loop_spec_v2.md`
- `notes/node_lifecycle_spec_v2.md`
- `notes/session_recovery_appendix.md`
- `notes/compile_failure_persistence.md`

Outputs:

- canonical node loop pseudocode
- subtask execution pseudocode
- recovery pseudocode
- failure/pause state machine
- pseudotests for runtime progression and interruption

### Batch B: Compilation pipeline

Primary sources:

- `notes/yaml_schemas_spec_v2.md`
- `notes/default_yaml_library_plan.md`
- `notes/hook_expansion_algorithm.md`
- `notes/override_conflict_semantics.md`
- `notes/code_vs_yaml_delineation.md`

Outputs:

- source loading pseudocode
- override resolution pseudocode
- hook expansion pseudocode
- workflow compilation pseudocode
- compile-failure pseudotests

### Batch C: Tree and dependency orchestration

Primary sources:

- `notes/child_materialization_and_scheduling.md`
- `notes/invalid_dependency_graph_handling.md`
- `notes/manual_vs_auto_tree_interaction.md`
- `notes/parent_failure_decision_spec.md`
- `notes/common_user_journeys_analysis.md`

Outputs:

- child materialization flow
- dependency validation flow
- parent escalation logic
- manual/auto reconcile flow
- pseudotests for deadlock, invalid dependency, and regeneration cases

### Batch D: Git, provenance, and operator surfaces

Primary sources:

- `notes/git_rectification_spec_v2.md`
- `notes/provenance_identity_strategy.md`
- `notes/cli_surface_spec_v2.md`
- `notes/action_automation_matrix.md`
- `notes/auditability_checklist.md`

Outputs:

- rectification pseudocode
- merge/rebuild pseudocode
- provenance update flow
- CLI-visible query expectations
- pseudotests for auditability and reproducibility

---

## Recommended starting sequence

Start with runtime and compilation, in this order:

1. `compile_workflow(...)`
2. `admit_node_run(...)`
3. `run_node_loop(...)`
4. `execute_compiled_subtask(...)`
5. `handle_subtask_failure(...)`
6. `recover_interrupted_run(...)`

Reason:

- these modules anchor most other specs
- they expose missing DB and CLI details quickly
- they give the best base for pseudotests

---

## Pseudotest model

Every module should gain a pseudotest file with cases such as:

- `accepts_valid_input`
- `rejects_invalid_structure`
- `persists_required_state`
- `does_not_skip_required_gate`
- `pauses_when_human_gate_is_set`
- `recovers_from_interrupted_session`
- `escalates_when_retry_budget_is_exhausted`
- `produces_cli-queryable_results`

Pseudotests should be declarative and scenario-based, not tied to a programming language yet.

---

## Immediate next files to create

1. `notes/pseudocode/00_compilation_plan.md`
2. `notes/pseudocode/catalog/source_to_artifact_map.md`
3. `notes/pseudocode/modules/compile_workflow.md`
4. `notes/pseudocode/modules/run_node_loop.md`
5. `notes/pseudocode/pseudotests/runtime_core_tests.md`

---

## Definition of success

This workspace is working when:

- each major v2 spec has a mapped pseudocode target
- each important runtime path has explicit loops and branch behavior
- each important durable state mutation is listed
- contradictions between specs are visible at pseudocode level
- pseudotests can be reviewed by AI for logical soundness before implementation
