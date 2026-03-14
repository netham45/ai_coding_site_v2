---
doc_type: runbook
verified_against:
  - cli
  - flow_inventory
flow_ids:
  - 07_pause_resume_and_recover_flow
  - 13_human_gate_and_intervention_flow
command_paths:
  - node pause
  - node resume
  - node pause-state
  - node recovery-status
  - node recovery-provider-status
  - session recover
  - session provider-resume
  - node interventions
  - node approve
---

# Pause, Resume, And Recovery Runbook

Use this runbook when a node is paused, blocked for intervention, or requires session recovery.

## Inspect Before Acting

```bash
PYTHONPATH=src python3 -m aicoding.cli.main node pause-state --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main node recovery-status --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main node recovery-provider-status --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main node interventions --node <node_id>
```

## Pause Or Resume The Node

```bash
PYTHONPATH=src python3 -m aicoding.cli.main node pause --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main node resume --node <node_id>
```

## Run Session Recovery

```bash
PYTHONPATH=src python3 -m aicoding.cli.main session recover --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main session provider-resume --node <node_id>
```

Use `provider-resume` only when provider-aware recovery is appropriate and restorable.

## Human Gate Path

If the node is user-gated or intervention-gated:

```bash
PYTHONPATH=src python3 -m aicoding.cli.main node approve --node <node_id>
```

Only use approval after confirming the pause/intervention reason through the inspection commands above.
