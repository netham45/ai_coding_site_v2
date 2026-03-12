# Verification Command Catalog

## Purpose

This note defines the canonical verification command families for the current repository state.

Use this file when a note, plan, checklist, or README needs to claim that a surface is verified.

Parallel-safe execution is the repository expectation for every test layer in this catalog.

Serial commands remain useful for local debugging and staged bring-up, but they do not imply that serial-only test behavior is acceptable.

A test or suite that fails only because it is run in parallel is defective until the isolation issue is fixed or the environment-capability gate is documented explicitly.

Execution-policy companion:

- `notes/catalogs/checklists/e2e_execution_policy.md`

## Command Families

### Root Shell Wrappers

Use these when you want the documented repo commands behind stable root-level `.sh` entrypoints:

```bash
./scripts/upgrade-db.sh
./scripts/downgrade-db.sh
./scripts/rebuild.sh
./scripts/reset-db.sh --yes
./scripts/run-node-dev.sh
./scripts/run-server.sh
./scripts/test-unit.sh
./scripts/test-integration.sh
./scripts/test-e2e.sh
./scripts/test-all.sh
```

These wrappers are convenience entrypoints. The underlying commands below remain the canonical behavior they must track.

### Environment And Database Foundation

Use these to confirm local CLI access and migration-head alignment:

```bash
PYTHONPATH=src python3 -m aicoding.cli.main admin db ping
PYTHONPATH=src python3 -m aicoding.cli.main admin db heads
PYTHONPATH=src python3 -m aicoding.cli.main admin db upgrade
PYTHONPATH=src python3 -m aicoding.cli.main admin db check-schema
```

### Unit And Bounded Documentation Checks

Use these for fast bounded proof during documentation and planning changes:

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_feature_checklist_docs.py tests/unit/test_feature_plan_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_notes_quickstart_docs.py
```

### Unit Suite

Use this for the repository unit layer:

```bash
PYTHONPATH=src python3 -m pytest tests/unit
```

### Integration Suite

Use this for the repository integration layer:

```bash
PYTHONPATH=src python3 -m pytest tests/integration
```

### Flow Contract Suite

Use this to verify the current bounded flow-contract layer:

```bash
PYTHONPATH=src python3 -m pytest tests/integration/test_flow_contract_suite.py -q
```

### YAML Flow Asset Contract Suite

Use this to verify executable YAML flow assets separately from the markdown flow-contract suite:

```bash
PYTHONPATH=src python3 -m pytest tests/integration/test_flow_yaml_contract_suite.py -q
```

### Performance Suite

Use this for the current performance harness layer:

```bash
PYTHONPATH=src python3 -m pytest tests/performance/test_harness.py -q
```

### Parallel Bounded Smoke

Use this to prove that unit, integration, and performance suites can execute concurrently without shared database-fixture contention:

```bash
PYTHONPATH=src python3 -m pytest tests/unit tests/integration tests/performance -n auto --dist=loadfile -q
```

This command is a normative bounded-layer contract check, not a release-readiness claim by itself.

### Real E2E Current Checkpoints

Use these commands only for the currently passing full-real E2E checkpoint set:

```bash
PYTHONPATH=src python3 -m pytest tests/e2e/test_web_project_top_level_bootstrap_real.py -q
PYTHONPATH=src python3 -m pytest tests/e2e/test_web_project_top_level_browser_real.py -q
PYTHONPATH=src python3 -m pytest tests/e2e/test_flow_01_create_top_level_node_real.py -q
PYTHONPATH=src python3 -m pytest tests/e2e/test_flow_02_compile_or_recompile_workflow_real.py -q
PYTHONPATH=src python3 -m pytest tests/e2e/test_flow_03_materialize_and_schedule_children_real.py -q
PYTHONPATH=src python3 -m pytest tests/e2e/test_flow_04_manual_tree_edit_and_reconcile_real.py -q
PYTHONPATH=src python3 -m pytest tests/e2e/test_flow_05_admit_and_execute_node_run_real.py -q
PYTHONPATH=src python3 -m pytest tests/e2e/test_e2e_operator_cli_surface.py -q
PYTHONPATH=src python3 -m pytest tests/e2e/test_e2e_prompt_and_summary_history_real.py -q
PYTHONPATH=src python3 -m pytest tests/e2e/test_e2e_compile_variants_and_diagnostics.py -q
PYTHONPATH=src python3 -m pytest tests/e2e/test_e2e_live_git_merge_and_finalize_real.py -q
```

Current git-proof caveat:

- `tests/e2e/test_web_project_top_level_browser_real.py` now proves the real browser flow against the daemon-served frontend for project selection, inline top-level creation, success redirect, and repo-backed bootstrap inspection through CLI/API surfaces.
- `tests/e2e/test_flow_11_finalize_and_merge_real.py` proves the shipped live bootstrap, merge, finalize, merge-event, and git-status path.
- `tests/e2e/test_e2e_live_git_merge_and_finalize_real.py` now also proves merged parent-repo file contents on disk after a clean multi-child merge and finalize, rerun reset/replay of current child finals on the parent merge tier, and abort-to-seed rollback after a live merge conflict.
- `tests/e2e/test_e2e_full_epic_tree_runtime_real.py` and `tests/e2e/test_e2e_incremental_parent_merge_real.py` are currently quarantined from this canonical checkpoint set because they still include synthetic workflow progression or other non-live-run-equivalent steps in at least part of their narrative.
- The repo must not treat hierarchy-wide live AI descent, incremental parent merge, or rebuild/cutover coordination as canonical passing real E2E until those suites satisfy the live-run-equivalence rule from `AGENTS.md`.

The current real-E2E harness now creates one database per test, so DB-backed execution no longer depends on a shared database fixture.

Any remaining inability to run eligible tests in parallel is an open defect unless it is explained by explicit environment-capability gating.

See `notes/catalogs/checklists/e2e_execution_policy.md` for the local, CI, gated/manual, and release-readiness execution expectations around these commands.

### Real E2E Bring-Up Targets

Use these when bringing up larger real narratives that still expose runtime gaps or
still contain synthetic workflow steps that prevent canonical E2E status:

```bash
python3 -m pytest tests/e2e/test_e2e_full_epic_tree_runtime_real.py -q
python3 -m pytest tests/e2e/test_e2e_automated_full_tree_cat_runtime_real.py -q
python3 -m pytest tests/e2e/test_flow_21_child_session_round_trip_and_mergeback_real.py -q
python3 -m pytest tests/e2e/test_e2e_incremental_parent_merge_real.py -q
python3 -m pytest tests/e2e/test_e2e_rebuild_cutover_coordination_real.py -q
python3 -m pytest tests/e2e/test_tmux_codex_idle_nudge_real.py -q
```

These commands must not be used to claim `verified`, `flow_complete`, or `release_ready` until the exact workflow passes with no synthetic workflow steps.

### Parallel All-Tests Meta-Verifier Bring-Up

Use this gated meta-test to recurse into the eligible `tests/` surface and run the child suite in parallel:

```bash
AICODING_ENABLE_META_PARALLEL_TEST=1 PYTHONPATH=src python3 -m pytest tests/integration/test_parallel_all_tests_meta.py -q
```

This is the current bring-up target for the repository-wide parallel test architecture.

- it excludes itself from the child run
- it filters marker-gated tests based on available capabilities
- it must not be treated as a passing default-local command until the underlying suite is green
- once the underlying suite is green, it becomes the authoritative proof that all eligible tests can run together in parallel

## Status Language Rule

These commands prove different layers.

- Passing a bounded or integration command may justify `implemented` or `verified` for that bounded layer only.
- Passing a real E2E command may justify `flow_complete` for the exact runtime narrative it proves.
- No command in this catalog may be used to claim `release_ready` by itself.

## Maintenance Rule

If a doc claims a surface is verified, flow-complete, or release-ready, it must either:

- cite one of the commands in this catalog
- or update this catalog in the same change to include the new canonical command

If a doc introduces a test command or suite that is expected to remain serial-only because of shared-state interference, the doctrine and implementation notes must be updated immediately because that is a correctness gap, not an invisible local convention.
