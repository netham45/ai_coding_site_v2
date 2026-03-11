# Task: Parallel All-Tests Meta-Verifier

## Goal

Design and implement a repository-authoritative verification surface that discovers the pytest suite under `tests/`, runs every eligible test in parallel, and itself serves as proof that the suite's fixtures and runtime resources are parallel-safe.

## Rationale

- Rationale: The repository currently has family-level pytest commands, but no canonical proof that the entire eligible suite can execute concurrently without hidden fixture contention, shared-resource collisions, or undocumented exclusions.
- Reason for existence: This task exists to make parallel safety an explicit, tested contract rather than an informal assumption, while also providing one high-signal command that answers "does everything that should run here pass together?"

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/28_F23_testing_framework_integration.md`
- `plan/checklists/04_test_coverage_and_release_readiness.md`
- `plan/checklists/16_e2e_real_runtime_gap_closure.md`
- `plan/e2e_tests/01_e2e_harness_and_command_foundation.md`
- `plan/e2e_tests/02_e2e_core_orchestration_and_cli_surface.md`
- `plan/e2e_tests/03_e2e_session_recovery_and_child_runtime.md`
- `plan/update_tests/01_batch_execution_groups.md`
- `plan/reconcilliation/03_per_e2e_test_database_isolation.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/catalogs/checklists/document_schema_rulebook.md`
- `notes/catalogs/checklists/document_schema_test_policy.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`
- `notes/planning/implementation/testing_framework_integration_decisions.md`
- `notes/planning/implementation/pytest_fixture_architecture_decisions.md`

## Scope

- Database: remove shared-database and shared-schema contention from unit, integration, and performance fixtures so parallel workers cannot terminate each other's connections or drop each other's tables.
- CLI: ensure CLI and CLI-to-daemon tests can run concurrently against isolated daemon/database contexts without shared auth-token or process collisions.
- Daemon: ensure in-process and subprocess daemon fixtures are worker-safe, port-safe, and runtime-dir-safe under parallel scheduling.
- YAML: no schema-behavior change is intended, but the meta-verifier must discover and execute YAML-related tests through the real pytest collection surface.
- Prompts: prompt assets are not the primary blocker, but prompt/runtime tests must remain eligible in the child pytest run and must not rely on shared mutable files.
- Tests: add one authoritative meta-test that discovers tests under `tests/`, computes the eligible parallel subset for the current environment, and fails if the child parallel run fails or if exclusions drift beyond the documented rules.
- Performance: choose and document an explicit `pytest-xdist` distribution strategy and worker posture that is realistic for local verification and CI use.
- Notes: update command catalog, execution policy, and any checklist/doc surfaces needed to describe the new canonical all-tests verifier and remaining gated exclusions honestly.

## Current State

The current suite has four important properties:

1. `tests/e2e/` already has per-test database isolation through dedicated database create/migrate/drop helpers.
2. Unit, integration, and performance tests still rely heavily on `migrated_public_schema`, which rebuilds a shared `public` schema and is not worker-safe.
3. tmux-backed session tests use the default tmux server rather than a per-harness socket or server namespace, so parallel real-runtime tests can still cross-talk even after DB isolation.
4. The repository has canonical family-level commands, but no single command or test that proves "all currently eligible tests pass together in parallel."

## Investigation Findings

### 1. Shared `public` schema is the primary bounded-suite blocker

Evidence:

- `tests/fixtures/db.py` currently exposes `clean_public_schema` and `migrated_public_schema`.
- `src/aicoding/db/bootstrap.py` resets the shared `public` schema by terminating sibling connections and dropping owned objects.

Consequence:

- parallel workers can:
  - kill each other's Postgres connections
  - race on Alembic version-table creation
  - observe partially reset schemas
  - fail with `duplicate alembic_version`, `UndefinedTable`, or `AdminShutdown`

### 2. E2E is only isolated at the database layer

Evidence:

- `tests/fixtures/e2e.py` creates one database, one runtime dir, one workspace, and one token file per harness.
- `tests/helpers/e2e.py` allocates a free port and starts one daemon process per harness.

Remaining blockers:

- tmux sessions still run on the default server
- free-port allocation is still a bind-release-rebind race
- provider-backed tests remain gated by credential availability and budget posture

### 3. A meta-test cannot simply run `pytest tests -n auto`

If implemented naively, the meta-test would:

- recursively invoke itself in the child pytest run
- potentially rerun documentation-only or gated suites without environment-aware filtering
- hide undocumented exclusions behind ad hoc `--ignore` flags

Therefore the meta-test needs a formal child-run contract.

## Design Objectives

The final surface should satisfy all of the following:

1. One canonical "all eligible tests in parallel" command exists and is documented.
2. One pytest test proves that command from inside the repository itself.
3. The test must dynamically discover tests under `tests/`, not rely on a hand-maintained file list.
4. The test must exclude only:
   - itself in the child run
   - tests gated by explicitly unavailable environment capabilities
5. Any exclusion beyond those rules must be explicit, documented, and test-visible.
6. The bounded suites and real-E2E suites must be parallel-safe at the resource layer before the meta-test is treated as authoritative.
7. The final result must still respect the repo's layered claim model: the meta-test is a proving surface, not a license to overclaim unsupported release readiness.

## Proposed Design

### A. Introduce worker-safe bounded-suite database isolation

Recommended posture:

- create one migrated database per pytest worker
- create one schema per test inside that worker database
- bind each test's engine/session to that schema using `search_path`

Why this shape:

- avoids repeated full migrations per test
- removes shared `public` contention
- keeps worker startup cost tolerable
- makes parallel bounded-suite execution realistic rather than merely correct in theory

Fallback posture if schema-scoped Alembic compatibility proves too awkward:

- create one migrated template database per worker
- clone a per-test database from that template

Non-goal:

- do not keep using `reset_public_schema()` for worker-parallel tests

### B. Introduce tmux server/socket isolation for real-runtime tests

Recommended posture:

- add a test-configurable tmux socket or server namespace
- thread that setting through:
  - daemon session harness
  - real E2E harness env
  - direct tmux subprocess calls in tests/helpers

Expected invariant:

- one harness must never see or kill another harness's tmux sessions

### C. Replace free-port probing with bound-port ownership

Recommended posture:

- either let the daemon bind port `0` and publish the actual port
- or hold the socket reservation until process startup completes

Reason:

- current `allocate_local_port()` is safe enough for serial runs but is not a rigorous parallel contract

### D. Add a child-pytest orchestration helper for the meta-test

Recommended implementation surface:

- one helper module under `tests/helpers/` or `tests/support/`
- one authoritative pytest test file, likely under `tests/integration/`

Responsibilities:

- run `pytest --collect-only` against `tests/`
- parse collected node IDs
- detect environment capabilities:
  - postgres availability
  - git binary availability
  - tmux availability
  - provider credentials availability
- compute marker exclusions for unavailable capabilities
- exclude the meta-test file itself from the child run
- invoke child pytest with `-n <workers>` and explicit distribution mode
- report:
  - total collected tests
  - eligible tests
  - excluded tests grouped by reason
  - child exit code

### E. Give the meta-test an explicit recursion boundary

Recommended posture:

- set an env var such as `AICODING_META_TEST_CHILD=1` for the child pytest process
- in the meta-test file:
  - if that env var is set, `pytest.skip(...)` or the file is excluded via `--ignore`

Preferred safety model:

- do both:
  - `--ignore <this_file>` for the child run
  - env-var guard inside the file as a second line of defense

### F. Make eligibility rules test-visible and strict

The meta-test should not silently omit tests.

Recommended rules:

- eligible tests are all collected tests under `tests/`
- exclusions are limited to:
  - the meta-test file itself
  - `requires_tmux` when tmux is unavailable
  - `requires_ai_provider` when provider credentials are unavailable
  - `requires_git` when git is unavailable
- if any future `serial_only`, `requires_docker`, or similar marker is introduced, the meta-test must fail until:
  - the marker is documented
  - the eligibility rules are updated
  - the command catalog / execution policy are updated if authoritative

## Recommended Phases

### Phase 1: Define the canonical parallel-verification contract

Outputs:

- task plan and durable log
- canonical command proposal
- explicit eligibility and exclusion rules

Exit criteria:

- the repo has one agreed contract for what "all tests it can find" means

### Phase 2: Harden bounded fixtures for worker safety

Primary changes:

- replace shared-`public` fixture strategy
- add worker-aware DB lifecycle helpers
- ensure app/CLI/daemon fixtures consume worker-safe URLs and schema context

Primary proof:

- unit/integration/performance suites pass under `pytest -n 2`

Exit criteria:

- no bounded suite still depends on shared-schema resets

### Phase 3: Harden E2E non-database resources

Primary changes:

- tmux socket/server isolation
- daemon port allocation hardening
- child resource teardown hardening

Primary proof:

- tmux-backed E2E spot checks pass under `pytest tests/e2e -n 2` for an eligible subset

Exit criteria:

- real-runtime tests are isolated at database, tmux, runtime-dir, token-file, workspace, and port layers

### Phase 4: Implement the meta-test

Primary changes:

- add discovery/orchestration helper
- add meta-test file
- add recursion guard
- add child-run result formatting for readable failure output

Recommended child command shape:

```bash
python3 -m pytest tests -n 2 --dist=loadfile --ignore <meta_test_file> <marker_expression>
```

Distribution mode to validate during implementation:

- start with `--dist=loadfile` to reduce fixture churn and file-local narrative collisions
- compare against `worksteal` or `loadscope` only after the initial parallel contract is stable

Exit criteria:

- the meta-test fails when the eligible child run fails
- the meta-test reports exclusions explicitly

### Phase 5: Document and adopt the new command layer

Update:

- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`
- any checklist or README surfaces that describe canonical test verification

Add canonical commands for:

- bounded parallel smoke
- full eligible-suite parallel meta-verifier
- gated full-suite run when tmux/provider/git resources are available

Exit criteria:

- the repo has one authoritative parallel-suite command and its claim boundary is documented

## Proposed Canonical Commands

These are planning targets, not yet adopted commands.

### Parallel bounded smoke

```bash
python3 -m pytest tests/unit tests/integration tests/performance -n auto --dist=loadfile -q
```

### Parallel eligible-suite meta-verifier

```bash
python3 -m pytest tests/integration/test_parallel_all_tests_meta.py -q
```

### Direct child-run equivalent for manual debugging

```bash
python3 -m pytest tests -n auto --dist=loadfile -q
```

The direct child-run command is only canonical after:

- worker-safe bounded fixtures exist
- tmux/daemon/E2E isolation is hardened
- marker gating rules are documented

## Parallel Run Plan

This section defines how the repository should progress from today's serial family runs to a real parallel all-tests verifier.

The point is not only to end with a meta-test, but to have a safe command ladder for getting there.

### Stage 0: Current baseline capture

Purpose:

- keep one known-good serial proving surface while parallel hardening is underway
- avoid confusing genuine regressions with fixture-contention regressions

Commands:

```bash
python3 -m pytest tests/unit -q
python3 -m pytest tests/integration -q
python3 -m pytest tests/performance -q
python3 -m pytest tests/e2e -q
```

Rules:

- use this stage while any shared-schema or shared-tmux fixture remains
- failures here are implementation regressions or existing environment issues, not parallelization fallout

### Stage 1: Parallel bounded-suite smoke

Purpose:

- prove that unit, integration, and performance tests can coexist across workers before involving real-runtime E2E resources

Target command:

```bash
python3 -m pytest tests/unit tests/integration tests/performance -n auto --dist=loadfile -q
```

Why this first:

- bounded suites are the largest share of the repository and currently suffer the strongest database contention
- this stage validates worker-safe DB fixtures without mixing in tmux/provider/git gating

Adoption gate:

- shared `public` resets are gone from the bounded-suite path
- no worker kills another worker's database connections
- the command can pass repeatedly on the same machine

### Stage 2: Parallel E2E infrastructure smoke

Purpose:

- prove that real daemon subprocesses, per-test databases, workspaces, auth tokens, ports, and tmux sockets can coexist

Target command:

```bash
python3 -m pytest tests/e2e -n auto --dist=loadfile -q -m "not requires_ai_provider"
```

Notes:

- begin with the non-provider subset because provider-backed narratives add cost and external variability
- keep `requires_git` and `requires_tmux` eligible when those tools are available

Adoption gate:

- each E2E harness has isolated database, workspace, token file, port, and tmux server/socket state
- no E2E test needs a global tmux namespace or shared daemon port assumptions

### Stage 3: Parallel gated E2E with provider-backed flows

Purpose:

- extend the E2E proof surface to the live-provider narratives when credentials and budget are intentionally supplied

Target command:

```bash
python3 -m pytest tests/e2e -n auto --dist=loadfile -q
```

Environment expectation:

- tmux available
- provider credentials configured
- PostgreSQL available
- git available for git-marked tests

Adoption gate:

- provider-backed flows no longer need implicit serialization beyond documented external-budget or policy reasons
- any still-serial resource constraint is documented explicitly and enforced through markers or command tiers

### Stage 4: Parallel all-eligible direct command

Purpose:

- establish the direct command that the meta-test will execute internally

Target command:

```bash
python3 -m pytest tests -n auto --dist=loadfile -q
```

Interpretation:

- "all" here means all tests collected under `tests/` that are eligible in the current environment
- eligibility is controlled by explicit marker/capability rules, not by hand-maintained file lists

Adoption gate:

- the repo has a documented eligibility algorithm
- the direct command succeeds when the environment satisfies its declared capabilities

### Stage 5: Meta-test adoption

Purpose:

- convert the direct parallel command into an authoritative repository test

Target command:

```bash
python3 -m pytest tests/integration/test_parallel_all_tests_meta.py -q
```

What the meta-test must do:

1. collect tests under `tests/`
2. compute eligible tests for the current environment
3. exclude only documented ineligible tests plus the meta-test file itself
4. spawn the child parallel pytest run
5. fail if the child run fails
6. fail if exclusions drift from the documented policy

Adoption gate:

- the meta-test is stable enough to be used as an authoritative verification surface
- command docs point to it explicitly

## Distribution Strategy

Initial recommendation:

- use `-n auto --dist=loadfile`

Why:

- `-n auto` makes the authoritative command scale with the machine that is actually running it instead of hard-capping modern multi-core systems
- `loadfile` minimizes cross-worker churn for tests that share file-local setup or heavy fixtures
- it is a better first proving surface than more aggressive balancing modes

Follow-up evaluation after stabilization:

- compare `loadfile` against `loadscope`
- measure whether a fixed worker count is ever still useful for debugging, but keep `-n auto` as the default proving surface
- promote only after measuring reliability, runtime, and fixture churn

## Eligibility Rules For Parallel Runs

The parallel command and the meta-test should use the same eligibility rules.

### Always eligible

- tests with no gating markers beyond ordinary pytest collection

### Eligible only when capability exists

- `requires_git`: only when git is installed and usable
- `requires_tmux`: only when tmux is installed and usable
- `requires_ai_provider`: only when live provider credentials and budget posture are intentionally supplied

### Never eligible in the child run

- the meta-test file itself

### Not allowed

- ad hoc `--ignore` patterns for unrelated failing areas
- silent omission of entire directories
- hand-maintained lists of "known parallel-safe files" as the final contract

## Implementation Order For Parallel Execution

1. Replace bounded shared-schema fixtures with worker-safe isolation.
2. Prove Stage 1 repeatedly until it is stable.
3. Add tmux socket isolation and daemon port hardening.
4. Prove Stage 2 repeatedly until it is stable.
5. Expand to provider-backed Stage 3 when credentials are intentionally present.
6. Add the child-run helper and meta-test.
7. Adopt Stage 4 and Stage 5 commands in the verification catalog and execution policy.

## Success Criteria For The Parallel Run Plan

- there is a documented command ladder from serial baseline to full eligible parallel execution
- each stage has a clear adoption gate
- the final meta-test is only introduced after the resource-isolation prerequisites are in place
- the direct parallel command and the meta-test share one eligibility model

## Risks

- schema-scoped isolation may expose code paths that assume `public` rather than connection-local schema search paths
- tmux isolation will require touching both runtime code and direct test subprocess calls
- the meta-test can become flaky if its exclusion rules are too permissive or too implicit
- a child pytest run from inside pytest can produce poor diagnostics unless stdout/stderr/report handling is designed intentionally
- provider-backed tests may remain unsuitable for always-on local default runs even after parallel hardening, so the command tiers must remain explicit

## Open Decisions

1. Should the authoritative parallel command use `-n auto` or a fixed low worker count such as `-n 2` for repeatability?
2. Should the meta-test live in `tests/integration/` or `tests/performance/`?
3. Should bounded suites use worker-db plus per-test-schema isolation, or worker-template-db plus per-test-db cloning?
4. Should the meta-test require real-E2E eligibility in the default environment, or only include gated E2E tests when capabilities are intentionally present?

## Verification

- Planning/schema docs: `python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_verification_command_docs.py -q`
- Current suite inventory reference: `python3 -m pytest --collect-only -q`
- Baseline family runs used during planning: `python3 -m pytest tests/unit -q`
- Baseline family runs used during planning: `python3 -m pytest tests/integration -q`
- Baseline family runs used during planning: `python3 -m pytest tests/performance -q`
- Baseline family runs used during planning: `python3 -m pytest tests/e2e -q`

## Exit Criteria

- The repository has an authoritative implementation plan for a parallel all-tests meta-verifier.
- The plan explicitly covers database, tmux, daemon, CLI, and child-pytest orchestration isolation requirements.
- The plan defines what counts as an eligible collected test and how exclusions are controlled.
- The plan defines the canonical command surfaces that will need to be adopted when implemented.
- The governing plan and development log pass the relevant document-schema tests.
