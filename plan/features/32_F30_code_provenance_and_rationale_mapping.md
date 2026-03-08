# Phase F30: Code Provenance And Rationale Mapping

## Goal

Track code/entity history and rationale links back to nodes and prompts.

## Scope

- Database: entity, relation, change, and rationale-link storage.
- CLI: entity history, changed-by, rationale, and relation inspection.
- Daemon: provenance extraction and rationale persistence at the right lifecycle points.
- YAML: provenance-policy tuning inputs where declarative control is appropriate.
- Prompts: docs/rationale prompts consume provenance; identity remains code-owned.
- Tests: exhaustive exact-match, inferred-match, rename/move, and confidence-reporting coverage.
- Performance: benchmark provenance extraction and query paths.
- Notes: update provenance identity notes if stronger matching categories are needed.
