# Checklist C14: Built-In YAML Library Family Verification

## Goal

Verify that the built-in YAML and prompt library is complete by family, not just present in aggregate.

## Verify

- structural YAML built-ins exist for nodes, tasks, subtasks, and layouts
- quality-gate YAML built-ins exist for validations, reviews, testing, and docs
- runtime-policy and hook built-ins exist and bind correctly to prompt assets
- prompt packs exist for decomposition, execution, errors, missed steps, idle nudges, pause/resume, and recovery
- every built-in asset compiles, resolves placeholders correctly, and is inspectable through CLI surfaces

## Tests

- exhaustive per-family compileability, schema-validity, prompt-binding, and placeholder-substitution tests
- performance checks for full built-in library discovery and compilation

## Notes

- update built-in library and prompt notes if any family expands, splits, or gains new contracts
