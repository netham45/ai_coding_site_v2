# Phase F15: Child Node Spawning

## Goal

Create and run child nodes from layouts with durable lineage and dependency-aware scheduling.

## Scope

- Database: child node creation, parent-child lineage, scheduling state.
- CLI: child materialization and child-state inspection surfaces.
- Daemon: layout materialization, child creation, scheduling, and parent wait behavior.
- YAML: default layout-driven child-spawn definitions.
- Prompts: layout generation and child-creation guidance prompts.
- Tests: exhaustive idempotent materialization, duplicate protection, ready/blocked scheduling, and create-from-layout coverage.
- Performance: benchmark materialization and scheduling with larger child sets.
- Notes: update child-materialization notes if insertion-point behavior changes.
