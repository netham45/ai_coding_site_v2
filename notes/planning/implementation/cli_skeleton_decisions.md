# CLI Skeleton Decisions

## Purpose

Capture implementation choices made while completing `plan/setup/03_cli_skeleton.md`.

## Decisions

### Command tree shape

- the CLI now uses top-level namespaces for `node`, `workflow`, `subtask`, `session`, `yaml`, `prompts`, `docs`, `admin`, and `debug`
- the earlier bootstrap commands remain available under `admin` rather than staying as flat top-level bootstrap-only commands
- placeholder command handlers are acceptable in this phase as long as the command tree, argument contracts, and handler registration are stable and testable

### Daemon boundary

- mutating CLI commands are modeled as daemon-boundary commands even before the daemon implements their endpoints
- local read-only bootstrap DB commands remain under `admin db` during setup because the daemon read API does not exist yet
- daemon connectivity and boundary inspection live under `debug daemon`

### Auth posture

- CLI daemon access uses the shared auth-token loader, preferring file-backed tokens when available
- missing-token behavior is now an explicit CLI error path rather than an incidental parser/runtime crash

### YAML and prompt posture

- the CLI exposes source-inspection hooks for YAML, prompts, and docs now so later implementation can fill in real content without restructuring the command tree

