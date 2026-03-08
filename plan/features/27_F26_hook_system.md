# Phase F26: Hook System

## Goal

Support policy-driven hook insertion across lifecycle points.

## Scope

- Database: persist selected/expanded hooks and hook lineage where needed.
- CLI: hooks-in-effect and hook-origin inspection.
- Daemon: hook selection, ordering, expansion, and legality checks.
- YAML: hook schemas and built-in hook definitions.
- Prompts: load and compile prompt-bearing hooks safely.
- Tests: exhaustive applicability, ordering, conflict, and expansion-diagnostic coverage.
- Performance: benchmark compile overhead from hook expansion.
- Notes: update hook algorithm notes if ordering edge cases emerge.
