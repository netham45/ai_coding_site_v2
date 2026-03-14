---
doc_type: operator_guide
verified_against:
  - cli
  - flow_inventory
flow_ids:
  - 02_compile_or_recompile_workflow_flow
command_paths:
  - workflow current
  - workflow show
  - workflow chain
  - workflow sources
  - workflow source-discovery
  - workflow schema-validation
  - workflow override-resolution
  - workflow hook-policy
  - workflow hooks
  - workflow rendering
  - workflow compile
  - workflow compile-failures
  - yaml sources
  - yaml resolved
  - yaml effective-policy
  - yaml override-chain
---

# Compile And YAML Inspection

Use this guide when you need to understand which workflow was compiled for a node, where it came from, and why the compiler resolved policies or overrides the way it did.

## Start From The Current Workflow Binding

```bash
PYTHONPATH=src python3 -m aicoding.cli.main workflow current --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main workflow show --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main workflow chain --node <node_id>
```

Use `workflow current` first to confirm the authoritative workflow id bound to the node. Then use `workflow show` and `workflow chain` to inspect the compiled tasks and subtask order for that specific workflow snapshot.

## Inspect Compile Inputs

```bash
PYTHONPATH=src python3 -m aicoding.cli.main workflow sources --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main workflow source-discovery --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main workflow schema-validation --node <node_id>
```

These commands answer three different questions:

- `workflow sources`: which source artifacts were captured for the compiled workflow
- `workflow source-discovery`: how the compiler found those inputs
- `workflow schema-validation`: which schema families and validation passes were applied during compile

## Inspect Policy Folding And Override Resolution

```bash
PYTHONPATH=src python3 -m aicoding.cli.main workflow override-resolution --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main workflow hook-policy --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main workflow hooks --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main workflow rendering --node <node_id>
```

Use this set when the compiled workflow shape does not match expectation. The output should make it clear whether the difference came from override precedence, policy folding, hook expansion, or rendering-time payload freezing.

## Inspect YAML Inputs Directly

```bash
PYTHONPATH=src python3 -m aicoding.cli.main yaml sources --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main yaml resolved --node <node_id> --family tasks
PYTHONPATH=src python3 -m aicoding.cli.main yaml effective-policy
PYTHONPATH=src python3 -m aicoding.cli.main yaml override-chain --node <node_id>
```

Use the YAML group when you need the source-side or resolved-document view rather than the workflow-side compile diagnostics.

## Recompile Or Inspect Compile Failures

```bash
PYTHONPATH=src python3 -m aicoding.cli.main workflow compile --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main workflow compile-failures --node <node_id>
```

`workflow compile` is the explicit recompile entrypoint for an authoritative node or candidate version. If compile fails, inspect durable failure output instead of assuming the failure is only visible in transient logs.
