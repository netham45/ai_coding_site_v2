# Phase F19: Version-Consistent Live Runtime Authority

## Goal

Ensure the live lifecycle and daemon-authority state for a logical node always points at the correct node version so superseded or stale versions cannot be resumed, supervised, auto-started, or rebound accidentally.

## Rationale

- Rationale: Most execution records in the repository are already version-scoped, but the shared live runtime authority rows are still keyed primarily by logical node identity, which creates a mismatch that can let stale version-owned runtime state linger after supersession or dependency-invalidated restart.
- Reason for existence: This phase exists to close that narrow authority gap without redesigning the broader run/session architecture that is already substantially version-aware.

## Related Features

Read these feature plans for implementation context and interaction boundaries:

- `plan/features/05_F02_node_versioning_and_supersession.md`
- `plan/features/13_F09_node_run_orchestration.md`
- `plan/features/16_F12_session_binding_and_resume.md`
- `plan/features/24_F19_regeneration_and_upstream_rectification.md`
- `plan/features/70_F19_live_rebuild_cutover_coordination.md`
- `plan/features/84_F19_dependency_invalidated_node_fresh_rematerialization.md`

## Required Notes

Read these note files before implementing or revising this phase:

- `notes/specs/runtime/node_lifecycle_spec_v2.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/contracts/runtime/cutover_policy_note.md`
- `notes/contracts/runtime/session_recovery_appendix.md`
- `notes/planning/implementation/session_binding_and_resume_decisions.md`
- `notes/planning/implementation/regeneration_and_upstream_rectification_decisions.md`

## Scope

- Database: extend the shared live runtime authority records so they carry the node version they currently describe, and define how stale version-owned rows are rejected or rebound during supersession and restart.
- CLI: existing operator inspection, rebuild-coordination, and cutover-readiness surfaces should expose enough version-consistency truth to explain when a logical node's live runtime state belongs to an obsolete version, stale candidate baseline, or superseded version and why that state is blocked or ignored.
- Daemon: require version-match checks across admission, authority mutation, session bind/recovery, supervision, and auto-start so only the intended current version can own live runtime state.
- Website: no browser-owned orchestration changes are required, but daemon-backed state reads should eventually surface version-mismatch blockers clearly.
- YAML: not applicable; this is runtime authority enforcement, not declarative policy shape.
- Prompts: no new prompt family is required, though runtime messaging may later need to explain stale-version blocking or invalidation cleanup.
- Tests: add bounded and integration proof that stale shared runtime state for superseded versions cannot trigger starts, resumes, supervision recovery, or auto child binding.
- Performance: version-consistency checks must remain constant-time or narrow-index lookups so they can run on every admission, supervision, and scheduling pass.
- Notes: update lifecycle, recovery, and rectification doctrine so live authority is explicitly version-consistent rather than merely logical-node-consistent.

## Proposed Implementation Direction

1. Extend shared live runtime rows such as `node_lifecycle_states` and `daemon_node_states` with `node_version_id` so they explicitly identify which version they currently govern.
2. On any path that starts or resumes work, first resolve the intended authoritative or restart-target version, then require the shared runtime rows to match that version before proceeding.
3. When supersession, cutover, or dependency-invalidated restart changes the active version, explicitly rebind the shared runtime rows to the new version and clear stale run/session linkage from the old one.
4. In session supervision and recovery, ignore or invalidate stale sessions whose `node_version_id` no longer matches the shared live runtime version for that logical node.
5. In auto-start and admission paths, add a final stale-version gate so a logical node with mismatched live runtime authority returns blocked/stale rather than starting work.
6. Preserve the existing version-scoped `node_runs`, `node_run_state`, and durable `sessions` model; this phase should align live authority with that model rather than replace it.

## Runtime Clarifications

- Version-consistent live authority must distinguish authoritative live lineage from non-authoritative candidate lineage; candidate versions may be inspectable and runnable for rebuild purposes without stealing authoritative runtime ownership prematurely.
- When cutover rebinds live runtime authority, it must do so against the enumerated required cutover scope and current authoritative baseline rather than assuming the latest created version is safe.
- Authoritative-baseline drift should block candidate cutover before any live runtime authority rows are rebound to the candidate version.
- This phase is the runtime guard that prevents stale shared state from bypassing the replay-versus-live-merge split introduced in F18/F19.

## Verification Expectations

- Bounded proof:
  - superseded-version shared lifecycle/authority state is rejected as stale
  - shared runtime rows rebind to the fresh dependency-invalidated version rather than the superseded version
  - stale sessions are not recovered or rebound once their node version is obsolete
  - auto child start skips stale-version live runtime state even when the logical node previously had active work
- Integration proof:
  - start/resume/supervision flows stay pinned to the intended version across supersede, candidate rebuild, and cutover boundaries
- Real E2E proof:
  - a real regenerate/supersede/cutover flow proves old version-owned runtime state does not restart after a new candidate becomes the valid live target and that stale candidate runtime authority is blocked after authoritative-baseline drift

## Exit Criteria

- shared live runtime authority explicitly names the node version it governs
- stale version-owned live runtime state cannot start, resume, recover, or auto-bind work
- supersession and dependency-invalidated restart rebind live authority to the correct version deterministically
- notes and proving layers describe this as a narrow runtime-authority consistency fix rather than a full run-architecture rewrite
