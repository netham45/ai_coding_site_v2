# Simulations

This folder contains simulated walkthroughs for the proposed flows currently described across `notes/`.

These simulations are intended for logic review, not marketing examples.
Each file should answer:

- what tasks and subtasks run
- what durable state changes happen
- what command/prompt boundaries exist
- where the current notes still leave execution holes or contradictions

## Canonical runtime flows

- `01_flow_a_create_and_compile_top_level_node.md`
- `02_flow_b_admit_and_run_ready_node.md`
- `03_flow_c_execute_one_compiled_subtask.md`
- `04_flow_d_spawn_and_reconcile_children.md`
- `05_flow_e_pause_or_fail.md`
- `06_flow_f_recover_interrupted_work.md`
- `07_flow_g_rectify_after_change.md`

## Default node-kind flows

- `08_epic_default_flow.md`
- `09_phase_default_flow.md`
- `10_plan_default_flow.md`
- `11_task_default_flow.md`

## Specialized operational flows

- `12_project_bootstrap_flow.md`
- `13_compile_failure_flow.md`
- `14_hook_expansion_flow.md`
- `15_invalid_dependency_graph_flow.md`
- `16_parent_child_failure_decision_flow.md`
- `17_child_session_mergeback_flow.md`
- `18_manual_vs_auto_tree_reconciliation_flow.md`
- `19_cutover_flow.md`

These are simulations, not implemented behavior.

Known limitation:

- several built-in task definitions are still only named in the notes, not fully specified as concrete YAML, so some subtask-level transcripts are necessarily inferred from the current pseudocode and supporting notes.
