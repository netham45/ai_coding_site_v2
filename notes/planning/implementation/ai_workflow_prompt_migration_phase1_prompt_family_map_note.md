# AI Workflow Prompt Migration Phase 1 Prompt Family Map

## Purpose

This note completes Phase 1 of `plan/tasks/2026-03-10_ai_workflow_prompt_migration_and_protocol_hardening.md`.

It maps the actual AI-facing prompt families by lifecycle stage so later prompt migration and protocol hardening can be scoped structurally instead of file-by-file.

## Source surfaces reviewed

- Prompt-pack markdown under `src/aicoding/resources/prompts/packs/default/`
- Python-rendered parent workflow prompts in `src/aicoding/daemon/workflows.py`
- Runtime-synthesized command-subtask prompts in `src/aicoding/daemon/run_orchestration.py`

## Main finding

The AI command lifecycle is not authored in one prompt library. It is split across three surfaces:

1. packaged prompt markdown
2. Python-rendered parent workflow prompt text
3. runtime-synthesized prompt text for command-only subtasks

Prompt migration therefore has to treat all three as first-class prompt families.

## Lifecycle family map

### 1. Bootstrap and active-session startup

Files:
- `src/aicoding/resources/prompts/packs/default/runtime/session_bootstrap.md`
- `src/aicoding/resources/prompts/packs/default/runtime/cli_bootstrap.md`
- `src/aicoding/resources/prompts/packs/default/runtime/replacement_session_bootstrap.md`
- `src/aicoding/resources/prompts/packs/default/runtime/resume_existing_session.md`
- `src/aicoding/resources/prompts/packs/default/recovery/replacement_session_bootstrap.md`
- `src/aicoding/resources/prompts/packs/default/recovery/resume_existing_session.md`
- `src/aicoding/resources/prompts/packs/default/recovery/recover_interrupted_session.md`

Lifecycle role:
- initial bind/rebind
- resume or replacement-session reconstruction
- durable-state reload before stage execution

Composite-command adoption:
- not direct first-family composite adopters

Migration posture:
- primarily behavioral/session-state prompts
- should teach state inspection and recovery discipline, not low-level success rituals
- strong overlap exists between `runtime/*` and `recovery/*` variants

### 2. Ordinary execution

Files:
- `src/aicoding/resources/prompts/packs/default/execution/implement_leaf_task.md`

Lifecycle role:
- ordinary prompt-driven leaf implementation

Composite-command adoption:
- direct adopter

Current posture:
- already migrated to `subtask succeed`
- still uses low-level `subtask fail` for bounded failure handling

### 3. Command-subtask execution

Source:
- `src/aicoding/daemon/run_orchestration.py` `_synthesized_command_subtask_prompt(...)`

Lifecycle role:
- command-only stages without authored prompt text
- validation/testing and ordinary command stages

Composite-command adoption:
- direct adopter

Current posture:
- migrated to `subtask report-command`
- remains runtime-synthesized rather than prompt-pack authored

### 4. Parent decomposition and parent workflow progression

Files:
- `src/aicoding/resources/prompts/packs/default/layouts/generate_phase_layout.md`
- `src/aicoding/resources/prompts/packs/default/layouts/generate_plan_layout.md`
- `src/aicoding/resources/prompts/packs/default/layouts/generate_task_layout.md`
- `src/aicoding/daemon/workflows.py` `_wrap_parent_workflow_subtask_prompt(...)`

Lifecycle role:
- generated child-layout authoring
- parent review routing
- child spawning and parent-side continuation

Composite-command adoption:
- partial candidate

Current posture:
- layout-generation prompt-pack files still teach the low-level ritual:
  - `summary register`
  - `subtask complete`
  - `workflow advance`
- Python-rendered parent workflow text repeats the same low-level ordinary-success ritual
- parent review path already uses composite `review run`

Migration posture:
- highest-priority remaining authored surface for composite ordinary-success migration
- should likely adopt `subtask succeed` for ordinary parent subtasks while keeping explicit `node register-layout` and other structural parent mutations

### 5. Review routing

Files:
- `src/aicoding/resources/prompts/packs/default/review/review_layout_against_request.md`
- `src/aicoding/resources/prompts/packs/default/review/review_node_output.md`
- `src/aicoding/resources/prompts/packs/default/quality/review_node_against_requirements.md`
- `src/aicoding/daemon/workflows.py` review branch inside `_wrap_parent_workflow_subtask_prompt(...)`

Lifecycle role:
- durable pass/revise/fail routing through review stages

Composite-command adoption:
- already composite through `review run`

Migration posture:
- should stay on `review run`
- hardening target is mostly protocol enforcement and duplicate-family cleanup, not a new success command

### 6. Pause and intervention

Files:
- `src/aicoding/resources/prompts/packs/default/pause/pause_for_user.md`
- `src/aicoding/resources/prompts/packs/default/runtime/pause_for_user.md`
- `src/aicoding/resources/prompts/packs/default/runtime/parent_pause_for_user.md`
- `src/aicoding/resources/prompts/packs/default/runtime/parent_local_replan.md`
- `src/aicoding/resources/prompts/packs/default/recovery/merge_conflict_pause.md`

Lifecycle role:
- blocked state explanation
- user-decision handoff
- parent-local replan or merge-conflict pause handling

Composite-command adoption:
- not direct first-family composite adopters

Migration posture:
- primarily behavioral and explanatory
- likely needs consolidation and clearer stage scoping more than command replacement

### 7. Idle, missed-step, and corrective prompts

Files:
- `src/aicoding/resources/prompts/packs/default/runtime/idle_nudge.md`
- `src/aicoding/resources/prompts/packs/default/runtime/missed_step.md`
- `src/aicoding/resources/prompts/packs/default/runtime/missing_required_output.md`
- `src/aicoding/resources/prompts/packs/default/runtime/command_failed.md`
- `src/aicoding/resources/prompts/packs/default/recovery/idle_nudge.md`
- `src/aicoding/resources/prompts/packs/default/recovery/repeated_missed_step.md`
- `src/aicoding/resources/prompts/packs/default/recovery/validation_failed.md`

Lifecycle role:
- daemon or operator correction when the session drifted, stalled, or failed

Composite-command adoption:
- indirect only

Migration posture:
- these prompts should not become primary workflow-authoring surfaces
- they should reference the active stage contract rather than re-teaching the whole workflow
- duplication between `runtime/*` and `recovery/*` remains high

### 8. Child-session delegation and parent reconciliation

Files:
- `src/aicoding/resources/prompts/packs/default/runtime/delegated_child_session.md`
- `src/aicoding/resources/prompts/packs/default/execution/reconcile_parent_after_merge.md`

Lifecycle role:
- child-session bounded delegation
- parent merge/reconcile follow-up

Composite-command adoption:
- likely partial

Migration posture:
- needs later review for whether ordinary completion should use `subtask succeed`
- currently more behavioral than strictly command-teaching

### 9. Docs and testing interpretation

Files:
- `src/aicoding/resources/prompts/packs/default/docs/build_node_docs.md`
- `src/aicoding/resources/prompts/packs/default/testing/interpret_test_results.md`

Lifecycle role:
- docs authoring
- analysis of test evidence

Composite-command adoption:
- deferred / stage-dependent

Migration posture:
- these prompts are mostly analytical today
- later migration has to decide whether they become explicit composite success adopters or stay subordinate helper prompts beneath another stage contract

## Initial migration buckets

### Bucket A: direct composite adopters now

- ordinary execution prompt family
- synthesized command-subtask family

### Bucket B: direct composite adopters next

- layout-generation prompt family
- Python-rendered parent ordinary-success path in `workflows.py`

### Bucket C: composite already exists, harden protocol only

- review prompt family

### Bucket D: behavioral/recovery families, not primary success-path teachers

- bootstrap
- recovery
- idle/corrective
- pause/intervention

## Structural inconsistencies to carry into later phases

- ordinary execution and command-subtask execution now use composite commands, but parent decomposition still teaches the older low-level success ritual
- review routing is composite while neighboring parent success paths remain low-level
- `runtime/*` and `recovery/*` still duplicate several lifecycle prompts with similar but not identical behavior
- Python-rendered prompt text in `workflows.py` is still a major AI command surface and must be migrated alongside markdown prompts
- some analytical prompt families still do not define a clear stage-close command boundary at all

## Resulting Phase 1 recommendation

The next prompt-migration implementation slice should not start with recovery or pause prompts.

It should start with the remaining ordinary-success authors:

1. parent layout-generation prompt-pack files
2. Python-rendered parent workflow ordinary-success guidance

That is the largest remaining place where AI sessions are still being taught the operator-style `summary register -> subtask complete -> workflow advance` path even after the composite command family exists.
