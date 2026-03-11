# Stage 05: Post-V1 Evolution

## Purpose

Post-v1 evolution exists to govern the repository after it already has a first proven release scope.

At this point the project no longer follows only a simple linear bootstrap path.

Instead, contributors choose among several different kinds of work, and each kind should reopen only the lifecycle gates it really needs.

This stage exists to prevent post-release work from collapsing into vague maintenance language.

## Stage Sub-Steps

### `post_v1.classify_workstream`

Why it exists:

- force the repository to name what kind of post-v1 change is actually being attempted

Required artifacts:

- governing task or epic context
- named workstream category

Acceptance criteria:

- the work is classified as one of:
  - local enhancement
  - major feature expansion
  - system overhaul
  - assurance or audit
  - migration or offload
  - sunset or archive
- the classification is justified in writing

Proof required:

- artifact existence check

Blocked claims:

- the repository has a governed post-v1 plan

Advance when:

- contributors can explain why this is the right workstream rather than defaulting to generic maintenance wording

### `post_v1.open_governing_context`

Why it exists:

- keep post-v1 programs governed by explicit plans instead of ad hoc edits

Required artifacts:

- governing epic, feature, or task-plan context
- intended verification and rollout surface

Acceptance criteria:

- the plan names the changed scope explicitly
- the plan names which lifecycle gates are being reopened
- the plan names the intended bounded and real-runtime proof surface

Proof required:

- review against the plan

Blocked claims:

- the change is fully scoped

Advance when:

- the repository can point to a governing context that explains the post-v1 program coherently

### `post_v1.reopen_affected_disciplines`

Why it exists:

- prevent large post-v1 work from skipping earlier lifecycle disciplines that have become relevant again

Required artifacts:

- updated notes
- updated checklists
- updated log entries

Acceptance criteria:

- architecture notes are reopened if system assumptions changed
- setup notes are reopened if new tooling or infrastructure is required
- feature-delivery notes are reopened if new implementation work exists
- hardening and E2E notes are reopened if runtime behavior changed
- migration or sunset notes are opened if the workstream requires them

Proof required:

- document review against the governing plan

Blocked claims:

- the changed scope is ready for stronger status language

Advance when:

- the repository has explicitly reopened every discipline the change actually affects and no more

### `post_v1.prove_changed_scope`

Why it exists:

- stop previously earned proof from being reused carelessly for new or changed runtime behavior

Required artifacts:

- bounded proof
- named E2E or audit proof target
- command record in the development log

Acceptance criteria:

- bounded commands pass for the changed scope
- real E2E, audit, migration, or sunset proof is named for the changed scope
- pass, fail, or residual gap is recorded honestly

Proof required:

- actual command execution

Blocked claims:

- `flow_complete`
- `release_ready`

Advance when:

- the new workstream has proof appropriate to its actual risk and runtime surface

### `post_v1.update_baseline_and_residual_gaps`

Why it exists:

- keep the repository honest about what remains proven, what is newly in flight, and what is still blocked

Required artifacts:

- operational-state checklist update
- residual-gap summary

Acceptance criteria:

- the prior baseline maturity claim remains visible for unaffected proven scope
- the active post-v1 workstream is visible
- blocked stronger claims for the changed scope are visible
- remaining gaps, rollback concerns, or deprecation obligations are stated explicitly

Proof required:

- artifact existence check

Blocked claims:

- trustworthy readiness language

Advance when:

- operators and contributors can tell what stayed proven, what is being changed, and what still is not ready

## Workstream Categories

Use these categories deliberately:

- `feature_expansion`: a new major product or subsystem slice that may need its own define, setup, implementation, and E2E path
- `system_overhaul`: a major architectural replacement, deep refactor, or subsystem redesign that invalidates old assumptions
- `assurance_audit`: security, compliance, privacy, resilience, or performance work whose primary purpose is risk reduction and proof quality
- `migration_offload`: cutover, coexistence, offloading, service extraction, or data movement work
- `sunset_archive`: controlled deprecation, archival, or shutdown work

Routine small enhancements may stay inside normal feature-delivery handling when they do not warrant a separate post-v1 program.

## What This Stage Should Produce

Minimum expected artifacts:

- a named post-v1 workstream
- governing plan context
- reopened lifecycle docs as needed
- checklist and log updates
- bounded proof
- named runtime, audit, migration, or sunset proof target

## Questions This Stage Must Answer

- Is this just feature delivery, or does it deserve a named post-v1 workstream?
- Which earlier lifecycle disciplines are reopened by this change?
- Which claims remain true for already-proven scope?
- Which new scope is still unproven?
- What rollout, rollback, audit, migration, or archival evidence is required?

## AI Instruction

If the repository is in post-v1 evolution stage, AI contributors should:

- classify the work before treating it as routine implementation
- reopen architecture, setup, migration, or E2E doctrine when the chosen workstream requires it
- preserve visibility of the baseline maturity already earned
- avoid hiding major programs under vague maintenance language

Suggested `AGENTS.md` line:

> After the first proven release scope exists, classify meaningful new work as feature expansion, system overhaul, assurance or audit, migration or offload, or sunset and archive when applicable. Reopen only the lifecycle gates the chosen workstream actually changes, and do not borrow stale proof from the pre-change runtime path.

## Entry Conditions

- At least one repository scope has already reached real bounded and runtime proof.
- New work no longer fits entirely inside the initial bootstrap path.

## Required Artifacts

- governing plan context
- workstream classification
- notes and checklist updates
- development-log updates
- proof commands for the changed scope

## Required Verification Surface

This stage should prove:

- the changed scope has fresh bounded proof
- the changed scope has a named runtime, audit, migration, or sunset proof target
- the operational-state checklist distinguishes baseline maturity from in-flight post-v1 work honestly

## Common Failure Modes

- Treating a major new feature program as if it were just a small enhancement.
- Performing a large architectural rewrite without reopening architecture and migration notes.
- Reusing old E2E confidence after changing the core runtime path.
- Calling security or compliance work complete because code changed without explicit audit closure evidence.
- Sunsetting behavior without documenting operator guidance, retention duties, or final archival proof.

## Exit Conditions

This stage is complete enough for a given workstream when:

- the workstream is explicitly named and governed
- the reopened disciplines have been handled
- proof exists for the changed scope at the right level
- the baseline maturity and residual gaps are both visible honestly
