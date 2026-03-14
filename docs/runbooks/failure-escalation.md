---
doc_type: runbook
verified_against:
  - cli
  - flow_inventory
flow_ids:
  - 08_handle_failure_and_escalate_flow
  - 13_human_gate_and_intervention_flow
command_paths:
  - node child-failures
  - node respond-to-child-failure
  - node events
  - node interventions
  - node intervention-apply
  - session nudge
  - session recover
  - session provider-resume
  - node recovery-status
  - node recovery-provider-status
---

# Failure And Escalation Runbook

Use this runbook when a node, child, or active session fails in a way that requires operator intervention rather than a simple pause/resume cycle.

## Inspect The Failure Surface First

```bash
PYTHONPATH=src python3 -m aicoding.cli.main node child-failures --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main node events --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main node interventions --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main node recovery-status --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main node recovery-provider-status --node <node_id>
```

Do not guess which path to take. Inspect the durable failure counters, event history, intervention items, and recovery classification first.

## Nudge Or Recover The Session

```bash
PYTHONPATH=src python3 -m aicoding.cli.main session nudge --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main session recover --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main session provider-resume --node <node_id>
```

Use `session nudge` when the session looks idle but not clearly dead. Use `recover` or `provider-resume` only after confirming the recovery classification supports that path.

## Apply A Parent Decision For Child Failure

```bash
PYTHONPATH=src python3 -m aicoding.cli.main node respond-to-child-failure \
  --node <node_id> \
  --child <child_node_id> \
  --action retry_child
```

Allowed actions are:

- `retry_child`
- `regenerate_child`
- `replan_parent`
- `pause_for_user`

Choose the action that matches the durable intervention reason rather than the most convenient retry.

## Apply Explicit Human Intervention

```bash
PYTHONPATH=src python3 -m aicoding.cli.main node intervention-apply \
  --node <node_id> \
  --kind <intervention_kind> \
  --action <action_name> \
  --summary "Operator rationale for the intervention"
```

Use this path when the node already exposes a concrete intervention item. The summary should explain why the chosen action is safe and sufficient.
