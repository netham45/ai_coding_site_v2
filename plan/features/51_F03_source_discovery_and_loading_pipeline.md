# Phase F03-S2: Source Discovery And Loading Pipeline

## Goal

Implement the first compiler stage: discovering and loading all compile inputs deterministically.

## Rationale

- Rationale: Compilation cannot be deterministic unless source discovery itself is deterministic about roots, family order, and duplicate handling.
- Reason for existence: This phase exists to define the first compiler stage and the exact input inventory every later stage depends on.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/07_F03_immutable_workflow_compilation.md`: F03 is the parent compiler feature for this stage.
- `plan/features/08_F05_default_yaml_library.md`: F05 provides one major input source family the loader must discover.
- `plan/features/10_F06_override_and_merge_resolution.md`: F06 relies on deterministic source ordering established here.
- `plan/features/43_F05_prompt_pack_authoring.md`: F05-S2 provides prompt assets that must be discoverable in the same pipeline.
- `plan/features/52_F03_schema_validation_compile_stage.md`: F03-S3 follows this stage in the compile pipeline.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/specs/yaml/yaml_schemas_spec_v2.md`
- `notes/catalogs/inventory/default_yaml_library_plan.md`
- `notes/specs/prompts/prompt_library_plan.md`
- `notes/pseudocode/00_compilation_plan.md`
- `notes/pseudocode/catalog/source_to_artifact_map.md`

## Scope

- Database: persist source-discovery/load diagnostics and source input inventory as needed.
- CLI: inspect discovered source inputs and load failures.
- Daemon: discover built-ins, project-local extensions, overrides, prompts, and policy docs in deterministic order.
- YAML: define loadable families and source roots cleanly.
- Prompts: ensure prompt assets are discoverable through the same deterministic resource pipeline.
- Tests: exhaustively cover missing sources, duplicate/ambiguous sources, and deterministic load order.
- Performance: benchmark source discovery and load time.
- Notes: update compile/input notes if real source categories differ.
