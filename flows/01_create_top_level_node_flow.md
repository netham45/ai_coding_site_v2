# Flow 01: Create Top-Level Node

## Purpose

Create a new top-level node from a user prompt or request file and leave it in a durable, inspectable state.

## Covers journeys

- create a top-level node from a prompt
- start work from vague or explicit operator input

## Entry conditions

- the user provides a prompt, request file, or equivalent creation payload
- the requested node kind and tier are allowed by project policy

## Task flow

1. capture operator input
2. resolve requested node kind, tier, title, and parent scope if any
3. select source YAML definitions from the built-in library and project overrides
4. persist source prompt/request lineage
5. create a new logical node and initial node version record
6. initialize branch identity and seed metadata
7. hand off to workflow compilation
8. leave the node in `COMPILED`, `READY`, or explicit compile-failed state

## Required subtasks

- `capture_creation_request`
- `resolve_node_definition`
- `resolve_source_documents`
- `persist_prompt_and_request_sources`
- `create_node_version`
- `initialize_git_metadata`
- `compile_initial_workflow`
- `publish_creation_summary`

## Required capabilities

- `ai-tool node create ...`
- prompt and source lineage persistence
- node version persistence
- branch/seed metadata creation
- workflow compilation trigger
- creation audit history

## Durable outputs

- logical node ID
- node version ID
- source prompt/request record
- source YAML lineage
- branch identity
- seed commit metadata
- compiled workflow or compile-failure record
- creation summary

## Failure cases that must be supported

- invalid requested node kind/tier
- missing source YAML
- conflicting overrides
- compile failure during initial setup
- branch initialization failure

## Completion rule

The node is queryable through the CLI with enough information to either run it, inspect compile failure, or revise the inputs.
