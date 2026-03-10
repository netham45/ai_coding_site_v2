# Full Real End-To-End Flow Hardening Plan

## Goal

Replace the current bounded flow-contract testing model with fully real end-to-end flow tests.

For every flow, the test must:

- start from a clean real environment
- boot the real application stack
- use real PostgreSQL state
- use the real daemon process and real API boundaries
- use real CLI commands where the flow is CLI-facing
- use real session management
- use real git repositories and real git operations where the flow involves git
- use real AI-provider execution where the flow depends on AI work
- wait for actual state transitions and actual responses
- verify durable outputs, audit records, and recovery surfaces after the real work finishes

This plan exists because the current flow suites are passing bounded contract tests, not full production-grade end-to-end tests.

## Non-Goals

This plan is not:

- a request to preserve existing shortcuts
- a request to keep fake backends in “end-to-end” coverage
- a request to treat simulation-derived YAML as sufficient execution
- a request to keep monkeypatched daemon bridges as the primary proof

Those shortcuts can still exist in unit or bounded integration coverage, but they must no longer be treated as full flow proof.

## Required Standard

The following must be true before a flow can be marked “fully end to end”.

### Environment standard

- real PostgreSQL
- real daemon startup
- real auth token file behavior
- real CLI invocation path where applicable
- real filesystem workspace
- real git repository operations where applicable
- real tmux-backed or real provider-backed session orchestration where applicable
- real AI-provider calls where the flow depends on AI output

### Prohibited shortcuts in full flow tests

- no fake session backend
- no in-process daemon bridge as the only proof
- no monkeypatched flow internals to force success
- no bypassing waits by directly mutating DB state
- no skipping AI steps by injecting synthetic summaries/prompts/results unless the flow is explicitly about operator repair of already-existing records
- no replacing git execution with durable staging reads
- no treating compile failure as “real” if the test never exercises the actual load/compile path

### Acceptance standard

A flow is only complete when its full test proves:

- runtime behavior
- durable state mutation
- inspectability
- recovery-relevant state
- user-visible CLI/API behavior
- no hidden bypasses

## Why This Is A Separate Hardening Track

The current repository now has:

- markdown flow specs
- executable YAML flow assets
- bounded flow contract tests

That is useful, but it is not equivalent to fully real end-to-end runtime proof.

The main incongruities are:

1. some flows currently use bounded assertions rather than full production narratives
2. some runtime flows still use fake session infrastructure in tests
3. some AI-dependent flows do not yet wait on live provider output
4. some git flows are proven through targeted execution, but not yet as one clean boot-to-finish system suite
5. the current flow suites still mix “contract correctness” with “runtime realism”

This plan separates those concerns and defines the migration path.

## Expected Failure Posture During This Plan

Flow-test failure is acceptable and expected during this hardening track.

That is not a loophole to ignore failures. It is an explicit part of the migration process.

Until the harness and runtime are brought up to the real E2E standard, some candidate full-flow tests will fail because they expose:

- missing runtime behavior
- bounded test shortcuts that are no longer acceptable
- incomplete session, git, or provider integration
- weak recovery behavior
- note/spec drift

During this plan, a failing flow test should be interpreted as:

- evidence that the current implementation is not yet fully real end to end for that flow
- useful gap discovery
- input to the next implementation phase

It should not be interpreted as:

- a reason to weaken the test
- a reason to relabel bounded coverage as full E2E proof
- a reason to silently skip the flow

The correct response to a failed full-flow test in this plan is:

1. record the exact failure and the missing capability it exposed
2. update notes if the failure reveals design ambiguity or drift
3. implement the missing runtime or harness behavior
4. rerun the same flow test

So for this specific plan:

- red tests are expected at intermediate stages
- undocumented red tests are not acceptable
- “expected to fail for now” must always be attached to a concrete missing capability and a follow-up phase

## Required Notes

Read and keep aligned with:

- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/specs/database/database_schema_spec_v2.md`
- `notes/specs/git/git_rectification_spec_v2.md`
- `notes/specs/prompts/prompt_library_plan.md`
- `notes/specs/yaml/yaml_schemas_spec_v2.md`
- `notes/specs/runtime/tmux_session_lifecycle_spec_v1.md#recovery-classification-and-actions`
- `notes/contracts/parent_child/child_session_mergeback_contract.md`
- `notes/contracts/runtime/cutover_policy_note.md`
- `notes/planning/implementation/per_flow_gap_remediation_plan.md`
- `notes/planning/implementation/missing_simulation_flow_yaml_and_test_plan.md`

## Phase 1: Define The Real E2E Test Contract

### Goal

Create one canonical repository definition of what counts as a “real end-to-end flow test”.

### Work

- define a test-category boundary between:
  - unit
  - bounded integration
  - real end-to-end flow
- document exactly which shortcuts are banned in full flow tests
- define required environment inputs:
  - provider credentials
  - workspace root
  - git availability
  - tmux availability
  - daemon port/token isolation
- define timeout, retry, and flake-handling rules for real provider-backed tests

### Deliverables

- new or updated note defining the real E2E standard
- explicit marker convention for pytest, for example:
  - `@pytest.mark.e2e_real`
  - `@pytest.mark.requires_ai_provider`
  - `@pytest.mark.requires_tmux`
  - `@pytest.mark.requires_git`

### Exit criteria

- the repo has one unambiguous definition of “full end to end”
- any future flow test can be judged against that definition without hand-waving

### Current progress

- implemented pytest markers:
  - `e2e_real`
  - `requires_git`
  - `requires_tmux`
  - `requires_ai_provider`
- implemented the first real E2E checkpoint for Flow 01 using:
  - real daemon subprocess startup
  - real auth token file behavior
  - real CLI subprocess invocation
  - real PostgreSQL-backed durable verification
- Flow 01 real E2E rerun now passes:
  - `python3 -m pytest tests/e2e/test_flow_01_create_top_level_node_real.py -q`
- see `notes/planning/implementation/real_e2e_flow_contract_phase1_decisions.md`

Canonical command rule:

- the current real-E2E command family is cataloged in `notes/catalogs/checklists/verification_command_catalog.md`
- the current local/CI/gated/manual execution posture is cataloged in `notes/catalogs/checklists/e2e_execution_policy.md`
- bounded or integration flow commands must not be cited here as if they were full real-E2E proof

## Phase 2: Build The Real E2E Harness

### Goal

Create a single reusable harness for full-system flow tests.

### Work

- start the real daemon process instead of relying on in-process bridge clients
- create isolated temp workspaces per test
- allocate isolated Postgres schema/database state per test run
- allocate isolated daemon auth token path per test
- allocate isolated daemon port per test
- support waiting for daemon health and readiness
- support teardown of daemon, tmux sessions, and temp repos

### Required outputs

- reusable fixtures for:
  - real daemon process
  - real CLI invocation against that daemon
  - isolated workspace root
  - isolated git repo root
  - isolated auth token path
  - isolated provider/session metadata

### Exit criteria

- a test can launch the real stack with no monkeypatched bridge
- the harness leaves no residue across test runs

### Current progress

- initial reusable real-daemon harness now exists in `tests/fixtures/e2e.py`
- initial real CLI subprocess helper now exists in `tests/helpers/e2e.py`
- real E2E checkpoints now exist for:
  - Flow 01 top-level creation
  - Flow 02 compile/recompile inspection
  - Flow 03 child materialization and scheduling
  - Flow 04 manual tree edit and preserve-manual reconciliation
  - Flow 05 run admission and durable subtask progress loop
  - Flow 06 operator/state/blocker inspection
  - Flow 07 tmux-backed session bind and recovery
  - Flow 08 child failure and parent escalation handling
  - Flow 09 turnkey quality-chain execution with project-local gate policy loading
  - Flow 10 regenerate/rectify execution with rebuild-history and coordination inspection
  - Flow 11 live git bootstrap, merge, and finalize execution
  - Flow 12 provenance refresh, rationale inspection, entity-history inspection, and docs build/show execution
  - Flow 13 pause approval, blocked resume, intervention apply, and post-approval resume execution
  - Flow 14 project bootstrap and project-local YAML onboarding through the real daemon/CLI path
  - Flows 15 through 18 built-in blueprint compile ladders through the real daemon/CLI path
  - the full serial Flow 01 through Flow 13 real-E2E batch currently passes
- current limitation:
  - the runtime now has a first-class workspace-root contract for project-local
    resources and default provenance refresh, but live git and session cwd ownership
    are still not unified around that same contract
  - DB-backed real E2E flows now have per-test database isolation, so the old
    shared-database cross-test interference issue has been removed at the DB layer
  - strict real-E2E tests now exist for simulation-derived flows `19` through `22`
  - flows `21` and `22` are expected to remain red until tmux sessions launch Codex
    rather than an interactive shell and the daemon can observe real session-produced
    work completion without operator-injected progress commands
  - remaining serialization decisions should be driven by non-database resources
    such as tmux, provider credentials, or especially heavy workspace narratives

## Phase 3: Build The Real AI Execution Harness

### Goal

Replace synthetic AI-step completion with actual provider-backed execution for AI-dependent flows.

### Work

- define the supported real provider mode for tests
- load credentials from real env/config
- implement provider-ready polling/wait semantics
- capture provider outputs, summaries, and failures durably
- define budget and timeout controls so the suite remains operable
- define how tests detect:
  - provider timeout
  - malformed response
  - interrupted session
  - recovery-required session

### Open reality to document

This phase must explicitly document:

- that full real AI tests require external credentials and spend
- how to skip or gate them when credentials are absent
- which subset must run in CI versus manual gated pipelines

### Exit criteria

- no AI-dependent flow relies on injected summaries or fake completions in the full E2E suite

## Phase 4: Build The Real Session And Tmux Harness

### Goal

Run session flows against the real session layer rather than the fake backend.

### Work

- require tmux for full session flows
- create isolated tmux session namespaces per test
- verify actual pane creation, attach metadata, idle polling, and recovery state
- prove child-session push/pop with real session objects
- prove provider/session recovery against actual session records and actual pane state

### Flows affected

- pause/resume/recover
- child-session round-trip
- provider-specific recovery
- human intervention around active sessions

### Exit criteria

- all session-oriented full flow tests run on real session infrastructure

## Phase 5: Build The Real Git Workspace Harness

### Goal

Run git flows in actual isolated repositories with actual branch, merge, conflict, abort, and finalize behavior.

### Work

- create isolated repos per flow test
- seed deterministic commit ancestry
- wire node versions to real repo roots
- prove:
  - clean merges
  - conflicted merges
  - abort-merge behavior
  - finalize commits
  - rebuild/cutover coordination against actual repo state
- verify the DB and CLI reflect the true git state, not just staged metadata

### Exit criteria

- git flows no longer rely on durable staging alone in full E2E coverage

## Phase 6: Convert The Existing Markdown Flow Suite To Real E2E

### Goal

Migrate `tests/integration/test_flow_contract_suite.py` from bounded flow contracts to real end-to-end execution where applicable.

### Work by flow family

#### Flow 01 to Flow 03

- create top-level node
- compile workflow
- materialize children

These should move first because they are the base of later flows.

#### Flow 04 to Flow 08

- manual tree reconciliation
- run execution
- inspection/blockers
- pause/resume/recover
- failure/escalation

These require real daemon, session, and durable runtime proof.

#### Flow 09 to Flow 13

- quality gates
- regeneration/rectification
- finalize/merge
- provenance/docs query
- human intervention

These require the real AI, git, and recovery harnesses.

### Exit criteria

- each markdown flow has either:
  - a real E2E test, or
  - an explicitly documented blocker with its own follow-up plan

## Phase 7: Convert The YAML Flow Suite To Real E2E

### Goal

Promote the YAML flow suite from bounded runtime contracts to fully real execution.

### Work by YAML flow

#### Flow 14

- real project bootstrap in a fresh workspace
- real local YAML authoring and validation
- real first compile in the project

#### Flow 15 to Flow 19

- real blueprint/compile/hook-stage proof against the live compiler

#### Flow 20

- real compile failure and reattempt against the actual failing source class under test

#### Flow 21

- real child-session round trip using real tmux/provider-backed sessions

#### Flow 22

- real sibling dependency wait path, ideally through actual materialized sibling structure where possible

### Exit criteria

- all YAML flow tests satisfy the same E2E standard as markdown flows

## Phase 8: Remove Bounded Shortcuts From Flow Coverage

### Goal

Prevent old bounded tests from being mistaken for full proof.

### Work

- relabel existing bounded flow tests as:
  - contract tests
  - bounded integration tests
- separate them from the real E2E suite in naming and markers
- remove or rewrite assertions that merely confirm shape while bypassing runtime work
- document any remaining bounded tests as lower-tier proof only

### Exit criteria

- nobody can point at a bounded test and claim “full end to end” by mistake

## Phase 9: Add Per-Flow Readiness Checklist

### Goal

Track which flows are truly real end-to-end and which are not.

### Work

Create a checklist with one row per flow and columns for:

- real daemon
- real CLI
- real Postgres
- real session layer
- real AI provider
- real git
- durable audit verification
- recovery verification
- no fake backend
- no monkeypatch bypass

### Exit criteria

- the repo has an honest status board for flow realism

## Phase 10: CI And Execution Strategy

### Goal

Make the full real E2E suite executable in practice.

### Work

- split test tiers:
  - default fast suite
  - bounded integration suite
  - real E2E local suite
  - real E2E gated CI suite
- define environment variable requirements
- define provider budget/time guardrails
- define how to run subsets safely

### Exit criteria

- there is a realistic path to running full real E2E coverage repeatedly

## Proposed Execution Order

1. Phase 1: Define The Real E2E Test Contract
2. Phase 2: Build The Real E2E Harness
3. Phase 4: Build The Real Session And Tmux Harness
4. Phase 5: Build The Real Git Workspace Harness
5. Phase 3: Build The Real AI Execution Harness
6. Phase 6: Convert The Existing Markdown Flow Suite To Real E2E
7. Phase 7: Convert The YAML Flow Suite To Real E2E
8. Phase 8: Remove Bounded Shortcuts From Flow Coverage
9. Phase 9: Add Per-Flow Readiness Checklist
10. Phase 10: CI And Execution Strategy

## Immediate Next Step

Start with Phase 1 and produce the canonical repository note that defines:

- what “real end to end” means here
- what is forbidden in those tests
- what infrastructure is mandatory
- how full flow tests differ from the current bounded contract suites
