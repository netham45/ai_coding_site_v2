# Checklist C01: CLI Command Inventory Verification

## Goal

Verify that all required CLI surfaces exist and behave as designed.

## Verify

- top-level create/start commands exist for prompt-driven node creation
- AI-facing progress commands exist
- operator inspection commands exist
- session/recovery/pause/merge/docs/provenance/yaml/prompt commands exist
- every user-visible action is automatable through the CLI

## Tests

- exhaustive command coverage, including malformed input and authorization failures
- performance checks for common commands and prompt/context retrieval

## Notes

- update CLI and automation notes when any surface is missing or changes
