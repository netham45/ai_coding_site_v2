# Checklist C03: Stage Design And Runtime Verification

## Goal

Verify that the implemented runtime matches the intended behavior across every stage.

## Verify

- stage startup context includes required dependency and child summaries
- every stage has correct prompt/context/validation wiring
- pause/failure/retry/recovery behavior matches the notes
- tmux/session integration, heartbeat handling, idle detection, and recovery behave as designed
- child-session and child-node flows preserve ownership correctly

## Tests

- exhaustive stage-by-stage runtime tests
- exhaustive pause/failure/recovery tests
- performance checks for hot runtime loops and idle/recovery paths

## Notes

- update runtime/session/recovery notes if any stage behavior differs in practice
