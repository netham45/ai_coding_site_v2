# Checklist C06: Prompt Rendering And Variable Substitution Verification

## Goal

Verify that prompt and subtask rendering semantics are fully implemented and safe.

## Verify

- `{{variable}}` substitution works from invoker/task context as intended
- source values and rendered values are inspectable where needed
- missing variables fail safely
- escaping and shadowing rules are deterministic
- prompt rendering and command rendering use the same frozen semantics where intended

## Tests

- exhaustive rendering tests for prompts, commands, env values, args, and YAML-defined renderable fields
- performance checks for render cost during compile and stage start

## Notes

- update YAML schema, prompt library, and code-vs-YAML notes if rendering semantics need elaboration
