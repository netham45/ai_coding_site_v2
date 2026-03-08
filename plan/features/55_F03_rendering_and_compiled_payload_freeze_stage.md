# Phase F03-S6: Rendering And Compiled Payload Freeze Stage

## Goal

Render variables/placeholders and freeze prompt/command payloads into compiled artifacts.

## Scope

- Database: persist rendered versus source payloads where auditability requires it.
- CLI: expose rendered compile outputs for inspection/debugging.
- Daemon: render prompts, commands, args, env, and related payload fields during compile or stage-assembly at the correct boundary.
- YAML: mark or define renderable fields and substitution rules.
- Prompts: freeze rendered prompt payloads and placeholder bindings deterministically.
- Tests: exhaustively cover render timing, placeholder substitution, missing data, and frozen payload reproducibility.
- Performance: benchmark rendering overhead during compile and stage assembly.
- Notes: update rendering and prompt notes when semantics are frozen.
