# Auditability Checklist

## Purpose

This document turns the auditability and reproducibility goals into a concrete review checklist.

The system design repeatedly asserts that:

- no critical orchestration state should exist only in memory
- node behavior should be reconstructible later
- git lineage, workflow lineage, prompt lineage, and rationale should be inspectable

This checklist exists to verify those claims systematically during spec review and later during implementation review.

Related documents:

- `notes/explorations/original_concept.md`
- `notes/planning/expansion/database_schema_v2_expansion.md`
- `notes/planning/expansion/runtime_pseudocode_plan.md`
- `notes/catalogs/traceability/action_automation_matrix.md`
- `notes/catalogs/traceability/cross_spec_gap_matrix.md`

---

## Core Auditability Rule

If a value can affect any of the following, it should have a durable representation or a deliberate, documented exception:

- execution behavior
- scheduling behavior
- pause/resume behavior
- failure handling
- rebuild/rectification behavior
- merge behavior
- operator decisions
- AI-session decisions
- debugging or incident analysis
- documentation or rationale output

If the system cannot later explain why it did something important, the design is carrying hidden state.

This remains true even if live coordination is daemon-owned.

Daemon-owned orchestration is acceptable only if coordination-relevant decisions and resulting transitions are persisted durably enough to reconstruct later.

---

## Checklist Use

Use this checklist during:

- spec review
- v2 rewrite review
- implementation review
- incident/debugging review

Each checklist item can be marked:

- `yes`
- `partial`
- `no`
- `not_applicable`

If a row is `partial` or `no`, capture:

- missing durable state
- missing CLI visibility
- missing pseudocode ownership
- missing audit trail

---

## Current Review Snapshot

This section records the current spec-stage assessment after the v2 rewrite and appendix pass.

These are not implementation guarantees yet. They reflect how complete the design is on paper today.

### Snapshot Legend

- `yes`: the spec package gives a strong answer already
- `partial`: the design direction is good, but one or more implementation-facing decisions are still open
- `no`: the design still lacks a credible answer

### Current Snapshot Summary

| Area | Current State | Notes |
| --- | --- | --- |
| Node identity and lineage | yes | Node versions, supersession, rebuild lineage, and hierarchy are well covered by the v2 DB/lifecycle/git specs. |
| Workflow compilation auditability | partial | Source lineage and resolved workflow lineage are strong; compile-failure persistence is now defined, but still needs folding into canonical implementation structures. |
| Runtime cursor and execution auditability | yes | Run state, cursor state, subtask attempts, and durable compiled workflows are strongly modeled. |
| Session auditability | partial | Session identity and recovery are well defined conceptually, but some edge-case event modeling still needs implementation-level decisions. |
| Dependency and scheduling auditability | partial | Dependency storage and validation direction are strong, but child scheduling and invalid-graph handling were only recently specified and need canonical folding. |
| Failure, pause, and escalation auditability | partial | Failure summaries and parent-decision logic are much stronger now, but workflow-event persistence is still a live decision. |
| Validation, review, and testing auditability | yes | These are now first-class families with explicit result models in the v2 spec package. |
| Git and rebuild auditability | partial | Merge/rebuild/cutover logic is strong, but authority/cutover implementation details still need final normalization. |
| Prompt, summary, and rationale auditability | partial | Prompt history and summaries are well modeled; summary taxonomy still needs final freezing. |
| Documentation and provenance auditability | partial | Docs/provenance are well integrated conceptually, but provenance identity remains confidence-based and needs careful implementation. |
| Action auditability | partial | The automation matrix is strong, but some mutation guardrails and command semantics still need implementation policy. |
| Reproducibility tests | partial | The design mostly supports reconstruction, but a few authority/event-history decisions still affect how cleanly that works in practice. |

### Highest Remaining Auditability Risks

- pause and workflow event history may still be too implicit if `workflow_events` is not added
- authoritative-version and cutover modeling may remain harder to inspect than desired if not made explicit in DB/state views
- summary taxonomy and source-role taxonomy still need final normalization
- provenance identity across refactors will remain confidence-based rather than perfectly deterministic

---

## Section 1: Node Identity And Lineage

### 1.1 Node version identity

- Is every node version durably identified?
- Is logical node identity distinct from version identity?
- Can the system explain which version superseded which older version?
- Can the system show when a version was created and why?

### 1.2 Hierarchy lineage

- Can the system reconstruct the parent/child tree for a node version?
- Can the system reconstruct ancestor and descendant chains?
- Can the system show sibling relationships for a node version?

### 1.3 Rebuild lineage

- Can the system explain why a rebuild happened?
- Can it show old version to new version mapping?
- Can it show whether the rebuild affected only the node, a subtree, or upstream ancestors?

---

## Section 2: Workflow Compilation Auditability

### 2.1 Source lineage

- Can the system show all source YAML documents used to compile a workflow?
- Can it distinguish built-in definitions from project-local extensions and overrides?
- Can it show the content hash of each source document?
- Can it show the source role for each input document?

### 2.2 Resolved workflow auditability

- Can the system show the fully resolved merged YAML?
- Can it show which hooks were inserted and why?
- Can it show which overrides changed the base definitions?
- Can it show the immutable compiled workflow snapshot used by a historical run?

### 2.3 Compilation failure visibility

- If compilation fails, is the failure durably recorded?
- Can the operator inspect what source inputs led to the failure?
- Can the system distinguish schema failure from merge/override failure from hook expansion failure?

---

## Section 3: Runtime Cursor And Execution Auditability

### 3.1 Run identity

- Can every node run be durably identified?
- Can the system distinguish daemon live authority from database durable record without leaving hidden coordination state?
- Are daemon decisions that affect execution durably represented after they take effect?
- Can the system show why the run was started?
- Can the system show which compiled workflow the run used?

### 3.2 Cursor state

- Can the system show the current task and subtask pointer?
- Can the system show the last completed subtask?
- Can the system show the current attempt number?
- Can the system show blocked/waiting status and reasons?

### 3.3 Subtask execution history

- Is every subtask attempt durably stored?
- Can the system show start time and end time for each attempt?
- Can the system show status, outputs, validations, summaries, and changed files?
- Can the system show git head before and after each attempt if relevant?

### 3.4 Hidden-state check

- Is any critical subtask state kept only in session memory?
- Is any important execution decision made without a durable record?

---

## Section 4: Session Auditability

### 4.1 Session identity

- Is every primary session durably recorded?
- Are pushed child sessions durably recorded?
- Is parent-child session linkage visible?

### 4.2 Recovery visibility

- Can the system show the last known heartbeat?
- Can it show whether a session was resumed, replaced, nudged, or abandoned?
- Can it show provider session identity if available?
- Can it show tmux session linkage?

### 4.3 Session event history

- Are meaningful session events stored durably?
- Can the system show bind, attach, heartbeat, nudge, recovery, and completion events?

### 4.4 Hidden-state check

- Is any resume-critical session information available only in tmux or provider memory?
- If yes, is there an explicit documented fallback?

---

## Section 5: Dependency And Scheduling Auditability

### 5.1 Dependency graph visibility

- Can the system show node dependencies durably?
- Can it show whether a dependency is child-based or sibling-based?
- Can it show the required dependency state?

### 5.2 Scheduling visibility

- Can the system explain why a node did or did not start?
- Can it show which dependencies blocked admission?
- Can it show which children were eligible to run concurrently?

### 5.3 Hidden-state check

- Is readiness ever determined by transient runtime-only state that is not reconstructible later?

---

## Section 6: Failure, Pause, And Escalation Auditability

### 6.1 Failure history

- Is every meaningful failure recorded durably?
- Can the system show which subtask failed?
- Can it show whether retries were attempted?
- Can it show the final failure summary?

### 6.2 Parent escalation visibility

- Can the system show which child failures affected a parent?
- Can it show parent failure counters or thresholds?
- Can it show why the parent retried, replanned, paused, or deferred to the user?

### 6.3 Pause/gating visibility

- Can the system show why a node is paused?
- Can it show which gate flag or approval boundary is active?
- Can it show the summary presented to the user at the pause point?

### 6.4 Hidden-state check

- Are pause reasons or retry decisions ever implicit rather than durably represented?

---

## Section 7: Validation, Review, And Testing Auditability

### 7.1 Validation visibility

- Can the system show all validation checks that ran?
- Can it show which checks passed or failed?
- Can it show the inputs or evidence used by those checks?

### 7.2 Review visibility

- Can the system show what was reviewed, against which criteria, and with what outcome?
- Can it show whether review caused revision, pause, or failure?

### 7.3 Testing visibility

- Can the system show which tests or suites ran?
- Can it show pass/fail/retry results?
- Can it show test failure summaries and gating consequences?

### 7.4 Hidden-state check

- Are any review/testing decisions only present in free-form session output rather than structured durable records?

---

## Section 8: Git And Rebuild Auditability

### 8.1 Branch lineage

- Can the system show the branch identity for a node version?
- Can it show seed commit and final commit?
- Can it show current active head if the node is in progress?

### 8.2 Merge auditability

- Can the system show which child finals were merged into a parent?
- Can it show merge order?
- Can it show merge conflicts and how they were resolved?

### 8.3 Rectification visibility

- Can the system show that a node was reset to seed?
- Can it show which child finals were reused during rebuild?
- Can it show which ancestors were rebuilt and in what order?

### 8.4 Hidden-state check

- Is any merge ordering or conflict resolution knowledge stored only in process memory or git reflog assumptions?

---

## Section 9: Prompt, Summary, And Rationale Auditability

### 9.1 Prompt history

- Can the system show prompts issued for each subtask or run stage?
- Can it show prompt roles and timestamps?

### 9.2 Summary history

- Can the system show summaries registered for subtask, node, failure, review, and rebuild contexts?
- Can it show which run or node version each summary belongs to?

### 9.3 Rationale visibility

- Can the system explain why code or plan changes were made?
- Can it link rationale back to node versions, prompts, or summaries?

### 9.4 Hidden-state check

- Is any important rationale only recoverable from transient terminal output or unstored AI context?

---

## Section 10: Documentation And Provenance Auditability

### 10.1 Docs generation visibility

- Can the system show when docs were built?
- Can it show local versus merged doc views?
- Can it show what inputs fed doc generation?

### 10.2 Provenance visibility

- Can the system show which nodes changed which code entities?
- Can it show entity relations?
- Can it show change rationale associated with those entities?

### 10.3 Hidden-state check

- Are provenance or docs outputs dependent on untracked extraction state or ephemeral caches?

---

## Section 11: Action Auditability

### 11.1 Mutation actions

- Does every mutation action have a durable effect record or a durable state change?
- Can the system later explain who or what triggered the action?

### 11.2 Automation parity

- If a user can perform an action manually, is there a CLI path for it?
- If a CLI mutation exists, is the resulting state observable afterward?

### 11.3 Hidden-state check

- Are there any important operator actions that leave no durable audit trail?

---

## Section 12: Reproducibility Tests

These are high-level reproducibility questions the design should be able to answer.

### 12.1 Reconstruct a historical run

Can the system reconstruct:

- the node version
- the compiled workflow
- the prompt history
- the subtask attempts
- the session binding
- the summaries
- the validations/reviews/tests
- the git start/end state

### 12.2 Reconstruct a rebuild

Can the system reconstruct:

- why a rebuild was triggered
- what version was replaced
- what descendants were regenerated
- what ancestors were rebuilt
- what merges were replayed

### 12.3 Reconstruct a final code state

Can the system explain:

- what node version produced it
- what child merges contributed to it
- what prompts and rationale contributed to it
- what docs/provenance outputs were generated from it

---

## Known Auditability Risks

Based on the current docs, the main auditability risks are:

1. review/testing results may remain too implicit if not given dedicated durable structures
2. pause and gating history may remain under-modeled if only current state is stored
3. session recovery may depend too much on external provider or tmux state
4. provenance identity across refactors may remain heuristic and need explicit confidence tracking
5. compile failure history may remain under-recorded if only success artifacts are modeled

---

## Recommended Follow-On Work

The next actions driven by this checklist are:

1. use this checklist while drafting `database_schema_spec_v2.md`
2. use this checklist while drafting `runtime_command_loop_spec_v2.md`
3. create a focused `review_testing_docs_yaml_plan.md`
4. decide whether pause/workflow event tables are required
5. decide whether compile-failure persistence needs dedicated structures

---

## Exit Criteria

This checklist is useful when:

- every major auditability category has a concrete yes/partial/no answer during review
- hidden-state risks are called out explicitly
- reproducibility can be evaluated systematically rather than rhetorically

The checklist should remain a living review document even after v2 specs are written.
