# Flow Coverage Checklist

## Purpose

This checklist is the quick-reference companion to:

- `notes/planning/implementation/scenario_and_flow_pytest_plan.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `tests/integration/test_flow_contract_suite.py`

It answers three questions for each canonical flow:

1. is there an executable pytest for it
2. what part of the flow is currently implemented
3. what remains missing, partial, or intentionally deferred

Status vocabulary rule:

- use `implemented`, `partial`, `verified`, and `flow_complete` deliberately
- do not treat a bounded flow-contract command as full real-E2E proof

Interpretation rule:

- bounded flow-contract status and real-E2E completion are tracked separately here
- `flow_complete` in the bounded column means the current bounded flow-contract suite passes for the declared scope
- real-E2E completion records whether the declared real runtime checkpoint exists and what it currently proves

## Flow Status Summary

| Flow | Bounded proof status | Real E2E target | Real E2E completion |
| --- | --- | --- | --- |
| 01 Create Top-Level Node | `partial` | `tests/e2e/test_flow_01_create_top_level_node_real.py` | `partial` |
| 02 Compile Or Recompile Workflow | `flow_complete` | `tests/e2e/test_flow_02_compile_or_recompile_workflow_real.py` | `partial` |
| 03 Materialize And Schedule Children | `flow_complete` | `tests/e2e/test_flow_03_materialize_and_schedule_children_real.py` | `partial` |
| 04 Manual Tree Edit And Reconcile | `partial` | `tests/e2e/test_flow_04_manual_tree_edit_and_reconcile_real.py` | `partial` |
| 05 Admit And Execute Node Run | `flow_complete` | `tests/e2e/test_flow_05_admit_and_execute_node_run_real.py` | `partial` |
| 06 Inspect State And Blockers | `flow_complete` | `tests/e2e/test_flow_06_inspect_state_and_blockers_real.py` | `partial` |
| 07 Pause Resume And Recover | `flow_complete` | `tests/e2e/test_flow_07_pause_resume_and_recover_real.py` | `partial` |
| 08 Handle Failure And Escalate | `partial` | `tests/e2e/test_flow_08_handle_failure_and_escalate_real.py` | `partial` |
| 09 Run Quality Gates | `partial` | `tests/e2e/test_flow_09_run_quality_gates_real.py` | `partial` |
| 10 Regenerate And Rectify | `partial` | `tests/e2e/test_flow_10_regenerate_and_rectify_real.py` | `partial` |
| 11 Finalize And Merge | `flow_complete` | `tests/e2e/test_flow_11_finalize_and_merge_real.py` | `partial` |
| 12 Query Provenance And Docs | `flow_complete` | `tests/e2e/test_flow_12_query_provenance_and_docs_real.py` | `partial` |
| 13 Human Gate And Intervention | `partial` | `tests/e2e/test_flow_13_human_gate_and_intervention_real.py` | `partial` |

## Coverage status

### 01 Create Top-Level Node Flow

- [x] Planned in `scenario_and_flow_pytest_plan.md`
- [x] Executable in `test_flow_contract_suite.py`
- [x] Phase 1 targeted rerun completed
- [x] Covered by a real CLI/daemon-backed happy path
- [x] Creates a durable node
- [x] Compiles a durable workflow
- [x] Optionally starts the first run
- [ ] Current top-level behavior is reconciled with the doctrine that any node kind may be top-level when created without a parent and allowed by hierarchy YAML
- [x] First real E2E checkpoint exists with real daemon subprocess plus real CLI subprocess
- [x] Product-owned configurable workspace root now exists for project resources and default provenance refresh
- [ ] Live git and session cwd ownership are still not unified around the workspace root

Latest targeted rerun:

- `python3 -m pytest tests/integration/test_flow_contract_suite.py::test_flow_contract_cases[01] -q`
- result: `1 passed`
- issues found: none for the current supported top-level path
- current conclusion: the current bounded test proves only the shipped `epic` path; Flow 01 remains doctrinally partial until built-in hierarchy YAML and startup coverage are reconciled with the generic `allow_parentless` rule

Real E2E checkpoint:

- `python3 -m pytest tests/e2e/test_flow_01_create_top_level_node_real.py -q`
- result: `1 passed`
- issues found during hardening:
  - the first pass exposed stale assumptions in the new test about operator-summary and git-branch response shapes
  - those assumptions were corrected to the actual daemon contract
- current conclusion: Flow 01 now has one real end-to-end checkpoint through the real daemon subprocess and real CLI subprocess, but it still proves only the current `epic` startup path rather than the full doctrinal top-level rule

### 02 Compile Or Recompile Workflow Flow

- [x] Planned in `scenario_and_flow_pytest_plan.md`
- [x] Executable in `test_flow_contract_suite.py`
- [x] Phase 1 targeted rerun completed
- [x] Covers compile, chain, and workflow inspection
- [x] Covers source discovery inspection
- [x] Covers schema validation inspection
- [x] Covers override resolution inspection
- [x] Covers hook and policy expansion inspection
- [x] Covers rendering and frozen payload inspection
- [x] Current authoritative compile scope documented as intentional for this flow
- [x] First real E2E checkpoint exists with real daemon subprocess plus real CLI subprocess
- [ ] Parallel-safe per-test DB isolation exists for real E2E compile-stage flow runs

Latest targeted rerun:

- `python3 -m pytest tests/integration/test_flow_contract_suite.py::test_flow_contract_cases[02] -q`
- result: `1 passed`
- issues found: none for the current authoritative compile path
- current conclusion: Flow 02 is `flow_complete` for the current bounded flow-contract layer and the current authoritative compile path

Real E2E checkpoint:

- `python3 -m pytest tests/e2e/test_flow_02_compile_or_recompile_workflow_real.py -q`
- result: `1 passed`
- issues found during hardening:
  - the first failure was caused by the earlier shared-database real E2E harness
  - the harness now creates one database per real E2E test, removing that database-layer interference
- current conclusion: Flow 02 now has one real end-to-end checkpoint, and the old shared-database parallel-safety limitation has been removed at the DB layer

### 03 Materialize And Schedule Children Flow

- [x] Planned in `scenario_and_flow_pytest_plan.md`
- [x] Executable in `test_flow_contract_suite.py`
- [x] Phase 1 targeted rerun completed
- [x] Covers pre-materialization inspection
- [x] Covers materialize-children execution
- [x] Covers post-materialization child inspection
- [x] Current built-in materialization scope documented as intentional for this flow
- [x] First real E2E checkpoint exists with real daemon subprocess plus real CLI subprocess

Latest targeted rerun:

- `python3 -m pytest tests/integration/test_flow_contract_suite.py::test_flow_contract_cases[03] -q`
- result: `1 passed`
- issues found: none for the current shipped built-in materialization path
- current conclusion: Flow 03 is `flow_complete` for the current bounded flow-contract layer and the current shipped built-in materialization path

Real E2E checkpoint:

- `python3 -m pytest tests/e2e/test_flow_03_materialize_and_schedule_children_real.py -q`
- result: `1 passed`
- issues found during hardening:
  - the first pass exposed a real CLI daemon timeout limit during child materialization
  - after that product fix, the only remaining failure was a stale test assumption about the
    `tree show --full` payload shape
- current conclusion: Flow 03 now has one real end-to-end checkpoint through the real daemon
  subprocess and real CLI subprocess

### 04 Manual Tree Edit And Reconcile Flow

- [x] Planned in `scenario_and_flow_pytest_plan.md`
- [x] Executable in `test_flow_contract_suite.py`
- [x] Phase 1 targeted rerun completed
- [x] Covers manual child creation
- [x] Covers manual authority-mode inspection
- [x] Explicit manual-vs-layout reconciliation choice surface
- [x] Preserve-manual hybrid reconciliation workflow
- [x] First real E2E checkpoint exists with real daemon subprocess plus real CLI subprocess
- [ ] Explicit structural layout replacement CLI surface
- [ ] Fully implemented layout-adoption / hybrid-merge reconciliation workflow

Latest targeted rerun:

- `python3 -m pytest tests/integration/test_flow_contract_suite.py::test_flow_contract_cases[04] -q`
- result: `1 passed`
- issues found: the preserve-manual path is now explicit, but structural layout replacement is still missing
- current conclusion: Flow 04 remains partial because explicit preserve-manual reconciliation now exists, but layout replacement and richer hybrid merge decisions are still missing

Real E2E checkpoint:

- `python3 -m pytest tests/e2e/test_flow_04_manual_tree_edit_and_reconcile_real.py -q`
- result: `1 passed`
- issues found during hardening:
  - none in the current shipped preserve-manual path
- current conclusion: Flow 04 now has one real end-to-end checkpoint for the current
  explicit preserve-manual reconciliation path, but the broader layout-replacement
  and hybrid-merge backlog remains open

### 05 Admit And Execute Node Run Flow

- [x] Planned in `scenario_and_flow_pytest_plan.md`
- [x] Executable in `test_flow_contract_suite.py`
- [x] Covers run admission
- [x] Covers prompt and context retrieval
- [x] Covers subtask start
- [x] Covers heartbeat recording
- [x] Covers summary registration
- [x] Covers complete and workflow advance
- [x] Covers explicit execution-result capture and durable attempt-history inspection
- [x] First real E2E checkpoint exists with real daemon subprocess plus real CLI subprocess
- [ ] Real daemon-owned external tool execution orchestration beyond the current durable control loop

Real E2E checkpoint:

- `python3 -m pytest tests/e2e/test_flow_05_admit_and_execute_node_run_real.py -q`
- result: `1 passed`
- issues found during hardening:
  - the initial failures were stale assumptions in the new test about `RunProgressResponse`
    and `SummaryRegistrationResponse` payload shapes
- current conclusion: Flow 05 now has one real end-to-end checkpoint for the shipped
  durable run-control loop, but it still does not prove daemon-owned external tool
  execution beyond that current control surface

### 06 Inspect State And Blockers Flow

- [x] Planned in `scenario_and_flow_pytest_plan.md`
- [x] Executable in `test_flow_contract_suite.py`
- [x] Covers node inspection
- [x] Covers tree inspection
- [x] Covers task and subtask inspection
- [x] Covers blocker inspection
- [x] Covers YAML/source lineage inspection
- [x] Covers workflow inspection
- [x] First real E2E checkpoint exists with real daemon subprocess plus real CLI subprocess
- [ ] Richer blocker scenarios beyond the current dependency state exercised in the flow suite

Real E2E checkpoint:

- `python3 -m pytest tests/e2e/test_flow_06_inspect_state_and_blockers_real.py -q`
- result: `1 passed`
- issues found during hardening:
  - the initial failures were stale assumptions in the new test about `RunProgressResponse`
    and current-subtask field names
- current conclusion: Flow 06 now has one real end-to-end checkpoint for the current
  operator and inspectability path

### 07 Pause Resume And Recover Flow

- [x] Planned in `scenario_and_flow_pytest_plan.md`
- [x] Executable in `test_flow_contract_suite.py`
- [x] Covers session binding
- [x] Covers stale-session classification
- [x] Covers recovery-status inspection
- [x] Covers session resume
- [x] Covers provider-specific recovery status and provider-aware resume
- [x] First real E2E checkpoint exists with real daemon subprocess plus real CLI subprocess plus real tmux backend

Real E2E checkpoint:

- `python3 -m pytest tests/e2e/test_flow_07_pause_resume_and_recover_real.py -q`
- result: `1 passed`
- issues found during hardening:
  - the original real-E2E harness had to be extended because it was hard-wired to the fake
    session backend
  - with a very low idle threshold, the first `session show-current` read can already be
    `stale_but_recoverable`
- current conclusion: Flow 07 now has one real end-to-end checkpoint for the tmux-backed
  session bind, stale classification, and recovery path

### 08 Handle Failure And Escalate Flow

- [x] Planned in `scenario_and_flow_pytest_plan.md`
- [x] Executable in `test_flow_contract_suite.py`
- [x] Covers child failure persistence
- [x] Covers parent response command
- [x] Covers child-failure counters
- [x] Covers parent decision history
- [x] Covers richer failure taxonomy and explicit decision-matrix reasoning in the runtime/API layer
- [x] First real E2E checkpoint exists with real daemon subprocess plus real CLI subprocess
- [ ] Multi-child and sibling-aware decision strategies remain limited

Real E2E checkpoint:

- `python3 -m pytest tests/e2e/test_flow_08_handle_failure_and_escalate_real.py -q`
- result: `1 passed`
- issues found during hardening:
  - none in the current single-child retry/escalation path
- current conclusion: Flow 08 now has one real end-to-end checkpoint for the shipped
  child-failure and parent-retry path, while the broader multi-child decision matrix
  remains out of scope

### 09 Run Quality Gates Flow

- [x] Planned in `scenario_and_flow_pytest_plan.md`
- [x] Executable in `test_flow_contract_suite.py`
- [x] Covers validation gate visibility
- [x] Covers review gate visibility
- [x] Covers testing gate visibility
- [x] Covers provenance refresh
- [x] Covers docs generation
- [x] Covers one turnkey built-in chain that runs validation, review, testing, provenance, docs, and final summary generation end to end
- [x] First real E2E checkpoint exists with real daemon subprocess plus real CLI subprocess and a real workspace-local project policy/override setup
- [ ] Live git finalize execution still remains outside Flow 09 and belongs to the later git execution slice
- [x] DB-backed real E2E runs now have per-test database isolation

Real E2E checkpoint:

- `python3 -m pytest tests/e2e/test_flow_09_run_quality_gates_real.py -q`
- result: `1 passed`
- issues found during hardening:
  - the daemon originally lacked a product-owned workspace-root contract for project-local
    policy and override YAML, which made a real quality-chain setup impossible without
    in-process catalog injection
  - after that product fix, the only remaining failure was a stale test assumption about
    the `node audit` payload shape
- current conclusion: Flow 09 now has one real end-to-end checkpoint for the shipped
  turnkey quality chain, project-local gate policy loading, provenance refresh, docs
  generation, and final-summary persistence

### 10 Regenerate And Rectify Flow

- [x] Planned in `scenario_and_flow_pytest_plan.md`
- [x] Executable in `test_flow_contract_suite.py`
- [x] Covers subtree regeneration
- [x] Covers upstream rectification
- [x] Covers rebuild-history inspection
- [x] Covers rebuild-coordination inspection for subtree/upstream scope
- [x] Covers candidate cutover-readiness inspection
- [x] Blocked rebuild/cutover attempts now leave durable coordination audit in `rebuild_events`
- [x] First real E2E checkpoint exists with real daemon subprocess plus real CLI subprocess
- [ ] Real live git rebuild/finalize execution still remains deferred

Real E2E checkpoint:

- `python3 -m pytest tests/e2e/test_flow_10_regenerate_and_rectify_real.py -q`
- result: `1 passed`
- issues found during hardening:
  - none in the shipped regenerate/rectify/coordination path
- current conclusion: Flow 10 now has one real end-to-end checkpoint for the current
  regenerate, rectify-upstream, rebuild-history, cutover-readiness, and rebuild-coordination
  surfaces, while live git rebuild/finalize execution remains out of scope

### 11 Finalize And Merge Flow

- [x] Planned in `scenario_and_flow_pytest_plan.md`
- [x] Executable in `test_flow_contract_suite.py`
- [x] Covers runtime-owned live git repo bootstrap
- [x] Covers real live git merge-children execution
- [x] Covers durable merge-event inspection
- [x] Covers durable merge-conflict recording and inspection
- [x] Covers real working-tree finalize execution
- [x] Covers end-to-end live git finalize path
- [x] Covers live git status inspection for the finalized parent repo
- [x] First real E2E checkpoint exists with real daemon subprocess plus real CLI subprocess plus actual git commits inside the bootstrapped repos
- [ ] Live git repos are still rooted in the daemon runtime tree rather than the workspace-root contract

Real E2E checkpoint:

- `python3 -m pytest tests/e2e/test_flow_11_finalize_and_merge_real.py -q`
- result: `1 passed`
- issues found during hardening:
  - the original runtime lacked a product-owned git bootstrap surface for the per-version repos
  - that gap was fixed by adding `git bootstrap-node`
- current conclusion: Flow 11 now has one real end-to-end checkpoint for the shipped
  live bootstrap, merge, finalize, merge-event, final-commit, and git-status path,
  but repo-root ownership is still not unified with the workspace-root contract

### 12 Query Provenance And Docs Flow

- [x] Planned in `scenario_and_flow_pytest_plan.md`
- [x] Executable in `test_flow_contract_suite.py`
- [x] Covers provenance refresh
- [x] Covers rationale inspection
- [x] Covers entity inspection
- [x] Covers relation inspection
- [x] Covers docs build and docs list
- [x] Provenance extraction now spans the current bounded Python plus JS/TS entity model
- [x] First real E2E checkpoint exists with real daemon subprocess plus real CLI subprocess
- [ ] Provenance extraction beyond the current bounded `module|class|function|method` model

Real E2E checkpoint:

- `python3 -m pytest tests/e2e/test_flow_12_query_provenance_and_docs_real.py -q`
- result: `1 passed`
- issues found during hardening:
  - the initial reruns exposed stale test assumptions about provenance canonical naming
    under the workspace root and the shape of `node audit.summary_history`
- current conclusion: Flow 12 now has one real end-to-end checkpoint for the shipped
  provenance-refresh, rationale, entity-history, relation, docs-build, docs-show,
  and node-audit path

### 13 Human Gate And Intervention Flow

- [x] Planned in `scenario_and_flow_pytest_plan.md`
- [x] Executable in `test_flow_contract_suite.py`
- [x] Covers pause-state inspection
- [x] Covers blocked resume before approval
- [x] Covers explicit approval
- [x] Covers resume after approval
- [x] Covers unified intervention catalog and apply entrypoint for pause approval
- [x] Runtime now exposes first-class intervention handling for pause approval, preserve-manual reconciliation, merge-conflict abort/resolve, and session recovery
- [x] First real E2E checkpoint exists with real daemon subprocess plus real CLI subprocess
- [ ] Rebuild- and cutover-specific intervention apply paths are still not unified
- [ ] Richer reconciliation decisions beyond `preserve_manual` are still missing

Real E2E checkpoint:

- `python3 -m pytest tests/e2e/test_flow_13_human_gate_and_intervention_real.py -q`
- result: `1 passed`
- issues found during hardening:
  - the initial rerun exposed a stale test assumption about the `node pause-state` payload shape
- current conclusion: Flow 13 now has one real end-to-end checkpoint for the shipped
  pause approval, blocked resume, intervention-catalog, intervention-apply, and resume path

## Repo-level findings

- [x] Canonical flows reviewed under `flows/`
- [x] Scenario sources reviewed under `notes/scenarios/`
- [x] Executable flow-suite test added
- [x] Stale `flows/README.md` language corrected from `C++` to `Python`
- [ ] Top-level `scenarios/` directory exists
- [ ] Top-level `scenarios2/` directory exists

Current note:

- the actual scenario sources are currently under `notes/scenarios/`

## Simulation-derived strict real-E2E checkpoints

### 19 Hook Expansion Compile-Stage Flow

- [x] YAML flow asset exists
- [x] Bounded YAML-flow contract exists
- [x] Strict real daemon/CLI subprocess checkpoint exists
- [x] Current strict checkpoint inspects real compile-stage hook expansion

Current gap note:

- the strict real-E2E test is currently red because the shipped task-node hook selection and
  expanded-step order differ from the older simulation-derived expectation

### 20 Compile Failure And Reattempt Flow

- [x] YAML flow asset exists
- [x] Bounded YAML-flow contract exists
- [x] Strict real daemon/CLI subprocess checkpoint exists
- [x] Current strict checkpoint exercises real compile failure, durable failure inspection, source repair, and recompile
- [ ] Source-discovery inspection for a compile-failed node currently works without a compiled workflow snapshot

Current gap note:

- the strict real-E2E test now shows that `workflow source-discovery --node ...` still returns
  `compiled workflow not found` after a failed compile
- that means compile-failed nodes do not yet have a first-class source-discovery inspection
  surface before successful recompilation

### 21 Child Session Round-Trip And Merge-Back Flow

- [x] YAML flow asset exists
- [x] Bounded YAML-flow contract exists
- [x] Strict real daemon/CLI/tmux checkpoint exists
- [ ] Live child tmux session currently produces durable merge-back without a synthetic `session pop` payload

Current gap note:

- the strict real-E2E test now waits for live child-session work instead of injecting a merge-back result
- this is expected to stay red until tmux sessions launch Codex and the daemon can observe real child-produced merge-back state
- the current first failure shows the tmux child session still presents a shell prompt with raw delegated prompt text rather than a Codex-launched child agent

### 22 Dependency-Blocked Sibling Wait Flow

- [x] YAML flow asset exists
- [x] Bounded YAML-flow contract exists
- [x] Strict real daemon/CLI/tmux checkpoint exists
- [ ] Dependency sibling currently reaches `COMPLETE` through a real live-session path without forced lifecycle mutation

Current gap note:

- the strict real-E2E test now waits for live sibling completion instead of forcing lifecycle state
- this is expected to stay red until tmux sessions launch Codex and the daemon can observe real completion from the live session
- the first strict run also exposed that the dependent sibling was still startable in the tested dependency scenario, so blocker enforcement is not yet matching the intended flow

## Reference rule

If a future feature claims to complete one of these flows, this checklist should be updated in the same change as:

- the relevant code
- the relevant tests
- the relevant design notes
