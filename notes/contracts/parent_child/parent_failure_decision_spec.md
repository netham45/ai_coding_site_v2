# Parent Failure Decision Spec

## Purpose

This document defines how a parent node should respond when one of its children fails.

This area has existed in the design at a policy level, but it has remained one of the most important unresolved runtime gaps. The goal here is to turn it into explicit decision logic that can later be folded into the canonical lifecycle/runtime specs.

Related documents:

- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/database/database_schema_spec_v2.md`
- `notes/specs/prompts/prompt_library_plan.md`
- `notes/catalogs/traceability/cross_spec_gap_matrix.md`

---

## Core Rule

Failure escalates only to the parent.

That means:

- a child does not directly fail the whole tree
- a child records its own failure durably
- the parent becomes the decision-maker for the next step
- the parent may retry, revise locally, pause for the user, or eventually fail upward through its own node behavior

This keeps failure handling compositional and prevents uncontrolled cross-tree escalation.

---

## Parent Failure Inputs

When a child fails, the parent decision logic should evaluate at least the following.

### Child-level inputs

- failed child node version ID
- child node kind and tier
- child failure summary
- child failed subtask or stage
- child retry history
- child run count
- whether the child failure occurred during normal generation or rectification

### Parent-level inputs

- parent node kind and tier
- parent current lifecycle state
- parent dependency state
- parent current child-failure counters
- parent retry/replan policy
- parent pause threshold policy
- whether the parent is already in a degraded or paused state

### Context-level inputs

- whether sibling children have already completed successfully
- whether the failed child is dependency-critical for other siblings
- whether the child was automatically generated or manually defined
- whether a recent parent layout or spec change likely caused the failure
- whether the failure type suggests local child retry versus parent replan

---

## Failure Classification

The parent should classify the child failure before deciding what to do.

Recommended failure classes:

- `transient_execution_failure`
- `validation_failure`
- `review_failure`
- `test_failure`
- `merge_conflict_unresolved`
- `manual_tree_conflict`
- `rectification_failure`
- `bad_layout_or_bad_requirements`
- `dependency_or_context_failure`
- `environment_failure`
- `provider_recovery_failure`
- `unknown_failure`

These classes do not need to be exposed exactly as written, but the decision logic needs categories like them.

---

## Parent Decision Outcomes

The parent should choose one of the following outcomes.

### Outcome 1: Retry child

Use when:

- the failure appears transient
- the child has remaining retry budget
- the failure does not indicate a structural planning issue

### Outcome 2: Regenerate child version

Use when:

- the child workflow/spec likely needs a clean rerun
- the failure suggests local child state corruption or stale assumptions
- the parent still believes the current layout/plan is valid

### Outcome 3: Replan or revise locally at parent

Use when:

- the child failure suggests the parent layout or requirements are wrong or incomplete
- multiple children are failing in related ways
- dependency assumptions are invalid

### Outcome 4: Pause for user

Use when:

- failure thresholds are exceeded
- the parent cannot resolve ambiguity safely
- the failure may indicate conflicting design goals
- manual approval or clarification is required

### Outcome 5: Fail upward later through parent failure

Use when:

- the parent’s own recovery attempts are exhausted
- the parent is itself blocked from progressing meaningfully

This is not an immediate direct child-to-grandparent escalation. The parent first becomes the failing node.

---

## Default Parent Decision Algorithm

The following is the recommended default decision order.

## Step 1: Record failure impact

When a child fails:

1. record the child failure summary against the parent context
2. increment:
   - total child failure count
   - consecutive child failure count
   - per-child failure count
3. mark the child as failed in the parent’s child-state view

The parent should not make a decision before the failure is durably recorded.

Canonical durability rule:

- total and consecutive counters live on `node_run_state`
- per-child counters live in `node_run_child_failure_counters`
- `workflow_events` records the decision trail, not the only durable home of required counters

Implementation staging note:

- the current implementation now persists per-child counters in `node_run_child_failure_counters` with the latest failure class, summary, subtask key, failed child run id, and last chosen decision
- parent decisions are recorded in `workflow_events` with `event_scope = parent_decision` and event types `parent_retry_child`, `parent_regenerate_child`, `parent_replan`, and `parent_pause_for_user`
- decision payloads now include explicit matrix detail: `failure_origin`, `classification_reason`, `decision_reason`, `options_considered`, `threshold_triggered`, `threshold_reason`, and the frozen threshold policy snapshot used for the decision
- the first implementation slice deliberately reuses `pause_context` plus `workflow_events` for pause/replan summaries instead of creating a separate dedicated parent-summary table

## Step 2: Classify the failure

Classify the child failure using:

- failure type
- child output summary
- failing stage
- recent history

If the failure cannot be classified confidently, treat it as `unknown_failure`.

## Step 3: Check hard stop thresholds

If any configured threshold is exceeded:

- total child failure threshold
- consecutive child failure threshold
- per-child failure threshold

then:

- produce a parent summary
- transition the parent to `PAUSED_FOR_USER`
- stop automatic recovery

This should be the default safety valve.

## Step 4: Check whether retry is appropriate

Retry the child if all of the following are true:

- failure class is retryable
- child retry budget remains
- the child is not blocked by a known invalid layout or parent assumption
- retry does not violate policy

If true:

- schedule child retry or rerun
- record the decision
- return

Current retryability guidance in the shipped matrix:

- `transient_execution_failure` -> prefer `retry_child` while threshold budget remains
- `environment_failure` -> prefer `retry_child` while threshold budget remains
- `merge_conflict_unresolved` -> prefer `regenerate_child`
- `rectification_failure` -> prefer `regenerate_child`
- `validation_failure` -> prefer `replan_parent`
- `review_failure` -> prefer `replan_parent`
- `test_failure` -> prefer `replan_parent`
- `bad_layout_or_bad_requirements` -> prefer `replan_parent`
- `dependency_or_context_failure` -> prefer `replan_parent`
- `manual_tree_conflict` -> prefer `replan_parent`
- `provider_recovery_failure` -> prefer `pause_for_user`
- `unknown_failure` -> prefer `pause_for_user`

## Step 5: Check whether child regeneration is appropriate

Regenerate the child version if:

- failure suggests stale child state or corrupted branch/workflow state
- retry alone is unlikely to help
- the parent still considers the current layout/requirements valid

If true:

- create superseding child version if policy allows
- schedule regenerated child
- record the decision
- return

## Step 6: Check whether parent-local replan is appropriate

Revise the parent layout or parent-local plan if:

- the failure suggests the child was given bad inputs
- multiple related children are failing
- dependency assumptions appear invalid
- the child goal is impossible or contradictory under current parent requirements

If true:

- transition parent into local replanning/review path
- record a summary explaining why the parent, not the child, is being changed
- update the parent’s layout or task plan
- restart affected child generation as needed
- return

## Step 7: Pause for user

If none of the above gives a confident safe path:

- register a structured parent summary
- transition parent to `PAUSED_FOR_USER`
- await explicit user guidance

---

## Parent Failure Prompt Payloads

The default prompt pack should include authored parent-failure messages rather than leaving this to improvised summaries.

The broader default text lives in `notes/specs/prompts/prompt_library_plan.md`.

## Parent pause-for-user payload

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
```

## Parent-local replan payload

```text
Revise the parent-local plan for node <node_id> because a child failure suggests
bad layout, missing requirements, or invalid dependency assumptions.

Failed child summary:
<child_failure_summary>

Current parent layout and constraints:
<current_layout_context>

Revise only what is needed to make the parent plan executable again.
Preserve still-valid sibling work when possible.
```

---

## Retryability Matrix

The default policy should treat failure classes approximately like this.

| Failure Class | Retry Child | Regenerate Child | Parent Replan | Pause For User |
| --- | --- | --- | --- | --- |
| transient_execution_failure | yes | maybe | no | maybe |
| validation_failure | maybe | maybe | maybe | maybe |
| review_failure | maybe | maybe | yes | maybe |
| test_failure | maybe | maybe | maybe | maybe |
| merge_conflict_unresolved | no | maybe | maybe | yes |
| bad_layout_or_bad_requirements | no | no | yes | maybe |
| dependency_or_context_failure | maybe | maybe | yes | maybe |
| environment_failure | maybe | maybe | no | maybe |
| unknown_failure | maybe | maybe | maybe | yes |

This matrix is guidance, not a substitute for policy rules.

---

## Consecutive Versus Total Failure Logic

These two counters should drive different decisions.

### Consecutive child failures

Use this to detect that the parent is actively stuck right now.

High consecutive failures should push the parent toward:

- replan
- pause for user

### Total child failures

Use this to detect broad instability over time.

High total failures should push the parent toward:

- more conservative automatic behavior
- faster user deferment

### Per-child failure count

Use this to detect one child repeatedly failing while others are healthy.

High per-child count should push the parent toward:

- regenerating or replanning around that child specifically

---

## Parent Summary Requirements

When the parent pauses or changes strategy because of child failure, it should register a structured summary including:

- failed child IDs and names
- child failure classes
- failed stages or subtasks
- retries already attempted
- whether sibling children succeeded
- likely root cause
- why the chosen parent action was selected
- recommended next actions

This summary is critical for both user understanding and later auditability.

---

## Pseudocode

```python
def handle_child_failure_at_parent(parent_node_id, child_node_id):
    failure = load_latest_child_failure(child_node_id)
    policy = load_parent_failure_policy(parent_node_id)
    counters = load_parent_failure_counters(parent_node_id)

    record_failure_against_parent(parent_node_id, child_node_id, failure)
    counters = increment_parent_failure_counters(parent_node_id, child_node_id)

    failure_class = classify_child_failure(failure)

    if thresholds_exceeded(counters, policy):
        summary = build_parent_pause_summary(parent_node_id, child_node_id, failure, counters)
        register_summary(parent_node_id, summary, "parent_child_failure_pause")
        transition_parent_to_paused(parent_node_id)
        return "paused_for_user"

    if should_retry_child(failure_class, child_node_id, policy):
        schedule_child_retry(child_node_id)
        record_parent_decision(parent_node_id, child_node_id, "retry_child", failure_class)
        return "retry_child"

    if should_regenerate_child(failure_class, child_node_id, policy):
        regenerate_child(child_node_id)
        record_parent_decision(parent_node_id, child_node_id, "regenerate_child", failure_class)
        return "regenerate_child"

    if should_replan_parent(parent_node_id, child_node_id, failure_class, policy):
        summary = build_parent_replan_summary(parent_node_id, child_node_id, failure, counters)
        register_summary(parent_node_id, summary, "parent_replan")
        enter_parent_replan_flow(parent_node_id)
        record_parent_decision(parent_node_id, child_node_id, "replan_parent", failure_class)
        return "replan_parent"

    summary = build_parent_pause_summary(parent_node_id, child_node_id, failure, counters)
    register_summary(parent_node_id, summary, "parent_child_failure_pause")
    transition_parent_to_paused(parent_node_id)
    record_parent_decision(parent_node_id, child_node_id, "pause_for_user", failure_class)
    return "paused_for_user"
```

---

## DB Implications

The current DB model can support much of this through:

- `node_run_state` counters
- `summaries`
- child/node status

But V2 implementation should consider whether additional structures are needed.

### Likely useful additions

- `parent_failure_decisions`

Possible fields:

- `id`
- `parent_node_version_id`
- `child_node_version_id`
- `failure_class`
- `decision_type`
- `decision_summary`
- `created_at`

### Possible alternative

Current canonical direction:

- parent decisions should at minimum be visible through canonical workflow-event storage
- a dedicated `parent_failure_decisions` table may still be useful if workflow-event payloads prove too opaque

---

## CLI Implications

The CLI should support visibility into this logic.

Likely useful commands:

- `ai-tool node child-failures --node <id>`
- `ai-tool node failure-counters --node <id>`
- `ai-tool node decision-history --node <id>`
- `ai-tool node respond-to-child-failure --node <id> --child <child_id> [--action <decision>]`

If the names differ, these capabilities should still exist.

---

## Interaction With Replanning

Parent replanning should be treated as a first-class parent response, not an accidental side effect.

When parent replanning happens:

1. the parent should record why child failure triggered replan
2. the parent should identify which children are affected
3. unaffected healthy children should be reused if policy allows
4. affected children may need regeneration or replacement

This helps avoid unnecessary full-tree churn.

---

## Interaction With User Guidance

The parent should defer to the user when:

- thresholds are exceeded
- the parent detects conflicting or impossible requirements
- the system cannot confidently choose between retry, regeneration, or replan
- automatic recovery would risk destructive or misleading behavior

User-facing summaries should be concise but structured enough to explain:

- what failed
- what the system tried
- what the system thinks is wrong
- what options exist next

---

## Recommended Next Follow-On Work

The next docs that should absorb this logic are:

1. `notes/specs/runtime/node_lifecycle_spec_v2.md`
2. `notes/specs/runtime/runtime_command_loop_spec_v2.md`
3. `notes/specs/database/database_schema_spec_v2.md`
4. `notes/specs/cli/cli_surface_spec_v2.md`

Then rerun the cross-spec gap matrix and reduce the severity of the parent-failure gap.

---

## Exit Criteria

This spec is complete enough when:

- the parent decision outcomes are explicit
- the parent decision order is explicit
- the role of counters and thresholds is explicit
- DB/CLI implications are identified
- the design no longer treats parent failure handling as only vague policy prose
