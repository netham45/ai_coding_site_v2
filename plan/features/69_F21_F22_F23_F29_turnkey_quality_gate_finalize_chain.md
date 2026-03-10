# Phase F21/F22/F23/F29-S1: Turnkey Quality Gate Finalize Chain

## Goal

Create a turnkey built-in end-to-end quality chain that runs validation, review, testing, provenance, docs, and finalize without stitched fixture setup.

## Rationale

- Rationale: The system already has durable validation, review, testing, provenance, and docs slices, but Flow 09 still requires stitched setup rather than one canonical built-in quality path.
- Reason for existence: This phase exists to turn the current collection of quality-gate features into one cohesive, end-to-end operator flow.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/25_F21_validation_framework.md`: F21 supplies validation gating.
- `plan/features/26_F22_review_framework.md`: F22 supplies review gating.
- `plan/features/28_F23_testing_framework_integration.md`: F23 supplies testing gating.
- `plan/features/32_F30_code_provenance_and_rationale_mapping.md`: F30 provides provenance refresh that sits late in the quality chain.
- `plan/features/33_F29_documentation_generation.md`: F29 supplies documentation generation that must participate in the chain.

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/planning/expansion/review_testing_docs_yaml_plan.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/prompts/prompt_library_plan.md`
- `notes/specs/yaml/yaml_schemas_spec_v2.md`
- `notes/specs/database/database_schema_spec_v2.md`
- `notes/planning/implementation/per_flow_gap_remediation_plan.md`

## Scope

- Database: ensure the full chain leaves a coherent durable record from gate results through provenance/docs/finalize state.
- CLI: expose a more natural end-to-end quality chain without requiring stitched test-only setup.
- Daemon: wire validation, review, testing, provenance refresh, docs generation, and finalize into one canonical orchestration path.
- YAML: author or refine the built-in task/library wiring needed for the full chain to be canonical and turnkey.
- Prompts: align built-in quality prompts so the chain is coherent from one stage to the next.
- Tests: exhaustively cover the full-chain happy path, gate failures, retries, partial success, and finalization readiness.
- Performance: benchmark the full quality chain and its read surfaces to avoid excessive end-to-end overhead.
- Notes: update quality-gate, provenance, docs, and finalize notes to describe the turnkey chain explicitly.
