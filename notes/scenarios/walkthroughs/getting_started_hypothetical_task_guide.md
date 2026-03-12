# Getting Started: First Daemon, First Workflow, First Inspection

## Purpose

This walkthrough is the current operator-facing getting-started path for the live repository state.

It is not "print hello in a terminal." The current hello world for this system is:

- create a top-level node from a prompt
- compile an immutable workflow
- start a durable run
- inspect the current workflow, task, and subtask
- optionally bind a session
- inspect or drive progress through the command loop

## Current hierarchy

The current default built-in ladder is:

- `epic` -> defaults to creating `phase` children
- `phase` -> defaults to creating `plan` children
- `plan` -> defaults to creating `task` children
- `task` -> default leaf implementation node

Doctrinal rule:

- top-ness is defined only by the absence of a parent node
- a user should be able to create a node of any kind as a top node when the hierarchy definition for that kind allows `allow_parentless: true`

Current implementation mismatch:

- the shipped built-in YAML and workflow-start path still expose only `epic` as parentless today
- treat that as a current reconciliation gap in the packaged hierarchy, not as the intended long-term rule for the system

## What "hello world" should be

Use one small prompt that is concrete enough to compile and inspect:

> Create a tiny greeting feature. Add a config file, generate a greeting artifact, add one repeatable verification command, and write a short summary.

That is enough to exercise prompt capture, compiled workflow state, session bootstrap, and subtask inspection.

## Prerequisites

Set up the orchestrator repo and database first:

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

Important current constraint:

- the admin/bootstrap commands above must be run from the orchestrator checkout root
- `admin db upgrade` depends on the local Alembic config in that repo and does not currently work from an arbitrary target repo directory
- `admin auth-token` reports whether the CLI will read the bearer token from `.runtime/daemon.token` or from `AICODING_AUTH_TOKEN`

Required local environment posture:

- `AICODING_DATABASE_URL` must point at a PostgreSQL database
- the daemon and CLI both read `.env` through `src/aicoding/config.py`
- the default daemon base URL is `http://127.0.0.1:8000`
- the default auth token file is `.runtime/daemon.token`
- the application default session backend is `tmux`
- the shared pytest harness currently forces `AICODING_SESSION_BACKEND=fake` for bounded tests

All commands below use the current CLI entrypoint:

```bash
PYTHONPATH=src python3 -m aicoding.cli.main ...
```

## Current verification status

The current getting-started path has live real-E2E proof for:

- `workflow start`
- read-side inspection with `node`, `workflow`, `task`, `subtask`, `tree`, `yaml`, and `node runs`
- operator pause and audit inspection
- tmux-backed `session bind` when the required environment capabilities are present

The guide still needs to distinguish that from broader write-path claims:

- bounded and integration tests cover manual progress commands such as `subtask start|heartbeat|complete|fail|succeed`, `subtask report-command`, and `workflow advance`
- real E2E proof today is stronger for daemon-driven live session progress than for an operator manually stepping every one of those mutations in a single narrative

## Phase 0: Start the daemon

Run the daemon in a separate shell after the database checks pass:

```bash
PYTHONPATH=src python3 -m aicoding.daemon.main
```

Equivalent development command:

```bash
uvicorn aicoding.daemon.app:create_app --factory --reload
```

What happens on startup:

- the daemon loads `.env` through `aicoding.config.Settings`
- it checks the database schema compatibility during app lifespan startup
- it creates or reuses the local bearer-token file at `.runtime/daemon.token`
- it starts the background loops that currently handle idle nudging and child auto-start

Useful first inspections once it is running:

```bash
PYTHONPATH=src python3 -m aicoding.cli.main admin daemon-boundary
PYTHONPATH=src python3 -m aicoding.cli.main debug daemon ping
PYTHONPATH=src python3 -m aicoding.cli.main debug daemon boundary
```

What you should expect:

- the CLI should now be able to reach the daemon at the configured host and port
- the CLI and daemon should agree on the token file path
- `debug daemon ping` should confirm the daemon health endpoint is reachable

## Phase 1: Start a top-level workflow

The real top-level hello-world entrypoint is:

```bash
PYTHONPATH=src python3 -m aicoding.cli.main workflow start \
  --kind epic \
  --title "Hello World Epic" \
  --prompt "Create a tiny greeting feature. Add a config file, generate a greeting artifact, add one repeatable verification command, and write a short summary."
```

What this does:

- creates the top-level node
- captures the source prompt
- compiles the authoritative workflow
- starts the first run unless you pass `--no-run`

What to capture from the response:

- `node.node_id`
- `node_version_id`
- `run_progress.run.id` if you started a run
- `run_progress.run.run_status`, which should normally be `RUNNING`

If you want compile-only startup:

```bash
python3 -m aicoding.cli.main workflow start \
  --kind epic \
  --title "Hello World Epic" \
  --prompt "Create a tiny greeting feature." \
  --no-run
```

## Phase 2: Inspect what got created

Take the `node_id` from `workflow start` and query it directly.

Core inspection commands:

```bash
python3 -m aicoding.cli.main node show --node <node_id>
python3 -m aicoding.cli.main node audit --node <node_id>
python3 -m aicoding.cli.main node events --node <node_id>
python3 -m aicoding.cli.main workflow current --node <node_id>
python3 -m aicoding.cli.main workflow show --node <node_id>
python3 -m aicoding.cli.main workflow chain --node <node_id>
python3 -m aicoding.cli.main workflow sources --node <node_id>
python3 -m aicoding.cli.main workflow hook-policy --node <node_id>
python3 -m aicoding.cli.main task current --node <node_id>
python3 -m aicoding.cli.main subtask current --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main subtask prompt --node <node_id>
python3 -m aicoding.cli.main subtask context --node <node_id>
python3 -m aicoding.cli.main prompts history --node <node_id>
python3 -m aicoding.cli.main summary history --node <node_id>
python3 -m aicoding.cli.main node runs --node <node_id>
python3 -m aicoding.cli.main node blockers --node <node_id>
python3 -m aicoding.cli.main yaml sources --node <node_id>
python3 -m aicoding.cli.main yaml resolved --node <node_id>
python3 -m aicoding.cli.main tree show --node <node_id> --full
```

Use these reads to answer:

- what node exists
- whether the workflow compiled
- which task is active
- which subtask is current
- what prompt the current subtask received
- what context the daemon assembled for stage startup
- which YAML and prompt assets contributed to the compile
- what durable events and audit records exist already
- whether anything is blocked

## Phase 3: Bind or inspect the active session

If the workflow was started with a run, you have two different session cases.

Case 1: inspection only, no active shell context yet.

Use node/run inspection alone:

```bash
python3 -m aicoding.cli.main node run show --node <node_id>
python3 -m aicoding.cli.main node recovery-status --node <node_id>
```

Case 2: you want a bound session.

If `AICODING_SESSION_BACKEND=tmux` and the required runtime capabilities are available, bind a primary session:

```bash
python3 -m aicoding.cli.main session bind --node <node_id>
python3 -m aicoding.cli.main session show-current
python3 -m aicoding.cli.main session show --node <node_id>
python3 -m aicoding.cli.main session list --node <node_id>
```

Bootstrap rule from the runtime notes:

- `session show-current` is the first safe read for an active shell
- it tells you the bound node, run status, and recovery classification
- after that, read `workflow current`, `subtask current`, `subtask prompt`, and `subtask context` with the node id it returned

Important practical distinction:

- `session show-current` is about the currently bound harness session for the shell you are in
- `session show --node <node_id>` is the operator read for the durable session attached to that node
- if you are only learning the workflow model, you can skip live session binding and still inspect almost everything else

## Phase 4: Understand phases, plans, tasks, and subtasks

The system has two layers you need to keep separate:

- node hierarchy: `epic`, `phase`, `plan`, `task`
- execution hierarchy inside one node: compiled `task` and compiled `subtask`

In practice:

- `epic`, `phase`, `plan`, and `task` are durable nodes in the tree
- `task current` shows the compiled workflow task currently active for one node run
- `subtask current` shows the executable step inside that compiled task

That means "task" is overloaded:

- node-kind `task` means a leaf node in the tree
- compiled workflow task means a stage inside one node's workflow

The CLI namespaces reflect that split:

- `node ...` and `tree ...` are about durable node structure
- `workflow ...`, `task ...`, and `subtask ...` are about the compiled execution state of one node

## Phase 5: Move the current subtask forward

The AI-facing command loop uses explicit progress mutations.

Read current work:

```bash
python3 -m aicoding.cli.main subtask current --node <node_id>
PYTHONPATH=src python3 -m aicoding.cli.main subtask prompt --node <node_id>
python3 -m aicoding.cli.main subtask context --node <node_id>
```

Then mutate progress.

For ordinary non-command subtasks, the current command surfaces are:

```bash
python3 -m aicoding.cli.main subtask start --node <node_id> --compiled-subtask <compiled_subtask_id>
python3 -m aicoding.cli.main subtask heartbeat --node <node_id> --compiled-subtask <compiled_subtask_id>
python3 -m aicoding.cli.main subtask complete --node <node_id> --compiled-subtask <compiled_subtask_id> --summary "Finished the current step."
python3 -m aicoding.cli.main subtask succeed --node <node_id> --compiled-subtask <compiled_subtask_id> --summary-file summaries/step_summary.md
python3 -m aicoding.cli.main workflow advance --node <node_id>
```

For command subtasks, the current command-reporting surface is:

```bash
python3 -m aicoding.cli.main subtask report-command --node <node_id> --compiled-subtask <compiled_subtask_id> --result-file command_result.json
```

If the step fails:

```bash
python3 -m aicoding.cli.main subtask fail --node <node_id> --compiled-subtask <compiled_subtask_id> --summary "Why the step failed."
```

Or with a file-backed summary:

```bash
python3 -m aicoding.cli.main subtask fail --node <node_id> --compiled-subtask <compiled_subtask_id> --summary-file failure_summary.md
```

If you need to register a durable summary artifact:

```bash
python3 -m aicoding.cli.main summary register --node <node_id> --file summary.md --type implementation
```

Important rule:

- `subtask complete` does not implicitly advance the workflow cursor
- use `workflow advance --node <node_id>` after successful completion
- `subtask succeed` is the higher-level helper for ordinary execution subtasks when you already have a summary file and want the daemon to route the workflow immediately
- `subtask report-command` is the higher-level helper for command subtasks that need a structured command result instead of a plain free-text success summary

## Phase 6: Pause, resume, and recover

The core run-control commands are:

```bash
python3 -m aicoding.cli.main workflow pause --node <node_id>
python3 -m aicoding.cli.main workflow resume --node <node_id>
python3 -m aicoding.cli.main node pause-state --node <node_id>
python3 -m aicoding.cli.main node recovery-status --node <node_id>
python3 -m aicoding.cli.main session resume --node <node_id>
python3 -m aicoding.cli.main session recover --node <node_id>
python3 -m aicoding.cli.main session nudge --node <node_id>
```

Use them when:

- a session went stale
- the daemon says the run is paused
- you need to classify whether to attach, resume, or recover

## Optional: Create descendants manually

If you want to see the node ladder directly instead of waiting for layout-driven child creation, create children manually:

```bash
python3 -m aicoding.cli.main node child create --parent <epic_id> --kind phase --title "Hello World Phase" --prompt "Break the epic into a small plan."
python3 -m aicoding.cli.main node child create --parent <phase_id> --kind plan --title "Hello World Plan" --prompt "Create one concrete implementation plan."
python3 -m aicoding.cli.main node child create --parent <plan_id> --kind task --title "Hello World Task" --prompt "Implement the greeting feature."
python3 -m aicoding.cli.main tree show --node <epic_id> --full
```

This is useful if you specifically want to learn the hierarchy model first.

## Quick mental model

For a first pass, think of the tool like this:

1. `workflow start` creates and optionally runs the top node.
2. `node`, `tree`, `yaml`, `prompts`, and `summary` commands explain durable structure, inputs, and history.
3. `workflow`, `task`, and `subtask` commands explain the compiled execution state for one node.
4. `session show-current` tells an active shell what it is attached to.
5. `subtask start|heartbeat|complete|fail`, `subtask succeed`, `subtask report-command`, and `workflow advance` are the current explicit progress surfaces.

That is the smallest real end-to-end hello-world for this repository today.
