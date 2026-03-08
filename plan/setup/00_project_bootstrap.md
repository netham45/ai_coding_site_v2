# Phase S00: Project Bootstrap

## Goal

Create the repository-level skeleton so implementation can begin cleanly.

## Scope

- Database: define local/CI PostgreSQL strategy and environment loading.
- CLI: create Python package/app entrypoint layout for commands using the default testing stack.
- Daemon: create Python app/service layout around FastAPI + Uvicorn.
- YAML: create built-in, project-local, override, and schema directories.
- Prompts: create prompt asset directories and naming conventions.
- Tests: create pytest layout, shared fixtures, factory helpers, and performance-test harness skeleton.
- Performance: add baseline timing harnesses for DB, CLI, compile, and runtime hot paths.
- Notes: document setup decisions if they differ from current assumptions.

## Exit Criteria

- Python project structure exists.
- setup instructions are reproducible.
- test and performance harnesses can run in empty-skeleton mode.
