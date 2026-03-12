# Tmux Session Lifecycle Spec V1

## Purpose

This document is the authoritative tmux session lifecycle note for the repository.

It consolidates the tmux-backed session model that was previously split across:

- the general runtime command loop spec
- the session recovery appendix
- implementation-decision notes about the tmux/session harness

This spec exists so contributors can answer one question from one note:

- how should tmux-backed session lifecycle work from fresh bind through recovery?

Related documents:

- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/specs/database/database_schema_spec_v2.md`
- `notes/specs/architecture/code_vs_yaml_delineation.md`

---

## Scope

This spec covers:

- primary tmux session lifecycle
- pushed child tmux session lifecycle at a high level
- tmux-backed recovery classification and actions
- prompt/bootstrap and resume contract for Codex-backed primary sessions
- durable records and inspection surfaces required to explain tmux behavior

This spec does not replace the broader runtime loop spec.

It narrows specifically to tmux/session lifecycle doctrine.

---

## Core Invariants

1. One active node run may have at most one authoritative active primary session.
2. tmux is a runtime transport and attachability boundary, not the durable source of truth.
3. Durable database state remains authoritative over tmux state when they disagree, unless the system explicitly proves the durable state is stale.
4. A tmux-backed session is not valid merely because a tmux pane exists; it must correspond to a durable session record and run.
5. Fresh primary-session bootstrap must use the canonical CLI prompt retrieval surface rather than reconstructing prompt text ad hoc inside tmux startup logic.
6. Prompt logging under `./prompt_logs/<project_name>/...` is an audit artifact, not the authoritative prompt source.
7. Fresh and replacement tmux sessions must be launched with the daemon-owned runtime environment required for CLI, auth-token, database, prompt, and provider access; tmux-server ambient environment is not authoritative.
8. Primary-session cwd must resolve to the authoritative node runtime repo when one exists; only nodes without a bootstrapped runtime repo may fall back to the configured daemon-owned workspace root.
9. Tmux pane/session existence and live runtime-process health are separate signals; a preserved dead pane must remain inspectable but may not be treated as a healthy session.
10. Recovery must prefer safe reuse of an existing valid session before replacement.
11. Replacement of a lost session must preserve the prior durable session history.
12. For unfinished runnable work, the daemon must supervise authoritative tracked primary sessions and ensure the required tmux session remains running; if safe replacement cannot be completed, the unfinished run must fail durably rather than remaining silently stuck.

---

## Tmux Session Model

### Primary session

The primary session is the active execution agent for one node run.

It is expected to have:

- one durable session row
- one tmux session name
- one working directory
- one authoritative run binding
- one current compiled subtask context

### Pushed child session

A pushed child session is a bounded delegated context session.

It may use tmux, but it does not become the durable owner of:

- node lifecycle
- compiled workflow ownership
- authoritative cursor state
- merge/cutover authority

The parent primary session remains the authoritative execution owner.

---

## Primary Session Lifecycle

### 1. Run admitted

Before tmux binding is legal:

- the node must have an authoritative version
- the active run must be admitted
- the compiled workflow cursor must exist durably

Top-level startup note:

- `workflow start` and the project-scoped website top-level create route treat `start_run = true` as a daemon-owned request to admit the run and bind the authoritative primary session in the same startup flow
- `--no-run` or `start_run = false` still stops at compiled/ready without creating a primary session

### 2. Bind request accepted

`session bind --node <node_id>` is the daemon-owned request that creates or reuses the authoritative primary session binding.

If a valid primary session already exists for the run:

- the daemon should reuse it rather than create a duplicate

If the existing durable record points at a missing tmux session:

- the daemon should invalidate the stale binding before replacement

### 3. Fresh tmux session created

For a fresh primary session:

- the daemon derives the tmux session name from durable run/session identity
- the daemon launches a tmux session in the authoritative node runtime repo when one exists
- the daemon enables tmux `remain-on-exit` for daemon-managed primary sessions so fast bootstrap failures leave an inspectable pane instead of disappearing immediately
- if the node has not yet bootstrapped a runtime repo, the daemon may fall back to the configured workspace-root cwd
- the daemon injects the daemon-owned runtime environment into tmux session creation rather than relying on preexisting tmux-server environment inheritance
- the daemon must not forward the parent shell's `TERM` into tmux session creation; tmux must set the pane terminal type itself, otherwise detached pytest/runtime launches can inherit `TERM=dumb` and break Codex bootstrap
- the daemon records launch metadata durably
- session inspection surfaces must expose both tmux pane existence and live-process/exit-status state so preserved dead panes are distinguishable from healthy live sessions

### 4. Prompt bootstrap and Codex launch

Fresh primary-session bootstrap is expected to:

- reference the canonical CLI prompt command:
  - `PYTHONPATH=src python3 -m aicoding.cli.main subtask prompt --node <node_id>`
- write the returned prompt to:
  - `./prompt_logs/<project_name>/...`
- invoke Codex with an instruction equivalent to:
  - `codex --yolo "Please read the prompt from <cli command to run the tool to retrieve the prompt for the current stage> and run the prompt"`

The prompt log is an audit/logging side effect.

Codex should be told to read the prompt from the CLI command, not from the prompt-log file path.

Implementation note:

- the shipped execution prompt now embeds the original node request through the compiled prompt body, so a freshly bootstrapped tmux/Codex session receives the user/task request directly from `subtask prompt` rather than needing an immediate follow-up context read just to recover that instruction

Provider integration note:

- live Codex may still present a workspace-trust prompt for a daemon-owned workspace even when launched with `codex --yolo ...`
- tmux-backed fresh and recovery launch must preseed a session-owned Codex `config.toml` with trusted-workspace entries for the intended workspace path and any adjacent daemon-owned path Codex resolves during startup
- tmux-backed launch should also invoke Codex with an explicit `-C <working_directory>` so provider-side workspace resolution does not drift away from the daemon-owned session cwd
- the daemon no longer drives that provider UI through tmux send-keys fallback logic; if provider-side trust preseed fails to suppress the prompt, that is treated as a launch-contract defect

### 5. Active execution

During steady-state execution, the primary session is expected to:

- inspect `session show-current`
- inspect the current workflow and current subtask
- retrieve prompt and context through the CLI
- mark start, heartbeat, completion, failure, and summaries through the CLI

### 6. Detached session

A session may be healthy but detached.

That means:

- the durable session record is still valid
- the tmux session still exists
- the pane process is still alive
- the system should prefer reattach, not replacement

### 7. Stale session

A session may be stale but still recoverable.

That means:

- the durable record still points to a live tmux session
- the pane process is still alive
- heartbeat or screen activity is old enough to classify the session as stale
- the system may resume or nudge depending on the runtime policy

### 8. Lost session

A session is lost when the durable record exists but the expected tmux session is gone or unusable.

When that happens:

- the old durable session must remain inspectable as prior history
- the run may still be resumable
- replacement logic, not silent reuse, becomes the valid path

Implementation note:

- a primary session is also treated as `lost` when tmux still preserves the pane but the pane process has already exited; that case must surface `tmux_session_exists=true` together with `tmux_process_alive=false` and any known exit status

---

## Recovery Classification And Actions

The runtime should classify the active primary-session situation using the following categories.

### `healthy`

- session exists
- tmux exists
- state is active enough to reuse safely

Action:

- reuse existing session

### `detached`

- session exists
- tmux exists
- user/operator is not attached

Action:

- attach existing session

### `stale_but_recoverable`

- session exists
- tmux exists
- heartbeat or activity is stale

Action:

- resume existing session, or nudge if the policy requires it

### `lost`

- durable session record exists
- tmux session is missing or unusable

Action:

- invalidate the stale session binding
- create a replacement session if the run is resumable

### `ambiguous`

- multiple active primary sessions or other ownership conflict exists

Action:

- stop automatic recovery
- pause for explicit operator intervention

### `non_resumable`

- run is marked non-resumable

Action:

- do not auto-resume
- require explicit user/operator intervention

---

## Replacement And Resume Contract

### Fresh session launch

Fresh launch is the path for:

- the first bind for an admitted run
- replacement after a lost session when the runtime chooses a new primary session

Fresh launch is expected to use the prompt/bootstrap contract in:

- `## Primary Session Lifecycle`
- `### 4. Prompt bootstrap and Codex launch`

### Replacement after tmux loss

If the expected tmux session is dead and the runtime chooses replacement:

- the prior session should be marked lost or invalidated durably
- the new primary session should have its own durable session row
- the replacement launch must be inspectable as a recovery event, not merely a new bind

### Autonomous supervision requirement

The daemon may not rely only on operator-triggered `session resume` or `session bind` calls to keep active work alive.

For authoritative tracked primary sessions tied to unfinished work:

- the daemon should periodically inspect whether the expected tmux session still exists
- if the expected tmux session is gone and the node/run is still eligible for execution, the daemon should attempt safe replacement automatically
- automatic creation or replacement should be limited to runnable or already-active work; it must not start tmux sessions for terminal, cancelled, superseded, or otherwise non-runnable nodes
- if the task or run is not complete and safe replacement cannot be created, the daemon should record that failed recovery durably and fail the run rather than leaving it in a silent stuck state

This autonomous supervision contract is part of the authoritative tmux lifecycle, not a best-effort optional enhancement.

### Resume command for dead-session recovery

When the recovery path chooses the provider-specific Codex resume route for a dead expected tmux session, the replacement launch contract is:

- `codex --yolo resume --last`

This path depends on stable working-directory semantics.

The session working directory must therefore remain part of the durable launch metadata.

---

## Prompt Bootstrap And Prompt-Log Contract

The prompt bootstrap contract exists to keep prompt delivery:

- inspectable
- reproducible
- aligned with the real CLI and daemon surfaces

### Prompt source

The authoritative prompt source for fresh bootstrap is the current-stage CLI retrieval command:

- `PYTHONPATH=src python3 -m aicoding.cli.main subtask prompt --node <node_id>`

### Prompt log

The prompt returned by that command should also be written under:

- `./prompt_logs/<project_name>/`

The log path should be deterministic enough to explain which run and compiled subtask it belongs to.

Recommended minimum identity:

- project name
- logical node id
- node run id
- compiled subtask id

### Audit rule

If the CLI retrieval command and the prompt-log file disagree, the system is inconsistent.

Tests should defend against that mismatch.

---

## Durable Records And Audit Surface

The tmux lifecycle is not sufficiently implemented unless operators can inspect it.

At minimum, durable records should explain:

- session id
- node version id
- node run id
- session role and status
- tmux session name
- provider session id if available
- working directory
- launch mode
- launch command
- attach command
- prompt CLI retrieval command for fresh launch
- prompt-log path for fresh launch
- recovery classification
- replacement or resume outcome

The tmux lifecycle should be explainable through the intended CLI and daemon surfaces without requiring direct tmux inspection as the only evidence.

---

## CLI And Inspection Surfaces

The tmux lifecycle depends on these operator and AI-facing surfaces at minimum:

- `workflow start --kind <kind> --prompt <prompt>`
- `session bind --node <node_id>`
- `session attach --node <node_id>`
- `session resume --node <node_id>`
- `session show-current`
- `session show --node <node_id>`
- `session events --session <session_id>`
- `node recovery-status --node <node_id>`
- `subtask current --node <node_id>`
- `PYTHONPATH=src python3 -m aicoding.cli.main subtask prompt --node <node_id>`
- `subtask context --node <node_id>`

If tmux lifecycle behavior cannot be explained through those surfaces plus durable state, the implementation is incomplete.

Implementation note:

- if session supervision marks the tracked primary session lost, records `supervision_recovery_failed`, and the run becomes terminally failed, `session show --node <node_id>`, `node run show --node <node_id>`, `subtask current --node <node_id>`, and `node recovery-status --node <node_id>` must remain inspectable through the latest failed run/session snapshot rather than collapsing immediately to a generic active-run error
- those fallback payloads should expose a bounded `terminal_failure` bundle and an `inspect_failed_run` recommendation
- `subtask prompt` and `subtask context` should remain non-runnable once that terminal failure is durable, but their rejection should explicitly direct the caller back to the failed-run inspection surfaces instead of saying only that no active run exists

---

## Backend Abstraction And Test Posture

tmux lifecycle must remain testable.

### Backend abstraction

- tmux integration should remain isolated behind a session-adapter abstraction
- deterministic fake-session coverage remains useful for bounded tests
- real tmux E2E remains required for final proving of tmux-backed runtime behavior

### Testing posture

Bounded proof should cover:

- name derivation
- launch-plan construction
- recovery classification
- durable session-event persistence

Real E2E proof should cover:

- actual tmux session creation
- actual Codex bootstrap rather than shell placeholder launch
- prompt-log creation
- real stale or lost recovery behavior
- real attach/resume surfaces

---

## Relationship To Other Notes

### `runtime_command_loop_spec_v2.md`

This remains the broad runtime-loop specification.

Use it for:

- overall AI-facing command loop
- workflow cursor ownership
- stage progression
- parent/child execution semantics

Use this tmux lifecycle spec for:

- tmux-backed session lifecycle detail
- prompt/bootstrap launch contract
- recovery classification and replacement rules

### `session_recovery_appendix.md`

That note should now be treated as legacy supplemental context.

The authoritative recovery rules for tmux-backed session lifecycle live here.

### `tmux_and_session_harness_decisions.md`

That note remains an implementation-decision history note.

It is not the primary doctrinal source for tmux lifecycle behavior.

---

## Current Known Gaps

The intended lifecycle is clearer than the current fully proven runtime.

Known current gaps include:

- real fresh primary-session Codex launch is still being hardened
- real tmux recovery currently still has gaps around when a live session should classify as `stale_but_recoverable` versus `lost`
- child tmux sessions still lag behind the primary-session Codex launch posture
- dedicated passing E2E suites for the full tmux lifecycle matrix are still incomplete
