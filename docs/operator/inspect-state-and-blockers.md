---
doc_type: operator_guide
verified_against:
  - cli
  - flow_inventory
flow_ids:
  - 06_inspect_state_and_blockers_flow
command_paths:
  - node blockers
  - node audit
  - node events
  - workflow chain
  - workflow sources
  - node runs
  - tree show
  - yaml sources
  - yaml resolved
---

# Inspect State And Blockers

Use this guide when a node exists and you need to understand its durable state, blockers, workflow inputs, and audit trail.

## Core Inspection Commands

```bash
PYTHONPATH=src python3 -m aicoding.cli.main node audit --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main node events --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main node blockers --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main node runs --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main workflow chain --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main workflow sources --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main tree show --node <node_id> --full
PYTHONPATH=src python3 -m aicoding.cli.main yaml sources --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main yaml resolved --node <node_id>
```

## What To Look For

- `node audit`: durable reconstruction bundle for the node
- `node events`: lifecycle and runtime history
- `node blockers`: current persisted blocker reasons
- `node runs`: current and prior run records
- `workflow chain`: workflow/task/subtask progression
- `workflow sources` and `yaml ...`: compile inputs and resolved assets
- `tree show --full`: surrounding hierarchy state

## When To Escalate

Move to a runbook if:

- the node is paused or blocked and you need recovery guidance
- the session cannot be resumed cleanly
- the blocker suggests a human gate or intervention path

For that path, use `docs/runbooks/pause-resume-recovery.md`.
