# Per-E2E-Test Database Isolation

## Goal

Change the real end-to-end harness so each E2E test runs against its own PostgreSQL database instead of sharing one database and resetting the public schema.

The intended result is:

- every real E2E test creates a unique database using the same server credentials
- migrations run inside that database before the daemon starts
- the real daemon and CLI for that test use only that database
- the database is dropped during teardown
- real E2E tests become parallel-safe at the database layer

## Rationale

- Rationale: The current real E2E harness still points every test at one shared database URL and relies on schema resets. That makes the suite serialize unnecessarily and creates cross-test interference risk.
- Reason for existence: This phase exists to move the real E2E layer to true database isolation so concurrent execution does not depend on polite sequencing.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/01_F31_daemon_authority_and_durable_orchestration_record.md`
- `plan/features/04_F07_durable_node_lifecycle_state.md`
- `plan/features/37_F10_top_level_workflow_creation_commands.md`
- `plan/features/57_F31_database_runtime_state_schema_family.md`
- `plan/features/58_F31_database_session_attempt_history_schema_family.md`
- `plan/features/59_F30_database_provenance_docs_audit_schema_family.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`
- `notes/catalogs/audit/flow_coverage_checklist.md`
- `notes/planning/implementation/full_real_end_to_end_flow_hardening_plan.md`
- `notes/planning/implementation/real_e2e_flow_contract_phase1_decisions.md`
- `notes/specs/database/database_schema_spec_v2.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`

## Scope

- Database: create and drop one isolated database per real E2E test, run migrations per database, and ensure teardown handles open connections safely.
- CLI: ensure real CLI subprocesses inherit the per-test database URL rather than the global default URL.
- Daemon: ensure each real daemon subprocess binds only to the per-test database and does not leak connections after teardown.
- YAML: no workflow-schema behavior change is intended; YAML is affected only insofar as the same compile/runtime paths must work in isolated databases.
- Prompts: not directly affected.
- Notes: update E2E policy, verification commands, and flow coverage notes to reflect the new database-isolation posture.
- Tests: update the E2E fixture layer and add fixture-level tests that prove unique database creation and cleanup.
- Performance: the harness may get slightly slower per test due to create/migrate/drop overhead; this is acceptable if it unlocks concurrent execution and cleaner isolation.

## Current State

The current E2E harness:

- allocates a unique port, runtime dir, token file, and workspace per test
- still passes the same shared `AICODING_DATABASE_URL` into every real daemon harness
- therefore remains non-parallel-safe at the database layer

The current Postgres role has now been verified to support `CREATE DATABASE` and `DROP DATABASE`, so this change is feasible in the current environment.

## Invariants

1. Each real E2E test must have a database name unique to that test invocation.
2. No two real E2E tests may share the same database URL.
3. Migration to head must happen before the daemon for that test begins serving requests.
4. Teardown must remove the test database even if the daemon exited unexpectedly.
5. Per-test isolation must be implemented in the harness/fixture layer, not by ad hoc logic in individual E2E tests.
6. Existing unit and bounded integration fixtures must not be silently converted to per-database isolation unless explicitly planned.

## Likely Implementation Surface

Primary files:

- `tests/fixtures/e2e.py`
- `tests/helpers/e2e.py`
- `tests/fixtures/db.py`

Likely supporting files:

- `tests/e2e/test_flow_01_create_top_level_node_real.py`
- `tests/e2e/test_flow_02_compile_or_recompile_workflow_real.py`
- `tests/e2e/test_flow_03_materialize_and_schedule_children_real.py`
- `tests/e2e/test_flow_04_manual_tree_edit_and_reconcile_real.py`
- `tests/e2e/test_flow_05_admit_and_execute_node_run_real.py`
- `tests/e2e/test_flow_06_inspect_state_and_blockers_real.py`
- `tests/e2e/test_flow_07_pause_resume_and_recover_real.py`
- `tests/e2e/test_flow_08_handle_failure_and_escalate_real.py`
- `tests/e2e/test_flow_09_run_quality_gates_real.py`
- `tests/e2e/test_flow_10_regenerate_and_rectify_real.py`

Potential new fixture/harness tests:

- `tests/unit/test_e2e_database_isolation_fixture.py`
- or a similarly named fixture-focused unit/integration test file

## Design Approach

Use the configured Postgres credentials as a base URL and derive:

- an admin connection URL targeting the `postgres` database
- a unique per-test database name such as `aicoding_e2e_<uuid>`
- a per-test application URL targeting that new database

The harness should then:

1. create the database through the admin connection
2. run migrations to head against the new database
3. start the daemon with `AICODING_DATABASE_URL` set to the per-test database URL
4. run the test
5. terminate the daemon
6. terminate or clear remaining DB connections if needed
7. drop the database

## Failure Handling Requirements

- if database creation fails, the test should fail immediately with the exact SQLAlchemy/Postgres error
- if migration fails, the test should fail and the partially created database should still be dropped
- if database drop fails due to active connections, the harness should first terminate remaining backends for that test database and retry the drop
- if teardown still fails, the harness should raise with the database name so cleanup is inspectable

## Expected Test Layers

- unit or fixture-focused proof for database-name generation and URL derivation
- integration or fixture-level proof for create/migrate/drop lifecycle
- real E2E reruns proving the updated harness works for existing real flow tests

## Canonical Verification Commands

Document and fixture checks after implementing this plan:

```bash
python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_verification_command_docs.py tests/unit/test_notes_quickstart_docs.py -q
```

Fixture and harness validation after implementation:

```bash
python3 -m pytest tests/unit/test_e2e_database_isolation_fixture.py -q
```

Real E2E spot checks after implementation:

```bash
python3 -m pytest tests/e2e/test_flow_01_create_top_level_node_real.py tests/e2e/test_flow_02_compile_or_recompile_workflow_real.py -q
```

Parallel smoke check target after implementation:

```bash
python3 -m pytest tests/e2e -q -n 2
```

If the repo does not currently use `pytest-xdist`, add or adjust the canonical parallel smoke-check command in `notes/catalogs/checklists/verification_command_catalog.md` when this phase lands.

## Phases

### Phase 1: Add per-test database lifecycle helpers

- add helper functions for:
  - deriving admin and per-test URLs
  - creating unique test database names
  - creating databases
  - dropping databases
  - terminating active connections when required

Exit criteria:

- helper logic is reusable and not embedded directly in one fixture

### Phase 2: Wire the real E2E fixture to isolated databases

- update `real_daemon_harness_factory` so each harness instance gets:
  - a unique database
  - migrations applied before daemon startup
  - a test-local `AICODING_DATABASE_URL`

Exit criteria:

- one E2E test run no longer depends on the shared base database contents

### Phase 3: Add fixture-focused proof

- add tests that prove:
  - the fixture creates unique database URLs
  - migrations can run in the isolated database
  - teardown drops the database

Exit criteria:

- the isolation mechanism itself has direct proof rather than only incidental E2E coverage

### Phase 4: Rerun and reconcile the real E2E suite

- rerun at least the existing real flow checkpoints against the new harness
- fix any assumptions that still rely on shared DB state
- update notes/checklists honestly if some real E2E flows remain serial for non-DB reasons

Exit criteria:

- the current real E2E checkpoints pass with isolated databases

### Phase 5: Update documentation and execution policy

- update `verification_command_catalog.md`
- update `e2e_execution_policy.md`
- update any flow coverage note that still claims the E2E harness is not parallel-safe because of shared DB state

Exit criteria:

- the docs describe the real harness accurately

## Risks

- create/migrate/drop per test will increase startup cost
- teardown may need explicit connection termination if the daemon or pool leaves sessions open
- some E2E tests may still not be safe to run concurrently because of tmux, workspace, or external-provider constraints even after DB isolation is fixed
- if the fixture logic accidentally leaks the shared base database URL, tests will appear isolated while still colliding

## Completion Criteria

This phase is complete only when:

1. each real E2E test gets its own database
2. migrations run automatically inside that database
3. the current real E2E checkpoints pass against the isolated harness
4. the relevant notes and command docs are updated
5. any remaining concurrency blockers outside the database layer are documented explicitly

## Initial Status

- status: `planned`
- implementation expectation: `straightforward`
- known prerequisite status: `met` because the `aicoding` Postgres role now supports create/drop database operations
