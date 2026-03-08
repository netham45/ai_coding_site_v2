# Phase F03-S5: Hook Expansion And Policy Resolution Compile Stage

## Goal

Implement hook expansion and policy resolution as explicit compile stages.

## Scope

- Database: persist hook-selection and policy-resolution diagnostics where needed.
- CLI: inspect hook expansion and effective policy in compile output.
- Daemon: run policy folding and deterministic hook expansion before final workflow assembly.
- YAML: support hook and policy definitions with explicit applicability and ordering semantics.
- Prompts: ensure prompt-bearing hooks resolve safely.
- Tests: exhaustively cover hook applicability, ordering, policy fold-in, and expansion rejection.
- Performance: benchmark compile overhead from hook and policy processing.
- Notes: update hook/policy notes when implementation freezes stage ordering.
