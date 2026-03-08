# Checklist C07: Verification Schema Family Verification

## Goal

Verify that validation, review, testing, docs, rectification, runtime-policy, and prompt-linked schema families are rigid and complete.

## Verify

- every verification-oriented YAML family has a real schema
- schemas reject malformed structures and illegal references
- schema families match the actual built-in files and runtime expectations

## Tests

- exhaustive valid/invalid schema-family tests
- performance checks for schema validation over large definition packs

## Notes

- update schema and family-inventory notes when any family expands or tightens
