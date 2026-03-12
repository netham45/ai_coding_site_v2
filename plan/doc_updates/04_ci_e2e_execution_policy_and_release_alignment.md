# Phase DU-04: CI, E2E Execution Policy, And Release Alignment

## Goal

Define how the new testing standards are operationally satisfied in local development, CI, gated/manual runs, and release-readiness review.

## Rationale

- Rationale: Requiring real E2E for feature completion is only workable if the repository also defines how and where those E2E suites are expected to run.
- Reason for existence: This phase exists to prevent the new standards from becoming ambiguous or impossible to execute in practice.

## Related Features

Read these implementation plans for context and interaction boundaries:

- `plan/e2e_tests/01_e2e_harness_and_command_foundation.md`
- `plan/e2e_tests/03_e2e_session_recovery_and_child_runtime.md`
- `plan/e2e_tests/05_e2e_git_rectification_and_cutover.md`
- `plan/update_tests/01_batch_execution_groups.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `README.md`
- `notes/planning/implementation/full_real_end_to_end_flow_hardening_plan.md`
- `notes/planning/implementation/real_e2e_flow_contract_phase1_decisions.md`
- `notes/catalogs/audit/flow_coverage_checklist.md`

## Scope

- Database: define expectations for real PostgreSQL use in local, CI, and gated E2E runs.
- CLI: define expectations for real CLI invocation in E2E execution policy.
- Daemon: define expectations for real daemon subprocess use and runtime isolation in E2E execution policy.
- YAML: define which YAML/compile suites must run in default CI versus gated E2E tracks.
- Prompts: define prompt/runtime/provider-related execution rules when prompt-dependent E2E requires external systems.
- Notes: update README and release-readiness notes to reflect the operational policy.
- Tests: define which suites are required in:
  - normal local iteration
  - standard CI
  - gated/manual E2E
  - release-readiness verification
- Performance: define where performance checks sit relative to bounded, integration, and E2E gates.

## Work

- define the default local proving ladder
- define the default CI proving ladder
- define gated/manual E2E expectations for:
  - git
  - tmux
  - provider-backed tests
  - environment-isolated tests
- define which completion claims can be made at each proving level
- define release-readiness criteria in operational terms
- update README and any release/readiness checklists that still assume the older test model

## Current DU-04 Outputs

- `notes/catalogs/checklists/e2e_execution_policy.md`
- README and command-catalog links to the execution policy
- hardening-plan alignment to the execution policy

## Canonical Verification Command

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_e2e_execution_policy_docs.py tests/unit/test_verification_command_docs.py tests/unit/test_feature_checklist_docs.py
```

## Exit Criteria

- the repository has an explicit operational policy for bounded, integration, and E2E test execution
- developers can tell which command set is expected locally, in CI, and in gated/manual environments
- release-readiness criteria match the new doctrine instead of the older bounded-proof model
