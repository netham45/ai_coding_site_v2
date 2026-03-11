# Prompt Library Plan

## Purpose

This document defines the default authored prompt pack for the system.

The existing notes already define prompt roles, prompt history, and prompt retrieval, but they do not yet provide one place that answers:

- what the default prompts are
- which runtime situation uses which prompt
- what completion or failure contract each prompt expects
- how CLI usage should be explained to a session when it starts, stalls, or recovers

This note is the missing prompt-layer counterpart to:

- `notes/catalogs/inventory/default_yaml_library_plan.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/planning/expansion/review_testing_docs_yaml_plan.md`
- `notes/specs/runtime/tmux_session_lifecycle_spec_v1.md#prompt-bootstrap-and-prompt-log-contract`
- `notes/contracts/parent_child/parent_failure_decision_spec.md`

Implementation staging note:

- the current implementation now ships authored default prompt assets for layout generation, execution, review, testing interpretation, docs generation, pause, and runtime bootstrap/recovery/nudge surfaces
- those prompts now carry explicit stage and recovery contracts instead of placeholder prose, and the packaged default system validates that built-in YAML prompt bindings resolve to real renderable assets
- the current implementation now also validates the packaged runtime/hook/policy layer as one operational-library contract, so required built-in prompt assets and prompt-reference keys fail compile-time integrity checks before workflow compilation if they drift
- the packaged `testing/interpret_test_results.md` prompt is now a daemon-exposed inspection surface for explicit testing stages, while the broader default node ladder still stages testing behind explicit task/policy/override selection instead of silently enabling `test_node` everywhere
- the current turnkey `node quality-chain` path reuses the existing built-in review/testing/docs/provenance prompt assets and does not introduce a separate prompt family for late-chain orchestration
- project policy now also controls prompt-pack selection at compile time, with the current implementation supporting safe selection between the packaged `default` and `project` prompt roots
- child-node spawning currently reuses those existing layout-generation prompts and the authored built-in layout YAMLs; no separate prompt family was required just to materialize default children durably
- manual tree construction currently does not introduce a new prompt family; explicit reconciliation guidance prompts remain deferred until the later remove/replace/reconcile phases
- conflict detection now adds a dedicated packaged recovery prompt for merge-conflict pause handling so operator-facing conflict summaries do not rely on ad hoc runtime strings
- parent-child merge/reconcile now uses the packaged `execution/reconcile_parent_after_merge.md` prompt as a first-class daemon-exposed inspection surface; the daemon pairs it with durable child-result and merge-event context rather than ad hoc runtime prose
- stage-start prompt retrieval now also carries a daemon-assembled context bundle so prompt consumers can reference durable startup metadata, dependency state, recent summaries, and child/reconcile context without scraping prior terminal output
- compile-time prompt rendering now uses a shared daemon renderer with deterministic scope precedence; rendered prompt text is frozen into compiled subtasks and durable prompt history, while prompt-template source lineage remains separate for auditability
- the frozen render stage is now inspectable directly through `workflow rendering`, so prompt-pack debugging does not require opening the full compiled workflow payload
- prompt-reference YAML is now schema-validated as its own rigid family: keys must use dotted identifiers, values must be prompt-pack-relative markdown paths, and referenced prompt assets must exist in the packaged prompt roots
- the execution prompt now treats an explicit node-authored wait-for-nudge instruction as higher priority than the default leaf-task CLI workflow, and it forbids replacing that wait with shell activity such as `sleep`, slash commands, polling, or background terminals; the only allowed pre-nudge output is at most one short visible operator-facing wait-status line that is not durably registered as a summary
- the packaged layout-generation prompts now include the explicit parent handoff `python3 -m aicoding.cli.main node register-layout --node {{node_id}} --file layouts/generated_layout.yaml` after writing the generated layout, so parent decomposition does not rely on implicit daemon workspace discovery

---

## Prompt Authoring Rules

Every built-in prompt should follow these rules.

### 1. State the exact job

The prompt should say what stage is being executed and what artifact or decision it is responsible for.

### 2. State the output contract explicitly

The prompt should say:

- what file(s) to write or update
- what structured response to return
- what status values are allowed

### 3. Reference CLI completion/failure commands when the session is expected to drive them

Operational prompts should remind the session how to:

- inspect current work
- mark progress
- register summaries
- fail safely instead of stalling

### 4. Avoid hiding validation logic in prose

The prompt may restate important checks, but compiled validations remain authoritative.

### 5. Be reusable with placeholders

Default prompts should prefer canonical placeholders such as:

- `{{node_id}}`
- `{{compiled_subtask_id}}`
- `{{layout_path}}`
- `{{summary_path}}`
- `{{user_request}}`
- `{{acceptance_criteria}}`

Compatibility note:

- legacy angle-bracket placeholders such as `<node_id>` are still supported by the renderer for compatibility
- new authored packaged prompts should prefer `{{variable}}`, and the default prompt pack now follows that rule
- only daemon-owned compile-time render contexts are authoritative; prompt files do not define their own rendering algorithm

---

## Prompt Families

The default prompt pack should cover at least:

1. layout generation
2. leaf-task execution
3. review/testing/docs stages
4. runtime CLI bootstrap and correction messages
5. idle nudge and recovery messages
6. parent failure and pause messages

---

## 1. Layout Generation Prompts

## PL01. Generate phase layout

Used by:

- epic-like parent nodes that must create `phase` children

Prompt:

```text
You are generating a phase layout for node <node_id>.

User request:
<user_request>

Available context:
- current node goal and rationale
- repository/research summaries
- policy constraints
- existing accepted child summaries if any

Produce a `layout_definition` that creates only the minimum set of `phase`
children required to satisfy the request.

Requirements:
- every child must have a clear goal and rationale
- dependencies must be valid and minimal
- acceptance criteria must be concrete and reviewable
- do not create duplicate or overlapping children
- prefer fewer, larger phases over speculative fragmentation

Write the layout to:
<layout_path>

Immediately after writing the approved layout, register it explicitly through:
`python3 -m aicoding.cli.main node register-layout --node {{node_id}} --file <layout_path>`

Return JSON only:
{"status":"OK","written_file":"<layout_path>","child_count":<n>}
or
{"status":"FAIL","message":"<reason>"}
```

## PL02. Generate plan layout

Used by:

- phase-like parent nodes that must create `plan` children

Prompt:

```text
You are generating a plan layout for node <node_id>.

Phase goal:
<node_goal>

Parent requirements:
<acceptance_criteria>

Create a `layout_definition` containing the minimum set of `plan` children
needed to deliver this phase coherently.

Requirements:
- each child kind must be `plan`
- each child must own a distinct slice of work
- dependencies must reflect real ordering constraints only
- acceptance criteria must mention outputs, validation, and summary/reporting
- avoid speculative children with no direct requirement trace

Write the layout to:
<layout_path>

Immediately after writing the approved layout, register it explicitly through:
`python3 -m aicoding.cli.main node register-layout --node {{node_id}} --file <layout_path>`

Return JSON only:
{"status":"OK","written_file":"<layout_path>","child_count":<n>}
or
{"status":"FAIL","message":"<reason>"}
```

## PL03. Generate task layout

Used by:

- plan-like parent nodes that must create `task` children

Prompt:

```text
You are generating a task layout for node <node_id>.

Plan goal:
<node_goal>

Plan acceptance criteria:
<acceptance_criteria>

Repository and prior context:
<relevant_context>

Create a `layout_definition` containing the minimum set of `task` children
needed to implement the plan.

Requirements:
- each child kind must be `task`
- each child must have a crisp implementation goal
- acceptance criteria must be directly testable
- avoid splitting work unless the boundary materially improves execution or
  dependency management
- if one task is enough, create exactly one task

Write the layout to:
<layout_path>

Immediately after writing the approved layout, register it explicitly through:
`python3 -m aicoding.cli.main node register-layout --node {{node_id}} --file <layout_path>`

Return JSON only:
{"status":"OK","written_file":"<layout_path>","child_count":<n>}
or
{"status":"FAIL","message":"<reason>"}
```

## PL04. Build leaf task execution plan

Used by:

- leaf `task` nodes that do not create child nodes but still need a concrete internal execution shape

Prompt:

```text
You are preparing the execution plan for leaf task node <node_id>.

Task goal:
<node_goal>

Acceptance criteria:
<acceptance_criteria>

Inspect the available codebase context and decide the smallest coherent set of
implementation steps needed to complete the task.

Return JSON only:
{
  "status":"OK",
  "implementation_targets":["..."],
  "validation_targets":["..."],
  "risks":["..."]
}
or
{"status":"FAIL","message":"<reason>"}
```

---

## 2. Execution And Reconcile Prompts

## PL05. Implement leaf task

Used by:

- the main implementation stage of a leaf `task` node

Prompt:

```text
Implement the current leaf task for node <node_id>.

Goal:
<node_goal>

Acceptance criteria:
<acceptance_criteria>

Relevant context:
<relevant_context>

Requirements:
- make only the changes needed for this task
- preserve existing behavior unless the task requires change
- update or add focused tests when needed
- do not claim completion unless the task outputs actually exist
- if blocked, stop and return a failure summary instead of guessing

Return JSON only:
{
  "status":"OK",
  "changed_files":["..."],
  "summary":"<concise summary>"
}
or
{
  "status":"FAIL",
  "message":"<blocking issue>",
  "recommended_failure_class":"<class>"
}
```

## PL06. Parent-local reconcile after child merge

Used by:

- parent reconcile stage after merging child finals or rebuilding from seed

Prompt:

```text
Reconcile parent node <node_id> after merging child outputs.

Merged child summaries:
<child_summaries>

Parent acceptance criteria:
<acceptance_criteria>

Ensure parent-local artifacts, summaries, and acceptance status remain correct.
Only make parent-local changes that are genuinely required by the merged child
state.

Return JSON only:
{
  "status":"OK",
  "summary":"<what changed or that no code change was needed>",
  "changed_files":["..."]
}
or
{"status":"FAIL","message":"<reason>"}
```

Implementation staging note:

- the current implementation now exposes this prompt directly through `node reconcile --node <id>`
- the daemon pairs it with durable `child_results`, `merge_events`, and `blocking_reasons` context so both operators and active sessions can inspect the same reconcile handoff state

---

## 3. Review, Testing, And Docs Prompts

## PL07. Review layout against request

Used by:

- `review_child_layout`

Prompt:

```text
Review the generated layout for node <node_id> against the request and current
context.

Check:
- correct child kind
- minimal child count
- no obvious scope overlap
- valid dependency references
- acceptance criteria cover outputs, validation, and summary/reporting

Return JSON only:
{
  "status":"PASS"|"REVISE"|"FAIL",
  "summary":"<concise assessment>",
  "findings":["..."]
}
```

## PL08. Review node output against requirements

Used by:

- `review_node`
- pre-finalization review

Implementation staging note:

- the current review runtime now expects structured `PASS|REVISE|FAIL` output semantics from this prompt family and persists the resulting status/findings into the durable review framework

Prompt:

```text
Review the current node output for node <node_id>.

Requirements:
<acceptance_criteria>

Inputs available:
- changed files
- validation results

Implementation note: validation-failure correction remains a runtime/quality behavior, but the prompt pack no longer keeps an unbound dedicated `recovery/validation_failed.md` asset unless that surface is rebound by active YAML or daemon selectors.
- test results
- summaries

Check for:
- requirement mismatch
- hidden regressions
- missing edge handling required by the request
- unnecessary scope expansion

Return JSON only:
{
  "status":"PASS"|"REVISE"|"FAIL",
  "summary":"<concise assessment>",
  "findings":["..."]
}
```

## PL09. Testing-stage interpretation prompt

Used by:

- testing stages when test commands have run and the system wants a concise stage summary

Prompt:

```text
Interpret the completed test results for node <node_id>.

Commands run:
<commands_run>

Observed outputs:
<test_outputs>

Pass rules:
<pass_rules>

Return JSON only:
{
  "status":"PASS"|"FAIL",
  "summary":"<concise test assessment>",
  "failed_commands":["..."]
}
```

## PL10. Build node docs

Used by:

- `build_node_docs`

Prompt:

```text
Build the documentation view for node <node_id>.

Include:
- node goal and acceptance criteria
- changed files or merged outputs
- relevant summaries
- review and test outcomes when available
- prompt lineage references where useful

Write outputs to:
<doc_output_paths>

Return JSON only:
{
  "status":"OK",
  "outputs":["..."],
  "summary":"<what was documented>"
}
or
{"status":"FAIL","message":"<reason>"}
```

Implementation note:

- the current documentation-generation slice renders markdown deterministically inside the daemon from durable operator, prompt-history, summary-history, review, testing, and rationale/provenance state
- no prompt-driven docs generation step is executed yet; this prompt remains reserved for a later richer authored-doc pass once the system needs narrative output beyond the deterministic audit views

---

## 4. Runtime CLI Bootstrap And Correction Prompts

## PL11. Session bootstrap / CLI usage prompt

Used by:

- newly bound primary sessions
- replacement sessions after recovery

Prompt:

```text
You are the active session for node <node_id> and compiled subtask
<compiled_subtask_id>.

Use the CLI, not memory, as the source of truth for current work.

Retrieve work with:
- `ai-tool session show-current`
- `ai-tool subtask current --node <node_id>`
- `ai-tool subtask prompt --node <node_id>`
- `ai-tool subtask context --node <node_id>`

While working:
- mark start with `ai-tool subtask start --compiled-subtask <compiled_subtask_id>`
- send heartbeats with `ai-tool subtask heartbeat --compiled-subtask <compiled_subtask_id>`

Implementation staging note:

- the current runtime slice persists `subtask start`
- heartbeat persistence now exists as durable active-attempt metadata, but dedicated heartbeat history is still deferred
- `ai-tool session show-current` now returns the durable node binding (`logical_node_id`, `node_kind`, `node_title`, `run_status`) plus `recovery_classification`, so bootstrap prompts can tell whether the session is healthy or stale before fetching stage work
- `ai-tool subtask prompt --node <node_id>` and `ai-tool subtask context --node <node_id>` now both expose `stage_context_json`, which carries durable startup metadata, current compiled-stage metadata, dependency summaries/blockers, recent prompt/summary history, and cursor-carried child/reconcile context for prompt consumers
- `ai-tool subtask context --node <node_id>` also mirrors that same bundle under `input_context_json.stage_context_json` so prompts or helper layers that already read context payloads do not need a separate bootstrap fetch path
- the shipped execution prompt now renders the original node request directly into the compiled prompt body through `{{node.prompt}}`, so a live tmux/Codex session receives the user/task request even before it decides whether to fetch extra context

When finished successfully:
- for ordinary leaf execution, write the required summary artifact and use `ai-tool subtask succeed --compiled-subtask <compiled_subtask_id> --summary-file <path>`
- for synthesized command subtasks, write `summaries/command_result.json` with at least the real `exit_code` and use `ai-tool subtask report-command --compiled-subtask <compiled_subtask_id> --result-file summaries/command_result.json`
- other lifecycle stages may still use their dedicated composite command or the retained low-level commands until the broader prompt migration lands

Implementation staging note:

- `summary register` is now a real durable command and now writes a dedicated `summaries` history row
- the packaged leaf execution prompt now uses `subtask succeed` as its ordinary success path, so it no longer teaches the full low-level `summary register -> subtask complete -> workflow advance` ritual for successful implementation stages
- synthesized command-subtask prompts now use `subtask report-command` as their command-stage reporting path, so they no longer teach `subtask complete` or `subtask fail` plus a separate `workflow advance` as the normal command-subtask happy path
- the packaged layout-generation prompts now also use `subtask succeed` after successful `node register-layout`, so parent decomposition no longer teaches the low-level success ritual in those authored prompt-pack files
- Python-rendered parent workflow prompts in `workflows.py` must follow the same rule: ordinary parent subtasks should teach `subtask succeed`, command-backed parent subtasks should teach `subtask report-command`, and review subtasks should stay on `review run`
- recovery-oriented built-in task bindings should prefer the `recovery/*` prompt family over duplicate `runtime/*` bootstrap/resume variants; the first retarget slice now binds child-summary recovery and interrupted-run recovery to `recovery/resume_existing_session.md` and `recovery/replacement_session_bootstrap.md`
- generic user-pause bindings should prefer the canonical `pause/*` family over duplicate generic `runtime/*` pause wording; the first retarget slice now binds generic pause tasks to `pause/pause_for_user.md` while keeping `runtime/parent_pause_for_user.md` for parent-specific failure handling
- composite-enabled execution prompts must treat a routed `completed` outcome as terminal; they should stop without extra low-level probing instead of teaching “confirm the run is finished” follow-up commands
- now-unbound duplicate runtime prompt files may not remain as dead assets; after prompt-family retargets land, the duplicate `runtime/pause_for_user.md`, `runtime/resume_existing_session.md`, and `runtime/replacement_session_bootstrap.md` files and their authoritative prompt-reference entries must be removed
- shipped execution prompts must stay within the bounded durable summary taxonomy; implementation-stage summaries currently register as `subtask`, not a separate `implementation` type
- the active attempt still mirrors registered summary metadata for compatibility with existing runtime and validation flows
- for non-composite paths, completion records the attempt result but does not itself move the cursor
- for non-composite paths, the next stage becomes active only after `ai-tool workflow advance --node <node_id>`
- `--result-file` on `subtask complete`, `subtask fail`, and `subtask report-command` is for structured execution-result payloads, so prompt examples should only point it at valid JSON files

Prompt-delivery note:

- `ai-tool subtask prompt --node <node_id>` now records a durable prompt-history row containing the rendered prompt content, the originating `source_subtask_key`, and the frozen template identity (`template_path`, `template_hash`) taken from the compiled subtask source metadata
- the returned prompt payload now also includes `stage_context_json` so runtime prompts can explicitly reference durable startup facts such as the original node prompt, the active trigger reason, dependency blockers, and the most recent run-local summaries without relying on conversational memory

If blocked or unable to satisfy the stage:
- write a concise failure summary
- fail safely with `ai-tool subtask fail --compiled-subtask <compiled_subtask_id> --summary-file <summary_path>`

Implementation staging note:

- the documented file-backed failure path is now implemented directly: the CLI reads `--summary-file` content locally and sends that content as the daemon-owned durable failure summary

- the current implementation marks the attempt `FAILED`, marks the run `FAILED`, and mirrors lifecycle visibility to a parent-facing failure state

Do not invent completion. Use the compiled prompt, context, and checks as the
authoritative stage contract.
```

## PL12. Missed-step / validation-failure prompt

Used by:

- runtime response when required outputs or checks are missing after an attempted completion

Prompt:

```text
The current stage for node <node_id> is not yet complete.

What is still missing:
<missing_requirements>

Current compiled subtask:
<compiled_subtask_id>

Next actions:
1. inspect the current prompt and context again
2. make the missing change or run the missing command
3. only then mark the subtask complete

Helpful CLI commands:
- `ai-tool subtask prompt --node <node_id>`
- `ai-tool subtask context --node <node_id>`
- `ai-tool validation show --node <node_id>`

If you cannot satisfy the missing requirement safely, register a failure summary
and fail the subtask instead of waiting idle.
```

## PL13. Command failed prompt

Used by:

- runtime response when a required command/test exits non-zero

Prompt:

```text
A required command failed for node <node_id>.

Failed command:
<failed_command>

Observed output:
<command_output>

Expected behavior:
<expected_behavior>

Fix the underlying issue and rerun the required command if policy allows.
If the failure reveals a real blocker or contradiction, write a failure summary
and fail the subtask rather than looping without progress.
```

## PL14. Missing required output prompt

Used by:

- runtime response when an expected file, artifact, or summary is absent

Prompt:

```text
The current stage for node <node_id> is missing a required output.

Missing outputs:
<missing_outputs>

Expected by this stage:
<expected_outputs_description>

Create or repair the missing output, then continue.
If the output cannot be produced under the current requirements, stop and fail
the subtask with a concise explanation.
```

---

## 5. Idle, Pause, And Recovery Prompts

## PL15. Idle nudge prompt

Used by:

- `session nudge`
- automatic idle recovery before replacement

Prompt:

```text
This session appears idle while node <node_id> is still active.

Current subtask:
<subtask_title>

Current prompt summary:
<prompt_summary>

To continue:
- inspect work with `ai-tool subtask prompt --node <node_id>`
- inspect context with `ai-tool subtask context --node <node_id>`
- send a heartbeat with `ai-tool subtask heartbeat --compiled-subtask <compiled_subtask_id>`

When done:
- complete with `ai-tool subtask complete --compiled-subtask <compiled_subtask_id>`

If blocked:
- write a concise failure or pause summary
- use `ai-tool subtask fail --compiled-subtask <compiled_subtask_id> --summary-file <summary_path>`

Do not stay idle if the stage is blocked. Either progress, fail safely, or wait
only when the compiled stage explicitly requires waiting.
```

## PL16. Pause-for-user prompt

Used by:

- runtime transition into `PAUSED_FOR_USER`

Implementation staging note:

- compiled subtasks may now carry `block_on_user_flag` and an optional `pause_summary_prompt`
- the shipped built-in pause gate currently pauses with the standard pause-for-user prompt and no separate summary-template override
- explicit approval currently uses CLI/API fields rather than a dedicated approval prompt template

Prompt:

```text
Automatic execution has paused for node <node_id>.

Pause reason:
<pause_reason>

What the system needs from the user:
<required_user_input>

Relevant summaries:
<relevant_summaries>

Do not continue autonomous work until the pause flag is cleared or explicit
guidance is provided.
```

## PL17. Resume existing session prompt

Used by:

- healthy/detached session recovery

Prompt:

```text
Resume active work for node <node_id>.

Recovered state:
- run id: <run_id>
- compiled subtask: <compiled_subtask_id>
- attempt number: <attempt_number>

Reload the current prompt and context through CLI before continuing:
- `ai-tool subtask current --node <node_id>`
- `ai-tool subtask prompt --node <node_id>`
- `ai-tool subtask context --node <node_id>`

Continue from the durable cursor. Do not skip or replay accepted subtasks.
```

## PL18. Replacement session bootstrap prompt

Used by:

- replacement primary sessions created after recovery

Implementation staging note:

- the packaged prompt pack now includes explicit recovery assets for interrupted-session recovery, reuse of an existing session, replacement-session bootstrap, and idle nudge guidance under `prompts/packs/default/recovery/`
- the current implementation also ships a repeated missed-step recovery prompt so the final bounded idle nudge can be stronger than the first reminder without changing workflow semantics
- the idle classifier now distinguishes `active`, `quiet`, and `idle` screen states; only `idle` sessions receive the PL15 nudge payload, while `quiet` sessions remain observable without being interrupted

Prompt:

```text
You are a replacement session for node <node_id>.

The prior session could not be reused safely.

Authoritative state:
- run id: <run_id>
- compiled subtask: <compiled_subtask_id>
- attempt number: <attempt_number>
- recovery reason: <recovery_reason>

Before doing work:
1. inspect current work through CLI
2. confirm the current stage contract
3. send a heartbeat

Required CLI:
- `ai-tool subtask current --node <node_id>`
- `ai-tool subtask prompt --node <node_id>`
- `ai-tool subtask context --node <node_id>`
- `ai-tool subtask heartbeat --compiled-subtask <compiled_subtask_id>`

If local git or output state does not match the current prompt/context, stop and
fail safely rather than guessing.
```

---

## 6. Child Session And Parent Failure Prompts

## PL19. Delegated child-session research prompt

Used by:

- pushed child sessions for bounded research/review/verification

Prompt:

```text
You are a bounded child session supporting parent node <node_id>.

Delegated question:
<delegated_question>

Constraints:
- do not edit parent workflow state
- do not claim parent-stage completion
- return only the focused findings needed by the parent

Return a concise structured summary with:
- findings
- recommended next action
- referenced files or artifacts
```

Implementation staging note:

- the current implementation now uses the packaged delegated child-session prompt when launching bounded child sessions through `session push`

## PL20. Parent pause-for-user summary prompt

Used by:

- parent failure decision logic when child failures exceed safe autonomy

Prompt:

```text
Parent node <node_id> is pausing for user guidance because child recovery is no
longer confidently safe.

Failed child:
<child_node_id>

Failure class:
<failure_class>

Observed pattern:
<failure_pattern_summary>

What the parent considered:
<decision_options_considered>

What the user needs to decide:
<required_user_decision>

Return a concise pause summary suitable for durable registration.
```

## PL21. Parent-local replan prompt after child failure

Used by:

- parent decision path that revises layout or requirements locally

Prompt:

```text
Revise the parent-local plan for node <node_id> because a child failure suggests
bad layout, missing requirements, or invalid dependency assumptions.

Failed child summary:
<child_failure_summary>

Current parent layout and constraints:
<current_layout_context>

Revise only what is needed to make the parent plan executable again.
Preserve still-valid sibling work when possible.

Return JSON only:
{
  "status":"OK",
  "summary":"<what changed and why>",
  "affected_children":["..."]
}
or
{"status":"FAIL","message":"<reason>"}
```

Implementation staging note:

- the current daemon slice now binds `runtime/parent_pause_for_user.md` when parent decision logic pauses for user after child failure
- `runtime/parent_local_replan.md` is now bound when the daemon classifies the child failure as requiring parent-local replanning

---

## Default Ownership Rule

This prompt library is a spec artifact, not an excuse to hide behavior in prose.

The system still needs:

- compiled tasks and subtasks
- explicit validations
- explicit result models
- explicit runtime policy

Prompts tell the session how to act inside those contracts. They do not replace the contracts.
