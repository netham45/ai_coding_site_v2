# Phase DS-05: Document Test Execution And Adoption Policy

## Goal

Define how document-schema tests are adopted, run, and maintained as part of normal repository work.

## Rationale

- Rationale: Schema rules are only effective if the repo also defines when and how their tests must run.
- Reason for existence: This phase exists to make document consistency testing part of the normal proving surface rather than an optional cleanup tool.

## Related Features

Read these implementation plans for context and interaction boundaries:

- `plan/doc_schemas/00_document_schema_master_plan.md`
- `plan/doc_updates/02_status_vocabulary_and_command_normalization.md`
- `plan/doc_updates/04_ci_e2e_execution_policy_and_release_alignment.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `AGENTS.md`
- `README.md`
- `notes/planning/implementation/project_development_flow_doctrine.md`

## Scope

- Database: define how doc tests interact with DB-backed command/status docs where needed.
- CLI: define how command-bearing docs are rerun and verified after doc changes.
- Daemon: define how daemon/runtime documentation families are rerun and verified after changes.
- YAML: define how schema-bearing docs and declarative tracking docs are rerun and verified after changes.
- Prompts: define how prompt-related authoritative docs are rerun and verified after changes.
- Notes: define the normal proving path for doc-schema tests.
- Tests: define when document tests run locally, in CI, and in broader release-readiness passes.
- Performance: keep the document test surface fast enough to run after doc changes without becoming a bottleneck.

## Work

- define canonical commands for document-schema tests
- define which document-family tests should run after which kinds of doc changes
- define how new authoritative document families adopt schema tests
- define how failures in document tests are triaged and resolved
- define how doc-schema tests fit into release-readiness and hardening passes

## Current DS-05 Outputs

- `notes/catalogs/checklists/document_schema_test_policy.md`
- document-schema execution-policy enforcement in `tests/unit/test_document_schema_docs.py`
- family README command/status linkage in `plan/checklists/README.md` and `plan/e2e_tests/README.md`

## Canonical Verification Command

```bash
python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_e2e_execution_policy_docs.py tests/unit/test_verification_command_docs.py
```

## Exit Criteria

- document-schema tests have canonical commands
- developers can tell which doc tests must run after a given documentation change
- new authoritative document families have a clear adoption path instead of ad hoc treatment
