# Scenario And Flow Pytest Plan

## Purpose

This note turns the narrative material in `notes/scenarios/` and the canonical runtime contracts in `flows/` into an executable pytest plan.

It has two goals:

1. define how every scenario and every flow should be exercised by tests
2. record the current implementation gaps the flow suite exposes or must deliberately work around

Canonical bounded-flow command:

```bash
python3 -m pytest tests/integration/test_flow_contract_suite.py -q
```

Use `notes/catalogs/checklists/verification_command_catalog.md` for the broader command family catalog and for the current real-E2E checkpoint commands.

## Source inventory reviewed

Scenario-like inputs currently live here:

- `notes/scenarios/journeys/common_user_journeys_analysis.md`
- `notes/scenarios/walkthroughs/getting_started_hypothetical_task_guide.md`
- `notes/scenarios/walkthroughs/hypothetical_plan_workthrough.md`

Canonical flow specs currently live here:

- `flows/01_create_top_level_node_flow.md`
- `flows/02_compile_or_recompile_workflow_flow.md`
- `flows/03_materialize_and_schedule_children_flow.md`
- `flows/04_manual_tree_edit_and_reconcile_flow.md`
- `flows/05_admit_and_execute_node_run_flow.md`
- `flows/06_inspect_state_and_blockers_flow.md`
- `flows/07_pause_resume_and_recover_flow.md`
- `flows/08_handle_failure_and_escalate_flow.md`
- `flows/09_run_quality_gates_flow.md`
- `flows/10_regenerate_and_rectify_flow.md`
- `flows/11_finalize_and_merge_flow.md`
- `flows/12_query_provenance_and_docs_flow.md`
- `flows/13_human_gate_and_intervention_flow.md`

## Important repo findings

The repo does not currently contain top-level `scenarios/` or `scenarios2/` directories.

For this test-planning pass, the effective scenario sources are the three documents under `notes/scenarios/`. If separate `scenarios/` or `scenarios2/` trees are intended, they need to be added or the request wording in future planning notes should be normalized to `notes/scenarios/`.

`flows/README.md` had a stale language-level statement claiming `C++` owns orchestration logic. The implementation stack is Python for daemon and CLI, so this note set now treats that wording as corrected documentation drift rather than an architectural option.

## Scenario coverage map

### `common_user_journeys_analysis.md`

This is the broadest coverage source. It maps directly to all thirteen flow docs.

### `getting_started_hypothetical_task_guide.md`

This is the shortest end-to-end happy path and maps most directly to:

- `01_create_top_level_node_flow`
- `02_compile_or_recompile_workflow_flow`
- `05_admit_and_execute_node_run_flow`
- `06_inspect_state_and_blockers_flow`
- `07_pause_resume_and_recover_flow`

### `hypothetical_plan_workthrough.md`

This is more aspirational and broader than the current runnable built-ins, but it still informs:

- `03_materialize_and_schedule_children_flow`
- `04_manual_tree_edit_and_reconcile_flow`
- `08_handle_failure_and_escalate_flow`
- `09_run_quality_gates_flow`
- `10_regenerate_and_rectify_flow`
- `11_finalize_and_merge_flow`
- `12_query_provenance_and_docs_flow`
- `13_human_gate_and_intervention_flow`

Important limitation:

- this walkthrough still assumes some broader plan-style built-ins and live git behavior that are intentionally staged or only partially implemented today

## Test strategy

The executable test surface for these notes is `tests/integration/test_flow_contract_suite.py`.

That suite does not treat the flow docs as prose only. It registers every `flows/*.md` file in a single flow registry and requires one executor per flow.

Each flow executor must do all of the following:

- name the exact flow document it covers
- list the scenario sources it is tied to
- declare whether current support is `full`, `partial`, or `deferred_heavy`
- run a real CLI and daemon-backed sequence for the supported portion of the flow
- assert durable state or inspectable outputs rather than just command success
- keep the known limitation text next to the executable case instead of leaving it implicit

The suite also contains a guard test that fails if a new flow document is added without a matching registered executor.

## Flow-by-flow test plan

| Flow | Current support | Planned executable test shape | Main assertions | Known limitation to document |
| --- | --- | --- | --- | --- |
| `01_create_top_level_node_flow` | partial | `workflow start --kind <allow_parentless kind> ...` | node created, workflow compiled, run optionally started, current workflow inspectable | current shipped coverage still assumes `epic`-only top-level behavior even though doctrine defines top-ness structurally through `allow_parentless` rather than through one semantic kind |
| `02_compile_or_recompile_workflow_flow` | full | `node create` + `workflow compile` + compile-stage inspection reads | current workflow, chain, source discovery, schema validation, override resolution, hook policy, rendering all available and consistent | no current missing runtime feature in the authoritative compile path; candidate/rebuild compile would be a future variant rather than a defect in this flow |
| `03_materialize_and_schedule_children_flow` | full | `node child-materialization` before and after `node materialize-children` | not-materialized before, created/materialized after, children and layout ids present | no current missing runtime feature in the shipped built-in path; richer blocked-child scheduling would be a future expansion rather than a defect in this flow |
| `04_manual_tree_edit_and_reconcile_flow` | partial | `node materialize-children` + `node child create` + `node child-reconciliation` + `node reconcile-children --decision preserve_manual` | parent enters hybrid, explicit reconcile choices are inspectable, preserve-manual converts the parent to manual authority | structural layout replacement and richer hybrid merge/adopt-layout decisions are still missing |
| `05_admit_and_execute_node_run_flow` | full | compile, transition ready, `node run start`, prompt/context/start/heartbeat/summary/complete/advance | durable current subtask, prompt id, summary history, explicit execution-result capture, attempt history, run stays inspectable | none for the current command-loop slice |
| `06_inspect_state_and_blockers_flow` | full | node, tree, workflow, task, subtask, sources, blockers reads | state reads agree on node/run/workflow identity and expose current execution context | blocker semantics are only as rich as current dependency graph state |
| `07_pause_resume_and_recover_flow` | full | fake session bind, stale classification, `session show-current`, `node recovery-status`, `node recovery-provider-status`, `session resume`, `session provider-resume` | recovery classification, provider-aware restoration status, and recommended actions are deterministic and durable | provider-aware recovery is still intentionally bounded to backend-matching restorable provider identities |
| `08_handle_failure_and_escalate_flow` | partial | create failed child, inspect counters/history, apply parent decision | counters increment, parent decision history persists, retry or pause action visible | richer failure taxonomy is still bounded to current heuristics |
| `09_run_quality_gates_flow` | partial | validation, review, testing, provenance refresh, docs build, final summary | gate result histories persist and the daemon now exposes one turnkey `node quality-chain` path for the built-in late chain | live git finalize execution still belongs to the later git execution slice rather than this quality-only flow |
| `10_regenerate_and_rectify_flow` | partial | `node regenerate`, `node rectify-upstream`, `node rebuild-history` | subtree and upstream rebuild events persist and are queryable | safe live cutover and active-old-run coordination remain conservative and staged |
| `11_finalize_and_merge_flow` | full | live merge/finalize surfaces: child results, reconcile prompt, merge events/conflicts, finalize commit, repo status | merge event/conflict records persist and are inspectable and the daemon now executes real git merge/finalize operations | rebuild-driven rectification still belongs to the later rebuild-specific git flow |
| `12_query_provenance_and_docs_flow` | full | provenance refresh, rationale/entity queries, docs build/list/show | provenance entities and relations persist, docs outputs query cleanly | provenance extraction now spans Python plus JS/TS, but is still intentionally bounded to the current `module|class|function|method` model |
| `13_human_gate_and_intervention_flow` | partial | pause gate, pause-state read, blocked resume, unified intervention catalog/apply, explicit approve, resume | pause entry, approval requirement, approval record, resume, and bounded unified intervention handling are durable | rebuild/cutover intervention apply paths and richer reconcile decisions are still incomplete |

## Concrete pytest design

The flow suite should use these patterns:

- one `FlowCase` registry entry per flow document
- one `test_every_flow_doc_has_a_registered_executor` guard
- one parametrized `test_flow_contract_cases` over the registry
- one helper layer for repeated setup:
  - daemon bridge wiring
  - node creation and compile helpers
  - ready-and-running node helpers
  - bounded fake-session setup
  - custom quality-gate catalogs for pause and testing flows

The suite should prefer real CLI commands and only use daemon-bridge calls when a stage needs structured completion payloads that the CLI does not expose directly.

## Gaps and code issues found during planning

### 1. Scenario path ambiguity

The user request named `scenarios`, `scenarios2`, and `flows`, but only `flows/` exists as a top-level directory. The scenario materials that actually exist are under `notes/scenarios/`.

Recommended follow-up:

- either add the missing top-level scenario directories if they are intended artifacts
- or standardize future planning language around `notes/scenarios/`

### 2. Flow 04 support is still partial

Manual child creation and explicit `preserve_manual` reconciliation are implemented, but structural layout replacement and richer layout-adoption / hybrid-merge reconciliation remain missing from the CLI/runtime flow.

Impact on tests:

- flow coverage can only validate the currently supported manual-authority subset

### 3. Flow 09 now has one turnkey daemon-owned chain

Validation, review, testing, provenance, and docs now run through one built-in `node quality-chain` command once the active run has reached its first quality gate. The remaining limitation is that live git finalize execution still belongs to the later git execution slice.

Impact on tests:

- the flow suite should validate the supported gate slices together, but treat the full idealized chain as partially implemented

### 4. Flow 11 now covers the direct live finalize path

Durable merge events, child-result inspection, conflict persistence, conflict resolution, live merge execution, abort-merge recovery, finalize commit creation, and live repo status inspection now exist. The remaining git-runtime gap is rebuild-driven rectification rather than the direct parent finalize path.

Impact on tests:

- the flow suite should assert durable pre-merge and conflict state, not pretend full live git execution exists

### 5. Flow 13 is still narrower than the broadest intervention note language

Pause gating and approval are implemented, and the runtime now has a bounded unified intervention catalog/apply surface for pause approval, preserve-manual reconciliation, merge-conflict handling, and session recovery. Rebuild/cutover intervention apply paths and richer reconciliation decisions are still not fully unified yet.

Impact on tests:

- the flow suite should cover the pause/approval/resume contract and document the rest as planned follow-up work

## Completion expectations for this planning slice

This planning pass is complete only if all of the following hold:

- every flow document has a registered executable pytest case
- the flow registry explicitly marks support level and limitation text
- the repo contains a note documenting the scenario inventory and gaps
- stale note drift discovered during planning is corrected adjacent to the test work
- targeted pytest coverage proves the new suite is runnable

## Adjacent notes

Implementation limitations found here should stay aligned with:

- `notes/catalogs/traceability/spec_traceability_matrix.md`
- `notes/catalogs/traceability/action_automation_matrix.md`
- `notes/catalogs/audit/auditability_checklist.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/git/git_rectification_spec_v2.md`
