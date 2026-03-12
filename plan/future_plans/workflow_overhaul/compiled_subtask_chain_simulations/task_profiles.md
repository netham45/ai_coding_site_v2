# Task Profile Simulations

## `task.implementation`

- Kind: `task`
- Child target: none
- Simulated compiled subtask chain:
  1. `load_task_context`
  2. `inspect_current_state`
  3. `edit_owned_artifacts`
  4. `run_declared_verification`
  5. `register_outputs_and_summary`
  6. `validate_completion_predicates`
  7. `complete_or_block`
- Main gate: block completion until required artifacts and bounded-proof evidence exist.

## `task.review`

- Kind: `task`
- Child target: none
- Simulated compiled subtask chain:
  1. `load_task_context`
  2. `inspect_declared_surfaces`
  3. `run_evidence_commands`
  4. `classify_findings`
  5. `register_outputs_and_summary`
  6. `validate_completion_predicates`
  7. `complete_or_block`
- Main gate: block completion until evidence and findings are durably recorded.

## `task.verification`

- Kind: `task`
- Child target: none
- Simulated compiled subtask chain:
  1. `load_task_context`
  2. `prepare_verification_environment`
  3. `run_declared_commands`
  4. `capture_command_results`
  5. `register_outputs_and_summary`
  6. `validate_completion_predicates`
  7. `complete_or_block`
- Main gate: block completion until declared command results are persisted honestly.

## `task.docs`

- Kind: `task`
- Child target: none
- Simulated compiled subtask chain:
  1. `load_task_context`
  2. `inspect_authoritative_docs`
  3. `edit_declared_documentation_surfaces`
  4. `run_doc_schema_or_supporting_checks`
  5. `register_outputs_and_summary`
  6. `validate_completion_predicates`
  7. `complete_or_block`
- Main gate: block completion until documentation updates and declared checks are persisted.

## `task.e2e`

- Kind: `task`
- Child target: none
- Simulated compiled subtask chain:
  1. `load_task_context`
  2. `prepare_runtime_environment`
  3. `run_real_e2e_commands`
  4. `capture_real_runtime_evidence`
  5. `register_outputs_and_summary`
  6. `validate_completion_predicates`
  7. `complete_or_block`
- Main gate: block completion until real-runtime evidence exists, not bounded substitutes.

## `task.remediation`

- Kind: `task`
- Child target: none
- Simulated compiled subtask chain:
  1. `load_task_context`
  2. `restate_triggering_finding`
  3. `apply_bounded_fix`
  4. `run_recheck_commands`
  5. `register_outputs_and_summary`
  6. `validate_completion_predicates`
  7. `complete_or_block`
- Main gate: block completion until the finding-to-fix-to-proof chain is durably recorded.
