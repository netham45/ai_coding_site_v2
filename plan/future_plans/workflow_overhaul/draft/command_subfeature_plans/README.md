# Command Subfeature Plans

This directory uses:

- a small foundation layer for the shared lifecycle interface and shared command scaffolding
- one file per built-in subtask command kind

These are deeper children of the broader unified-command-lifecycle draft feature plan under `draft_feature_plans/30_unified_command_lifecycle_contract.md`.

## Families

### Command Lifecycle Foundations

- `00_shared_lifecycle_interface.md`
- `01_state_legality_and_action_result_models.md`
- `02_handler_registry_and_runtime_dispatch.md`
- `03_yaml_boundary_and_operator_projection.md`
- `04_corrective_expansion_and_reverification.md`

### Execution Command Handlers

- `run_prompt.md`
- `run_command.md`
- `run_tests.md`
- `validate.md`
- `review.md`

### Context And Reporting Command Handlers

- `build_context.md`
- `build_docs.md`
- `write_summary.md`
- `collect_child_summaries.md`
- `record_merge_metadata.md`
- `update_provenance.md`

### Wait And Gate Command Handlers

- `wait_for_children.md`
- `wait_for_sibling_dependency.md`
- `pause_on_user_flag.md`

### Structural Command Handlers

- `spawn_child_node.md`
- `spawn_child_session.md`
- `merge_children.md`
- `finalize_node.md`
- `finalize_git_state.md`
- `reset_to_seed.md`

### Recovery And Session Command Handlers

- `recover_cursor.md`
- `rebind_session.md`
- `nudge_session.md`
