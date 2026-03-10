# Built-In Validation, Review, Testing, And Docs Library Authoring Decisions

## Phase

- `plan/features/61_F05_builtin_validation_review_testing_docs_library_authoring.md`

## Decision

- Keep the active default node ladders unchanged for now.
- Treat the packaged validation, review, testing, and docs YAML families as one inspectable built-in quality library.
- Fail workflow compilation early when required quality assets, prompt bindings, task-family bindings, or canonical gate ordering are broken.

## Why

- The built-in quality families already exist as authored assets, so the main remaining gap was integrity and inspectability rather than raw file creation.
- Expanding the active default node ladders to run more gates in this slice would change runtime behavior beyond library authoring.
- Compile-time failure is a better boundary than indirect runtime breakage when the shipped built-in quality pack is incomplete or inconsistent.

## Added In This Slice

- local CLI inspection for the built-in quality library manifest
- integrity checks for required built-in validation, review, testing, and docs YAML files
- prompt-asset and prompt-reference validation for the built-in quality surfaces
- task-to-definition binding validation for the packaged gate/docs tasks
- canonical built-in gate-order validation across node task ladders
- a small benchmark-baseline increase for quality-library scans and compile-adjacent flows, reflecting the added prompt-reference and cross-family binding checks that now run before workflow compilation

## Deliberate Deferrals

- no silent insertion of `test_node`, `build_node_docs`, or `finalize_node` into the active default node ladders
- no runtime-policy expansion that forces additional quality gates beyond the current staged workflow surface
- no new daemon API surface was required because this slice is a local built-in-library inspection boundary
