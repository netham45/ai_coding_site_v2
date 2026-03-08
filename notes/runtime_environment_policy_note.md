# Runtime Environment Policy Note

## Purpose

This document defines how optional isolated execution environments should fit into the orchestration model.

The original design wants the system to support child work in isolated containers or namespace-separated environments for cases such as:

- tests requiring network ports
- conflicting runtime dependencies
- risky verification steps
- bounded external-access work

This note turns that requirement into a concrete policy shape so the system can either:

- include isolated environments as a first-class capability, or
- defer them intentionally without leaving the design ambiguous

Related documents:

- `notes/original_concept.md`
- `notes/yaml_schemas_spec_v2.md`
- `notes/runtime_command_loop_spec_v2.md`
- `notes/database_schema_spec_v2.md`
- `notes/cross_spec_gap_matrix.md`

---

## Core Rule

Environment isolation is an execution policy, not a new ownership model.

That means:

- isolated execution does not create a new node lineage concept
- isolated execution does not transfer branch ownership
- isolated execution does not bypass durable run/session tracking
- isolated execution is a runtime-policy modifier on how certain work is executed

The node run remains the orchestration owner even when work happens inside an isolated environment.

---

## What Isolation Is For

The environment model should support at least these cases.

## Case 1: Port-bound tests

Example:

- integration tests need exclusive access to ports

## Case 2: Dependency isolation

Example:

- child work needs packages or tools not safe to share with the parent environment

## Case 3: Risk containment

Example:

- verification steps may execute risky commands or untrusted build/test flows

## Case 4: Network-scoped work

Example:

- a task may require network access or intentionally restricted network access

---

## What Isolation Is Not For

Isolation should not be used as a replacement for:

- node hierarchy
- child-node ownership
- pushed child-session semantics
- durable state tracking

In other words:

- child nodes solve orchestration decomposition
- pushed child sessions solve context isolation
- environment isolation solves runtime/environment isolation

These are different axes and should not be conflated.

---

## Recommended Scope

Recommended first-class scope for isolated environments:

- optional
- subtask-level or task-level execution policy
- most commonly used for testing, verification, or special commands

Recommended non-goals for first implementation:

- full arbitrary per-node infrastructure orchestration
- complicated multi-container distributed orchestration
- hidden environment behavior with no explicit policy reference

---

## Isolation Modes

The design should support a small explicit set of modes.

### Mode 1: `none`

Meaning:

- execute in the normal project/runtime environment

### Mode 2: `container`

Meaning:

- run inside a managed containerized environment

### Mode 3: `namespace`

Meaning:

- run in process/system namespace isolation without full containerization

### Mode 4: `custom_profile`

Meaning:

- use a project-defined runtime isolation profile

Recommended initial design stance:

- support `none`, `container`, and `namespace` conceptually
- allow `custom_profile` only if project policy explicitly defines it

---

## Policy Placement

Environment isolation policy should be configurable, but not every runtime behavior needs to live in the compiled workflow.

Recommended split:

### Compiled workflow should include

- whether a task/subtask requires isolation
- which isolation profile ID is requested
- whether network is allowed
- whether this requirement is mandatory or best-effort

### Runtime environment config may include

- container image mapping
- namespace implementation details
- launcher details
- host-specific runtime integration

Reason:

- the semantic requirement belongs to workflow lineage
- the infrastructure implementation detail may remain operational/runtime-specific

---

## Suggested YAML Shape

If environment policy is included in YAML, it should likely look like this.

```yaml
environment_policy_definition:
  id: string
  isolation_mode: none|container|namespace|custom_profile
  allow_network: boolean
  profile_name: string
  mandatory: boolean
  resource_hints:
    cpu: string
    memory: string
  allowed_subtask_types:
    - string
```

And a task/subtask could reference it like:

```yaml
subtask_definition:
  id: run_tests
  type: run_tests
  environment_policy_ref: isolated_test_env
```

---

## Runtime Semantics

If a subtask requires isolated execution:

1. runtime loads the isolation policy
2. runtime resolves the actual environment launcher/config
3. runtime launches the subtask work in the isolated environment
4. outputs, summaries, and exit status return to the main node run
5. durable state is recorded exactly as if the work had run locally

Key rule:

- isolation affects execution context, not orchestration truth ownership

---

## Failure Semantics

Isolation introduces new failure classes that should be explicit.

Recommended environment-related failure classes:

- `environment_launch_failure`
- `environment_dependency_failure`
- `environment_network_policy_failure`
- `environment_timeout_failure`
- `environment_cleanup_failure`

These failures should feed into normal subtask failure handling and parent failure logic.

They should not bypass ordinary retry/pause/escalation behavior.

---

## Best-Effort vs Mandatory Isolation

The policy should distinguish:

### Mandatory isolation

Meaning:

- if the isolated environment cannot be created, the subtask must fail

### Best-effort isolation

Meaning:

- if the isolated environment cannot be created, the runtime may fall back to normal execution if policy allows

Recommended default:

- testing or risky verification should usually use mandatory isolation when isolation is requested

---

## Session Relationship

Environment isolation is not the same as pushed child sessions.

Possible combinations:

- primary session running a subtask in an isolated environment
- pushed child session running bounded work in an isolated environment

But these are still separate dimensions:

- session = who is thinking/operating
- environment = where the command/work executes

The design should preserve this distinction.

---

## DB Implications

The current DB model does not yet explicitly track environment policy usage.

Possible additions if this stays in scope:

### Add to compiled subtasks

- `environment_policy_ref`

### Add to subtask attempts

- `execution_environment_json`

Possible contents:

- isolation mode
- profile name
- container or namespace ID if applicable
- network mode

### Possible future table

- `environment_runs`

This may be useful if environment lifecycle becomes operationally important, but may be unnecessary for first implementation.

---

## CLI Implications

If environment isolation is in scope, operators should be able to inspect:

- whether a subtask requires isolation
- what policy was requested
- whether isolation succeeded
- what environment mode was used

Likely useful commands or output fields:

- `ai-tool subtask show --compiled-subtask <id>`
- `ai-tool subtask attempts --compiled-subtask <id> --verbose`
- maybe `ai-tool environment show --attempt <id>`

If names differ, the capability should still exist.

---

## Security And Risk Notes

Isolation can reduce risk, but only if it is explicit and inspectable.

The design should avoid:

- hidden fallback from isolated to non-isolated execution without audit trail
- hidden network access changes
- environment-specific behavior that is not visible in run history

Any fallback should be:

- policy-controlled
- durably recorded
- operator-visible

---

## Recommended Default Policy For First Implementation

If isolated environments remain in scope for first implementation, use this default:

1. support only a small set of environment profiles
2. apply isolation at subtask level
3. store requested policy in compiled workflow
4. store actual execution environment details in subtask attempts
5. treat environment launch failures as ordinary subtask failures

This keeps the capability bounded and compatible with the rest of the orchestration model.

---

## Recommended Deferment Policy

If isolated environments are too large for first implementation, defer them explicitly like this:

- keep `environment_policy_definition` in the spec as optional
- keep runtime/DB extension points ready
- implement only `none` mode initially
- mark container/namespace execution as deferred

This is preferable to pretending support exists while leaving the behavior undefined.

---

## Recommendation

Recommended current planning stance:

- keep environment isolation in the design
- classify it as optional for the first implementation slice
- preserve schema/runtime extension points now
- do not let it block the rest of the orchestration system

This gives you a real place for the feature without forcing immediate infrastructure complexity.

---

## Recommended Next Follow-On Work

The next docs that should absorb this logic are:

1. `notes/yaml_schemas_spec_v2.md`
2. `notes/runtime_command_loop_spec_v2.md`
3. `notes/database_schema_spec_v2.md`
4. `notes/cross_spec_gap_matrix.md`

Then lower the severity of the isolated-environment gap and mark it as either:

- deferred intentionally
- included as bounded optional capability

---

## Exit Criteria

This note is complete enough when:

- environment isolation is clearly separated from node/session ownership
- isolation modes are explicit
- compiled-workflow versus runtime-config boundary is explicit
- failure behavior is explicit
- first-implementation scope is explicit

At that point, isolated execution is no longer a vague concept floating outside the architecture.
