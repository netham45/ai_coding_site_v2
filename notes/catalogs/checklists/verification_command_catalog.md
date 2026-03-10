# Verification Command Catalog

## Purpose

This note defines the canonical verification command families for the current repository state.

Use this file when a note, plan, checklist, or README needs to claim that a surface is verified.

Execution-policy companion:

- `notes/catalogs/checklists/e2e_execution_policy.md`

## Command Families

### Environment And Database Foundation

Use these to confirm local CLI access and migration-head alignment:

```bash
python3 -m aicoding.cli.main admin db ping
python3 -m aicoding.cli.main admin db heads
python3 -m aicoding.cli.main admin db upgrade
python3 -m aicoding.cli.main admin db check-schema
```

### Unit And Bounded Documentation Checks

Use these for fast bounded proof during documentation and planning changes:

```bash
python3 -m pytest tests/unit/test_document_schema_docs.py tests/unit/test_feature_checklist_docs.py tests/unit/test_feature_plan_docs.py tests/unit/test_task_plan_docs.py tests/unit/test_notes_quickstart_docs.py
```

### Unit Suite

Use this for the repository unit layer:

```bash
python3 -m pytest tests/unit
```

### Integration Suite

Use this for the repository integration layer:

```bash
python3 -m pytest tests/integration
```

### Flow Contract Suite

Use this to verify the current bounded flow-contract layer:

```bash
python3 -m pytest tests/integration/test_flow_contract_suite.py -q
```

### YAML Flow Asset Contract Suite

Use this to verify executable YAML flow assets separately from the markdown flow-contract suite:

```bash
python3 -m pytest tests/integration/test_flow_yaml_contract_suite.py -q
```

### Performance Suite

Use this for the current performance harness layer:

```bash
python3 -m pytest tests/performance/test_harness.py -q
```

### Real E2E Current Checkpoints

Use these commands for the currently implemented real E2E checkpoint set:

```bash
python3 -m pytest tests/e2e/test_flow_01_create_top_level_node_real.py -q
python3 -m pytest tests/e2e/test_flow_02_compile_or_recompile_workflow_real.py -q
python3 -m pytest tests/e2e/test_flow_03_materialize_and_schedule_children_real.py -q
python3 -m pytest tests/e2e/test_flow_04_manual_tree_edit_and_reconcile_real.py -q
python3 -m pytest tests/e2e/test_flow_05_admit_and_execute_node_run_real.py -q
python3 -m pytest tests/e2e/test_e2e_operator_cli_surface.py -q
python3 -m pytest tests/e2e/test_e2e_prompt_and_summary_history_real.py -q
python3 -m pytest tests/e2e/test_e2e_compile_variants_and_diagnostics.py -q
```

The current real-E2E harness now creates one database per test, so DB-backed execution no longer depends on a shared database fixture.

Remaining serialization, if any, should be driven by non-database resources such as tmux, provider credentials, or especially heavy workspace narratives.

See `notes/catalogs/checklists/e2e_execution_policy.md` for the local, CI, gated/manual, and release-readiness execution expectations around these commands.

### Real E2E Bring-Up Targets

Use these when bringing up larger real narratives that are intentionally expected to fail while runtime gaps are still being exposed:

```bash
python3 -m pytest tests/e2e/test_e2e_full_epic_tree_runtime_real.py -q
```

This command is for full-tree narrative bring-up only. It must not be used to claim `verified`, `flow_complete`, or `release_ready` until the planned mergeback, regeneration, and rebuild stages actually pass.

## Status Language Rule

These commands prove different layers.

- Passing a bounded or integration command may justify `implemented` or `verified` for that bounded layer only.
- Passing a real E2E command may justify `flow_complete` for the exact runtime narrative it proves.
- No command in this catalog may be used to claim `release_ready` by itself.

## Maintenance Rule

If a doc claims a surface is verified, flow-complete, or release-ready, it must either:

- cite one of the commands in this catalog
- or update this catalog in the same change to include the new canonical command
