# Flow 12: Query Provenance And Docs

## Purpose

Provide rationale, code provenance, entity history, and generated documentation views for completed or in-progress work.

## Covers journeys

- inspect why something changed
- inspect which node or prompt changed an entity
- build or inspect docs for a node or subtree

## Entry conditions

- the caller requests provenance, rationale, entity history, or docs for a node, subtree, file, or code entity

## Task flow

1. resolve the requested subject: node, subtree, file, entity, or doc view
2. load prompt, summary, and workflow lineage relevant to the subject
3. load code-entity identities and change links
4. resolve confidence-scored identity matches where needed
5. load relations and changed-by history
6. generate or retrieve documentation view if requested
7. present a normalized explanation to the caller

## Required subtasks

- `resolve_query_subject`
- `load_prompt_and_summary_lineage`
- `load_entity_history`
- `resolve_entity_identity_confidence`
- `load_relation_graph`
- `build_or_load_docs`
- `render_provenance_view`

## Required capabilities

- `ai-tool prompts list|show ...`
- `ai-tool rationale show ...`
- `ai-tool entity show|history|relations|changed-by ...`
- `ai-tool docs build-node-view|build-tree ...`
- `ai-tool docs show ...`

## Durable outputs

- optional docs artifacts
- provenance query response
- optional doc-build history

## Failure cases that must be supported

- ambiguous entity identity after rename or move
- missing provenance linkage for older nodes
- stale docs artifact needing rebuild

## Completion rule

The caller can trace code and documentation back to node lineage, prompt lineage, and rationale history with explicit confidence where identity is inferred.
