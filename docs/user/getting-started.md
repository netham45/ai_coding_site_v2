---
doc_type: user_guide
verified_against:
  - cli
  - config
flow_ids:
  - 01_create_top_level_node_flow
  - 05_admit_and_execute_node_run_flow
command_paths:
  - admin doctor
  - admin print-settings
  - admin auth-token
  - admin db ping
  - admin db upgrade
  - admin db check-schema
  - admin daemon-boundary
  - debug daemon ping
  - debug daemon boundary
  - workflow start
  - node show
  - node audit
  - node events
  - workflow current
  - task current
  - subtask current
  - subtask prompt
  - session show-current
config_fields:
  - database_url
  - daemon_host
  - daemon_port
  - auth_token_file
  - session_backend
---

# Getting Started

Use this guide to bring up the repository locally, start the daemon, create one top-level workflow, and inspect the resulting durable state.

## Prerequisites

- Python virtual environment
- PostgreSQL reachable through `AICODING_DATABASE_URL`
- repository checkout root as the current working directory

## Bootstrap The Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
PYTHONPATH=src python3 -m aicoding.cli.main admin doctor
PYTHONPATH=src python3 -m aicoding.cli.main admin print-settings
PYTHONPATH=src python3 -m aicoding.cli.main admin auth-token
PYTHONPATH=src python3 -m aicoding.cli.main admin db ping
PYTHONPATH=src python3 -m aicoding.cli.main admin db upgrade
PYTHONPATH=src python3 -m aicoding.cli.main admin db check-schema
```

Current important defaults:

- the daemon base URL is derived from `AICODING_DAEMON_HOST` and `AICODING_DAEMON_PORT`
- the daemon token file defaults to `.runtime/daemon.token`
- the default session backend is `tmux`

## Start The Daemon

```bash
PYTHONPATH=src python3 -m aicoding.daemon.main
```

Equivalent development command:

```bash
uvicorn aicoding.daemon.app:create_app --factory --reload
```

Useful first daemon inspections:

```bash
PYTHONPATH=src python3 -m aicoding.cli.main admin daemon-boundary
PYTHONPATH=src python3 -m aicoding.cli.main debug daemon ping
PYTHONPATH=src python3 -m aicoding.cli.main debug daemon boundary
```

## Start A Top-Level Workflow

```bash
PYTHONPATH=src python3 -m aicoding.cli.main workflow start \
  --kind epic \
  --title "Hello World Epic" \
  --prompt "Create a tiny greeting feature. Add a config file, generate a greeting artifact, add one repeatable verification command, and write a short summary."
```

Capture the returned `node.node_id`. You will use it for the read-side inspection commands below.

## Inspect The Result

```bash
PYTHONPATH=src python3 -m aicoding.cli.main node show --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main node audit --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main node events --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main workflow current --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main task current --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main subtask current --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main subtask prompt --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main session show-current
```

If you want the more detailed operator flow, continue with:

- `docs/operator/first-live-run.md`
- `docs/operator/inspect-state-and-blockers.md`

## Transitional Note

The older walkthrough in `notes/scenarios/walkthroughs/getting_started_hypothetical_task_guide.md` is now a historical migration pointer. This file is the primary getting-started entrypoint.
