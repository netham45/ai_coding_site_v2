# Child Session Merge-Back Contract

## Purpose

This document defines how a pushed child session returns its work to the parent session.

The system already distinguishes:

- child nodes, which own their own runs
- pushed child sessions, which are temporary context-isolated helpers

What remained underspecified was the exact contract for how pushed child sessions hand results back to the parent.

This note makes that handoff explicit enough to support:

- runtime implementation
- auditability
- CLI behavior
- safe parent-session resume

Related documents:

- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/runtime/tmux_session_lifecycle_spec_v1.md#recovery-classification-and-actions`
- `notes/specs/database/database_schema_spec_v2.md`
- `notes/catalogs/traceability/cross_spec_gap_matrix.md`

---

## Core Rule

Pushed child sessions do not mutate the parent cursor directly.

Instead:

1. parent session pushes child session
2. child session performs bounded work
3. child session produces a structured return artifact
4. parent runtime attaches that artifact to parent context
5. parent session resumes and decides how to use it

This keeps ownership clear:

- parent owns node run and cursor
- child session owns only its bounded result payload

---

## What A Child Session Is Allowed To Return

A pushed child session should return one or more of:

- summary text
- structured findings
- file paths to produced artifacts
- suggested next actions
- failure reason if it could not complete

It should not directly return:

- cursor advancement commands as authoritative truth
- branch ownership changes
- direct mutation of parent lifecycle state without parent/runtime acceptance

---

## Recommended Return Artifact Shape

The merge-back contract should use a structured return artifact.

Example conceptual shape:

```yaml
child_session_result:
  child_session_id: string
  parent_node_id: string
  parent_compiled_subtask_id: string
  status: success|partial|failed
  summary: string
  findings:
    - string
  artifacts:
    - path: string
      type: file|report|notes|other
  suggested_next_actions:
    - string
```

This does not have to be literal YAML in implementation, but the returned structure should be conceptually similar.

---

## Child Session Status Outcomes

The child session should end in one of these outcome categories.

### `success`

Meaning:

- bounded work completed
- summary/artifacts are ready for parent use

### `partial`

Meaning:

- useful information was gathered, but the child session could not fully complete the intended bounded task

### `failed`

Meaning:

- the child session could not complete usable work
- failure summary should still be returned if possible

The parent should treat these as advisory bounded-work outcomes, not as direct node-run terminal states.

---

## Parent Merge-Back Behavior

When a child session finishes:

1. validate the returned artifact
2. persist the child session result or summary
3. attach result to the parent subtask context
4. mark child session complete
5. return control to the parent session

The parent session then decides whether to:

- continue
- revise
- push another child session
- fail/pause according to the parent subtask logic

The child session itself should not make that final decision.

---

## Parent Context Attachment Rule

The parent should receive the child session result as explicit context input to the still-active parent compiled subtask.

That means:

- the parent subtask remains the same logical stage
- the child session result becomes one of the parent subtask’s inputs

This is important because pushed child sessions are context helpers, not independent workflow stages.

Implementation staging note:

- the current implementation now attaches merge-back payloads into the parent subtask context through the active run state's current subtask context surface
- the canonical durable store remains `child_session_results`; the attached parent-context copy is a convenience projection for the still-active parent subtask

---

## Artifact Return Rule

If the child session produced files or other artifacts:

- the parent should receive references to them
- the parent should validate them if required
- the parent should decide whether they satisfy the bounded-work purpose

The system should not assume file production alone means success.

---

## Failure Merge-Back Rule

If the child session fails:

- it should still attempt to return a structured failure summary
- the failure should be attached to the parent context
- the parent decides whether:
  - the failure is acceptable and still informative
  - another child session should be pushed
  - the parent subtask should fail or pause

This keeps the child session from bypassing parent failure logic.

---

## Validation Of Child Results

The parent or runtime should validate:

- that the child result belongs to the expected parent subtask
- that the child session ID is valid
- that the returned artifact shape is structurally valid
- that required files or outputs exist if claimed

If the returned artifact is invalid:

- do not merge it silently
- record the issue
- treat the child session result as failed or invalid

---

## Pseudocode

```python
def pop_child_session(child_session_id, summary_file):
    result = load_child_session_result(summary_file)
    validate_child_session_result(result, child_session_id)

    persist_child_session_result(child_session_id, result)
    attach_result_to_parent_context(
        parent_subtask_id=result.parent_compiled_subtask_id,
        child_session_id=child_session_id,
        result=result,
    )

    mark_child_session_complete(child_session_id, result.status)
    return "merged_back"
```

---

## Parent Resume Rule

After merge-back:

- the parent session should resume at the same compiled subtask it was on before the push
- it should not auto-advance unless the parent runtime logic explicitly accepts the child-session result and completes the parent subtask

This prevents pushed child work from creating hidden cursor jumps.

## Child Bootstrap Prompt Rule

The delegated child-session bootstrap prompt must include:

- the durable child session id
- the explicit `session pop --session <id> --file <path>` command the child must run to merge back
- the allowed result shape fields
- clear instruction that the delegated `reason` is the authoritative scope unless additional concrete child inputs are present

If the delegated reason is present but no further concrete child work is available in the prompt or workspace, the child session may return a bounded `partial` result instead of stalling while searching for hidden scope.

---

## DB Implications

The current DB model supports:

- `sessions`
- `session_events`
- `summaries`
- `child_session_results`

`child_session_results` is the canonical durable store for pushed child-session return artifacts.

Minimum fields:

- `id`
- `child_session_id`
- `parent_compiled_subtask_id`
- `status`
- `result_json`
- `created_at`

Summaries and session events may still provide convenience views, but they are not the only durable home for the returned artifact.

---

## CLI Implications

Current or likely useful commands:

- `ai-tool session push --node <id> --reason <reason>`
- `ai-tool session pop --session <id> --file <path>`
- `ai-tool session show --session <id>`
- `ai-tool session events --session <id>`

Potential useful addition:

- `ai-tool session result show --session <id>`

Implementation staging note:

- the current implementation expects the pop file to be JSON carrying the structured merge-back artifact rather than a plain summary-only text file

If naming differs, the capability should still exist.

---

## Interaction With Recovery

If a child session is interrupted:

- the parent cursor should remain unchanged
- the child session can be recovered or replaced independently if policy allows
- if recovery fails, the parent should receive a child-session failure summary rather than ambiguous silence

This is important because pushed child sessions are optional bounded helpers, not the primary run owner.

---

## Interaction With Parent Failure Logic

Child-session failure is not the same as child-node failure.

It should usually be treated as:

- a subtask-level bounded helper failure inside the parent node

The parent subtask may then:

- retry pushing a child session
- continue with partial results
- fail or pause

This should not automatically increment parent child-node failure counters unless the system intentionally broadens the term “child” to include sessions, which is not recommended.

---

## Open Decisions Still Remaining

### D01. Whether partial results should count as success for parent gating

Recommended direction:

- parent logic should decide, not the child session

### D02. Whether child sessions may return multiple artifact files

Recommended direction:

- yes, as long as they are referenced explicitly

---

## Recommended Next Follow-On Work

The next docs that should absorb this logic are:

1. `notes/specs/runtime/runtime_command_loop_spec_v2.md`
2. `notes/specs/database/database_schema_spec_v2.md`
3. `notes/specs/cli/cli_surface_spec_v2.md`
4. `notes/catalogs/traceability/cross_spec_gap_matrix.md`

Then reduce the severity of the child-session merge-back gap.

---

## Exit Criteria

This note is complete enough when:

- the child-session return artifact is explicit
- parent ownership is explicit
- merge-back validation is explicit
- DB and CLI implications are identified

At that point, pushed child sessions are concrete enough to stop being a vague runtime convenience.
