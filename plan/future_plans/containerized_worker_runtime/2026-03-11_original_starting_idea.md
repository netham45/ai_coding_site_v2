# Original Starting Idea

This note preserves the rough idea as stated before narrowing it into a recommended direction.

## Core Thought

Workers would run in a container.

YAML would provide some way to define the Dockerfile, and the system would spawn a container for each run based on that Dockerfile.

The lifecycle plans would tell the AI to set up the container it should use for development by writing the Dockerfile and then running the relevant tests inside that environment.

## Motivation

The main motivations are:

- port isolation for tests
- dependency isolation between workers
- safer execution of risky setup or verification commands
- keeping worker-specific environment assumptions explicit instead of leaking into the host

## Open Question

Should the system start with:

- Docker or another OCI-style container engine

or:

- a more manual systemd-isolated or namespace-isolated system

The attraction of the lower-level route is that it might be less heavy.

The concern is that it may effectively turn into rebuilding a large part of what Docker or another OCI runtime already solves:

- image build semantics
- filesystem layering
- environment packaging
- network namespace setup
- NAT and port publishing
- cleanup and inspection

That tension is the reason this future-plan bundle exists.
