# Runtime Tuning Matrix

## Purpose

This document catalogs the main runtime and policy tuning dimensions that are likely to appear across the system.

The goal is to answer, for each tuning category:

- what behavior it controls
- what usually happens if it is increased or decreased
- whether it belongs in compiled YAML, live runtime config, or code constants
- whether project-level override is safe

This is intended to make the compile boundary more concrete and to prevent policy from drifting into the wrong layer.

Related documents:

- `notes/runtime_command_loop_spec_v2.md`
- `notes/yaml_schemas_spec_v2.md`
- `notes/review_testing_docs_yaml_plan.md`
- `notes/parent_failure_decision_spec.md`
- `notes/session_recovery_appendix.md`
- `notes/cutover_policy_note.md`
- `notes/override_conflict_semantics.md`

---

## Placement Rule

Use this rule before placing a tuning value:

1. if changing the value changes workflow structure, gating order, retry eligibility, merge semantics, or user-visible completion criteria, it belongs in compiled YAML lineage
2. if changing the value only alters runtime pacing, polling, heartbeat, or bounded operational behavior without changing semantic workflow meaning, it belongs in runtime config
3. if the value is an implementation invariant, safety floor, schema default, or anti-footgun guard that projects should not casually change, it belongs in code constants

Short version:

- semantic behavior: YAML
- operational behavior: runtime config
- invariants and hard guardrails: code constants

---

## Matrix

| Tuning Category | What It Controls | If Increased | If Decreased | Best Home | Safe Project-Level Override? | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| prompt strictness vs creativity | How constrained prompt instructions are for generation, revision, review, and reconciliation work. | Usually yields more deterministic output, less variance, fewer novel alternatives, and less drift. | Usually yields more exploration and originality, but also more inconsistency and more cleanup/review burden. | YAML when it changes task semantics; runtime config only for temporary operator-mode presets. | yes, with limits | Safe when scoped to task/review definitions. Unsafe if changed invisibly at runtime for an already-compiled run. |
| decomposition depth | How aggressively the system decomposes parent work into child nodes, child sessions, or deeper task trees. | More parallelism and narrower unit scope, but higher orchestration overhead, more merge/review surfaces, and more parent-child coordination risk. | Simpler orchestration and fewer merge points, but larger work units, higher context pressure, and weaker isolation of failures. | YAML | yes | This changes workflow shape and lineage, so it should compile into the plan rather than live only in runtime knobs. |
| retry aggressiveness | How readily the runtime retries failing subtasks, children, tests, or reviewable steps before escalating. | More autonomous recovery and resilience to flaky failures, but higher cost, longer loops, and more risk of wasting time on non-retryable issues. | Faster escalation and clearer operator visibility, but lower tolerance for transient failures. | YAML for semantic retry policy; runtime config for bounded pacing between retries. | yes, bounded | Retry budgets and retryable classes are workflow policy. Backoff timing can stay runtime-side. |
| idle thresholds | How long a session may stay quiet before nudges or idle handling begin. | Fewer false-positive nudges and less interruption of long-running work, but slower detection of stuck sessions. | Faster detection and more responsive supervision, but more risk of nudging healthy but quiet work. | runtime config | yes | The runtime spec already treats idle timeout and max nudge count as likely runtime policy unless they change semantic outcomes. |
| recovery thresholds | When the runtime replaces a session, marks it lost, or pauses instead of trying to resume. | More willingness to recover automatically from stale/lost sessions, but more chance of resuming under ambiguity. | More conservative recovery and more pauses for user, but lower automation and higher operator burden. | mixed: runtime config plus code constants | partially | Time-based freshness checks fit runtime config. Invariant-violation handling and ambiguity safety floors should remain code-level. |
| review strictness | How demanding review criteria are and how easily review failures block progress. | Higher quality bar, more catches before testing/finalize, but more revisions and more cost. | Faster throughput and fewer review pauses, but more semantic defects may leak downstream. | YAML | yes | Review criteria, required scopes, and fail/pass consequences are semantic gates and should be lineage-visible. |
| test gate strictness | How strongly test outcomes block continuation, including suite selection and allowed failure thresholds. | Safer outputs and stronger release confidence, but slower cycles and more blocked work from flaky or expensive tests. | Faster iteration and cheaper runs, but more regressions can escape into merge/finalize paths. | YAML | yes, carefully | Allow project override, but keep a hard minimum safety floor in code for obviously invalid states if needed. |
| rebuild scope aggressiveness | How broadly rectification and supersession rebuild affected nodes and ancestors after a change. | Better consistency and less stale downstream state, but higher rebuild cost and more churn. | Smaller blast radius and faster recovery, but more risk of stale outputs or partial inconsistency. | YAML | yes, bounded | This changes authoritative lineage and cutover behavior, so it should not be a hidden runtime-only toggle. |
| merge batching behavior | Whether merges happen eagerly, incrementally, or in larger ordered batches, and how many child results are combined at once. | Larger batches reduce repeated merge overhead but increase conflict surface and harder diagnosis when something fails. | Smaller batches simplify attribution and conflict isolation but can increase total merge work. | YAML | yes | This affects merge semantics and review ordering, so it belongs with rectification/merge policy, not ad hoc operator config. |
| user escalation thresholds | When the system stops autonomous handling and pauses for explicit user/operator intervention. | More tolerance before escalation, which can improve autonomy but risks long unproductive loops. | Faster human visibility and lower runaway risk, but more interruptions and less unattended progress. | mixed: YAML plus code constants | partially | Semantic pause thresholds and failure counters belong in YAML. Absolute safety-stop ceilings are better kept in code constants. |

---

## Recommended Placement By Category

### Best candidates for compiled YAML

These directly change workflow meaning or visible gating behavior:

- prompt strictness vs creativity
- decomposition depth
- retry aggressiveness
- review strictness
- test gate strictness
- rebuild scope aggressiveness
- merge batching behavior
- user escalation thresholds

### Best candidates for runtime config

These are mainly operational pacing controls:

- idle thresholds
- retry backoff timing
- heartbeat cadence
- session freshness windows

### Best candidates for code constants

These should usually remain implementation-owned unless there is a strong reason otherwise:

- invariant-violation handling for duplicate active primary sessions
- minimum safety behavior under ambiguous recovery state
- hard anti-loop ceilings
- non-bypassable auditability and persistence requirements

---

## Override Safety Guidance

Project-level override is usually safe when all of the following are true:

- the override is visible in source YAML or an explicit project policy document
- the changed behavior is expected and auditable in lineage
- the override does not break global invariants
- the override does not silently weaken recovery or audit safety below system floors

Project-level override is usually unsafe when it would:

- bypass durable recording requirements
- weaken invariant checks for recovery ambiguity
- change semantic gates for an already-running compiled workflow without recompilation
- make merge, retry, or escalation behavior depend on hidden operator-local state

---

## Suggested Next Step

The current notes imply two follow-on artifacts would be useful:

1. a concrete `runtime_policy_definition` expansion that separates operational knobs from semantic workflow policy
2. a small catalog of code-level safety floors that projects are never allowed to override
