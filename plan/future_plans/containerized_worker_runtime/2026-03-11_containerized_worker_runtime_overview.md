# Containerized Worker Runtime Overview

## Purpose

Preserve and elaborate a future direction where worker execution can happen inside isolated per-run containers built from explicit project-facing runtime specs.

This is not an implementation plan.

It is a working note for a deferred launcher strategy that expands the already-deferred isolation feature.

## Position In The Current Design

The current repository already has the right high-level boundary for this idea:

- environment isolation is an execution-policy modifier
- node runs remain the orchestration owner
- YAML can request isolation
- actual container and namespace launchers are intentionally deferred

That means this future direction should not invent:

- a separate worker-authority model
- container-specific lineage
- hidden side channels around the daemon

The future launcher should plug into existing node-run orchestration and durable attempt recording.

## The Most Important Clarification

The future system should create a fresh runtime container per run, not necessarily a fresh image build per run.

Those are different things.

Recommended future posture:

- build an image when the declared build spec digest changes
- cache and reuse that image across many runs
- create a fresh container instance for each run attempt
- record which image digest and container ID were used for that attempt

Without this distinction, startup cost would become unnecessarily high and the feature would be harder to use for normal test and verification loops.

## Probable Build Contract

The eventual build contract likely needs three distinct layers.

### Layer 1: Workflow-declared need

This is the part YAML should express.

Examples:

- isolation mode requested
- build spec reference or runtime profile reference
- whether network is allowed
- whether published ports are allowed
- whether isolation is mandatory

### Layer 2: Build specification

This is the part that describes how the image is constructed.

Examples:

- build context path
- Dockerfile path
- optional build arguments
- optional cache policy
- optional mounted inputs or secrets policy

### Layer 3: Host launcher policy

This should stay outside YAML unless there is a strong reason otherwise.

Examples:

- which OCI engine is allowed on the host
- rootless versus privileged mode
- port publishing implementation
- cleanup TTL and garbage collection
- image store location

This preserves the existing code-vs-YAML boundary: YAML declares intent, but host infrastructure policy remains operational.

## Five-System Impact If This Ever Becomes Real Work

### Database

Would likely need durable records for:

- resolved build spec digest
- image digest or image reference
- container ID or runtime handle
- launch timestamps
- cleanup status
- isolation failure classification

### CLI

Would likely need command surfaces for:

- inspect requested versus resolved environment
- inspect image build status
- inspect container launch failures
- inspect published ports and network posture
- trigger cleanup or retry safely

### Daemon

Would remain the launcher authority.

It would likely own:

- build cache lookup
- image build execution
- runtime admission checks
- container start and stop
- log and artifact capture
- teardown and garbage collection

### YAML

Would likely need a higher-level build-spec reference rather than arbitrary launcher details.

The future contract should avoid shoving raw host-specific Docker command strings into YAML.

### Prompts

Lifecycle and execution prompts would eventually need to say:

- when the AI is expected to author or modify a Dockerfile
- how to validate it
- how to react when image build or launch fails
- how to distinguish host fixes from container-specific fixes

## Main Invariants Worth Preserving

- Isolation remains a runtime-policy modifier, not a lineage model.
- A node run owns the result even when execution happens in a container.
- Every attempt records the requested and resolved environment shape durably.
- Mandatory isolation failure fails the run attempt rather than silently falling back.
- Best-effort isolation fallback is durable, inspectable, and explicit.
- A fresh run container should be disposable and reproducible from a recorded build spec digest.
- Cleanup must not erase the audit trail needed to explain what happened.

## Main Risks

- image builds becoming too slow for normal feature work
- YAML gaining too much launcher-specific detail
- hidden host dependencies making runs non-reproducible
- port publishing and network policy becoming ambiguous
- privileged container requirements quietly expanding the trust boundary
- AI-authored Dockerfiles drifting away from the real runtime expectations of the repository

## Provisioning Failure And Escalation Model

If this direction becomes real work, container provisioning failure should not immediately collapse into a generic child failure or an automatic parent bounce.

The better model is:

1. the run enters an explicit environment-provisioning failure state
2. the daemon records the requested contract, resolved launcher mode, and useful launcher diagnostics
3. the failure is classified before any retry or escalation happens

Useful future classes:

- `retryable_infra`
  - transient engine, pull, timeout, or port-allocation problems
  - handle with daemon-owned retries first
- `child_fixable_spec`
  - invalid Dockerfile, broken image build step, missing package, bad build context
  - send the failure back to the same node so it can fix the runtime spec it owns
- `parent_replan_required`
  - impossible or contradictory runtime expectations coming from the higher-level plan
  - escalate to the parent with a structured diagnosis so the parent can re-evaluate and restart or regenerate
- `operator_blocked`
  - host engine missing, permissions absent, host policy forbids the requested mode
  - block for operator action instead of burning cycles in child-parent churn

So the answer to "should it bounce back to the parent" is:

- sometimes, but only when the parent is the layer with actual planning authority to fix the problem

This avoids turning every container failure into a costly replanning cascade.

## Most Likely Narrow v0 Direction

If this ever becomes active work, the safest initial slice is probably:

- one Docker-compatible OCI runner
- Linux-only assumptions
- one build context rooted in the worker repo
- one Dockerfile path declared by policy
- per-run fresh container instances
- image caching by build-spec digest
- limited network modes such as `disabled`, `default`, and `published_ports`
- no multi-container orchestration
- no Kubernetes-style abstractions
- no manual namespace-stack implementation in v0

That would prove the core operator and AI workflow without overcommitting to a broad container platform.
