# Authority And API Model

## Purpose

This note defines the authoritative runtime ownership model for orchestration, persistence, and client access.

The goal is to remove ambiguity around:

- whether the database or daemon owns live coordination
- how CLI and future web surfaces talk to the system
- what must be persisted durably
- what may remain ephemeral at runtime

Related documents:

- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/database/database_schema_spec_v2.md`
- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/catalogs/traceability/action_automation_matrix.md`

---

## Core Decision

The daemon is the live orchestration authority.

The database is the durable canonical record.

Implementation staging note:

- early authority slices may persist daemon-owned runtime records keyed by external node identifiers before the richer `node_versions`/`node_runs` schema families are implemented
- that staging choice does not change the core rule that the daemon owns live mutations and the database owns the durable record

That means:

- the daemon decides admission, locking, coordination, recovery, cutover, and other live orchestration behavior
- the database stores durable state, history, lineage, and results needed for recovery, auditability, and operator inspection
- the CLI and future web/dashboard surfaces should talk to the daemon rather than performing operational coordination directly through database access

This model is preferred over direct CLI-to-database coordination because it gives the system one clear live authority while preserving durable explainability.

---

## Role Boundaries

### Daemon

The daemon owns:

- run admission
- active locking and coordination
- session binding and rebinding
- idle detection and nudging
- pause/resume/cancel decisions
- child scheduling
- supersession cutover decisions
- recovery decisions
- validation of mutating commands before durable acceptance

The daemon may hold ephemeral in-memory state for convenience, but no coordination-critical decision should exist only in memory after it affects system behavior.

### Database

The database owns the durable canonical record for:

- node versions
- authoritative-versus-latest-created version selection
- compiled workflows
- run state and cursor state
- subtask attempts
- session history and recovery-critical session facts
- workflow-event history for pause, recovery, parent decisions, and cutover
- pause, failure, rebuild, merge, and related event/history structures
- prompts, summaries, quality-gate results, docs, and provenance views

The database must be sufficient to reconstruct what happened and to resume safely after daemon interruption.

### CLI And Web Clients

The CLI and future web/dashboard clients should act as daemon clients.

They should:

- send read and mutation requests to the daemon API
- receive results assembled from daemon-controlled logic and durable state
- avoid embedding orchestration rules locally

Direct database access may still exist for debugging, admin work, or offline inspection, but it should not be the default operational interface.

---

## Access Model

For now, the daemon should expose its client surface over HTTPS.

Recommended initial access model:

- HTTPS transport
- runtime-generated cookie for authentication
- local-first deployment assumptions

This is intentionally simple and should be treated as an initial access model rather than a final security architecture.

The runtime-generated cookie should be:

- created at daemon startup
- scoped to the daemon instance
- required for CLI and web requests
- replaceable on daemon restart

Future authentication models can supersede this, but the initial design should still assume authenticated client access rather than unauthenticated local calls.

---

## Persistence Rule

If the daemon makes a decision that affects:

- execution progress
- coordination
- pause/resume behavior
- recovery behavior
- cutover behavior
- operator-visible status

then that decision or its resulting state transition must be persisted durably.

Examples:

- admitting a run
- binding or replacing a primary session
- transitioning to paused state
- classifying and escalating failure
- selecting authoritative lineage during cutover

Current canonical selectors should include:

- `sessions` as the owner of current primary-session identity
- explicit authoritative-versus-latest-created version selection for logical nodes

The daemon may compute such decisions live, but after acting on them it must persist enough state for later explanation and safe recovery.

---

## Recommended Wording For Canonical Specs

Use language like:

- "the daemon is the live orchestration authority"
- "the database is the durable canonical record"
- "CLI and web clients interact with the daemon API"

Avoid ambiguous shorthand like:

- "the database is the runtime truth source"

unless the document is explicitly talking only about durable historical reconstruction rather than live coordination.

---

## Current Security Bound

The runtime-generated cookie over HTTPS is good enough for an initial local-first implementation, but it should be treated as a bounded temporary access model.

Open future concerns include:

- multi-user auth
- remote access hardening
- token rotation
- session expiration
- privilege separation
- auditability of auth-sensitive actions

Those concerns do not block the current authority decision.
