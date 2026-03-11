# YAML Schema And Field Rigidity Priority 3 Phase 2 Family Rigidity Note

## Purpose

This note records the Phase 2 implementation slice for `plan/tasks/2026-03-11_yaml_schema_and_field_rigidity_priority3.md`.

The goal of this phase is to add the missing authored-family rigidity layer for the deferred Priority 3 families without inventing new runtime behavior.

## Implemented Changes

### 1. Hook schema-negative and authored-library hardening

The hook schema layer now explicitly rejects:

- blank `when`
- `run_prompt` hook steps without a non-empty `prompt`
- `validate` hook steps without a non-empty `command`
- `run_command` hook steps without a non-empty `command`

This closes a real schema-level gap. Those requirements were already implicit in the authored built-ins and operational-library checks, but they were not enforced directly by the hook validator model.

The authored-library layer now also iterates every built-in hook document and asserts:

- validation passes
- ids are unique
- `when` is non-blank
- run-step types are non-blank
- prompt-bearing run steps actually declare prompts
- command-bearing run steps actually declare commands

### 2. Runtime-policy authored-library rigidity

The runtime-policy family already had schema-level uniqueness validation for its ref buckets and real policy-resolution/runtime proof.

This phase adds the missing authored-library loop that asserts for every built-in `runtime_policy_definition`:

- validation passes
- ids are unique
- `defaults` is non-empty
- each ref bucket remains unique

This is intentionally narrower than a new runtime-policy integration suite because effective-policy/runtime coverage already exists.

### 3. Testing authored-library rigidity

The testing family already had:

- schema validation
- quality-library checks
- testing runtime/result-routing proof

This phase adds the missing authored-library loop that asserts for every built-in testing definition:

- validation passes
- ids are unique
- `scope` is non-blank
- every command has non-blank `command` and `working_directory`
- `on_result.pass_action` and `on_result.fail_action` are non-blank

The schema-negative matrix was also widened with:

- empty `working_directory`

### 4. Docs authored-library rigidity

The docs family already had:

- schema validation
- quality-library checks
- docs runtime build/list/show proof

This phase adds the missing authored-library loop that asserts for every built-in docs definition:

- validation passes
- ids are unique
- `scope` is non-blank
- outputs are present
- every output has non-blank `path` and `view`

The schema-negative matrix was also widened with:

- blank output `view`

## Why This Is The Right Layer

This phase intentionally stays at the schema-negative and authored-family-library layers because that was the still-missing proof.

It does not:

- add a new per-file test for every asset
- replace grouped operational or quality library checks
- duplicate the existing daemon/runtime testing and docs execution coverage
- invent new CLI or daemon commands

## Remaining Phase Boundary

The remaining question for this task is only whether a targeted DB-backed integration recheck is still needed after the hook schema-model hardening.

The current best read is:

- runtime-sensitive proof already exists for hooks, runtime policies, testing, and docs
- a final DB-backed recheck should still be run for this task when the shared test database is idle, because the task changed `validate_yaml_document(...)` behavior through the hook validator model

## Next Step

Phase 3 should rerun the relevant existing DB-backed integration surfaces once the shared test database is not in use by unrelated pytest jobs, then close the task honestly as `complete` or leave it `partial` if that recheck cannot be performed.
