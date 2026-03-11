# Docker Versus Namespace Runtime Direction

## Question

Should the first real isolated-worker launcher use:

- a Docker-compatible OCI container runtime

or:

- a lower-level systemd or namespace-managed execution model

## Recommendation

The first implementation should use a Docker-compatible OCI runtime behind a thin launcher abstraction.

In practice that likely means designing for an OCI image and container model first, while leaving room for Docker, Podman, or another compatible engine behind the scenes.

## Why This Is The Better First Step

### 1. It matches the user's build idea directly

The starting idea is already framed around:

- a Dockerfile
- building an environment from that Dockerfile
- launching a fresh isolated runtime per run

An OCI-style runner matches that mental model without translation overhead.

### 2. It avoids rebuilding a lot of infrastructure by hand

A lower-level namespace or systemd approach still has to answer:

- how root filesystems are built
- how package installation is cached
- how build layers are reused
- how network namespaces are created
- how NAT and port publishing are configured
- how logs and artifacts are captured
- how lifecycle cleanup is made reliable

That is exactly where a lot of hidden complexity lives.

### 3. It gives a better reproducibility story earlier

A Dockerfile plus build context digest is a stronger reproducibility unit than:

- a shell script that mutates a namespace rootfs
- a hand-built systemd service template
- a set of ad hoc network namespace commands

The repo is already very sensitive to auditability and replayability, so that matters.

### 4. It is easier to document for AI workers

Telling an AI:

- edit `Dockerfile.worker`
- run the build validation command
- fix the failing dependency or port issue

is clearer than teaching it a bespoke rootfs and netns orchestration stack.

## Why The Lower-Level Route Is Still Interesting

The namespace or systemd route is still attractive for some reasons:

- it could be lighter for certain local workloads
- it may avoid a full Docker daemon dependency
- it could eventually provide tighter host integration
- it could enable specialized execution profiles later

But those advantages are more compelling after the core isolation behavior already works.

They are weaker as a first implementation argument because they arrive together with much more launcher and networking complexity.

## Specific Concern: NAT And Netns

The user's instinct here is right.

Once the design requires features like:

- isolated network stacks
- published ports
- outbound network restrictions
- loopback behavior
- host-to-container communication

the systemd and raw-namespace approach quickly becomes a real networking product surface.

At that point the project is no longer just building "a lighter worker launcher."

It is building:

- rootfs management
- namespace lifecycle management
- firewall or NAT policy
- port forwarding rules
- diagnostics for all of the above

That is very likely the moment where the project starts reimplementing a meaningful slice of container-runtime behavior.

## Recommended Architecture Stance

The future implementation should not hardcode "Docker" as the architecture.

It should hardcode the higher-level model:

- OCI-style image build contract
- OCI-style per-run container contract
- runtime engine hidden behind a Python launcher interface

That keeps the initial plan pragmatic without forcing the long-term engine choice too early.

## Deferred Follow-On Option

Once an OCI-based launcher exists and the repository has real evidence about:

- build overhead
- runtime overhead
- network needs
- cleanup pain points

then a second launcher family could be evaluated for:

- rootless Podman
- `systemd-nspawn`
- a custom namespace runner

That later decision would be informed by real usage instead of speculation.

## Bottom Line

If the question is "what should the future plan recommend first," the answer should be:

- use an OCI container model first
- keep the engine abstract
- defer raw namespace or systemd implementations until the project has proven that the extra complexity is justified
