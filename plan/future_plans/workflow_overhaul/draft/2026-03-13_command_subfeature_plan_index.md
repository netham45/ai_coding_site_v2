# Command Subfeature Plan Index

## Purpose

Provide a deeper implementation-sized breakdown for the unified command lifecycle feature where one draft feature plan is too coarse to govern both the shared lifecycle foundations and every built-in subtask command kind.

## Structure

The directory now uses:

- shared foundation plans for the abstract interface and shared lifecycle scaffolding
- one standalone child plan per built-in subtask command kind

All command-specific plans depend on the foundation layer.

## Families

### Command Lifecycle Foundations

- `command_subfeature_plans/00_shared_lifecycle_interface.md`
- `command_subfeature_plans/01_state_legality_and_action_result_models.md`
- `command_subfeature_plans/02_handler_registry_and_runtime_dispatch.md`
- `command_subfeature_plans/03_yaml_boundary_and_operator_projection.md`
- `command_subfeature_plans/04_corrective_expansion_and_reverification.md`

### Execution Command Handlers

- `command_subfeature_plans/run_prompt.md`
- `command_subfeature_plans/run_command.md`
- `command_subfeature_plans/run_tests.md`
- `command_subfeature_plans/validate.md`
- `command_subfeature_plans/review.md`

### Context And Reporting Command Handlers

- `command_subfeature_plans/build_context.md`
- `command_subfeature_plans/build_docs.md`
- `command_subfeature_plans/write_summary.md`
- `command_subfeature_plans/collect_child_summaries.md`
- `command_subfeature_plans/record_merge_metadata.md`
- `command_subfeature_plans/update_provenance.md`

### Wait And Gate Command Handlers

- `command_subfeature_plans/wait_for_children.md`
- `command_subfeature_plans/wait_for_sibling_dependency.md`
- `command_subfeature_plans/pause_on_user_flag.md`

### Structural Command Handlers

- `command_subfeature_plans/spawn_child_node.md`
- `command_subfeature_plans/spawn_child_session.md`
- `command_subfeature_plans/merge_children.md`
- `command_subfeature_plans/finalize_node.md`
- `command_subfeature_plans/finalize_git_state.md`
- `command_subfeature_plans/reset_to_seed.md`

### Recovery And Session Command Handlers

- `command_subfeature_plans/recover_cursor.md`
- `command_subfeature_plans/rebind_session.md`
- `command_subfeature_plans/nudge_session.md`

## Relationship To Broader Draft Feature Plans

These command subfeature plans are the deeper children of:

- `draft_feature_plans/30_unified_command_lifecycle_contract.md`
