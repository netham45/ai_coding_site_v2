# Phase F16: Manual Tree Construction

## Goal

Let users define and edit trees manually without breaking layout-driven safety.

## Scope

- Database: structural authority metadata and origin tracking.
- CLI: manual create/edit/replace flows for tree structure.
- Daemon: hybrid-tree safety and reconciliation enforcement.
- YAML: manual-layout and hybrid-authority support where needed.
- Prompts: minimal manual-reconciliation guidance prompts.
- Tests: exhaustive manual-only, hybrid, authority-conflict, and regeneration-after-manual-edit coverage.
- Performance: benchmark tree inspection with authority metadata.
- Notes: update manual-vs-auto notes when real edge cases appear.
