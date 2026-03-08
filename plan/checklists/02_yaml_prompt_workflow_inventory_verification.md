# Checklist C02: YAML, Prompt, And Workflow Inventory Verification

## Goal

Verify that all required declarative assets exist and compile into the expected workflows.

## Verify

- all required built-in node/task/subtask/layout definitions exist
- validation/review/testing/docs/rectification/runtime-policy/prompt/hook files exist
- variable substitution/rendering behavior is implemented and documented
- compiled workflows contain the expected prompt, task, and subtask structure
- code/YAML boundaries remain aligned with the delineation note

## Tests

- exhaustive schema-validity and compileability tests for every built-in file
- exhaustive variable-substitution tests, including missing variables and escaping
- performance checks for resource loading and compile cost

## Notes

- update YAML, prompt, and code-vs-YAML notes if implementation reveals new required assets
