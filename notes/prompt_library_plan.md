# Prompt Library Plan

## Purpose

This document defines the default authored prompt pack for the system.

The existing notes already define prompt roles, prompt history, and prompt retrieval, but they do not yet provide one place that answers:

- what the default prompts are
- which runtime situation uses which prompt
- what completion or failure contract each prompt expects
- how CLI usage should be explained to a session when it starts, stalls, or recovers

This note is the missing prompt-layer counterpart to:

- `notes/default_yaml_library_plan.md`
- `notes/runtime_command_loop_spec_v2.md`
- `notes/review_testing_docs_yaml_plan.md`
- `notes/session_recovery_appendix.md`
- `notes/parent_failure_decision_spec.md`

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

Default prompts should use placeholders such as:

- `<node_id>`
- `<compiled_subtask_id>`
- `<layout_path>`
- `<summary_path>`
- `<user_request>`
- `<acceptance_criteria>`

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

Prompt:

```text
Review the current node output for node <node_id>.

Requirements:
<acceptance_criteria>

Inputs available:
- changed files
- validation results
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
- `ai-tool subtask current --node <node_id>`
- `ai-tool subtask prompt --node <node_id>`
- `ai-tool subtask context --node <node_id>`

While working:
- mark start with `ai-tool subtask start --compiled-subtask <compiled_subtask_id>`
- send heartbeats with `ai-tool subtask heartbeat --compiled-subtask <compiled_subtask_id>`

When finished successfully:
- register any required summary with `ai-tool summary register ...` if needed
- then complete with `ai-tool subtask complete --compiled-subtask <compiled_subtask_id>`

If blocked or unable to satisfy the stage:
- write a concise failure summary
- fail safely with `ai-tool subtask fail --compiled-subtask <compiled_subtask_id> --summary-file <summary_path>`

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

---

## Default Ownership Rule

This prompt library is a spec artifact, not an excuse to hide behavior in prose.

The system still needs:

- compiled tasks and subtasks
- explicit validations
- explicit result models
- explicit runtime policy

Prompts tell the session how to act inside those contracts. They do not replace the contracts.
