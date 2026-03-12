# Project Lifecycle Overview

## Purpose

This repository uses staged development so it can grow from empty scaffold to real runtime behavior without drifting into undocumented assumptions or overstated completion claims.

The default stage sequence is:

1. genesis
2. architecture
3. setup
4. feature delivery
5. hardening and end-to-end proof
6. post-v1 evolution

## Core Rule

Before meaningful work begins:

1. read this file
2. read the current stage note
3. read `plan/checklists/00_project_operational_state.md`
4. read the governing task plan

## Relationship Between Artifacts

### `AGENTS.md`

`AGENTS.md` is the always-on doctrine summary.

### `notes/lifecycle/*.md`

Lifecycle notes contain stage-specific operating rules and sub-step gates.

### `plan/checklists/00_project_operational_state.md`

This is the maturity rollup surface.

### `plan/tasks/*.md`

Task plans govern meaningful work.

### `notes/logs/**/*.md`

Development logs record what actually happened.

### `notes/catalogs/checklists/*.md`

Checklist and command-catalog notes define proving and status discipline.

## Core Principles

- notes are implementation assets
- systems must be considered explicitly
- stack choices must be declared explicitly when they are made
- bounded proof is not final runtime proof
- checklists and logs are required
- stronger completion language must be earned
- post-v1 work must still be governed intentionally

## Stage Map

- `01_stage_00_genesis.md`
- `02_stage_01_architecture.md`
- `03_stage_02_setup.md`
- `04_stage_03_feature_delivery.md`
- `05_stage_04_hardening_and_e2e.md`
- `06_stage_05_post_v1_evolution.md`

## Exit Condition

This overview is doing its job when contributors can identify:

- the current stage
- the next governing note to read
- the checklist that records current maturity
- the difference between implemented, verified, flow-complete, and release-ready
