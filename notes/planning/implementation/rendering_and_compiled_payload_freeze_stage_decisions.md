# Rendering And Compiled Payload Freeze Stage Decisions

## Decision

Phase `55_F03_rendering_and_compiled_payload_freeze_stage` is implemented as an explicit read surface over the frozen rendering payload already stored in `compiled_workflows.resolved_yaml.rendering`.

## Why

- compile-time rendering is already authoritative in the daemon and already freezes rendered prompt or command payloads into compiled subtasks
- a dedicated stage-inspection command makes the rendered artifacts auditable without requiring callers to parse the full compiled workflow blob
- keeping the stage read-only avoids introducing duplicate persistence for already-frozen data

## Implementation Shape

- daemon endpoints:
  - `GET /api/nodes/{id}/workflow/rendering`
  - `GET /api/workflows/{id}/rendering`
- CLI command:
  - `ai-tool workflow rendering --node <id>|--workflow <id>`
- payload includes:
  - canonical and legacy syntax flags
  - frozen compiled-subtask rendering payloads
  - compiled-subtask count

## Deliberate Non-Changes

- no new database schema was needed for this phase
- render semantics remain owned by the shared renderer and the compile pipeline; this phase only exposes the frozen result
