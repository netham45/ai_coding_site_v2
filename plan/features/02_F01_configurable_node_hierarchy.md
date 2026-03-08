# Phase F01: Configurable Node Hierarchy

## Goal

Support configurable tiers and node kinds instead of hardcoding one ladder.

## Scope

- Database: flexible node kind/tier storage and parent/child constraint storage.
- CLI: visible kind/tier reporting and top-level create-from-prompt surfaces for arbitrary `--kind`.
- Daemon: enforce parent/child legality and create top-level nodes from prompt-driven requests.
- YAML: node definition schemas and built-in/default node definitions.
- Prompts: generic node-kind placeholders and top-level creation prompt support.
- Tests: exhaustive coverage for valid/invalid hierarchies, arbitrary top-level create flows, and custom ladders.
- Performance: benchmark hierarchy traversal and create-from-prompt overhead.
- Notes: update hierarchy and entrypoint notes if custom ladders need more fields.
