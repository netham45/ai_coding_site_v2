# Phase F31A: Database Runtime State Schema Family

## Goal

Implement the PostgreSQL schema family for live orchestration state.

## Scope

- Database: define tables, constraints, indexes, and migrations for nodes, node relationships, lifecycle state, dependency state, run admission, run state, pause flags, and rebuild eligibility.
- CLI: expose read paths needed to inspect runtime state cleanly.
- Daemon: use these records as the authoritative source for scheduling and state-transition legality.
- YAML: no new YAML semantics beyond aligning runtime state names with compiled workflow expectations.
- Prompts: no direct prompt semantics beyond ensuring prompt stages map cleanly onto stored runtime state.
- Tests: exhaustively test valid state creation, illegal transitions, dependency blocking, pause semantics, rebuild eligibility, and every persistence rule.
- Performance: benchmark hot runtime reads and write-heavy transition paths.
- Notes: update runtime/database notes if the live state model needs stricter normalization or additional state categories.

## Exit Criteria

- the live orchestration state model is explicit, durable, indexed, and fully test-backed.
