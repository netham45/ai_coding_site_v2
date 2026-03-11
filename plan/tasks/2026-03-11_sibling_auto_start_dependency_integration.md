# Task: Sibling Auto-Start Dependency Integration Coverage

## Goal

Add integration coverage that proves the backend auto-start loop starts multiple sibling children concurrently when they do not block each other and keeps dependency-blocked siblings from starting until prerequisites complete.

## Rationale

- Rationale: Dependency admission alone is not enough for the child-runtime contract; the backend also needs integration proof that readiness is classified independently across sibling sets and that the child auto-start loop admits every eligible sibling rather than only the first convenient one.
- Reason for existence: The current integration surface proves one ready child and one blocked child, but it does not yet prove the broader sibling-graph concurrency patterns the runtime claims to support.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/11_F08_dependency_graph_and_admission_control.md`
- `plan/features/20_F15_child_node_spawning.md`
- `plan/features/64_F08_F15_richer_child_scheduling_and_blocker_explanation.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/contracts/parent_child/child_materialization_and_scheduling.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/pseudocode/modules/schedule_ready_children.md`
- `notes/catalogs/checklists/verification_command_catalog.md`

## Scope

- Database: exercise durable child nodes, dependency edges, lifecycle rows, runs, and session binding records through the integration harness.
- CLI: not directly changed in this batch.
- Daemon: prove the background child auto-start loop classifies and admits siblings independently according to dependency truth.
- YAML: use real generated layout documents to express each sibling graph under test.
- Prompts: no prompt text changes are expected in this batch.
- Tests: add integration coverage for independent siblings, simple chain blocking, fan-out unblock behavior, and mixed independent-plus-dependent scheduling.
- Performance: keep the new tests bounded and polling-based without introducing long sleeps.
- Notes: update notes only if implementation or runtime behavior differs from the current child-scheduling contract.

## Plan

### Phase 1A: Shared integration harness

1. Add a test helper that writes and registers a generated child layout for a parent under a temporary workspace.
2. Add a helper that polls the daemon-backed run/session surfaces until the child auto-start loop has either started the expected children or timed out.
3. Reuse the real background loop in `create_app()` with the fake session backend.

Exit criteria:

- integration tests can define arbitrary sibling dependency graphs through real layout registration and materialization

### Phase 1B: Sibling scheduling matrix

1. Add an integration test for two independent siblings where both auto-start.
2. Add an integration test for a simple chain `1 -> 2` where only `1` auto-starts and `2` stays blocked until `1` completes, then `2` auto-starts.
3. Add an integration test for fan-out `1 -> 2` and `1 -> 3` where `2` and `3` are both blocked first, then both auto-start after `1` completes.
4. Add an integration test for mixed graph `1`, `2 -> 3` where `1` and `2` auto-start together and `3` remains blocked until `2` completes.

Exit criteria:

- the integration suite proves concurrent child auto-start eligibility and dependency gating across the requested sibling graphs

### Phase 1C: Verification and task closure

1. Run targeted integration tests for the new scheduling cases.
2. Run the task-plan, log-schema, and verification-command doc checks because authoritative docs changed.
3. Update the development log with actual results and remaining gaps, if any.

Exit criteria:

- targeted integration and doc-schema verification commands pass

## Verification

- `python3 -m pytest tests/integration/test_daemon.py::test_background_child_auto_run_loop_starts_multiple_independent_siblings -q`
- `python3 -m pytest tests/integration/test_daemon.py::test_background_child_auto_run_loop_blocks_simple_chain_until_dependency_completes tests/integration/test_daemon.py::test_background_child_auto_run_loop_unblocks_fan_out_siblings_together_after_shared_prerequisite tests/integration/test_daemon.py::test_background_child_auto_run_loop_starts_independent_siblings_while_leaving_dependent_third_blocked -q`
- `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_verification_command_docs.py -q`

## Exit Criteria

- The backend auto-start loop starts multiple independent siblings without waiting on unrelated incomplete siblings.
- Dependency-blocked siblings remain unstarted until their prerequisites reach `COMPLETE`.
- Newly unblocked siblings can auto-start in the same scheduling slice after prerequisite completion.
- The plan and development log record the proving commands honestly.
