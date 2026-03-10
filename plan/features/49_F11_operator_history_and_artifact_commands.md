# Phase F11-S2: Operator History And Artifact Commands

## Goal

Implement the operator CLI command family for history, artifacts, YAML, prompts, docs, and provenance.

## Rationale

- Rationale: Current-state views are not enough for audit-heavy workflows; operators also need access to prompts, docs, provenance, merges, and rebuild history.
- Reason for existence: This phase exists to expose the historical and artifact-focused command family that complements the live-state inspection surface.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/15_F11_operator_cli_and_introspection.md`: F11 is the parent feature for this command family.
- `plan/features/31_F28_prompt_history_and_summary_history.md`: F28 provides prompt and summary history surfaces.
- `plan/features/32_F30_code_provenance_and_rationale_mapping.md`: F30 provides provenance and rationale data exposed here.
- `plan/features/33_F29_documentation_generation.md`: F29 provides docs artifacts and history views.
- `plan/features/48_F11_operator_structure_and_state_commands.md`: F11-S1 provides the complementary live-state and structure commands.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/specs/database/database_schema_spec_v2.md`
- `notes/catalogs/audit/auditability_checklist.md`
- `notes/specs/provenance/provenance_identity_strategy.md`
- `notes/specs/prompts/prompt_library_plan.md`

## Scope

- Database: create read models for prompts, summaries, docs, provenance, rebuilds, merges, and workflow history.
- CLI: implement:
  - prompt and summary history commands
  - docs list/show/build inspection commands
  - provenance/entity/rationale commands
  - source/resolved YAML commands
  - merge/rebuild history commands
- Daemon: serve daemon-owned inspection where live state matters.
- YAML: expose source/resolved artifacts clearly.
- Prompts: prompt-lineage inspection commands must reflect actual prompt-template identity.
- Tests: exhaustively cover historical inspection, empty-history cases, and artifact lookup correctness.
- Performance: benchmark history and artifact query paths.
- Notes: update introspection and provenance/docs notes if new inspection surfaces are required.
