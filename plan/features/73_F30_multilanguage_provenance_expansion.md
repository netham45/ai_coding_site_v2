# Phase F30-S1: Multilanguage Provenance Expansion

## Goal

Expand provenance and rationale mapping beyond the current bounded Python-only entity model.

## Rationale

- Rationale: Provenance queries and rationale inspection already work, but the current extractor intentionally covers only Python `module`, `class`, `function`, and `method` entities plus a small relation set.
- Reason for existence: This phase exists to broaden provenance from a useful bounded slice into a more representative project-wide audit surface.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/32_F30_code_provenance_and_rationale_mapping.md`: F30 introduced the current bounded provenance model.
- `plan/features/33_F29_documentation_generation.md`: F29 consumes some of the same project-structure information for docs generation.
- `plan/features/35_F36_auditable_history_and_reproducibility.md`: F36 reconstructs audit views that must remain coherent as provenance expands.
- `plan/features/59_F30_database_provenance_docs_audit_schema_family.md`: F30-S2 added the DB views that may need to widen as provenance scope expands.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/specs/provenance/provenance_identity_strategy.md`
- `notes/specs/database/database_schema_spec_v2.md`
- `notes/catalogs/audit/auditability_checklist.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/planning/implementation/per_flow_gap_remediation_plan.md`

## Scope

- Database: widen provenance persistence and current-state views only as needed for new entity and relation families.
- CLI: ensure rationale/entity/history/relation reads remain coherent when multiple languages or richer entity classes are introduced.
- Daemon: extend provenance extraction, matching, and relation modeling beyond the current bounded Python set.
- YAML: keep provenance extraction semantics code-owned rather than declarative.
- Prompts: update provenance or audit prompts only where richer entity models change user-visible expectations.
- Tests: exhaustively cover new entity families, relation types, matching confidence, history output, and backward compatibility for the existing Python model.
- Performance: benchmark extraction, refresh, and relation-query costs as the provenance surface broadens.
- Notes: update provenance, audit, and database notes so the expanded identity strategy is explicit.
