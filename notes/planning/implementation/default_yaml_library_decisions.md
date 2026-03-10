# Default YAML Library Decisions

Date: 2026-03-08
Phase: `plan/features/08_F05_default_yaml_library.md`

## Decisions

1. The built-in YAML library is now authored broadly, not scaffold-only.
   The repository ships meaningful packaged documents across node, task, subtask, layout, validation, review, testing, docs, rectification, runtime, hook, prompt-reference, and policy families.

2. Library authoring is deliberately wider than current runtime binding.
   The default node kinds still reference the smaller task set already exercised by the current compiler and runtime slices. Additional authored tasks and support definitions are packaged now so later runtime phases can bind them without another scaffold-only pass.

3. The schema validator was upgraded in the same phase.
   The previous scaffold validator shape was too weak to support real authored built-ins, so task/subtask/layout/review/testing/docs/runtime/hook/policy validation moved to richer family-specific models.

4. Prompt assets are now treated as real packaged dependencies of the built-in library.
   Prompt-reference YAML points at authored prompt assets instead of placeholder strings, so built-in loading and workflow compilation can freeze those bindings deterministically.

## Deferred Work

- binding the broader authored task chain into the default node kinds
- consuming reusable standalone `subtasks/*.yaml` definitions during workflow compilation rather than only task-local authored subtasks
- later-stage override and hook expansion that will make more of the packaged library runtime-authoritative
