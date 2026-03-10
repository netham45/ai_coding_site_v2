# Immutable Workflow Compilation Decisions

Date: 2026-03-08
Phase: `plan/features/07_F03_immutable_workflow_compilation.md`

## Decisions

1. The first compiler slice uses the authoritative node version as the compile target.
   The public mutation path is `workflow compile --node <id>`, which resolves the current authoritative version and compiles that version's captured source set.

2. Compile success and compile failure are both durable.
   Successful compiles persist immutable workflow/task/subtask rows and move the current workflow pointer on `node_versions.compiled_workflow_id`.
   Failed compiles persist a `compile_failures` record and clear the current workflow binding for that authoritative version.

3. Failed recompiles are treated as authoritative visibility changes, not transient warnings.
   The lifecycle surface moves to `COMPILE_FAILED` so the operator does not silently keep running against a stale compiled snapshot after the source set changed.

4. The initial compiled workflow graph is intentionally minimal.
   Because the built-in task/layout YAML is still scaffold-shaped, the first compiler emits one compiled task per resolved task definition and one `run_prompt` compiled subtask per compiled task, with sequential dependency edges between adjacent subtasks.

5. Prompt freezing happens at compile time.
   The compiler freezes the referenced node prompt template together with the node version prompt and task definition payload into compiled subtask prompt text so later prompt-asset edits do not change in-flight execution semantics.

## Deferred Work

- override resolution stages
- hook expansion stages
- rendered multi-subtask task payloads
- compile-by-version and candidate-version compile flows
- run-aware workflow chain state instead of structure-only chain output
