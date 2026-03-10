# Built-In Runtime Policy, Hook, And Prompt Library Authoring Decisions

## Phase

- `plan/features/62_F05_builtin_runtime_policy_hook_prompt_library_authoring.md`

## Decision

- Keep the current runtime behavior staged as-is.
- Treat the packaged runtime definitions, runtime policies, hook definitions, environment policies, prompt references, and required operational prompts as one inspectable operational library.
- Fail workflow compilation early when required operational assets or cross-family references are broken.

## Why

- The built-in operational assets already exist as authored files, so the main remaining gap was integrity and inspectability rather than raw file creation.
- The runtime/compiler already consumes these files for policy resolution, hook expansion, prompt lineage, and environment metadata, which makes compile-time integrity checks the correct boundary.
- Expanding runtime semantics in this slice would mix library authoring with orchestration behavior changes.

## Added In This Slice

- local CLI inspection for the built-in operational library manifest
- integrity checks for required built-in runtime, hook, policy, environment, and prompt-reference YAML files
- required prompt-asset and prompt-reference validation for the shipped operational prompt set
- runtime-action validation against the built-in subtask catalog
- policy-reference validation across runtime definitions and hooks
- a small benchmark baseline for the operational-library integrity scan, reflecting the prompt-asset and cross-family reference checks

## Deliberate Deferrals

- no new YAML family for prompt-pack metadata beyond the existing prompt-reference boundary
- no expansion of runtime-only hook execution beyond the current staged compile-time hook model
- no new launcher behavior for container or namespace environments
