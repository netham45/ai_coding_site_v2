# Runtime Command Loop Spec V2

## Purpose

This document defines the canonical AI-facing execution loop for nodes, compiled subtasks, tmux-backed sessions, pushed child sessions, and CLI-driven runtime control.

V2 expands the prior runtime loop spec by:

- aligning the loop with the v2 lifecycle model
- aligning the loop with explicit review/testing/docs result handling
- clarifying actor ownership between session, runtime, and durable state
- clarifying recovery and idle-session behavior
- clarifying child-node and pushed-child-session orchestration
- clarifying daemon/API authority boundaries

Design goals:

- the same CLI should serve both operators and AI sessions
- no critical runtime state should exist only in memory
- every node run should be resumable from durable state
- execution should always be explainable from compiled workflow plus durable history
- the daemon should be the live orchestration authority while durable state remains recoverable from the database

---

## 1. Core runtime model

### Primary rule

Default behavior:

- one node version
- one active node run
- one primary session binding
- one compiled workflow cursor

That means:

- the node run is the durable execution owner
- the primary session is the active execution agent
- the compiled workflow defines the executable stages
- the daemon is the live orchestration authority
- the database is the durable canonical record for runtime state and history

### Client access rule

Operational clients should talk to the daemon API rather than coordinating directly through database access.

Recommended initial access model:

- HTTPS transport
- runtime-generated cookie authentication
- CLI and future web/dashboard clients acting as daemon clients

### Optional pushed child session

A subtask may temporarily push work into a bounded child session when context isolation is useful.

Examples:

- research
- review
- focused verification
- summarization

This push/pop mechanism is for context management only.

It does not transfer:

- node ownership
- branch ownership
- compiled workflow ownership
- cursor ownership

The parent session remains the owner of node execution.

---

## 2. Actor ownership model

The runtime needs explicit ownership boundaries.

### Node run

Owns:

- compiled workflow binding
- current cursor state
- lifecycle state
- durable execution history

### Primary session

Owns:

- active interaction with the current subtask
- heartbeats
- prompt/context retrieval
- progress commands

### Pushed child session

Owns:

- bounded delegated context work
- delegated summary output

### Runtime/orchestrator layer

Owns:

- run admission
- session binding/rebinding
- idle detection
- recovery logic
- child scheduling
- upstream rebuild orchestration
- API request validation and mutation authorization
- persistence of coordination-relevant transitions

Rule:

- if a state transition affects global coordination or recoverability, it should not rely on unstored session-local knowledge
- if a mutating operation affects live coordination, it should be accepted through daemon logic before becoming authoritative

---

## 3. tmux model

Detailed tmux lifecycle doctrine now lives in:

- `notes/specs/runtime/tmux_session_lifecycle_spec_v1.md#tmux-session-model`
- `notes/specs/runtime/tmux_session_lifecycle_spec_v1.md#primary-session-lifecycle`
- `notes/specs/runtime/tmux_session_lifecycle_spec_v1.md#recovery-classification-and-actions`

Sessions run inside tmux.

Each primary node session should record:

- session ID
- node version ID
- node run ID
- tmux session name
- provider session ID if available
- working directory
- last heartbeat time
- current compiled subtask ID

tmux requirements:

- a node run must be attachable through tmux
- terminal detach must not lose node state
- host reboot or tmux loss must still allow DB-driven resume or replacement-session recovery

Implementation note:

- tmux access should be isolated behind an adapter abstraction so fake-session-backed tests can exercise bind, attach, capture, idle, and recovery behavior deterministically
- the current implementation now adds a concrete session-manager layer on top of that adapter
- primary tmux session names are now derived from durable run/session identity rather than a generic node-only label
- primary sessions now target a Codex bootstrap path that retrieves the current-stage prompt through the CLI and logs it under `./prompt_logs/<project_name>/...`; pushed-child sessions are still a separate lifecycle surface and may lag behind the primary-session posture
- session inspection surfaces now expose the persisted working directory, provider session id, tmux existence, and attach command when the backend is real tmux

---

## 4. High-level node execution loop

A normal node execution loop is:

1. node run is admitted
2. primary session binds to node run
3. session retrieves compiled workflow and current cursor
4. session retrieves current subtask payload
5. session performs subtask work
6. session records progress through CLI
7. runtime validates results and advances cursor if accepted
8. quality-gate stages run in canonical order
9. when all stages are done, node finalization runs

The loop must remain CLI-driven and inspectable.

Implementation staging note:

- the current implementation now persists one durable primary-session record for an active run in `sessions`
- bind/attach/resume reuse the existing primary session when safe and create a replacement durable session record when the harness session is missing
- parent-local child-merge handoff is now also durable: after a staged merge run, the daemon stores `parent_reconcile_context` in the active run cursor so the session can resume or inspect that stage without rebuilding it from memory
- command-only subtasks may not surface as bare shell text alone; when a compiled subtask has `command_text` but no authored `prompt_text`, `subtask prompt --node <id>` must synthesize a reporting contract that tells the AI to start the attempt, run the command once, persist at least `{"exit_code": ...}` through `subtask report-command`, and continue in the same session when a later stage exists
- leaf execution prompts may not stop at `workflow advance` alone; after a successful advance they must tell the AI to query `subtask current`, fetch `subtask prompt` for the next stage when one exists, and continue in the same session so quality-gate subtasks receive their full authored or synthesized prompt contract

---

## 5. Required AI-facing command loop

At minimum the runtime loop should support commands like these.

### Session bootstrap

- `ai-tool workflow start --kind <kind> --prompt <prompt>`
- `ai-tool session bind --node <id>`
- `ai-tool session show-current`
- `ai-tool workflow current --node <id>`

Implementation staging note:

- `workflow start --kind <kind> --prompt <prompt> [--title <title>] [--no-run]` now creates the top-level node, captures source lineage, compiles the authoritative workflow, and optionally admits the first run in one daemon-owned mutation
- `session bind --node <id>` now requires an admitted active run and creates or reuses the durable primary session record for that run
- `session show-current` now resolves from the durable primary-session table instead of only the session harness adapter
- `session show-current` now also returns the bound `logical_node_id`, `node_kind`, `node_title`, current `run_status`, and derived `recovery_classification` so session bootstrap can safely discover what work it is attached to before reading workflow or subtask state
- session bind/replacement flows now record concrete tmux launch metadata, including the derived session name, launch command, working directory, and tmux attach target
- compile-time source capture must be idempotent within one compile pass: repeated resolved inputs for the same `(source_group, relative_path, source_role)` may not create duplicate `node_version_source_documents` rows, and sibling-tier `node_definition` overrides present in one workspace must not break compile for a different node kind
- built-in validation commands used by leaf/runtime workflows must target the active workspace, not repository-internal fixture paths; the default validation gate and validation hook now use `python3 -m pytest -q` rather than repo-specific schema-test paths
- command-based validation subtasks now default to an implicit `command_exit_code == 0` gate when no explicit `checks` list is authored, so built-in validation hooks can remain concise without breaking `workflow advance`

### Prompt and context retrieval

- `ai-tool subtask current --node <id>`
- `ai-tool subtask prompt --node <id>`
- `ai-tool subtask context --node <id>`
- `ai-tool subtask environment --node <id>`
- `ai-tool node child-results --node <id>`
- `ai-tool node reconcile --node <id>`

Implementation staging note:

- `node child-results --node <id>` now exposes authoritative child finals, blocked-child classification, and deterministic merge order
- `node reconcile --node <id>` now exposes the packaged parent-local reconcile prompt plus the current derived reconcile context
- `subtask context --node <id>` now includes durable `parent_reconcile_context` when a staged child merge has already run for the active parent node run
- that same `parent_reconcile_context` channel now also carries daemon-assembled incremental merge conflict handoff context when the parent merge lane blocks on a conflicted child merge
- `subtask prompt --node <id>` and `subtask context --node <id>` now expose the same daemon-assembled `stage_context_json` bundle so stage startup does not depend on terminal scrollback or ad hoc session memory
- that bundle currently includes:
  - startup metadata from the authoritative node version and run
  - current stage metadata from the compiled subtask
  - dependency edges and persisted blocker state for the node version
  - recent prompt deliveries and summaries for the run
  - cursor-carried pause, child-session, and parent-reconcile context
- `subtask context --node <id>` now also mirrors the same `stage_context_json` under `input_context_json.stage_context_json` so existing context consumers can adopt the richer startup contract incrementally
- the startup portion currently includes the user-supplied node prompt, node title, node kind, run number, trigger reason, and compiled workflow id
- the shipped execution prompt now renders the user-supplied node prompt directly into the compiled prompt body, so the bootstrap path can carry the original request without requiring a separate context fetch before the session begins work
- the stage portion currently includes compiled task/subtask ids, source subtask key, subtask type, title, and frozen environment request metadata
- compile-time rendering now freezes prompt and command text before runtime stage execution begins; stage startup consumes that frozen rendered payload plus `stage_context_json` rather than rerendering templates at prompt-fetch time
- `subtask environment --node <id>` now exposes the current compiled subtask's frozen environment request so the session can tell whether the next step is host, delegated-profile, or best-effort isolation work before starting the attempt

### Progress marking

- `ai-tool subtask start --compiled-subtask <id>`
- `ai-tool subtask heartbeat --compiled-subtask <id>`
- `ai-tool subtask succeed --compiled-subtask <id> --summary-file <path>`
- `ai-tool subtask report-command --compiled-subtask <id> --result-file result.json`
- `ai-tool subtask complete --compiled-subtask <id>`
- `ai-tool subtask fail --compiled-subtask <id> --summary-file <path>`

Implementation staging note:

- the current runtime slice durably supports `subtask start`, `subtask complete`, `subtask fail`, `subtask succeed`, and `subtask report-command`
- `subtask fail` now supports the documented file-backed AI path: the CLI reads `--summary-file <path>` locally and sends the file content as the durable failure summary
- `subtask succeed` now owns the ordinary non-command success path: it registers the durable summary artifact, completes the active attempt, advances the workflow, and returns a routed outcome
- `subtask report-command` now owns the command-stage reporting path: it records the explicit execution result, completes or fails the attempt as appropriate, advances daemon-owned validation/testing gates, and returns a routed outcome
- `subtask heartbeat` now persists the latest heartbeat timestamp on both the active attempt output payload and the run cursor metadata; dedicated heartbeat history remains deferred
- `subtask start` now resolves and persists `execution_environment_json` on the attempt before work proceeds
- unsupported mandatory isolation requests fail immediately at start time, while unsupported non-mandatory requests are recorded as explicit host fallbacks rather than silently proceeding
- `--result-file` on `subtask complete`, `subtask fail`, and `subtask report-command` is reserved for explicit `execution_result_json` payloads, so the referenced file must be valid JSON rather than a Markdown summary artifact

### Summary and artifact registration

- `ai-tool summary register --node <id> --file <path> --type <type>`
- `ai-tool prompts list --node <id>`

Implementation staging note:

- `subtask prompt --node <id>` now records a durable prompt-delivery artifact each time the current prompt is fetched
- `summary register --node <id> --file <path> --type <type>` now records a durable summary-history row in addition to the active-attempt compatibility mirror
- shipped prompts and examples must keep `summary_type` within the bounded orchestration taxonomy; implementation-stage summaries currently register as `subtask`
- validation checks that require a written summary now consult the durable summary history as well as the mirrored attempt payload

### Cursor control

- `ai-tool workflow advance --node <id>`
- `ai-tool workflow pause --node <id>`
- `ai-tool workflow resume --node <id>`
- `ai-tool node interventions --node <id>`
- `ai-tool node intervention-apply --node <id> --kind <kind> --action <action>`

### Recovery

- `ai-tool session nudge --node <id>`
- `ai-tool session resume --node <id>`
- `ai-tool session recover --node <id>`
- `ai-tool session provider-resume --node <id>`
- `ai-tool session attach --node <id>`
- `ai-tool node recovery-status --node <id>`
- `ai-tool node recovery-provider-status --node <id>`

Implementation staging note:

- `session resume --node <id>` now runs provider-agnostic recovery against durable run state instead of assuming provider identity is sufficient
- `session recover --node <id>` is an explicit alias for the same recovery path
- `node recovery-status --node <id>` now exposes the current recovery classification and recommended action from the daemon
- `node recovery-provider-status --node <id>` now exposes the provider-aware restoration view, including whether the persisted provider identity still exists and whether direct rebind is possible
- `session provider-resume --node <id>` now attempts provider-aware rebound before falling back to the provider-agnostic recovery path
- `session show --node <id>`, `session show --session <id>`, and `session show-current` now also expose the same `recommended_action` when the selected row is the active primary session, so session-control clients can decide whether to attach or resume from the ordinary session read path
- the current staged classifier distinguishes `healthy`, `detached`, `stale_but_recoverable`, `lost`, `missing`, `ambiguous`, and `non_resumable`
- the current provider-aware enhancement is intentionally bounded: it only performs direct rebind when the durable provider identity matches the active backend and that provider session still exists
- `session nudge --node <id>` now performs bounded idle inspection against the active primary session, evaluates the captured pane content even when the provider UI is in alt-screen, records durable nudge audit events, and escalates to `PAUSED_FOR_USER` when the configured nudge budget is exhausted

The command names may evolve, but the behavior must exist.

---

## 6. Canonical node loop pseudocode

```python
def run_node_loop(node_id):
    run = admit_or_load_active_run(node_id)
    session = bind_or_resume_primary_session(run.id)

    while True:
        state = load_run_state(run.id)
        subtask = get_current_compiled_subtask(run.id)

        if subtask is None:
            finalize_completed_workflow(run.id)
            break

        mark_subtask_started(run.id, subtask.id, session.id)
        result = execute_compiled_subtask(run.id, subtask, session.id)

        if result.status == "ok":
            persist_subtask_outputs(run.id, subtask.id, result)
            run_required_validations(run.id, subtask.id, result)
            mark_subtask_complete(run.id, subtask.id)
            advance_cursor(run.id)
            continue

        if result.status == "pause":
            register_summary(node_id, result.summary_path, "pause")
            transition_run_to_paused(run.id, result.pause_flag)
            break

        if result.status == "failed":
            register_summary(node_id, result.summary_path, "failure")
            handle_subtask_failure(run.id, subtask.id, result)
            break
```

This pseudocode is intentionally high-level. The implementation must expand each helper into durable state transitions.

---

## 7. Canonical subtask loop

For each compiled subtask:

1. retrieve current compiled subtask ID
2. retrieve prompt, command, context, and prior results
3. create or update the current subtask attempt
4. mark subtask started
5. perform work
6. persist outputs and summaries
7. run required validations
8. record attempt result
9. either:
   - advance cursor
   - retry
   - pause for user
   - fail to parent

The cursor must advance only after successful completion and accepted validations.

Implementation staging note:

- the current implementation persists one durable `node_runs` row per admitted active run, one `node_run_state` row for the live cursor, and one `subtask_attempts` row per started attempt
- ordinary prompt-driven execution stages now have an initial composite success path: `subtask succeed` records the durable summary artifact, completes the active ordinary-stage attempt, advances the workflow, and returns a routed outcome of `next_stage`, `paused`, `completed`, or `failed`
- command subtasks now have an initial composite reporting path: `subtask report-command` records the structured execution result, completes or fails the current command stage as appropriate, advances when appropriate, and returns the same routed outcome family
- parent decomposition prompts must use those same composite paths by stage type: layout-generation and other ordinary parent subtasks should teach `subtask succeed`, command-backed parent subtasks should teach `subtask report-command`, and parent review subtasks should continue to use `review run`
- recovery-oriented built-in tasks should bind to the `recovery/*` prompt family where the runtime owner is session reconstruction or interrupted-run recovery, rather than teaching duplicate `runtime/*` bootstrap/resume variants
- generic user-pause tasks should bind to one canonical generic pause prompt family, while parent-failure-specific pause prompts remain distinct runtime-owner-specific surfaces
- composite-enabled prompts must treat routed `completed` as terminal success and stop without issuing extra low-level inspection or workflow-mutation commands against the closed run
- duplicate prompt assets that are no longer bound by runtime YAML or daemon-owned prompt selection must be removed rather than left as compatibility-only dead files
- `subtask complete` records attempt completion durably, but the cursor advances only when `workflow advance --node <id>` is called
- `subtask fail` marks the run `FAILED` and mirrors lifecycle visibility to `FAILED_TO_PARENT`
- dedicated heartbeat history and richer pause/recovery orchestration remain later runtime slices

---

## 8. Subtask handler classes

The runtime should dispatch by compiled subtask type.

### Handler families

- `run_prompt`
- `run_command`
- `build_context`
- `wait_for_children`
- `wait_for_sibling_dependency`
- `validate`
- `review`
- `run_tests`
- `build_docs`
- `write_summary`
- `finalize_node`
- `spawn_child_session`
- `spawn_child_node`
- `reset_to_seed`
- `merge_children`
- `update_provenance`

Each handler must define:

- expected inputs
- expected outputs
- failure behavior
- pause behavior if applicable
- validation behavior

---

## 9. Quality-gate runtime ordering

The default built-in runtime order is:

1. reconcile
2. validation
3. review
4. testing
5. provenance update
6. docs build
7. finalize

Runtime rule:

- validation, review, testing, provenance, and docs may compile into ordinary subtasks, but they are still semantically meaningful named stages
- the current runtime also exposes a daemon-owned turnkey `node quality-chain` path that drives the built-in validation, review, and testing gates to completion and then records provenance, docs, and a final node summary once the active run completes

### Validation stage

- executes required checks
- records `validation_results`
- blocks advancement on required failure

### Review stage

- builds review input context
- records `review_results`
- decides continue, revise, pause, or fail

Implementation staging note:

- the current runtime now persists review gate outcomes in `review_results`
- the latest per-attempt review summary is mirrored into `subtask_attempts.review_json`
- `workflow advance` now evaluates `review` subtasks and routes `passed`, `revise`, and `failed` outcomes through daemon-owned cursor/lifecycle transitions
- the current default `revise_action` routing rewinds to the last non-gate implementation subtask so validation and review re-run naturally on the next pass

### Testing stage

- executes testing definitions
- records `test_results`
- decides continue, fail, or policy-allowed override

Implementation staging note:

- the current runtime now evaluates `run_tests` subtasks as a first-class gate, persists durable `test_results`, mirrors the latest summary into `subtask_attempts.testing_json`, and lets `workflow advance` route pass, retry-pending, fail-to-parent, and pause-for-user outcomes
- retry behavior is currently driven by testing-definition retry policy, but the packaged default node workflows still rely on explicit task/policy/override selection to introduce `test_node` rather than enabling testing on every built-in node by default

### Provenance stage

- refreshes entity and rationale mappings

### Docs stage

- builds local or merged documentation views

---

## 10. Prompt retrieval behavior

Every executable step should be retrievable through CLI rather than only as ephemeral terminal text.

The session should be able to ask for:

- current subtask prompt
- current subtask command
- current subtask context
- previous subtask summaries
- dependency summaries when relevant
- child summaries when relevant
- review/validation/testing results when relevant

This keeps execution restartable and auditable.

---

## 10A. Runtime guidance prompt payloads

The runtime should not rely on improvised operator text when starting, correcting, nudging, or recovering sessions.

The default prompt pack for these payloads lives in `notes/specs/prompts/prompt_library_plan.md`.

At minimum the runtime should have authored payloads for:

- initial CLI/bootstrap guidance
- missed-step or validation-failure correction
- command failure correction
- missing-output correction
- idle nudge
- pause-for-user handoff
- resume existing session
- replacement-session bootstrap

### Default CLI/bootstrap payload

```text
You are the active session for node <node_id> and compiled subtask
<compiled_subtask_id>.

Retrieve work with:
- `ai-tool subtask current --node <node_id>`
- `ai-tool subtask prompt --node <node_id>`
- `ai-tool subtask context --node <node_id>`

Use:
- `ai-tool subtask start --compiled-subtask <compiled_subtask_id>`
- `ai-tool subtask heartbeat --compiled-subtask <compiled_subtask_id>`
- `ai-tool subtask complete --compiled-subtask <compiled_subtask_id>`
- `ai-tool subtask fail --compiled-subtask <compiled_subtask_id> --summary-file <summary_path>`

Do not rely on unstored terminal context. The CLI and durable run state are the
authoritative execution contract.
```

Implementation staging note:

- the current command loop slice now exposes real `subtask prompt`, `subtask context`, `subtask heartbeat`, and `summary register` commands
- heartbeat persistence currently updates active-attempt and run-cursor metadata only
- summary registration currently attaches durable summary payloads to the active subtask attempt ahead of the later dedicated summary-history phases
- stage startup now depends on daemon-assembled durable context rather than prior terminal output; restarting a session and refetching `subtask prompt` or `subtask context` should yield the same startup categories for the active stage
- when a rendered execution prompt explicitly instructs a session to wait for a daemon idle nudge before beginning work, that wait gate overrides the generic leaf-task CLI workflow; the session must remain genuinely idle rather than substituting shell wait commands, background terminals, slash commands, or ad hoc polling

### Default missed-step payload

```text
The current stage is not complete yet for node <node_id>.

Missing requirements:
<missing_requirements>

Reload the current prompt/context through CLI, satisfy the missing requirement,
and only then mark the stage complete.

If you cannot satisfy the requirement safely, fail the subtask with a concise
summary instead of waiting idle.
```

---

## 11. Subtask attempt ownership

The runtime must make the subtask-attempt lifecycle explicit.

### Attempt lifecycle

1. create attempt row
2. mark started
3. collect heartbeats while active
4. capture outputs and changes
5. capture validations and summaries
6. mark terminal status

### Ownership rule

The session may initiate progress commands, but the durable acceptance of completion should be runtime-validated against the compiled workflow and required checks.

This prevents cursor corruption from incomplete or invalid session-side assumptions.

---

## 12. Pause and gating behavior

When a subtask or stage encounters a user gate:

1. complete the current durable attempt state
2. register a pause summary
3. set `pause_flag_name`
4. transition the run to `PAUSED_FOR_USER`
5. expose the pause reason through CLI

Resume requires:

- clearing or approving the gate
- restoring the same compiled workflow and cursor
- continuing from the correct post-gate stage

The runtime must not silently skip a user gate on resume.

Implementation note:

- gated compiled subtasks may carry `block_on_user_flag` and an optional `pause_summary_prompt`
- when the runtime lands on a gated subtask, it pauses before attempt start, persists `pause_context` in the durable cursor, and records `pause_entered`
- explicit operator approval records `pause_cleared` without resuming the run yet
- resume is rejected until the active pause flag is approved unless the daemon is executing an internal forced recovery path
- `node pause-state`, `node events`, `workflow approve`, and `node approve` are now implemented against that durable pause model
- the runtime now also exposes a bounded unified human-intervention catalog through `node interventions --node <id>` and `node intervention-apply --node <id> --kind <kind> --action <action>`
- the current intervention catalog aggregates the already durable pause, child-reconciliation, merge-conflict, session-recovery, and blocked-cutover attention state rather than creating a second intervention ledger
- currently supported intervention actions are:
  - `approve_pause`
  - `preserve_manual`
  - `abort_merge`
  - `resolve_conflict`
  - `resume_session`
- rebuild and cutover decisions are not yet fully symmetrical on that apply surface; blocked cutover currently appears as read-only attention

---

## 13. Failure handling

When a subtask fails:

1. classify the failure
2. record a failure summary
3. evaluate retry policy
4. either:
   - retry the current subtask
   - pause for the user
   - fail the node to parent

### Retry rule

Retries should be driven by compiled retry policy, not by ad hoc session behavior.

### Parent escalation rule

If the node fails upward:

1. the child records `FAILED_TO_PARENT`
2. the parent increments child-failure counters
3. the parent decides whether to retry, replan, pause, or fail further upward

This decision path must be durable and inspectable.

Recommended default parent decision order:

1. record the failure impact durably in parent context
2. classify the failure
3. evaluate hard-stop thresholds
4. retry the child if the failure is retryable and budget remains
5. regenerate the child version if retry is insufficient but parent assumptions remain valid
6. revise or replan locally at the parent if the failure indicates bad inputs, bad layout, or impossible requirements
7. pause for the user if ambiguity or safety thresholds prevent autonomous handling
8. fail upward only through the parent's own resulting failure path

Implementation staging note:

- the current daemon slice now exposes `node child-failures`, `node decision-history`, and `node respond-to-child-failure`
- automatic parent decisions now classify failures from the latest failed child attempt summary, quality-gate payloads, source subtask identity, and lifecycle context
- current decision payloads now expose `failure_origin`, `classification_reason`, `decision_reason`, `options_considered`, `threshold_triggered`, and the applied threshold policy
- explicit operator overrides are supported for `retry_child`, `regenerate_child`, `replan_parent`, and `pause_for_user`

---

## 14. Child node orchestration

Child-node work is different from pushed child sessions.

### Child-node lifecycle

1. materialize layout-defined children
2. persist child node versions
3. persist child dependency edges
4. schedule any ready children
5. wait for dependencies or completion as needed
6. collect child summaries and child final outputs
7. reconcile parent

### Runtime rules

- child nodes own their own runs and sessions
- parent nodes do not share cursor ownership with children
- parent nodes may query child state through CLI and DB

Implementation staging note:

- the current implementation materializes children through a daemon-owned `node materialize-children --node <id>` path
- parent-generated child layouts now require an explicit `node register-layout --node <id> --file <path>` handoff before they become authoritative
- `node materialize-children --node <id>` now resolves the effective layout from the registered `layouts/generated_layout.yaml` when the current workspace file hash matches the latest durable layout-registration event for that node, and otherwise falls back to the packaged built-in layout for the parent kind
- the packaged layout-generation prompts now tell parent sessions to write `layouts/generated_layout.yaml` and immediately run `node register-layout --node <id> --file layouts/generated_layout.yaml`; runtime does not promise ambient discovery of unregistered generated layouts
- materialization creates child hierarchy rows, authoritative child versions, compiled workflows, ready lifecycle state, and sibling dependency edges in durable storage
- parent-visible scheduling is currently exposed as derived classifications (`ready`, `blocked`, `invalid`, `impossible_wait`) rather than a separate schedule snapshot table
- the daemon now runs a background child auto-start loop that first advances pending incremental parent merges plus stale-child refresh for auto-run children, then admits `ready` child nodes with trigger reason `auto_run_child` and binds their primary sessions without an operator `node run start` or `session bind`
- final authoritative parent reconcile now happens only after all required children are already merged upward into the parent lineage the daemon is orchestrating; the reconcile stage is parent-local synthesis, not the first child-to-parent merge step
- dependency-blocked siblings remain unstarted until readiness changes

### Scheduling rule

Any child whose dependencies are satisfied should be eligible to start immediately.

---

## 15. Pushed child session behavior

### Push

Command shape:

- `ai-tool session push --node <id> --reason <reason>`

Push should:

- create a child session record
- snapshot bounded parent context
- launch isolated child session context
- preserve parent cursor without advancing it

Implementation staging note:

- `session push --node <id> --reason <reason>` now requires an active primary session and creates a durable `pushed_child` session linked to that parent session
- the current implementation launches the child through the same session adapter abstraction used for primary sessions and records the delegated prompt path in session events

### Child session work

The pushed child session performs focused work and ends by producing a summary or artifact set for the parent.

The child session should return a structured result contract that includes at minimum:

- child session ID
- parent compiled subtask ID
- outcome status such as `success|partial|failed`
- summary text
- referenced artifacts if any
- suggested next actions if relevant

### Pop

Command shape:

- `ai-tool session pop --session <id> --summary-file <path>`

Pop should:

- persist child-session summary
- validate the returned result structure
- attach the summary to parent subtask context
- mark child session complete
- return control to the parent session

Implementation staging note:

- `session pop --session <id> --file <path>` now reads a JSON result artifact, validates the bounded merge-back shape, persists it in `child_session_results`, and attaches the same payload into the parent subtask context
- the parent run remains on the same compiled subtask after pop; no hidden cursor advancement occurs

After merge-back:

- the parent resumes at the same compiled subtask it was on before the push
- the parent runtime decides whether the returned result is sufficient to continue or whether the parent subtask should retry, revise, fail, or pause

This is for context isolation only. The parent node remains the owner of git state and workflow progress.

---

## 16. Recovery and resume behavior

If a run is interrupted:

1. inspect `node_runs`, `node_run_state`, `sessions`, and current git state
2. determine whether the bound primary session is still recoverable
3. if recoverable, reattach or resume it
4. if not recoverable, create a replacement session
5. reload compiled workflow and current cursor
6. continue from the current compiled subtask

### Recovery priorities

1. preserve durable cursor correctness
2. preserve session continuity when possible
3. avoid duplicate active primary sessions
4. avoid losing the current subtask attempt history

Recommended recovery scenarios to distinguish explicitly:

- healthy attached session
- healthy detached session
- stale session with live tmux
- lost tmux with recoverable run
- provider session available but tmux lost
- resumable run with no viable session
- non-resumable run
- git state mismatch
- duplicate active primary sessions

### Provider-agnostic rule

If provider session identity is unavailable or unreliable, recovery should still work using:

- node run state
- tmux session state if available
- branch/head state
- compiled workflow and attempt history

If provider or tmux state conflicts with durable run state, the durable run state is authoritative unless the runtime explicitly proves it is stale.

---

## 17. Idle detection and nudge behavior

If a session goes idle unexpectedly:

1. detect missing or stale heartbeat
2. inspect current run state
3. reissue current subtask summary and context
4. remind the session how to complete or fail the stage
5. record a nudge event

The nudge payload should include:

- current subtask title
- prompt or command summary
- expected completion command
- expected failure-summary command

Repeated idle behavior should be bounded by runtime policy and may escalate into:

- another nudge
- pause for user
- failure handling

Implementation staging note:

- the current implementation derives idle state from tmux/fake-session polling rather than a dedicated heartbeat-history table
- idle audit is currently recorded through `session_events` using `nudged`, `nudge_skipped`, `nudge_suppressed`, and `nudge_escalated`
- stable alt-screen sessions are classified from their captured pane content and may be nudged automatically once they remain unchanged past the idle threshold; alt-screen only blocks nudging when the captured content still shows active-work markers
- the staged escalation path pauses the run with `pause_flag_name = "idle_nudge_limit_exceeded"` after the configured max nudge count is exceeded
- the current classifier now also records `screen_polled` evidence with pane-hash comparison metadata and classifies the screen as `active`, `quiet`, or `idle`
- first-sample polling may still classify as `idle` when the idle threshold is already exceeded, but the daemon's autonomous background loop now waits for later `unchanged_screen_past_idle_threshold` evidence before emitting the first timeout-driven nudge
- daemon-originated nudge text is treated as non-progress for subsequent idle checks so repeated nudge/escalation decisions do not reset themselves accidentally
- once the active compiled subtask has durably registered a summary, later idle sweeps suppress further nudges for that session attempt with `nudge_skipped(reason=summary_already_registered)` so end-of-flow output generation is treated as done-enough progress rather than a reason to nag again

Recommended workflow-event scope for first implementation:

- pause entered/cleared
- recovery attempted/succeeded/failed
- replacement session created
- parent decision events
- cutover events

---

## 18. Compilation boundary and runtime policy

The runtime must respect the compile boundary.

Compiled workflow includes:

- resolved tasks and subtasks
- hooks
- validations
- selected review/testing/docs stages
- dependency graph

Pure runtime policy may remain outside compiled workflow if it does not change semantic workflow behavior.

Examples of likely runtime policy:

- heartbeat interval
- idle timeout
- maximum nudge count

If a policy changes stage structure or gating behavior, it must be part of compiled workflow lineage.

Implementation staging note:

- the current compiler now materializes supported hooks as explicit compiled subtasks before runtime begins; the daemon executes those subtasks through the normal compiled workflow cursor rather than as hidden runtime side effects
- `workflow hooks --node <id>` and `workflow hooks --workflow <id>` are now the canonical inspection surfaces for selected hooks, skipped hooks, and hook-expanded subtask order

---

## 19. Rectification command loop behavior

Rectification should use the same durable execution model as normal runs.

### Rectification loop

1. create or load rectification run
2. bind primary session
3. execute reset-to-seed stage
4. execute merge-children stage
5. execute reconcile stage
6. execute validation, review, testing, provenance, docs, and finalize stages
7. if successful, continue upstream rectification if required

### Conflict handling

If merge conflict occurs:

1. persist merge-conflict record
2. transition into reconcile/conflict-resolution stage
3. if resolved, continue the quality-gate pipeline
4. if unresolved, fail to parent or pause for user according to policy

---

## 20. Required operator surfaces for runtime debugging

Operators and AI sessions should be able to inspect:

- current run state
- current compiled subtask
- current subtask attempt
- active primary session
- pushed child sessions
- validation/review/testing results
- dependency blockers
- active pause reason
- recent session events
- recent summaries

No critical runtime variable should be hidden only in process memory.

---

## 21. Operational rule

A node run must always be reconstructible from:

- source YAML and overrides as of compilation time
- compiled workflow snapshot
- current cursor state
- prior subtask attempts
- session records and events
- quality-gate results
- summaries
- git seed/head/final lineage

If the runtime cannot reconstruct execution from those artifacts, it is violating the model.

Implementation staging note:

- the current runtime now supports durable attempt-history reads through `subtask attempts --node <id>` and `subtask attempt-show --attempt <id>`
- `subtask complete` and `subtask fail` may now carry explicit `execution_result_json` payloads; these are stored durably and mirrored into `output_json` for compatibility with already-implemented gate/runtime consumers
- real shell or tool execution still remains session-driven rather than daemon-owned

---

## 22. V2 closure notes

This V2 runtime loop spec resolves or reduces the following prior gaps:

- clearer actor ownership between session, runtime, and durable state
- clearer integration of review/testing/docs into the runtime loop
- clearer recovery and nudge behavior
- clearer distinction between child nodes and pushed child sessions

Remaining follow-on work still needed:

- fold the child-session result contract into final DB and CLI implementation details
- wire the frozen minimum workflow-event set for pause, recovery, parent decisions, and cutover into implementation-grade runtime, DB read-model, and CLI planning
- align implementation slicing with the current authority and recovery model
