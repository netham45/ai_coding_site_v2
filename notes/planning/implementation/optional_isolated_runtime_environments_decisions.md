# Optional Isolated Runtime Environments Decisions

## Scope implemented in this slice

- Added validated `environment_policy_definition` YAML plus built-in environment policy documents.
- Added immutable compiled-workflow environment snapshots on compiled subtasks.
- Added durable per-attempt execution-environment snapshots and CLI/daemon inspection surfaces.
- Added focused unit, integration, CLI, and performance coverage for environment-policy loading and runtime recording.

## Key implementation decisions

- Environment isolation remains an execution-policy concern, not a new ownership or session model. The node run and primary session stay authoritative.
- The immutable workflow now freezes only the requested environment contract: `environment_policy_ref` and `environment_request_json`.
- Project-policy `environment_profiles` are enforced at compile time for `custom_profile` requests so undeclared profiles fail before runtime.
- Runtime launch behavior is deliberately staged:
  - `none` executes on the host runtime.
  - declared `custom_profile` requests are surfaced as delegated/manual-profile execution metadata.
  - unsupported `container` and `namespace` requests fall back to host execution when non-mandatory.
  - unsupported mandatory isolation requests fail the attempt immediately with durable environment-launch metadata.
- Attempt-level `execution_environment_json` is the canonical durable record of how the runtime interpreted the compiled request, including fallback or failure classification.

## Boundaries kept in place

- This slice does not add real container, namespace, or sandbox launchers.
- Launcher-specific operational config stays outside compiled YAML and outside the database schema for now.
- Environment selection remains declared from YAML and project policy; there is no interactive per-attempt override path in the CLI.

## Deferred work

- Real launcher implementations for container and namespace isolation remain deferred.
- Cleanup, teardown, and resource-accounting semantics for isolated environments remain deferred until a launcher exists.
- Profile-specific prompt guidance remains minimal because the current runtime only records delegated/manual-profile execution rather than driving a full launcher handshake.
