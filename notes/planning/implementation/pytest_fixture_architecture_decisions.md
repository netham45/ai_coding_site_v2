# pytest Fixture Architecture Decisions

## Purpose

Capture implementation choices made while completing `plan/setup/11_pytest_fixture_architecture.md`.

## Decisions

### Fixture layering

- database fixtures now separate engine, session-factory, session, isolated-schema, clean-public-schema, and migrated-public-schema responsibilities
- CLI tests now have a `cli_runner` fixture that returns a structured result object instead of repeating `run(...)` plus `json.loads(...)`
- daemon tests now have dedicated auth/token and app-client fixtures, plus a reusable in-process daemon bridge for CLI-to-daemon integration tests

### Resource and prompt posture

- resource fixtures now include deterministic YAML-compile and prompt-render contexts so later compiler and prompt-contract tests do not need to invent ad hoc payloads
- fixture contexts stay intentionally small and scaffold-oriented until real compiler/runtime contracts replace them

### Test-infrastructure posture

- the repository now tests the fixture architecture directly for determinism, migrated-schema setup, authenticated daemon bridging, and expected misuse behavior
- integration tests were updated in representative areas to consume shared fixture helpers instead of duplicating setup logic
- bounded database fixtures now target isolated per-test PostgreSQL databases instead of rebuilding one shared `public` schema, trading some setup cost for worker-safe parallel execution
- real E2E fixtures now assign a per-test `TMUX_TMPDIR` so tmux-backed runtime tests do not share the default server namespace
- real E2E daemon fixtures now reserve and hand off an already-bound listener socket to Uvicorn so parallel startup cannot lose the chosen port between discovery and bind
- fixture isolation is an invariant, not a best-effort optimization: tests must own their database, schema, process, workspace, token, port, and tmux resources tightly enough to remain parallel-safe whenever the required environment capabilities exist

### Performance posture

- fixture-startup overhead is now part of the performance harness so CLI fixture invocation and packaged-resource loading remain lightweight
