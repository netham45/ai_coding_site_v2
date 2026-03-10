# Phase E2E-04: E2E Quality, Docs, Provenance, And Audit

## Goal

Create real E2E suites for validation, review, testing, prompts, summaries, provenance, documentation, audit history, and reproducibility behavior.

## Rationale

- Rationale: The system's claimed value depends heavily on quality gates, prompt history, provenance, generated docs, and reconstructible audit history, but these are easy to under-prove through bounded helper tests.
- Reason for existence: This phase exists to ensure the full quality and audit plane is proven through real orchestration runs and real inspectability surfaces.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/06_F27_source_document_lineage.md`
- `plan/features/25_F21_validation_framework.md`
- `plan/features/26_F22_review_framework.md`
- `plan/features/27_F26_hook_system.md`
- `plan/features/28_F23_testing_framework_integration.md`
- `plan/features/31_F28_prompt_history_and_summary_history.md`
- `plan/features/32_F30_code_provenance_and_rationale_mapping.md`
- `plan/features/33_F29_documentation_generation.md`
- `plan/features/35_F36_auditable_history_and_reproducibility.md`
- `plan/features/42_F05_subtask_library_authoring.md`
- `plan/features/43_F05_prompt_pack_authoring.md`
- `plan/features/44_F04_validation_review_testing_docs_rectification_schema_families.md`
- `plan/features/45_F04_runtime_policy_and_prompt_schema_families.md`
- `plan/features/57_F31_database_runtime_state_schema_family.md`
- `plan/features/58_F31_database_session_attempt_history_schema_family.md`
- `plan/features/59_F30_database_provenance_docs_audit_schema_family.md`
- `plan/features/69_F21_F22_F23_F29_turnkey_quality_gate_finalize_chain.md`
- `plan/features/73_F30_multilanguage_provenance_expansion.md`

## Required Notes

- `notes/specs/prompts/prompt_library_plan.md`
- `notes/specs/provenance/provenance_identity_strategy.md`
- `notes/specs/database/database_schema_spec_v2.md`
- `notes/catalogs/audit/auditability_checklist.md`
- `notes/contracts/persistence/compile_failure_persistence.md`
- `notes/catalogs/checklists/verification_command_catalog.md`
- `notes/catalogs/checklists/e2e_execution_policy.md`

## Scope

- Database: assert durable validation/review/testing results, prompt history, summary history, provenance rows/views, documentation outputs, and audit snapshots.
- CLI: prove operator reads for validation, review, testing, docs, provenance, rationale, audit, and history surfaces through the real CLI path.
- Daemon: drive actual run progression and quality-chain behavior through the real daemon and real persistence boundaries.
- YAML: prove built-in quality gates, docs definitions, hooks, and prompt references through actual compiled/runtime selection.
- Prompts: prove prompt-pack selection, prompt delivery/history, recovery and quality prompts where applicable.
- Notes: document the canonical E2E commands for quality/audit suites and the remaining partial areas.
- Tests: build suite families around whole-node quality narratives rather than isolated helper-level proofs.
- Performance: keep these E2E suites bounded enough for targeted reruns while still proving the full quality chain.

## Proposed Suite Families

- `tests/e2e/test_e2e_quality_chain_real.py`
- `tests/e2e/test_e2e_prompt_and_summary_history_real.py`
- `tests/e2e/test_e2e_provenance_and_docs_real.py`
- `tests/e2e/test_e2e_audit_and_reproducibility_real.py`

## Exit Criteria

- quality, docs, provenance, and audit features are proven through real runtime execution and real operator inspection surfaces
- prompt and summary history behavior is proven through real delivery and real durable reads
- documentation and provenance are not considered verified by existence-only proof
