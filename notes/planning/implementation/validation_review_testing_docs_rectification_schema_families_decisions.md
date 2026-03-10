# Validation, Review, Testing, Docs, And Rectification Schema Family Decisions

## Phase

- `plan/features/44_F04_validation_review_testing_docs_rectification_schema_families.md`

## Decision Summary

- The higher-order YAML families already existed, so this phase tightened them rather than introducing new families.
- `validation_definition`, `review_definition`, `testing_definition`, `docs_definition`, and `rectification_definition` now reject invalid field combinations directly in the schema layer.
- Review and hook prompt-bearing fields are now validated against the packaged prompt catalog during YAML validation.

## Frozen Constraints

- validation checks must use supported built-in check types and required companion fields
- review definitions must declare at least one applicability selector and at least one criterion
- testing commands must have non-empty command and working directory values
- docs outputs must have non-empty `path` and `view`
- rectification definitions must include at least one unique subtask and non-empty trigger and entry-task values

## Boundary Clarification

- This phase did not add new DB tables or daemon APIs because schema-family persistence and validation-report storage already existed.
- The implementation value here is earlier rejection: invalid higher-order YAML now fails during schema validation rather than leaking into compile-time or runtime-specific errors.
