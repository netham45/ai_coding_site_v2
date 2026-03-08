# Phase F03-S1: Variable Substitution And Context Rendering

## Goal

Support invoker-driven variable substitution in YAML and prompt/command rendering, including forms such as `{{variable}}`.

## Scope

- Database: persist rendered-versus-source values where auditability requires it, especially for prompts and commands.
- CLI: expose enough source/rendered context to debug substitution results safely.
- Daemon: implement the rendering engine, variable precedence rules, missing-variable behavior, escaping, and safe render timing.
- YAML: add explicit schema support for invoker variables, renderable fields, and variable scope inheritance.
- Prompts: allow prompt assets and subtask fields to reference rendered variables deterministically.
- Tests: exhaustively cover substitution success, missing variables, shadowing, escaping, nested scopes, invoker inheritance, and illegal render targets.
- Performance: benchmark render cost during compile and stage startup.
- Notes: update schema, prompt, and code-vs-YAML notes to freeze rendering semantics.
