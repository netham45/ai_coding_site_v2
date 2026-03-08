# DB Operation Simulations

These files simulate the database operations implied by the current v2 notes.

They focus on:

- row creation and updates
- ordering of writes
- which transitions are durable versus daemon-only
- where the schema still leaves logic or integrity gaps

Files:

- `01_top_level_node_creation.md`
- `02_run_admission_and_subtask_execution.md`
- `03_child_materialization_and_scheduling.md`
- `04_quality_gate_and_summary_persistence.md`
- `05_session_recovery_and_child_sessions.md`
- `06_rectification_merge_and_cutover.md`
- `07_compile_failure_pause_and_events.md`
