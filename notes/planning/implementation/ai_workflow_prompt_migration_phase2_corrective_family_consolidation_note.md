# AI Workflow Prompt Migration Phase 2 Corrective Family Consolidation Note

## Purpose

This note completes Phase 2 of `plan/tasks/2026-03-10_ai_workflow_prompt_migration_and_protocol_hardening.md`.

It reviews the overlapping corrective prompt families and freezes which ones should remain distinct, which ones should become more explicitly stage-scoped, and which ones are effectively duplicate surfaces.

## Surfaces reviewed

Prompt files:

- `src/aicoding/resources/prompts/packs/default/runtime/*.md`
- `src/aicoding/resources/prompts/packs/default/recovery/*.md`
- `src/aicoding/resources/prompts/packs/default/pause/*.md`

Runtime and YAML bindings:

- `src/aicoding/daemon/app.py`
- `src/aicoding/daemon/session_records.py`
- `src/aicoding/daemon/parent_failures.py`
- `src/aicoding/resources/yaml/builtin/system-yaml/prompts/default_prompt_refs.yaml`
- built-in task/subtask YAML prompt refs under `src/aicoding/resources/yaml/builtin/system-yaml/`

## Main finding

The overlap is real, but it is not uniform.

There are three different kinds of duplication:

1. true near-duplicates that should probably converge
2. similar prompts that are bound to different runtime owners and should remain distinct
3. generic corrective prompts that should survive, but only as narrow stage-correction prompts rather than secondary workflow-authoring systems

## Consolidation decisions

### 1. Idle nudge prompts

Files:

- `runtime/idle_nudge.md`
- `recovery/idle_nudge.md`

Observed bindings:

- daemon idle nudging uses `recovery/idle_nudge.md`
- built-in `nudge_idle_session` task uses `runtime/idle_nudge.md`
- built-in `nudge_session` subtask uses `recovery/idle_nudge.md`

Assessment:

- these are not currently equivalent in tone or scope
- `recovery/idle_nudge.md` is the daemon-owned recovery/correction prompt
- `runtime/idle_nudge.md` is a shorter generic prompt used in built-in runtime task flow

Decision:

- keep both for now
- make the boundary explicit:
  - `recovery/idle_nudge.md` is daemon-owned idle recovery
  - `runtime/idle_nudge.md` is lightweight runtime correction inside a bounded workflow task

Required follow-up:

- later hardening should ensure only one of them is taught in any given AI path
- the runtime note should explicitly distinguish daemon idle recovery from generic runtime corrective prompts

### 2. Resume and replacement bootstrap prompts

Files:

- `runtime/resume_existing_session.md`
- `recovery/resume_existing_session.md`
- `runtime/replacement_session_bootstrap.md`
- `recovery/replacement_session_bootstrap.md`
- `recovery/recover_interrupted_session.md`

Observed bindings:

- built-in recovery subtasks use the `recovery/*` variants
- built-in runtime tasks also reference the `runtime/*` variants

Assessment:

- these are functionally overlapping
- the `recovery/*` variants are stronger and more explicit about durable-state reconstruction
- the `runtime/*` variants are shorter but do not appear to encode a materially different runtime owner

Decision:

- these should converge conceptually on the `recovery/*` family
- `recovery/recover_interrupted_session.md` should remain the highest-level recovery narrative
- `runtime/resume_existing_session.md` and `runtime/replacement_session_bootstrap.md` are the clearest consolidation candidates

Required follow-up:

- later migration should retarget runtime YAML/task references toward the `recovery/*` family where semantics match
- once retargeted and verified, the duplicate `runtime/*` variants can be removed or reduced to aliases if the prompt-reference model still needs named compatibility

### 3. Pause prompts

Files:

- `pause/pause_for_user.md`
- `runtime/pause_for_user.md`
- `runtime/parent_pause_for_user.md`
- `recovery/merge_conflict_pause.md`

Observed bindings:

- built-in `pause_for_user` task uses `runtime/pause_for_user.md`
- parent-failure routing uses `runtime/parent_pause_for_user.md`
- merge-conflict reconciliation uses `recovery/merge_conflict_pause.md`
- `pause/pause_for_user.md` exists in the prompt pack and references table but is not the main bound runtime task surface

Assessment:

- `runtime/parent_pause_for_user.md` is meaningfully distinct because it is parent/child-failure specific
- `recovery/merge_conflict_pause.md` is also distinct because it is merge-conflict specific
- `pause/pause_for_user.md` and `runtime/pause_for_user.md` are the overlapping generic pair

Decision:

- keep `runtime/parent_pause_for_user.md` and `recovery/merge_conflict_pause.md` distinct
- generic user-pause prompting should converge on one canonical generic pause prompt
- `pause/pause_for_user.md` should likely become the canonical generic explanatory pause prompt
- `runtime/pause_for_user.md` is a compatibility/retarget candidate rather than a permanent independent family

Required follow-up:

- later migration should choose one canonical generic pause file and retarget YAML/task references
- the retained generic pause prompt must stay explanatory, not become a substitute workflow-authoring surface

### 4. Missed-step and missing-output correction

Files:

- `runtime/missed_step.md`
- `recovery/repeated_missed_step.md`
- `runtime/missing_required_output.md`
- `runtime/command_failed.md`
- `recovery/validation_failed.md`

Assessment:

- these are not simple duplicates
- they cover different correction triggers:
  - generic workflow-step drift
  - repeated idle/missed progress escalation
  - missing artifact
  - command failure
  - failed validation gate

Decision:

- keep these separate
- but keep them narrow
- they should reference the active stage contract and durable evidence, not restate whole workflow loops or teach composite-vs-low-level command surfaces from scratch

### 5. Parent-local correction

Files:

- `runtime/parent_local_replan.md`
- `runtime/parent_pause_for_user.md`

Observed bindings:

- `parent_failures.py` selects these based on parent decision type

Assessment:

- these are runtime-owner-specific and should remain distinct

Decision:

- keep distinct
- no consolidation needed in this phase

## Consolidation matrix

### Keep distinct

- `recovery/idle_nudge.md`
- `runtime/idle_nudge.md`
- `runtime/parent_pause_for_user.md`
- `recovery/merge_conflict_pause.md`
- `runtime/missed_step.md`
- `recovery/repeated_missed_step.md`
- `runtime/missing_required_output.md`
- `runtime/command_failed.md`
- `recovery/validation_failed.md`
- `runtime/parent_local_replan.md`

### Converge later

- `runtime/resume_existing_session.md` -> converge toward `recovery/resume_existing_session.md`
- `runtime/replacement_session_bootstrap.md` -> converge toward `recovery/replacement_session_bootstrap.md`
- `runtime/pause_for_user.md` and `pause/pause_for_user.md` -> converge to one canonical generic pause prompt

## Structural rule for later implementation

Corrective prompts must stop acting like alternate workflow manuals.

They should do only one of:

1. restate the current stage and tell the AI to follow the current stage contract
2. explain a bounded corrective or recovery action owned by the daemon/runtime
3. explain a bounded user-pause or parent-failure state

They should not:

- reteach the full happy-path command loop
- introduce alternate low-level command choreography when composite commands exist
- blur runtime recovery with ordinary stage execution

## Resulting Phase 2 recommendation

The next implementation slice should not try to rewrite every corrective prompt.

It should target the real structural duplicates first:

1. runtime vs recovery resume/bootstrap prompts
2. generic pause prompt duplication

Then Phase 3 can harden protocol expectations with a clearer distinction between:

- ordinary stage commands
- recovery/corrective prompts
- operator/debug-only command paths
