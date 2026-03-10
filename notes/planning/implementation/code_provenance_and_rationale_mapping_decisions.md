# Code Provenance And Rationale Mapping Decisions

## Phase

- `plan/features/32_F30_code_provenance_and_rationale_mapping.md`

## Decisions

- Provenance is refreshed explicitly through the daemon with `node provenance-refresh --node <id>` instead of trying to keep code-entity state continuously in sync on every workflow mutation.
- The first bounded extractor only supports Python `module`, `class`, `function`, and `method` entities plus `contains` and `calls` relations.
- Exact identity is anchored by entity type, canonical name, file path, and signature.
- Rename or move continuity is currently heuristic and requires matching entity type, normalized signature, and stable hash; those rows are recorded with explicit confidence instead of being treated as exact.
- Every node-version/entity observation stores the observed name, path, signature, and stable hash snapshot so later audit reads can explain why a match was made.
- The bounded default daemon refresh path scans the repository `src/` tree when present. Explicit workspace roots still scan the provided tree directly.
- Provenance refresh records a durable `provenance` summary entry so rationale generation and later audit surfaces have a stable summary anchor even when no user-authored summary exists for the node version.

## Deferred

- Non-Python entity families such as files, endpoints, tests, variables, and types.
- Relation-graph similarity and split/merge-aware identity matching.
- Automatic refresh triggers tied to workflow or git lifecycle transitions.
