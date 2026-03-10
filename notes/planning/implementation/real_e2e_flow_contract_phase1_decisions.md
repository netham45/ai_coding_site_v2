# Real E2E Flow Contract Phase 1 Decisions

## Purpose

Record the first concrete repository slice from the real end-to-end hardening plan.

This note exists because the earlier flow suites used `fastapi.testclient.TestClient`
and daemon-bridge helpers, which are useful bounded integration tests but do not
meet the repository's own "real end to end" standard.

## What is now implemented

- repository-wide pytest markers for real end-to-end flow work:
  - `e2e_real`
  - `requires_git`
  - `requires_tmux`
  - `requires_ai_provider`
- a real daemon subprocess harness in `tests/fixtures/e2e.py`
- a real CLI subprocess path in `tests/helpers/e2e.py`
- Flow 01 converted to a real end-to-end checkpoint in
  `tests/e2e/test_flow_01_create_top_level_node_real.py`
- Flow 02 converted to a real end-to-end checkpoint in
  `tests/e2e/test_flow_02_compile_or_recompile_workflow_real.py`
- Flow 03 converted to a real end-to-end checkpoint in
  `tests/e2e/test_flow_03_materialize_and_schedule_children_real.py`
- Flow 04 converted to a real end-to-end checkpoint in
  `tests/e2e/test_flow_04_manual_tree_edit_and_reconcile_real.py`
- Flow 05 converted to a real end-to-end checkpoint in
  `tests/e2e/test_flow_05_admit_and_execute_node_run_real.py`
- Flow 06 converted to a real end-to-end checkpoint in
  `tests/e2e/test_flow_06_inspect_state_and_blockers_real.py`
- Flow 07 converted to a real end-to-end checkpoint in
  `tests/e2e/test_flow_07_pause_resume_and_recover_real.py`
- Flow 08 converted to a real end-to-end checkpoint in
  `tests/e2e/test_flow_08_handle_failure_and_escalate_real.py`
- Flow 09 converted to a real end-to-end checkpoint in
  `tests/e2e/test_flow_09_run_quality_gates_real.py`
- Flow 10 converted to a real end-to-end checkpoint in
  `tests/e2e/test_flow_10_regenerate_and_rectify_real.py`
- Flow 11 converted to a real end-to-end checkpoint in
  `tests/e2e/test_flow_11_finalize_and_merge_real.py`
- Flow 12 converted to a real end-to-end checkpoint in
  `tests/e2e/test_flow_12_query_provenance_and_docs_real.py`
- Flow 13 converted to a real end-to-end checkpoint in
  `tests/e2e/test_flow_13_human_gate_and_intervention_real.py`
- Flow 01 through Flow 13 real end-to-end checkpoints are passing
- a full serial Flow 01 through Flow 13 real-E2E batch rerun is passing

## Real boundary for the first slice

Flow 01 now proves:

- real PostgreSQL state
- real daemon startup via `uvicorn`
- real auth token file creation and reuse
- real HTTP daemon boundary
- real CLI process invocation
- durable node creation
- durable workflow compilation
- durable audit and source-lineage inspection

Flow 02 now proves:

- real workflow recompile through the CLI and daemon API
- real compile-stage inspection for:
  - current workflow
  - chain
  - source discovery
  - schema validation
  - override resolution
  - hook policy
  - rendering
  - compile-failure inspection
  - version-targeted stage reads

Flow 03 now proves:

- real child materialization through the CLI and daemon API
- real post-materialization child inspection
- real tree inspection for materialized children
- real scheduling-state proof for the shipped built-in child layout path

Flow 04 now proves:

- real manual child creation through the CLI and daemon API
- real hybrid-child reconciliation inspection
- real explicit preserve-manual reconciliation execution
- real post-reconcile child and tree inspection for the current manual-preservation path

Flow 05 now proves:

- real run admission through the CLI and daemon API
- real prompt and context retrieval for the current subtask
- real subtask start, heartbeat, summary registration, completion, and advance
- real durable run-progress and summary-history inspection after advancement

Flow 06 now proves:

- real operator-summary inspection
- real tree inspection
- real current-task inspection
- real current-subtask inspection
- real blocker inspection
- real YAML source-lineage inspection
- real workflow snapshot inspection

Flow 07 now proves:

- real tmux-backed session binding
- real session state inspection through `session show-current`
- real stale-session recovery classification through the live poller
- real provider-agnostic resume through the daemon and CLI runtime

Flow 08 now proves:

- real child run failure through the CLI and daemon API
- real parent response-to-child-failure handling
- real durable child-failure counter inspection
- real durable parent decision-history inspection

Flow 09 now proves:

- real project-local policy and override loading through the daemon-owned workspace root
- real quality-chain execution through validation, review, and testing
- real provenance refresh against the configured workspace root
- real docs generation and durable final-summary persistence
- real audit, rationale, and summary-history inspection after the quality chain completes

Flow 10 now proves:

- real subtree regeneration through the daemon and CLI runtime
- real upstream rectification through the daemon and CLI runtime
- real rebuild-history inspection after both operations
- real candidate cutover-readiness inspection
- real live rebuild-coordination inspection for upstream scope

Flow 11 now proves:

- real live git repo bootstrap through the daemon and CLI runtime
- real child finalize through an actual git commit plus runtime finalization
- real child merge execution through the daemon and CLI runtime
- real durable merge-event inspection after the merge
- real parent finalize execution and final-commit inspection
- real live git status inspection after finalization

Flow 12 now proves:

- real provenance refresh against a real workspace source tree
- real rationale inspection after durable provenance refresh
- real entity, entity-history, changed-by, and relation inspection through the CLI and daemon runtime
- real docs build, docs list, and docs show through the CLI and daemon runtime
- real node-audit inspection of documentation outputs and provenance summary history

Flow 13 now proves:

- real project-local pause-gate override loading through the daemon-owned workspace root
- real pause-state inspection through the CLI and daemon runtime
- real blocked resume before explicit approval
- real unified intervention catalog inspection for pause approval
- real pause approval through `node intervention-apply`
- real resume after approval through the daemon and CLI runtime

The test explicitly does not use:

- `TestClient`
- in-process daemon bridge clients
- monkeypatched CLI daemon clients
- direct DB mutation to force state

## Workspace-root limitation exposed by implementation

The original hardening passes exposed a real product gap: the daemon did not own a
configurable workspace-root contract for project-local resources.

That is now partially fixed:

- `AICODING_WORKSPACE_ROOT` now drives the project resource catalog roots for:
  - `yaml_project`
  - `yaml_project_policies`
  - `yaml_overrides`
  - `prompt_project`
  - `docs`
- default provenance refresh now scans the configured workspace root when one exists

That change is what made Flow 09's real quality-chain checkpoint possible without
in-process catalog injection.

What is still not complete:

- live git working-tree ownership is still not yet rooted in the same product-owned workspace contract
- live Codex task execution still needs stronger runtime guidance so the session records durable task progress through the intended CLI/runtime contract rather than drifting into generic repo or CLI exploration

## Consequence for later phases

Later real E2E flows that depend on:

- live git working trees
- live Codex task execution through the intended CLI/runtime contract
- AI-produced filesystem artifacts

should not be marked complete until the remaining workspace-root consumers are
aligned with the same runtime contract.

## Additional limitation exposed by implementation

The initial real E2E hardening pass exposed that DB-backed flows were not safe to
run in parallel against the same shared database fixture.

That limitation has now been addressed at the harness layer by creating one
database per real E2E test and running migrations inside that database before the
daemon starts.

So the current real E2E posture is now:

- real daemon and real CLI proof is in place
- DB-backed real E2E flows are isolated at the database layer
- any remaining serialization should be justified by non-database resources such
  as tmux, provider credentials, or unusually heavy workspace narratives

## Flow 01 hardening note

The first Flow 01 rerun exposed stale assumptions in the new test:

- `node show` returns flat operator-summary lifecycle fields, not a nested `lifecycle` object
- `git branch show` returns `active_branch_name`, not `branch_name`

Those were test-contract mismatches, not product bugs, and were corrected in the
real E2E test without weakening the runtime proof.

## Flow 03 hardening note

The first Flow 03 rerun exposed two issues:

- the CLI daemon client timeout was too short for real child materialization in the
  subprocess-backed path
- the new test assumed `tree show --full` returned a nested `root/children` payload,
  but the real daemon contract returns a flat tree catalog with `root_node_id` and
  `nodes`

The timeout issue was a real product limitation and was fixed by introducing a
configurable daemon request timeout in the CLI settings path.

The tree-shape issue was a test-contract mismatch, not a product bug, and was
corrected in the real E2E test without weakening the runtime proof.

## Flow 04 hardening note

The first Flow 04 real E2E pass succeeded without requiring product fixes.

That does not close the broader Flow 04 backlog. The runtime still does not have:

- explicit structural layout replacement
- layout-adoption reconciliation
- richer hybrid merge decisions beyond `preserve_manual`

So the real E2E checkpoint proves the current shipped preserve-manual path, not the
full older simulation narrative.

## Flow 05 hardening note

The first Flow 05 reruns exposed only test-contract mismatches in the new test:

- `subtask start` and `subtask complete` return `RunProgressResponse` with `latest_attempt`
  using durable enum-like statuses such as `RUNNING` and `COMPLETE`
- `workflow advance` returns run/state progress, not a standalone `status` field
- `node run show --node ...` returns `RunProgressResponse`, not a wrapper with top-level
  `node_id`

Those were corrected in the real E2E test without weakening the runtime proof.

## Batch verification note

After Flow 13 landed, the repository ran the full serial real-E2E checkpoint batch:

- `python3 -m pytest tests/e2e/test_flow_01_create_top_level_node_real.py tests/e2e/test_flow_02_compile_or_recompile_workflow_real.py tests/e2e/test_flow_03_materialize_and_schedule_children_real.py tests/e2e/test_flow_04_manual_tree_edit_and_reconcile_real.py tests/e2e/test_flow_05_admit_and_execute_node_run_real.py tests/e2e/test_flow_06_inspect_state_and_blockers_real.py tests/e2e/test_flow_07_pause_resume_and_recover_real.py tests/e2e/test_flow_08_handle_failure_and_escalate_real.py tests/e2e/test_flow_09_run_quality_gates_real.py tests/e2e/test_flow_10_regenerate_and_rectify_real.py tests/e2e/test_flow_11_finalize_and_merge_real.py tests/e2e/test_flow_12_query_provenance_and_docs_real.py tests/e2e/test_flow_13_human_gate_and_intervention_real.py tests/unit/test_notes_quickstart_docs.py -q`

Result:

- `18 passed in 352.33s (0:05:52)`

That batch confirms the current canonical real-E2E flow set is stable when the
flows are run together serially against per-test isolated databases, daemon
ports, auth tokens, and workspace roots.

## Flow 07 hardening note

Flow 07 required a real harness extension, not a product change:

- the original real-E2E fixture was hard-wired to the fake session backend
- the real-E2E harness now supports backend-specific daemon launch through
  `real_daemon_harness_factory`

The first tmux-backed Flow 07 rerun also exposed a real timing property:

- with a very low idle threshold, the first `session show-current` read may already
  be `stale_but_recoverable` rather than `detached`

That is valid runtime behavior, so the test now accepts either initial state and
still requires the stale-and-recoverable path before resume.

## Flow 08 hardening note

The first Flow 08 real E2E pass succeeded without requiring product fixes.

That proves the current single-child failure and parent retry path is real through the
daemon and CLI runtime.

It does not close the broader remaining gap around richer multi-child and sibling-aware
decision strategies, which still belongs to the later hardening track.

This Flow 05 checkpoint still proves the current durable control loop, not full daemon-owned
external tool execution beyond the existing compiled prompt/summary/progress path.

## Flow 09 hardening note

The first Flow 09 real E2E pass exposed one real product gap and one test-contract mismatch.

Product gap:

- the daemon could not load project-local policy and override YAML from a product-owned
  workspace root, which prevented a real quality-chain setup without in-process test catalog injection

That gap was fixed by introducing `AICODING_WORKSPACE_ROOT`-driven project resource roots
and by making default provenance refresh honor the configured workspace root.

Test-contract mismatch:

- `node audit` returns `node_id` and `node_summary`, not a nested `node` payload

That mismatch was corrected in the real E2E test without weakening the runtime proof.

## Flow 10 hardening note

The first Flow 10 real E2E pass succeeded without requiring product fixes.

That proves the shipped regenerate, rectify-upstream, rebuild-history, cutover-readiness,
and rebuild-coordination surfaces are real through the daemon and CLI runtime.

It does not close the later live git rebuild/finalize execution work, which still belongs
to the deeper git-backed hardening slices.

## Flow 11 hardening note

The first Flow 11 hardening pass exposed a real product gap:

- there was no runtime-owned way to bootstrap the per-version live git repos

That gap was fixed by adding the daemon and CLI `git bootstrap-node` surface, which
now allows the real E2E test to create the repos through the product and then use
actual `git` commands inside those repos for the child change commit.

The resulting checkpoint proves the shipped live merge/finalize path is real through
the daemon and CLI runtime.

One boundary remains explicit:

- the live git repos still live under the daemon runtime tree rather than the
  workspace-root contract used for project YAML and default provenance loading

## Flow 12 hardening note

The first Flow 12 real E2E reruns exposed only test-contract mismatches in the new test:

- provenance canonical names for the workspace source tree include the `src.` module prefix
- `node audit.summary_history` is a catalog payload with `summaries`, not a raw list

Those were corrected in the real E2E test without weakening the runtime proof.

## Flow 13 hardening note

The first Flow 13 real E2E rerun exposed only a test-contract mismatch in the new test:

- `node pause-state` returns `pause_flag_name`, `approval_required`, and `approved`,
  not the older ad hoc `pause_active` and `pause_approved` field names

That was corrected in the real E2E test without weakening the runtime proof.

## Flow 06 hardening note

The first Flow 06 reruns exposed only test-contract mismatches in the new test:

- `subtask current` returns `RunProgressResponse`, not a payload with top-level `node_id`
- the current-subtask payload uses `id` and `source_subtask_key`, not `subtask_key`

Those were corrected in the real E2E test without weakening the runtime proof.
