# State Value Catalog

## Purpose

This document freezes the shared status and type vocabulary used across the v2 specs.

The design now has enough structure that vocabulary drift is becoming the next source of inconsistency. This catalog exists to give the system one canonical place for bounded values such as:

- node lifecycle states
- run statuses
- session roles and statuses
- summary types
- failure classes
- dependency types
- validation/review/testing result statuses

This document should feed directly into migration-grade DB design, runtime state handling, and CLI output semantics.

Related documents:

- `notes/database_schema_spec_v2.md`
- `notes/node_lifecycle_spec_v2.md`
- `notes/runtime_command_loop_spec_v2.md`
- `notes/cli_surface_spec_v2.md`
- `notes/parent_failure_decision_spec.md`
- `notes/session_recovery_appendix.md`

---

## Rule

If a value is bounded enough to affect execution, persistence, auditability, or CLI behavior, it should appear in this catalog or be intentionally documented as open-ended.

Free-form text should not be used where bounded operational state is expected.

---

## 1. Node Lifecycle States

Recommended canonical values:

- `DRAFT`
- `COMPILED`
- `READY`
- `RUNNING`
- `WAITING_ON_CHILDREN`
- `WAITING_ON_SIBLING_DEPENDENCY`
- `RECTIFYING_SELF`
- `RECTIFYING_UPSTREAM`
- `VALIDATION_PENDING`
- `REVIEW_PENDING`
- `TESTING_PENDING`
- `PAUSED_FOR_USER`
- `FAILED_TO_PARENT`
- `COMPLETE`
- `SUPERSEDED`
- `CANCELLED`
- `COMPILE_FAILED`

### Notes

- `COMPILE_FAILED` is recommended if compile-failure persistence becomes first-class in runtime state
- some of the pending states may be modeled as visible stage ownership rather than separate state-machine checkpoints, but the vocabulary should still remain consistent

---

## 2. Node Run Status

Recommended canonical values:

- `PENDING`
- `RUNNING`
- `PAUSED`
- `FAILED`
- `COMPLETE`
- `CANCELLED`

### Notes

- this is distinct from node lifecycle state
- a node lifecycle state may be broader than the active run status

---

## 3. Dependency Types

Recommended canonical values:

- `child`
- `sibling`

No other dependency types should be allowed unless the hierarchy rules are intentionally expanded.

---

## 4. Dependency Required States

Recommended canonical values:

- `COMPLETE`

Optional future expansions if needed:

- `READY`
- `VALIDATED`
- `REVIEWED`

Recommended current stance:

- keep this simple unless a strong use case requires finer-grained dependency gating

---

## 4A. Lineage Scope

Recommended canonical values:

- `authoritative`
- `candidate`

---

## 5. Session Roles

Recommended canonical values:

- `primary`
- `pushed_child`

These should be enough for the current session model.

---

## 6. Session Status

Recommended canonical values:

- `STARTING`
- `ACTIVE`
- `DETACHED`
- `STALE`
- `RECOVERING`
- `COMPLETED`
- `FAILED`
- `CANCELLED`
- `INVALIDATED`

### Notes

- `DETACHED` means session still exists but no current user/operator attachment
- `STALE` means heartbeat or liveness expectations are not being met
- `INVALIDATED` is useful for duplicate or replaced sessions

---

## 7. Session Event Types

Recommended canonical values:

- `bound`
- `attached`
- `detached`
- `heartbeat`
- `nudged`
- `resume_requested`
- `resumed`
- `replacement_created`
- `completed`
- `failed`
- `cancelled`
- `invalidated`

---

## 7A. Workflow Event Types

Recommended canonical values:

- `pause_entered`
- `pause_cleared`
- `pause_resumed`
- `recovery_attempted`
- `recovery_succeeded`
- `replacement_session_created`
- `recovery_failed`
- `parent_retry_child`
- `parent_regenerate_child`
- `parent_replan`
- `parent_pause_for_user`
- `cutover_completed`
- `lineage_superseded`

Recommended canonical event scopes:

- `pause`
- `recovery`
- `parent_decision`
- `cutover`

---

## 8. Compiled Subtask Types

Recommended canonical values:

- `run_prompt`
- `run_command`
- `build_context`
- `wait_for_children`
- `wait_for_sibling_dependency`
- `reset_to_seed`
- `merge_children`
- `validate`
- `review`
- `run_tests`
- `build_docs`
- `write_summary`
- `finalize_node`
- `spawn_child_session`
- `spawn_child_node`
- `update_provenance`

---

## 8A. Child Origin Types

Recommended canonical values:

- `manual`
- `layout_generated`
- `layout_generated_then_modified`

---

## 8B. Parent Child Authority Modes

Recommended canonical values:

- `manual`
- `layout_authoritative`
- `hybrid`

---

## 9. Subtask Attempt Status

Recommended canonical values:

- `STARTED`
- `RUNNING`
- `SUCCEEDED`
- `FAILED`
- `PAUSED`
- `CANCELLED`

Recommended simplification:

- if `STARTED` and `RUNNING` feel redundant in implementation, keep one but apply it consistently

---

## 10. Validation Check Types

Recommended canonical values:

- `file_exists`
- `file_updated`
- `command_exit_code`
- `json_schema`
- `yaml_schema`
- `ai_json_status`
- `file_contains`
- `git_clean`
- `git_dirty`
- `summary_written`
- `docs_built`
- `provenance_updated`
- `dependencies_satisfied`
- `session_bound`

---

## 11. Validation Result Status

Recommended canonical values:

- `PASSED`
- `FAILED`
- `SKIPPED`

Optional future value:

- `WARNING`

Recommended current stance:

- avoid `WARNING` until the runtime knows exactly how warnings affect gating

---

## 12. Review Scope

Recommended canonical values:

- `layout`
- `node_output`
- `merge_result`
- `docs`
- `policy_compliance`
- `custom`

---

## 13. Review Result Status

Recommended canonical values:

- `PASSED`
- `REVISE`
- `FAILED`
- `SKIPPED`

### Notes

- `REVISE` is important because review is not just pass/fail

---

## 14. Testing Scope

Recommended canonical values:

- `unit`
- `integration`
- `smoke`
- `project_custom`

---

## 15. Test Result Status

Recommended canonical values:

- `PASSED`
- `FAILED`
- `SKIPPED`
- `FLAKY_RETRY`

### Notes

- `FLAKY_RETRY` is optional; if included, define exactly how it affects final gating
- simplest first implementation may omit it and model retries elsewhere

---

## 16. Summary Types

Recommended canonical values:

- `subtask`
- `failure`
- `pause`
- `node`
- `review`
- `testing`
- `validation`
- `rectification`
- `parent_replan`
- `parent_child_failure_pause`
- `docs`
- `provenance`

### Notes

- this list may expand, but it should remain bounded and intentional
- avoid turning summary types into free-form prose labels

---

## 17. Prompt Roles

Recommended canonical values:

- `main_prompt`
- `subtask_prompt`
- `pause_summary_prompt`
- `review_prompt`
- `testing_prompt`
- `docs_prompt`
- `system_prompt`

---

## 18. Failure Classes

This catalog combines runtime and parent-facing failure categories.

Recommended canonical values:

- `transient_execution_failure`
- `validation_failure`
- `review_failure`
- `test_failure`
- `merge_conflict_unresolved`
- `bad_layout_or_bad_requirements`
- `dependency_or_context_failure`
- `environment_failure`
- `hook_expansion_failure`
- `compile_failure`
- `unknown_failure`

### Notes

- not every subsystem needs all of these
- but the taxonomy should remain conceptually aligned

---

## 19. Compile Failure Stages

Recommended canonical values:

- `source_discovery`
- `source_loading`
- `extension_resolution`
- `override_resolution`
- `schema_validation`
- `policy_resolution`
- `hook_expansion`
- `workflow_compilation`
- `compiled_graph_validation`
- `workflow_persistence`

---

## 20. Compile Failure Classes

Recommended canonical values:

- `missing_source`
- `duplicate_source_ambiguity`
- `override_missing_target`
- `override_merge_conflict`
- `schema_validation_failure`
- `policy_resolution_failure`
- `hook_expansion_failure`
- `compiled_workflow_structure_failure`
- `compiled_dependency_graph_failure`
- `workflow_persistence_failure`
- `unknown_compile_failure`

---

## 21. Merge Conflict Resolution Status

Recommended canonical values:

- `UNRESOLVED`
- `RESOLVED`
- `FAILED`

---

## 22. Source Scope

Recommended canonical values:

- `builtin`
- `project_extension`
- `project_override`

---

## 23. Source Role

Recommended canonical values:

- `base_definition`
- `extension_definition`
- `override_definition`
- `policy_definition`
- `hook_definition`
- `review_definition`
- `testing_definition`
- `docs_definition`
- `rectification_definition`

### Notes

- this catalog directly supports source-lineage clarity in compilation

---

## 24. Merge Modes

Recommended canonical values:

- `replace`
- `deep_merge`
- `append_list`
- `replace_list`

---

## 25. Environment Isolation Modes

Recommended canonical values:

- `none`
- `container`
- `namespace`
- `custom_profile`

---

## 26. Authority / Lineage Status

If explicit authority modeling is added, recommended conceptual values are:

- `candidate`
- `authoritative`
- `superseded`
- `failed_candidate`

### Notes

- this is not yet guaranteed to be a first-implementation DB field
- but if explicit authority tracking is added, use this vocabulary consistently

---

## 27. Recommended Catalog Priorities

The highest-priority catalogs to enforce first are:

1. node lifecycle state
2. node run status
3. session role and session status
4. compiled subtask type
5. validation/review/test result statuses
6. summary type
7. compile failure stages and classes

These are the values most likely to cause cross-spec drift if left loose.

---

## 28. Open Decisions Still Remaining

### D01. Whether `COMPILE_FAILED` becomes a first-class lifecycle state

Recommended direction:

- yes, if compile failures become durably persisted and operationally visible

### D02. Whether `WARNING` exists for validation

Recommended direction:

- defer unless warning semantics are clearly defined

### D03. Whether `FLAKY_RETRY` exists as explicit test result status

Recommended direction:

- optional; avoid unless implementation really benefits from it

---

## 29. Recommended Next Follow-On Work

The next docs that should absorb this catalog are:

1. `notes/database_schema_spec_v2.md`
2. `notes/node_lifecycle_spec_v2.md`
3. `notes/runtime_command_loop_spec_v2.md`
4. `notes/cli_surface_spec_v2.md`
5. `notes/cross_spec_gap_matrix.md`

Then implementation planning can use this catalog as the enum/check-constraint source.

---

## Exit Criteria

This catalog is complete enough when:

- all major bounded state vocabularies are listed
- overlapping terms are normalized
- implementation-facing DB/runtime/CLI work can reference one shared source

At that point, vocabulary drift should be much lower across the spec set.
