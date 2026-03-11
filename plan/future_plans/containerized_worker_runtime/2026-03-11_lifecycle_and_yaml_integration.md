# Lifecycle And YAML Integration

## Purpose

Describe how a future containerized-worker direction could fit the project-lifecycle notes and the YAML policy boundary without pretending those contracts are already adopted.

## Lifecycle Fit

The project-skeleton lifecycle examples suggest the right place to introduce this behavior.

### Setup-stage usage

During setup-oriented work, lifecycle instructions could tell the AI to:

- create the initial worker runtime definition
- author the Dockerfile or equivalent image spec in the repo
- run the bounded runtime-build validation command
- record the resulting runtime assumption in the lifecycle notes

This is useful when a repository wants a standard development container early.

### Feature-delivery usage

During feature work, lifecycle instructions could tell the AI to:

- revise the worker runtime definition only when the feature genuinely changes runtime needs
- validate the image build
- rerun the bounded and integration tests inside the isolated runtime when that is the intended proving surface
- update notes and logs when the runtime contract changes

This keeps the container definition treated as a real implementation asset, not a hidden helper file.

### Hardening and E2E usage

Later hardening notes could require:

- proof that the isolated runtime behaves like the intended real target
- real E2E runs through the daemon-owned launcher path
- audit surfaces for build, launch, cleanup, and failure inspection

That is where the repo would move from "we can build a worker image" to "the orchestrator can use it reliably."

## Prompt Implications

If lifecycle plans eventually include container setup, the prompts should be explicit about the boundary.

The AI should not be told only:

- "make the container work"

It should be told:

- which Dockerfile or build-spec file it owns
- which validation command proves the image build
- which tests must run in the isolated runtime
- how to record runtime changes in notes, logs, and checklists
- what to do when the launcher cannot satisfy a mandatory isolation request

That keeps runtime setup from becoming undocumented prompt folklore.

## Suggested Future YAML Direction

The future YAML shape should probably not inline a full Dockerfile body directly into workflow YAML.

That would make workflow definitions too heavy and blur the code-versus-YAML boundary.

The cleaner direction is:

- YAML references a named runtime build spec or profile
- the runtime build spec points to a Dockerfile path and build context
- the Dockerfile itself lives as a normal file in the worker repo

That gives the AI something concrete to edit while keeping workflow YAML declarative.

## Example Shape

This is only a sketch:

```yaml
environment_policy_definition:
  id: isolated_pytest_worker
  isolation_mode: container
  mandatory: true
  allow_network: false
  runtime_build_ref: python_test_worker
  network_mode: disabled

runtime_build_definition:
  id: python_test_worker
  context_path: .
  dockerfile_path: infra/worker.Dockerfile
  build_args:
    PYTHON_VERSION: "3.12"
```

The important point is not the exact fields.

The important point is the split:

- workflow YAML asks for a runtime profile
- a repo-visible build definition describes the image inputs
- the host launcher decides how to satisfy that request

## Recommended Future Operator Surfaces

If this direction becomes active work, the daemon and CLI likely need explicit surfaces for:

- show the requested runtime build ref for a node run
- show the resolved image digest used by an attempt
- show whether the image came from cache or rebuild
- show the network mode and published ports
- show launch and cleanup failures separately from test-command failures

Without those inspection surfaces, containerized workers would be hard to diagnose.

## Parent And Operator Escalation Rule

Lifecycle guidance should distinguish who is expected to react when provisioning fails.

Recommended future posture:

- same node fixes child-owned runtime spec errors
- parent replans only when the failure means the higher-level runtime expectations were wrong
- operator intervention is required when the host cannot satisfy the declared isolation mode at all

That means lifecycle prompts should tell AI workers not to blindly restart or regenerate parents on every build or launch failure.

They should instead:

- inspect the classified failure
- decide whether the runtime spec is locally fixable
- escalate to the parent only when the parent owns the bad assumption
- surface operator-blocking failures honestly without pretending more planning will solve them

## Most Important Guardrail

The lifecycle system should tell AI workers to maintain the container definition only when the repository truly wants containerized development or verification.

It should not force every project into container authoring by default.

A good future posture is:

- host execution remains the default
- containerized execution is an explicit project policy choice
- lifecycle notes can opt a project into container authoring and validation once that choice is made
