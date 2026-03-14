---
doc_type: operator_guide
verified_against:
  - cli
  - flow_inventory
flow_ids:
  - 03_materialize_and_schedule_children_flow
  - 04_manual_tree_edit_and_reconcile_flow
  - 10_regenerate_and_rectify_flow
command_paths:
  - node child create
  - node children
  - node child-materialization
  - node register-layout
  - node materialize-children
  - node child-reconciliation
  - node reconcile-children
  - node child-results
  - node reconcile
  - node regenerate
  - node rectify-upstream
  - node rebuild-history
  - node rebuild-coordination
  - node version cutover-readiness
  - tree show
  - rebuild show
---

# Tree Materialization And Rebuild

Use this guide when you are creating children, mixing manual edits with layout-managed structure, or rebuilding a subtree after the authoritative version changes.

## Inspect The Current Tree And Child State

```bash
PYTHONPATH=src python3 -m aicoding.cli.main tree show --node <node_id> --full
PYTHONPATH=src python3 -m aicoding.cli.main node children --node <node_id> --versions
PYTHONPATH=src python3 -m aicoding.cli.main node child-materialization --node <node_id>
```

Start here before making structural changes. These commands show the current subtree, authoritative child versions, and layout-driven materialization state.

## Add Manual Children Or Materialize A Registered Layout

```bash
PYTHONPATH=src python3 -m aicoding.cli.main node child create \
  --parent <node_id> \
  --kind task \
  --title "Child title" \
  --prompt "Describe the child work."

PYTHONPATH=src python3 -m aicoding.cli.main node register-layout --node <node_id> --file <layout_file>
PYTHONPATH=src python3 -m aicoding.cli.main node materialize-children --node <node_id>
```

Use `node child create` for explicit manual authority. Use `register-layout` plus `materialize-children` when the parent is following a generated layout path.

## Reconcile Manual And Layout Authority

```bash
PYTHONPATH=src python3 -m aicoding.cli.main node child-reconciliation --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main node reconcile-children --node <node_id> --decision preserve_manual
PYTHONPATH=src python3 -m aicoding.cli.main node child-results --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main node reconcile --node <node_id>
```

These commands are the operator surface for hybrid trees. Inspect reconciliation choices first, then apply an explicit decision instead of relying on silent overwrite behavior.

## Regenerate Or Rectify The Tree

```bash
PYTHONPATH=src python3 -m aicoding.cli.main node regenerate --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main node rectify-upstream --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main node rebuild-history --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main node rebuild-coordination --node <node_id> --scope subtree
PYTHONPATH=src python3 -m aicoding.cli.main rebuild show --node <node_id>
```

Use `regenerate` to create and compile a candidate subtree rebuild. Use `rectify-upstream` when the rebuild must propagate through ancestors. Inspect history and coordination blockers before assuming cutover is ready.

## Check Candidate Readiness Before Promotion

```bash
PYTHONPATH=src python3 -m aicoding.cli.main node version cutover-readiness --version <version_id>
```

Promotion readiness must be explicit. Do not treat a generated candidate as authoritative until the cutover-readiness surface shows the expected blockers are cleared.
