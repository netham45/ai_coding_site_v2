---
doc_type: operator_guide
verified_against:
  - cli
  - flow_inventory
flow_ids:
  - 09_run_quality_gates_flow
  - 11_finalize_and_merge_flow
  - 12_query_provenance_and_docs_flow
command_paths:
  - node validate
  - review run
  - review show
  - testing run
  - testing show
  - node quality-chain
  - node provenance-refresh
  - docs build-node-view
  - docs build-tree
  - docs list
  - docs show
  - rationale show
  - entity show
  - entity history
  - entity relations
  - entity changed-by
  - git finalize-node
  - git merge-children
  - git merge-events show
  - git final show
---

# Quality, Provenance, And Finalize

Use this guide after implementation work has progressed far enough to run quality gates, refresh provenance, inspect durable docs outputs, and finalize or merge the authoritative result.

## Run Or Inspect Quality Gates

```bash
PYTHONPATH=src python3 -m aicoding.cli.main node validate --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main review run --node <node_id> --status pass --summary "review passed"
PYTHONPATH=src python3 -m aicoding.cli.main review show --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main testing run --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main testing show --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main node quality-chain --node <node_id>
```

Use the individual commands when you need a specific gate outcome. Use `node quality-chain` when the built-in validation, review, testing, provenance, docs, and finalize chain is the correct operator action for the active run.

## Refresh Provenance And Inspect Durable Docs

```bash
PYTHONPATH=src python3 -m aicoding.cli.main node provenance-refresh --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main docs build-node-view --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main docs build-tree --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main docs list --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main docs show --node <node_id> --scope local
```

This path refreshes durable provenance/rationale mappings and then inspects the node-local or merged documentation outputs the daemon knows about.

## Query Rationale And Entity History

```bash
PYTHONPATH=src python3 -m aicoding.cli.main rationale show --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main entity show --name <canonical_entity_name>
PYTHONPATH=src python3 -m aicoding.cli.main entity history --name <canonical_entity_name>
PYTHONPATH=src python3 -m aicoding.cli.main entity relations --name <canonical_entity_name>
PYTHONPATH=src python3 -m aicoding.cli.main entity changed-by --name <canonical_entity_name>
```

Use these commands when you need the provenance trail behind a node change or need to inspect which node versions changed a specific code entity.

## Finalize Or Merge The Authoritative Result

```bash
PYTHONPATH=src python3 -m aicoding.cli.main git finalize-node --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main git final show --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main git merge-children --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main git merge-events show --node <node_id>
```

Use finalize only after the node is ready for a real live finalize commit. Use the merge commands to inspect or execute the deterministic parent merge path once child finals are available.
