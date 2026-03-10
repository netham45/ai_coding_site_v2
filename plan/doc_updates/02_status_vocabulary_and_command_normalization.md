# Phase DU-02: Status Vocabulary And Command Normalization

## Goal

Normalize completion language and canonical verification commands across the repository.

## Rationale

- Rationale: The repo currently mixes older and newer status language and contains command references that were written under different assumptions.
- Reason for existence: This phase exists to make status claims and proving commands trustworthy again.

## Related Features

Read these implementation plans for context and interaction boundaries:

- `plan/update_tests/00_raise_existing_tests_to_doctrine_level.md`
- `plan/e2e_tests/01_e2e_harness_and_command_foundation.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `README.md`
- `notes/planning/implementation/project_development_flow_doctrine.md`
- `notes/catalogs/audit/flow_coverage_checklist.md`
- `notes/planning/implementation/scenario_and_flow_pytest_plan.md`
- `notes/planning/implementation/full_real_end_to_end_flow_hardening_plan.md`

## Scope

- Database: normalize migration-head and schema-check language in docs.
- CLI: normalize CLI command references and proving commands in docs.
- Daemon: normalize daemon/API verification references where they differ from current expectations.
- YAML: normalize compile/schema/proof language so validation is not confused with runtime completion.
- Prompts: normalize prompt existence versus prompt-runtime proof language.
- Notes: update current docs to use the same status vocabulary and command surface.
- Tests: this phase does not change test code directly, but aligns the commands that prove test layers.
- Performance: normalize performance-check command references and stale assumptions.

## Work

- define one canonical status vocabulary:
  - `implemented`
  - `verified`
  - `partial`
  - `flow_complete`
  - `release_ready`
- identify and update docs that still use weaker or ambiguous language such as:
  - covered
  - complete
  - exists
  - resolved in principle
  - needs review
  when those terms are being used as completion claims rather than planning inventory labels
- reconcile canonical command references across:
  - `README.md`
  - notes
  - plans
  - checklists
  - flow docs
  - E2E docs
- ensure command references clearly distinguish:
  - bounded test commands
  - integration/flow commands
  - E2E commands
  - performance commands

## Current DU-02 Outputs

- `notes/catalogs/checklists/verification_command_catalog.md`
- normalized command references in `README.md`
- normalized bounded-flow and real-E2E command references in flow/hardening notes

## Canonical Verification Command

```bash
python3 -m pytest tests/unit/test_verification_command_docs.py tests/unit/test_feature_checklist_docs.py tests/unit/test_notes_quickstart_docs.py
```

## Exit Criteria

- authoritative repo surfaces use consistent completion language
- canonical proving commands are consistent across repo surfaces
- no current authoritative doc implies that bounded proof is final completion proof
