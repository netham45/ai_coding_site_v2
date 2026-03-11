# Task: Testing Doctrine Parallel Execution Requirement

## Goal

Author the doctrine and command-surface updates needed to make parallel-safe test execution an explicit repository rule: all tests should be expected to run in parallel, and any test that fails only because of parallel execution must be treated as a defect rather than an acceptable limitation.

## Rationale

- Rationale: The repository already has partial parallel-test hardening and a dedicated meta-verifier bring-up plan, but the higher-level doctrine still does not state the stronger rule that parallel-unsafety is itself a correctness problem.
- Reason for existence: This task exists to align the testing doctrine, command catalog, execution policy, and adjacent implementation notes with the repository expectation that parallel execution is the default proving posture, while still describing the current gap honestly.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/28_F23_testing_framework_integration.md`
- `plan/checklists/04_test_coverage_and_release_readiness.md`
- `plan/update_tests/01_batch_execution_groups.md`
- `plan/tasks/2026-03-11_parallel_all_tests_meta_verifier_plan.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `notes/catalogs/checklists/document_schema_rulebook.md`
- `notes/catalogs/checklists/document_schema_test_policy.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`
- `notes/planning/implementation/project_development_flow_doctrine.md`
- `notes/planning/implementation/testing_framework_integration_decisions.md`
- `notes/planning/implementation/pytest_fixture_architecture_decisions.md`

## Scope

- Database: document that database-backed tests must use worker-safe isolation and that shared database state blocking parallel execution is a defect to be fixed, not a normal operating mode.
- CLI: update doctrine and command surfaces so CLI-facing verification narratives assume parallel-safe execution where the CLI test surface is part of the suite.
- Daemon: state that daemon/runtime tests must tolerate concurrent workers and isolated runtime resources; daemon-related serialization must be treated as a bug or an explicitly tracked blocker.
- YAML: no YAML schema behavior change is intended, but YAML-driven test assets remain part of the parallel-safe test expectation and must not be excluded silently.
- Prompts: no prompt contract change is intended, but prompt-related tests must remain eligible in the same parallel doctrine and should not depend on shared mutable prompt artifacts.
- Tests: update the repository testing doctrine so parallel execution is the normative expectation across bounded, integration, performance, and real-E2E layers; make it explicit that a test which cannot run in parallel is failing an important contract.
- Performance: define the intended parallel posture without overclaiming current speed or stability; distinguish "parallel-safe" from "parallel-optimized" and preserve honest command-tier language.
- Notes: update the doctrine, execution policy, command catalog, and any adjacent checklist/note surfaces needed so the new rule is stated consistently and current noncompliance remains documented as partial or in-progress.

## Current State

The repository currently has four relevant doctrine and proving properties:

1. `AGENTS.md` strongly requires comprehensive testing, but it does not yet explicitly say that every test should be parallel-safe or that parallel-only failures are defects.
2. `notes/catalogs/checklists/verification_command_catalog.md` already includes a parallel bounded-smoke command and a gated parallel meta-verifier bring-up command.
3. `notes/catalogs/checklists/e2e_execution_policy.md` still allows language such as "selective or staged parallelism" for some real-resource-heavy narratives, which is weaker than the doctrine the user requested.
4. `plan/tasks/2026-03-11_parallel_all_tests_meta_verifier_plan.md` documents concrete technical blockers that currently prevent the full suite from being treated as parallel-safe today.

## Design Objectives

The doctrine update should satisfy all of the following:

1. State unambiguously that all tests are expected to be runnable in parallel.
2. State unambiguously that a test failing only under parallel execution is an issue to be fixed.
3. Avoid silently converting the current repository state into a false claim that the suite is already fully parallel-safe.
4. Keep environment-capability gating distinct from serialization defects:
   - unavailable tmux, git, provider credentials, or similar capabilities may justify gating
   - shared mutable resources, fixture contention, or cross-test interference may not be normalized as acceptable serialization
5. Keep the command catalog and execution policy aligned with the new doctrine.
6. Point clearly at the implementation/proving work that must close the current gap, especially the existing parallel meta-verifier task.

## Proposed Doctrine Changes

### A. Add a repository-level testing rule in `AGENTS.md`

Add language in the testing doctrine sections that:

- all tests should be runnable in parallel
- test isolation is part of correctness, not optional hardening
- failures caused by concurrent execution indicate a defect in fixtures, runtime isolation, or test design
- serial-only execution is not an acceptable steady-state proving posture

### B. Tighten the development-flow doctrine

Update `notes/planning/implementation/project_development_flow_doctrine.md` so:

- canonical verification commands prefer or include parallel-safe proving surfaces
- testing-stage descriptions treat parallel execution as the normal expectation
- remediation guidance distinguishes real environment gating from test-isolation defects

### C. Tighten command and execution-policy wording

Update:

- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`

So they:

- describe parallel commands as normative proof targets rather than optional convenience checks
- describe any remaining serial execution as temporary gap posture only
- avoid language that implies cross-test interference is an acceptable operational constraint

### D. Align implementation-facing testing notes

Update:

- `notes/planning/implementation/testing_framework_integration_decisions.md`
- `notes/planning/implementation/pytest_fixture_architecture_decisions.md`

So they:

- explicitly treat worker safety as a repository contract
- connect fixture/runtime isolation work to the broader doctrine
- record any newly clarified invariant about per-test resource ownership

### E. Preserve honest status language

The doctrine update must also state that:

- the rule is repository policy immediately once adopted
- the current implementation may still be `partial` or `in_progress` against that rule
- existing blockers remain tracked until the parallel meta-verifier and supporting isolation work actually pass

## Recommended Phases

### Phase 1: Inventory the current testing-doctrine surfaces

Read and compare:

- `AGENTS.md`
- `notes/planning/implementation/project_development_flow_doctrine.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`
- `notes/planning/implementation/testing_framework_integration_decisions.md`
- `notes/planning/implementation/pytest_fixture_architecture_decisions.md`

Exit criteria:

- the exact doctrine surfaces that need wording changes are listed before editing begins

### Phase 2: Draft the doctrine language

Primary changes:

- add the repository-wide parallel-test rule
- define parallel-only failures as defects
- distinguish capability gating from serialization defects

Exit criteria:

- every affected doctrine surface uses the same claim language

### Phase 3: Align proving and status surfaces

Primary changes:

- update canonical command language
- update execution-tier wording
- ensure adjacent notes point to the existing implementation gap honestly

Exit criteria:

- no authoritative testing note implies that serial execution remains an acceptable steady-state contract

### Phase 4: Run document-family verification

Primary proof:

- relevant document-schema tests pass after the doctrine edits

Exit criteria:

- the updated doctrine and command surfaces pass the repository’s authoritative document checks

## Verification

Planning-target verification commands for the follow-on doctrine-edit task:

```bash
python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_verification_command_docs.py tests/unit/test_e2e_execution_policy_docs.py -q
```

If `AGENTS.md` receives wording that is also enforced elsewhere later, expand the command set in the same change.

## Exit Criteria

- A follow-on documentation change updates the authoritative testing doctrine to say all tests should run in parallel.
- That change states plainly that a test failing under parallel execution is an issue.
- The doctrine update does not overclaim current repository compliance.
- The command catalog and execution policy remain consistent with the updated doctrine.
- The relevant document-family tests pass for the changed surfaces.
