# Getting Started: Hello World Through The Orchestrator

## Purpose

This is the shortest spec-aligned walkthrough for a first real run through the tool.

It is not "print hello in a terminal." The system's hello world is:

- create a top-level node from a prompt
- compile an immutable workflow
- start a durable run
- inspect the current task and subtask
- bind a session
- mark progress through the command loop

## Current hierarchy

The built-in hierarchy currently is:

- `epic` -> top-level kind
- `phase` -> child of `epic`
- `plan` -> child of `phase`
- `task` -> child of `plan`

Important current constraint:

- only `epic` is parentless today
- if you want to start from one command, use `workflow start --kind epic ...`
- `phase`, `plan`, and `task` show up as descendants, either from layout materialization or manual child creation

## What "hello world" should be

Use one small prompt that is concrete enough to compile and inspect:

> Create a tiny greeting feature. Add a config file, generate a greeting artifact, add one repeatable verification command, and write a short summary.

That is enough to exercise prompt capture, compiled workflow state, session bootstrap, and subtask inspection.

## Prerequisites

Set up the repo and database first:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
python3 -m aicoding.cli.main admin doctor
python3 -m aicoding.cli.main admin db ping
python3 -m aicoding.cli.main admin db upgrade
```

Run the daemon in a separate shell:

```bash
uvicorn aicoding.daemon.app:create_app --factory --reload
```

All commands below use the current CLI entrypoint:

```bash
python3 -m aicoding.cli.main ...
```

## Phase 1: Start a top-level workflow

The real top-level hello-world entrypoint is:

```bash
python3 -m aicoding.cli.main workflow start \
  --kind epic \
  --title "Hello World Epic" \
  --prompt "Create a tiny greeting feature. Add a config file, generate a greeting artifact, add one repeatable verification command, and write a short summary."
```

What this does:

- creates the top-level node
- captures the source prompt
- compiles the authoritative workflow
- starts the first run unless you pass `--no-run`

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
python3 -m aicoding.cli.main workflow current --node <node_id>
python3 -m aicoding.cli.main task current --node <node_id>
python3 -m aicoding.cli.main subtask current --node <node_id>
python3 -m aicoding.cli.main subtask prompt --node <node_id>
python3 -m aicoding.cli.main subtask context --node <node_id>
python3 -m aicoding.cli.main node runs --node <node_id>
python3 -m aicoding.cli.main node blockers --node <node_id>
python3 -m aicoding.cli.main tree show --node <node_id> --full
```

Use these reads to answer:

- what node exists
- whether the workflow compiled
- which task is active
- which subtask is current
- what prompt the current subtask received
- what context the daemon assembled for stage startup
- whether anything is blocked

## Phase 3: Bind or inspect the active session

If the workflow was started with a run, bind a primary session:

```bash
python3 -m aicoding.cli.main session bind --node <node_id>
python3 -m aicoding.cli.main session show-current
python3 -m aicoding.cli.main session show --node <node_id>
```

Bootstrap rule from the runtime notes:

- `session show-current` is the first safe read for an active shell
- it tells you the bound node, run status, and recovery classification
- after that, read `workflow current`, `subtask current`, `subtask prompt`, and `subtask context` with the node id it returned

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
python3 -m aicoding.cli.main subtask prompt --node <node_id>
python3 -m aicoding.cli.main subtask context --node <node_id>
```

Then mutate progress:

```bash
python3 -m aicoding.cli.main subtask start --node <node_id> --compiled-subtask <compiled_subtask_id>
python3 -m aicoding.cli.main subtask heartbeat --node <node_id> --compiled-subtask <compiled_subtask_id>
python3 -m aicoding.cli.main subtask complete --node <node_id> --compiled-subtask <compiled_subtask_id> --summary "Finished the current step."
python3 -m aicoding.cli.main workflow advance --node <node_id>
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

## Phase 6: Pause, resume, and recover

The core run-control commands are:

```bash
python3 -m aicoding.cli.main node pause --node <node_id>
python3 -m aicoding.cli.main node resume --node <node_id>
python3 -m aicoding.cli.main node pause-state --node <node_id>
python3 -m aicoding.cli.main node recovery-status --node <node_id>
python3 -m aicoding.cli.main session resume --node <node_id>
python3 -m aicoding.cli.main session recover --node <node_id>
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
2. `node` and `tree` commands explain durable structure and lifecycle.
3. `workflow`, `task`, and `subtask` commands explain the compiled execution state for one node.
4. `session show-current` tells an active shell what it is attached to.
5. `subtask start|heartbeat|complete|fail` plus `workflow advance` drive the command loop.

That is the smallest real end-to-end hello-world for this repository today.
