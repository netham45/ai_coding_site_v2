# Top-Level Workflow Creation Commands Decisions

## Scope implemented in this slice

- Added a daemon-owned top-level startup flow that creates a parentless node, captures source lineage, compiles the workflow, transitions to `READY`, and optionally admits the first run.
- Added the API surface `POST /api/workflows/start`.
- Added CLI entrypoints `workflow start` and top-level `node create --compile [--start-run]`.
- Added unit, integration, CLI, and performance coverage for the create/compile/start flow.

## Key implementation decisions

- This slice does not add a new database table. The startup request is represented through existing durable artifacts:
  - the created node and initial node version
  - source-lineage capture
  - the compiled workflow or durable compile failure
  - the lifecycle transition to `READY`
  - the first admitted run when requested
- The first admitted run now uses `trigger_reason = workflow_start` so startup-originated runs are distinguishable from later manual starts.
- `workflow start` derives a title from the prompt when none is supplied, but `node create --compile ...` keeps the explicit `--title` requirement of the existing `node` surface.
- Top-level startup is intentionally limited to kinds whose YAML definition allows `allow_parentless = true`.
- The system doctrine is that any node kind may be top-level if it has no parent and its hierarchy definition allows `allow_parentless = true`.
- The current shipped built-in YAML still marks only `epic` as `allow_parentless`, so current startup behavior is narrower than the intended doctrine and should be treated as a reconciliation gap in the packaged hierarchy and tests.

## Boundaries kept in place

- Parented manual creation still uses the existing `node create --parent ...` and `node child create ...` flows.
- Startup does not generate child layouts automatically in this slice; it only creates the top-level node and its initial compiled/run state.
- Compile failure is returned as a partial-success startup result rather than rolled back, because the created node and durable failure record are useful operator artifacts.

## Deferred work

- Automatic top-level kind inference from prompt content remains deferred; the operator still supplies `--kind`.
- Richer request-audit metadata for startup intent remains deferred beyond the existing durable node/run/compiler artifacts.
- The packaged hierarchy and startup tests still need reconciliation with the doctrine that top-ness is structural rather than tied to `epic`.
