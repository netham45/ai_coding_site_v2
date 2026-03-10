# Phase F30A: Database Provenance, Documentation, And Audit Schema Family

## Goal

Implement the PostgreSQL schema family for provenance, rationale, documentation, review/testing outcomes, merges, and audit trails.

## Rationale

- Rationale: Provenance, docs, quality-gate outcomes, and audit trails need first-class relational storage if they are going to be queryable at scale.
- Reason for existence: This phase exists to give those cross-cutting history surfaces a concrete schema family instead of leaving them as incidental attachments.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/32_F30_code_provenance_and_rationale_mapping.md`: F30 is the parent provenance feature for this schema family.
- `plan/features/33_F29_documentation_generation.md`: F29 stores documentation artifacts and history in this schema area.
- `plan/features/25_F21_validation_framework.md`: F21 contributes durable validation results here.
- `plan/features/26_F22_review_framework.md`: F22 contributes review findings and outcomes here.
- `plan/features/28_F23_testing_framework_integration.md`: F23 contributes testing results here.
- `plan/features/35_F36_auditable_history_and_reproducibility.md`: F36 depends on these durable audit records.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/specs/database/database_schema_spec_v2.md`
- `notes/planning/expansion/database_schema_v2_expansion.md`
- `notes/specs/provenance/provenance_identity_strategy.md`
- `notes/catalogs/audit/auditability_checklist.md`
- `notes/planning/expansion/review_testing_docs_yaml_plan.md`

## Scope

- Database: define tables, constraints, indexes, and migrations for code provenance links, rationale records, source-document lineage, documentation artifacts, validation/review/testing results, merge records, rectification history, and audit events.
- CLI: expose query surfaces for provenance lookup, rationale traversal, docs inspection, review/testing history, merge history, and audit export.
- Daemon: persist all quality gates, merge outcomes, and provenance updates as first-class durable records.
- YAML: align validation/review/testing/docs identities with stored result records.
- Prompts: ensure review/testing/docs prompts can be tied back to durable result and rationale records.
- Tests: exhaustively test lineage integrity, rationale linkage, artifact versioning, merge/audit persistence, and every foreign-key or uniqueness rule.
- Performance: benchmark provenance lookup, audit-history scans, and documentation artifact retrieval paths.
- Notes: update provenance/audit/docs notes when storage structure or query semantics need clarification.

## Exit Criteria

- auditability, provenance, and documentation persistence are explicit, queryable, and fully test-backed.
