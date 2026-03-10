# Per-Flow Gap Remediation Plan

## Purpose

This note defines the next work in the format requested for flow completion:

- each flow is handled separately
- each flow advances in explicit phases
- each phase starts by running the relevant flow test
- each phase records the issues and missing features exposed by that test run
- each phase then defines the next implementation slice from the observed failures

This note is paired with:

- `tests/integration/test_flow_contract_suite.py`
- `notes/catalogs/audit/flow_coverage_checklist.md`
- `notes/planning/implementation/scenario_and_flow_pytest_plan.md`

Status language rule:

- the `full`, `partial`, and `deferred_heavy` labels in this document describe bounded flow-contract support only
- they do not mean the flow already has full real-E2E completion
- use `notes/catalogs/audit/flow_coverage_checklist.md` and `notes/catalogs/checklists/feature_checklist_backfill.md` for the current real-E2E target and completion posture

## Required phase loop

Every flow below uses the same execution loop.

### Phase 1: Baseline Flow Test Run

- run the current flow test
- record exact failures, conflicts, missing reads, missing mutations, and partial behavior
- classify the flow as `full`, `partial`, or `deferred_heavy`

### Phase 2: Minimum Surface Closure

- implement the smallest missing CLI/API/read/mutation surface required by the failed test
- re-run the same flow test
- record what still fails

### Phase 3: Runtime Behavior Closure

- implement the missing orchestration, state-transition, persistence, or compile/runtime behavior exposed by the test
- re-run the same flow test
- record what still fails

### Phase 4: Audit And Recovery Closure

- implement any missing inspectability, audit trail, durable event history, or recovery semantics the flow still lacks
- re-run the same flow test
- record the remaining limitations

### Phase 5: Full Flow Confirmation

- run the complete flow test again
- mark the bounded flow-contract layer `flow_complete` if it is now fully supported for the declared scope
- otherwise record the exact remaining deferred behavior and carry it into a new follow-up plan

## Flow-by-flow phases

### Flow 01: Create Top-Level Node

Current bounded tested status:

- `partial`

Observed baseline from the current flow test:

- top-level creation works
- compile works
- optional run start works
- current practical limitation is that the shipped built-in hierarchy and tests still only exercise `epic` as parentless, even though the doctrine defines top-ness structurally through `allow_parentless`

Phase 1 execution result:

- `python3 -m pytest tests/integration/test_flow_contract_suite.py::test_flow_contract_cases[01] -q`
- result: `1 passed`
- observed issues: none in the current supported top-level path
- confirmed limitation after the targeted rerun: Flow 01 coverage is still too narrow because it proves only the current `epic` path instead of the broader hierarchy rule

Phase 2 decision:

- reviewed hierarchy and startup notes plus runtime tests
- result: the runtime surface is generic, but the built-in hierarchy YAML and workflow-start tests are narrower than the doctrine
- conclusion: `epic`-only parentless behavior should be treated as a reconciliation target, not as the intended steady-state rule

Phase 3 decision:

- no additional generic API design was needed, but built-in hierarchy YAML, startup tests, and top-level walkthrough docs still need reconciliation so Flow 01 proves the intended doctrine rather than one shipped default

Phase 4 decision:

- no additional audit or recovery closure work was needed for Flow 01
- durable node creation, compile result, lifecycle result, and optional run admission are already inspectable and covered by tests

Phase 5 confirmation:

- Flow 01 should remain `partial` until the shipped built-in hierarchy, tests, and walkthroughs are reconciled with the doctrinal rule that any kind may be top-level when created without a parent and allowed by hierarchy YAML

Next phases:

- reconcile the built-in hierarchy YAML and startup tests with the doctrinal `allow_parentless` rule
- extend Flow 01 coverage so it proves more than the single current `epic` path

### Flow 02: Compile Or Recompile Workflow

Current bounded tested status:

- `full` for the authoritative compile path

Observed baseline from the current flow test:

- compile, chain, source discovery, schema validation, override resolution, hook/policy inspection, and rendering inspection all work
- current limitation is scope: the flow test validates the authoritative compile path only

Phase 1 execution result:

- `python3 -m pytest tests/integration/test_flow_contract_suite.py::test_flow_contract_cases[02] -q`
- result: `1 passed`
- observed issues: none in the current authoritative compile path
- confirmed limitation after the targeted rerun: candidate-version compile and rebuild compile are better treated as future compile-flow variants, not as missing behavior in the current authoritative compile flow

Phase 2 decision:

- no minimum surface closure work was needed
- the current compile inspection surfaces already expose:
  - workflow chain
  - source discovery
  - schema validation inventory
  - override resolution
  - hook/policy expansion
  - rendering and frozen payloads

Phase 3 decision:

- no runtime behavior closure work was needed for the current authoritative compile path

Phase 4 decision:

- no additional audit or recovery closure work was needed for Flow 02
- durable compile diagnostics and compile-stage read surfaces are already inspectable and covered by tests

Phase 5 confirmation:

- Flow 02 is `flow_complete` for the current bounded flow-contract slice
- candidate-version compile and rebuild compile now have a dedicated follow-up implementation track under `plan/features/63_F03_candidate_and_rebuild_compile_variants.md`

Next phases:

- none for the current slice
- candidate-version compile and rebuild compile are now treated as explicit compile-flow variants rather than implicit future-only behavior; keep Flow 02 focused on the authoritative compile contract

### Flow 03: Materialize And Schedule Children

Current bounded tested status:

- `full` for the shipped built-in materialization path

Observed baseline from the current flow test:

- pre-materialization inspection works
- materialize-children works
- post-materialization child inspection works
- current limitation is that the exercised scheduling behavior is bounded to the current built-in layouts

Phase 1 execution result:

- `python3 -m pytest tests/integration/test_flow_contract_suite.py::test_flow_contract_cases[03] -q`
- result: `1 passed`
- observed issues: none in the current shipped built-in materialization path
- confirmed limitation after the targeted rerun: richer ready-versus-blocked child scheduling should be treated as a future expansion of Flow 03 rather than a missing behavior in the currently shipped built-in path

Phase 2 decision:

- no minimum surface closure work was needed
- the current materialization inspection surfaces already expose:
  - pre-materialization state
  - materialize-children mutation result
  - post-materialization child inspection

Phase 3 decision:

- no runtime behavior closure work was needed for the current built-in layout-driven materialization path

Phase 4 decision:

- no additional audit or readback closure work was needed for Flow 03 in the current built-in path

Phase 5 confirmation:

- Flow 03 is `flow_complete` for the current bounded flow-contract slice
- richer blocked-child scheduling should be reopened later as a new Flow 03 expansion only if the runtime adds more complex scheduling expectations

Next phases:

- none for the current slice
- if the runtime grows a richer blocked-child scheduling contract, reopen Flow 03 with an additional blocked-descendant test variant

### Flow 04: Manual Tree Edit And Reconcile

Current bounded tested status:

- `partial`

Observed baseline from the current flow test:

- manual child creation works
- manual authority-mode inspection works
- missing features are:
  - no explicit structural layout replacement surface
  - no richer hybrid merge/adopt-layout reconciliation path

Phase 1 execution result:

- `python3 -m pytest tests/integration/test_flow_contract_suite.py::test_flow_contract_cases[04] -q`
- result: `1 passed`
- observed issues: the new explicit preserve-manual reconciliation path works, but structural layout replacement is still absent
- confirmed limitation after the targeted rerun: Flow 04 remains partial because preserve-manual reconciliation now exists, while layout replacement and richer hybrid merge decisions are still absent

Phase 2 decision:

- minimum missing surfaces still required:
  - explicit layout replacement command
  - richer reconcile choices beyond `preserve_manual`

Phase 3 decision:

- runtime behavior closure is still required after those surfaces exist:
  - safe structural replacement for layout-managed trees
  - safe hybrid merge/adopt-layout behavior

Phase 4 decision:

- audit and inspectability work is still needed once hybrid reconciliation exists:
  - record why the tree became hybrid
  - record which reconcile choice was taken
  - expose the current authority and reconcile state clearly to operators

Phase 5 confirmation:

- Flow 04 is not complete
- the current manual-child plus preserve-manual subset is stable and verified
- the remaining work is specifically the missing structural layout replacement and richer hybrid merge path, not instability in the already-supported manual-child path

Next phases:

- Phase 2: add the missing minimum operator surfaces:
- Phase 2: add the missing minimum operator surfaces:
  - layout replacement command
  - richer reconcile choices beyond `preserve_manual`
- Phase 3: implement the remaining structural replacement and hybrid-authority merge behavior those new surfaces require
- Phase 4: add audit and inspectability for manual edits versus layout-owned edits
- Phase 5: re-run a fuller Flow 04 test that includes manual edit plus explicit reconcile and document any remaining hybrid edge cases

### Flow 05: Admit And Execute Node Run

Current bounded tested status:

- `full` for the durable command loop

Observed baseline from the current flow test:

- run admission works
- prompt/context/start/heartbeat/summary/complete/advance work
- explicit execution-result capture and durable attempt-history reads now exist
- current limitation is that the test still focuses on durable control-loop behavior, not real daemon-owned external execution semantics

Next phases:

- Phase 1: re-run `Flow 05` and record whether any real external execution semantics are still required beyond the current explicit result-capture contract
- Phase 2: expose the minimum missing read or mutation surfaces if reruns show hidden attempt or environment state
- Phase 3: implement daemon-owned external execution only if the flow is expanded to require live tool-launch authority
- Phase 4: add audit/recovery assertions for execution-environment and attempt history
- Phase 5: extend the flow test only if the runtime has grown beyond the current durable control loop

### Flow 06: Inspect State And Blockers

Current tested status:

- `full` for the current inspection surface

Observed baseline from the current flow test:

- node/tree/task/subtask/workflow/source reads work
- blocker inspection works, but the exercised case is light
- blocker explanation now has a dedicated implementation follow-up under `plan/features/64_F08_F15_richer_child_scheduling_and_blocker_explanation.md`
- current limitation is depth, not correctness

Next phases:

- Phase 1: re-run `Flow 06` and capture the exact blocker payloads for the current simple case
- Phase 2: add any missing inspection surface if richer blocker explanations are still absent
- Phase 3: implement richer blocker-state reporting for dependency, pause, user-gate, and recovery blockers
- Phase 4: add audit/readback checks that prove blocker origin and clearing history
- Phase 5: expand the flow test to cover multiple blocker classes if the runtime now supports them

### Flow 07: Pause Resume And Recover

Current tested status:

- `full` for the current recovery slice

Observed baseline from the current flow test:

- session bind works
- stale-session classification works
- recovery-status and session resume work
- provider-aware status and provider-aware rebound now exist for restorable provider sessions
- current limitation is that provider-aware recovery remains bounded to backend-matching restorable provider identities

Next phases:

- Phase 1: re-run `Flow 07` and record whether the current provider-aware and provider-agnostic outputs are sufficient for all recovery classes
- Phase 2: add any minimum missing read surface if healthy, stale, detached, and lost states are not distinguished clearly enough
- Phase 3: expand provider-specific recovery only if additional provider backends or restoration modes are introduced
- Phase 4: ensure auditability of recovery decisions and replacement-session bootstraps
- Phase 5: expand the flow test into subcases if provider-specific semantics become first-class

### Flow 08: Handle Failure And Escalate

Current tested status:

- `partial`

Observed baseline from the current flow test:

- the current flow test now proves:
  - child failure persistence
  - parent response command
  - child-failure counters
  - parent decision history
- current limitation is breadth:
  - only one realistic child-failure path is exercised in the flow suite itself
  - the runtime now exposes a broader failure taxonomy and explicit decision-matrix reasoning, but the executable flow still under-covers multi-class and multi-child cases
  - sibling-aware weighting and cluster-level failure interpretation remain intentionally limited even with the broader matrix

Next phases:

- Phase 1: re-run `Flow 08` and capture the exact current response for the tested retry/escalation branch
- Phase 2: expose any missing decision/read surfaces for alternate failure classes
- Phase 3: implement missing parent-decision branches revealed by new subcases:
  - retry child
  - regenerate child
  - replan parent
  - pause for user
- Phase 4: add audit and inspectability for failure classification, automatic versus explicit decisions, and repeated-failure thresholds
- Phase 5: split Flow 08 into multiple test variants until the decision matrix is fully represented

### Flow 09: Run Quality Gates

Current tested status:

- `partial`

Observed baseline from the current flow test:

- validation, review, testing, provenance, docs, and final summary generation are now exercised through one daemon-owned `node quality-chain` path
- the stitched per-stage manual calls were removed from the executable flow
- remaining limitation is boundary, not basic runtime wiring:
  - live git finalize execution still belongs to the later git execution slice rather than this quality-only flow

Next phases:

- Phase 1: re-run `Flow 09` on the turnkey path and confirm validation/review/testing/provenance/docs/final summary all remain durable
- Phase 2: widen the flow to cover gate failure and retry branches through the same turnkey command
- Phase 3: decide whether late-chain provenance/docs/finalize should remain daemon-owned or become compiled subtasks for the default node ladder
- Phase 4: ensure audit/readback remains compact and stable as the turnkey chain grows
- Phase 5: fold any remaining finalize semantics that belong to quality-only completion into this flow after the git execution slice lands

### Flow 10: Regenerate And Rectify

Current tested status:

- `partial`

Observed baseline from the current flow test:

- subtree regenerate works
- upstream rectify works
- rebuild history works
- rebuild coordination and cutover-readiness reads now exist
- blocked rebuild and cutover attempts now leave durable rebuild-event audit
- current limitation is now narrower: real live git rebuild/finalize execution is still staged

Next phases:

- Phase 1: re-run `Flow 10` and preserve the current rebuild-coordination and cutover-readiness outputs as the supported baseline
- Phase 2: if needed, widen the blocker taxonomy for multi-node and multi-session live conflicts
- Phase 3: keep real live git rebuild/finalize execution work in the later git feature rather than overloading Flow 10
- Phase 4: add recovery semantics only if live rebuild execution introduces additional abandoned/partial states
- Phase 5: fold true end-to-end rebuild execution assertions into Flow 10 after the git execution slice lands

### Flow 11: Finalize And Merge

Current tested status:

- `full`

Observed baseline from the current flow test:

- live merge-children now performs real git fetch/merge against the per-version runtime repos
- durable merge events and merge conflicts are inspectable
- live finalize now creates a real finalize commit and records the resulting final commit SHA
- the current test now proves a true end-to-end finalize-and-merge happy path

Next phases:

- Phase 1: keep rerunning `Flow 11` as the happy-path regression test for live merge/finalize
- Phase 2: extend the flow only if a richer finalize policy or multi-stage finalize gate is added
- Phase 3: keep conflict-heavy and rebuild-heavy git cases in the adjacent git and rebuild flows instead of overloading Flow 11
- Phase 4: expand audit assertions if new git-runtime workflow events are added
- Phase 5: reopen only if the direct parent merge/finalize contract changes

Important priority note:

- `Flow 11` is no longer the primary missing runtime gap
- remaining git-runtime gaps are now concentrated in rebuild-driven rectification and broader intervention policy, not the direct finalize-and-merge happy path

### Flow 12: Query Provenance And Docs

Current tested status:

- `full` for the current bounded provenance model

Observed baseline from the current flow test:

- provenance refresh works
- rationale/entity/relation reads work
- docs build/list/show work
- current limitation is that provenance extraction is still intentionally bounded to the current `module|class|function|method` model even though it now spans Python plus JS/TS implementation code

Next phases:

- Phase 1: re-run `Flow 12` and record whether the current provenance/doc outputs are sufficient for the intended product scope
- Phase 2: add any minimum read surface required for missing provenance or docs inspection
- Phase 3: implement richer provenance extraction only if the rerun or note review shows it is required
- Phase 4: add audit coverage for expanded provenance identity or relation models
- Phase 5: extend the flow test if provenance scope grows

### Flow 13: Human Gate And Intervention

Current tested status:

- `partial`

Observed baseline from the current flow test:

- pause-state inspection works
- blocked resume before approval works
- explicit approval works
- resume after approval works
- a bounded unified intervention surface now exists for pause approval, preserve-manual reconciliation, merge-conflict handling, and session recovery
- current limitation is that rebuild-driven and cutover-specific decisions are not yet fully on the same apply surface, and richer reconciliation actions are still limited

Next phases:

- Phase 1: re-run `Flow 13` and preserve the exact current pause/approve/resume behavior as the baseline
- Phase 2: expose direct rebuild and cutover intervention surfaces plus richer reconciliation actions
- Phase 3: implement the remaining decision routing for rebuild/cutover intervention handling
- Phase 4: extend intervention audit and operator inspection only if the existing `workflow_events` model becomes too narrow
- Phase 5: expand the flow test from pause approval to the broader intervention matrix already partially implemented

## Cross-cutting issue: scenario source layout mismatch

Observed baseline:

- the request language refers to `scenarios` and `scenarios2`
- the actual reviewed scenario sources are under `notes/scenarios`

Phases:

- Phase 1: decide whether `scenarios/` and `scenarios2/` are intended real repo roots
- Phase 2: either add them or standardize all planning and audit notes around `notes/scenarios`
- Phase 3: re-run the note-audit checks and remove ambiguity from the checklist and planning notes

## Recommended order

If the next work should prioritize the largest runtime gaps exposed by the tests:

1. Flow 11
2. Flow 04
3. Flow 09
4. Flow 13
5. Flow 08
6. Flow 10

If the next work should prioritize making the flow suite itself more representative before deeper runtime work:

1. Flow 08
2. Flow 13
3. Flow 04
4. Flow 09

## Maintenance rule

When any of the phases above is executed:

- run the relevant flow test first
- document the observed failures in the same change
- implement only the next closure slice for that flow
- re-run the same flow test
- update:
  - `test_flow_contract_suite.py`
  - `flow_coverage_checklist.md`
  - the relevant design notes
