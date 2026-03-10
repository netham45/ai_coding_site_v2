# Configurable Node Hierarchy Decisions

## Purpose

Capture implementation choices made while completing `plan/features/02_F01_configurable_node_hierarchy.md`.

## Decisions

### Hierarchy posture

- hierarchy semantics now come from YAML-backed node definitions rather than hardcoded `epic -> phase -> plan -> task` checks in code
- the built-in package still ships semantic defaults (`epic`, `phase`, `plan`, `task`), but they sit on a generic `kind` and `tier` substrate
- daemon code enforces parent/child legality from loaded hierarchy definitions instead of embedding those constraints in CLI command logic

### Database posture

- this slice introduces durable `node_hierarchy_definitions` and `hierarchy_nodes` tables for configurable kind/tier storage and manual/top-level creation records
- these tables are a staging layer ahead of the richer `node_versions` lineage model that later features will implement
- built-in hierarchy definitions are synced into the database by the daemon when the hierarchy schema is available

### CLI and daemon posture

- CLI now supports daemon-backed `node create`, `node show`, `node children`, `node ancestors`, and `node kinds`
- top-level create flows accept arbitrary `--kind` values as long as the loaded hierarchy registry permits them
- child creation legality is enforced by the daemon using parent/child kind and tier constraints from YAML

### Test and performance posture

- coverage now includes built-in hierarchy loading, custom ladder validation, durable node creation, and CLI/daemon round trips for hierarchy reads
- migration and performance expectations were updated so the hierarchy schema is part of the tested baseline
