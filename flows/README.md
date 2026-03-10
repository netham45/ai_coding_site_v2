# Flows

This folder defines the task flows the system needs in order to support the common user journeys identified in:

- `notes/scenarios/journeys/common_user_journeys_analysis.md`
- `notes/specs/architecture/code_vs_yaml_delineation.md`

These are canonical task-flow specs.

They are not:

- simulations
- walkthroughs
- UX examples
- implementation tickets

`simulations/` is not the model for this folder. If a simulation disagrees with a flow here, the flow definition should be treated as the stronger artifact.

These flow specs describe:

- when the flow is used
- which tasks/subtasks it must perform
- which programmatic capabilities it depends on
- what durable outputs and decisions it must leave behind
- what invariants and completion rules must hold

They should be read with one boundary in mind:

- YAML defines declarative workflow structure, policy, and content
- C++ defines compilation, orchestration, state transitions, recovery, persistence, and safety-critical algorithms

## Flow index

- `01_create_top_level_node_flow.md`
- `02_compile_or_recompile_workflow_flow.md`
- `03_materialize_and_schedule_children_flow.md`
- `04_manual_tree_edit_and_reconcile_flow.md`
- `05_admit_and_execute_node_run_flow.md`
- `06_inspect_state_and_blockers_flow.md`
- `07_pause_resume_and_recover_flow.md`
- `08_handle_failure_and_escalate_flow.md`
- `09_run_quality_gates_flow.md`
- `10_regenerate_and_rectify_flow.md`
- `11_finalize_and_merge_flow.md`
- `12_query_provenance_and_docs_flow.md`
- `13_human_gate_and_intervention_flow.md`

## Coverage summary

Together these flows cover the main product journeys:

- create work from a prompt
- compile and validate workflow definitions
- decompose work into children
- run AI task loops
- inspect status and blockers
- recover interrupted execution
- handle failure and impossible waits
- run validation/review/testing gates
- regenerate or rectify after changes
- finalize and merge outputs
- inspect rationale, provenance, and docs
- pause for and accept human decisions

## Design rule

Every flow here assumes:

- the daemon/runtime is the live orchestration authority
- the database is the durable canonical record
- the CLI is the user-facing and AI-facing control surface
- no important transition should exist only in memory

## Reading rule

Each flow should be interpreted as:

- a required runtime capability
- a reusable task graph or orchestration pattern
- a durable state-transition contract

Each flow should not be interpreted as:

- a single scripted happy-path demo
- a mock CLI transcript
- a one-off scenario
