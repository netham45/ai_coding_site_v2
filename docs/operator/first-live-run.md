---
doc_type: operator_guide
verified_against:
  - cli
  - flow_inventory
flow_ids:
  - 01_create_top_level_node_flow
  - 05_admit_and_execute_node_run_flow
  - 06_inspect_state_and_blockers_flow
command_paths:
  - workflow start
  - node show
  - workflow current
  - workflow show
  - task current
  - subtask current
  - subtask prompt
  - subtask context
  - node audit
  - node events
  - session bind
  - session show-current
  - session show
  - session list
  - node run show
  - node recovery-status
---

# First Live Run

This guide walks an operator through the first live runtime narrative that matters in the current repository state: start a top-level node, inspect the compiled workflow, and bind or inspect the active session.

## 1. Start The Workflow

```bash
PYTHONPATH=src python3 -m aicoding.cli.main workflow start \
  --kind epic \
  --title "Operator First Run" \
  --prompt "Create a tiny greeting feature. Add a config file, generate a greeting artifact, add one repeatable verification command, and write a short summary."
```

Record the returned `node.node_id`.

## 2. Confirm The Runtime Surface

```bash
PYTHONPATH=src python3 -m aicoding.cli.main node show --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main node audit --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main node events --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main workflow current --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main workflow show --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main task current --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main subtask current --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main subtask prompt --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main subtask context --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main node run show --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main node recovery-status --node <node_id>
```

Use these reads to confirm:

- the top-level node exists
- the authoritative workflow compiled
- the current task and subtask are visible
- the current prompt surface is inspectable
- the active run is durably visible

## 3. Bind The Session If Needed

```bash
PYTHONPATH=src python3 -m aicoding.cli.main session bind --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main session show-current
PYTHONPATH=src python3 -m aicoding.cli.main session show --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main session list --node <node_id>
```

This path is appropriate when the daemon and session backend are available and you want an active bound session rather than inspection only.

## 4. Continue With Detailed Inspection

For blocker-focused inspection, continue with `docs/operator/inspect-state-and-blockers.md`.
