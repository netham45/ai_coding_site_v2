# AI Command Lifecycle Structural Review Note

## Purpose

This note completes the structural review defined in `plan/tasks/2026-03-10_ai_command_lifecycle_structural_review.md`.

It turns the broad AI command-surface audit into a lifecycle map:

- what AI flow families actually exist
- which stages they occupy
- which prompts and commands drive each stage
- where the lifecycle branches
- where the lifecycle is currently structurally clean versus split across overlapping systems

This note is still review and planning only. It does not start implementation fixes.

Related documents:

- `plan/tasks/2026-03-10_ai_command_lifecycle_structural_review.md`
- `plan/tasks/2026-03-10_full_ai_prompt_command_surface_review.md`
- `notes/planning/implementation/full_ai_prompt_command_surface_review_note.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/runtime/tmux_session_lifecycle_spec_v1.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/specs/prompts/prompt_library_plan.md`

---

## Lifecycle Families

The current repository has these actual AI flow families.

### Primary lifecycle families

These are the flows that can form part of an ordinary node run:

1. top-level startup and run admission
2. primary-session bind and bootstrap
3. stage bootstrap and context loading
4. ordinary implementation or parent work execution
5. command-subtask execution
6. parent decomposition and child-structure work
7. quality-gate progression
8. terminal completion

### Corrective or exceptional families

These are not the main happy path, but they are part of the lifecycle:

1. idle nudge
2. missed-step correction
3. pause for user
4. parent pause or local replan
5. session resume or replacement bootstrap
6. interrupted-session recovery
7. validation or command failure correction

### Specialized branch families

These are meaningful lifecycle branches with their own boundaries:

1. pushed child-session delegation and merge-back
2. parent reconcile after child merge
3. child materialization and child scheduling
4. provider-aware versus provider-agnostic recovery

---

## Stage-By-Stage Lifecycle Map

## Stage 1: Top-Level Startup

### Entry conditions

- a user or operator creates a top-level node
- the node kind is eligible for top-level startup

### Main commands

- `workflow start --kind <kind> --prompt <prompt>`

### Prompt surfaces

- no ordinary stage prompt yet
- startup is daemon-owned and later flows into session bootstrap

### Durable evidence

- top-level node creation
- authoritative node version
- compiled workflow
- first run admission when applicable

### Exit or handoff

- handoff into primary-session bind and bootstrap

### Structural status

- relatively clean
- already composite and daemon-owned

---

## Stage 2: Primary Session Bind And Bootstrap

### Entry conditions

- an active run exists
- a primary session is required or resumed

### Main commands

- `session bind --node <id>`
- `session show-current`
- `workflow current --node <id>`
- `subtask prompt --node <id>`

### Prompt surfaces

- `runtime/session_bootstrap.md`
- `runtime/cli_bootstrap.md`
- tmux/Codex bootstrap path from `notes/specs/runtime/tmux_session_lifecycle_spec_v1.md`

### Durable evidence

- session row
- tmux launch metadata
- prompt delivery history
- current run binding

### Exit or handoff

- handoff into stage bootstrap and context loading

### Structural status

- partially clean
- the runtime and tmux specs define the main behavior
- overlapping `runtime/*` and `recovery/*` bootstrap prompts already blur ordinary bootstrap versus recovery bootstrap

---

## Stage 3: Stage Bootstrap And Context Loading

### Entry conditions

- a current compiled subtask exists
- the session needs the current prompt and context

### Main commands

- `subtask current --node <id>`
- `subtask prompt --node <id>`
- `subtask context --node <id>`
- `subtask environment --node <id>`

### Prompt surfaces

- `execution/implement_leaf_task.md`
- `layouts/generate_*_layout.md`
- synthesized command-subtask prompts in `run_orchestration.py`
- workflow-rendered parent guidance in `workflows.py`

### Durable evidence

- prompt delivery history
- stage context bundle
- current run state

### Exit or handoff

- handoff into one of:
  - ordinary execution
  - command-subtask execution
  - review routing
  - parent-specific orchestration

### Structural status

- structurally central but overloaded
- this stage is reused by many later subsystems and currently inherits different command rituals depending on prompt source

---

## Stage 4: Ordinary Execution

### Entry conditions

- current subtask is a normal implementation or parent work stage

### Main commands

- `subtask start --node <id> --compiled-subtask <id>`
- do work
- `summary register --node <id> --file <path> --type subtask`
- `subtask complete --node <id> --compiled-subtask <id> --summary ...`
- `workflow advance --node <id>`

### Prompt surfaces

- `execution/implement_leaf_task.md`
- workflow-rendered parent-subtask guidance in `workflows.py`

### Durable evidence

- subtask attempts
- summary history
- run cursor changes

### Exit or handoff

- handoff to:
  - next subtask bootstrap
  - quality gates
  - terminal completion

### Structural status

- structurally messy
- one ordinary stage success is split across several low-level commands
- the prompt layer carries a lot of sequencing burden here

---

## Stage 5: Command-Subtask Execution

### Entry conditions

- compiled subtask has command text without an authored prompt

### Main commands

- `subtask current`
- `subtask start`
- `subtask context`
- run command once
- write `summaries/command_result.json`
- `subtask complete --result-file ...` or `subtask fail --summary-file ... --result-file ...`
- `workflow advance`

### Prompt surfaces

- synthesized prompts in `src/aicoding/daemon/run_orchestration.py`

### Durable evidence

- attempt row
- execution result JSON
- possible failure summary
- later validation/testing review data on the same attempt

### Exit or handoff

- handoff to next-stage bootstrap or terminal completion

### Structural status

- separate custom lifecycle branch
- not authored in prompt markdown
- effectively a runtime-generated mini command language

---

## Stage 6: Parent Decomposition And Child Structure Work

### Entry conditions

- current node is acting as a parent
- current subtask is a decomposition, layout, spawn, or parent-review stage

### Main commands

- `node register-layout --node <id> --file layouts/generated_layout.yaml`
- `summary register`
- `subtask complete`
- `workflow advance`
- repeated `subtask current`
- repeated `subtask prompt`
- `node child-materialization --node <id>` as a structural inspection surface

### Prompt surfaces

- `layouts/generate_phase_layout.md`
- `layouts/generate_plan_layout.md`
- `layouts/generate_task_layout.md`
- parent rendered guidance from `src/aicoding/daemon/workflows.py`

### Durable evidence

- layout registration events
- child materialization state
- child nodes and child runs
- summary history and prompt history

### Exit or handoff

- either descend into child work
- remain in parent orchestration
- or continue to parent quality/review stages

### Structural status

- structurally mixed
- part of the lifecycle is explicit and good (`node register-layout`)
- part is an AI-driven structural polling loop taught in Python-rendered text

---

## Stage 7: Quality-Gate Progression

### Entry conditions

- ordinary work has completed and the workflow enters validation, review, testing, docs, or provenance stages

### Main commands

- validation path:
  - generic command-subtask loop
  - `workflow advance`
- review path:
  - `review run --node <id> --status ... --summary ...`
- testing path:
  - either command-subtask loop or daemon-owned testing gate
- docs path:
  - currently more analytical than command-explicit
- turnkey path:
  - `node quality-chain --node <id>` exists as a separate daemon-owned composite flow

### Prompt surfaces

- `review/review_layout_against_request.md`
- `review/review_node_output.md`
- `quality/review_node_against_requirements.md`
- `testing/interpret_test_results.md`
- `docs/build_node_docs.md`

### Durable evidence

- validation results
- review results
- test results
- docs outputs
- summary history

### Exit or handoff

- continue
- revise/rewind
- pause for user
- fail to parent
- terminal completion

### Structural status

- highly inconsistent
- review already uses a composite stage-outcome command
- validation/testing often still rely on the low-level ordinary or command-subtask ritual
- some quality prompts are analytical rather than operational

---

## Stage 8: Pause And Intervention

### Entry conditions

- user decision required
- policy gate reached
- parent failure or local replan needed

### Main commands

- operator-facing intervention surfaces exist:
  - `workflow pause`
  - `workflow resume`
  - `node interventions`
  - `node intervention-apply`
  - `node approve`

### Prompt surfaces

- `runtime/pause_for_user.md`
- `pause/pause_for_user.md`
- `runtime/parent_pause_for_user.md`
- `runtime/parent_local_replan.md`

### Durable evidence

- pause flags
- pause context
- intervention state
- workflow events

### Exit or handoff

- resume ordinary execution
- local replan
- remain blocked for user

### Structural status

- prompt side is duplicated and somewhat muddy
- daemon side is more coherent than the prompt side

---

## Stage 9: Idle, Missed-Step, And Corrective Guidance

### Entry conditions

- idle detection fires
- missed-step detection fires
- command failure or missing output correction is needed

### Main commands

- often prose-first rather than explicit command lists
- may lead back into:
  - `subtask prompt`
  - `subtask current`
  - `subtask heartbeat`
  - `subtask fail`

### Prompt surfaces

- `runtime/idle_nudge.md`
- `recovery/idle_nudge.md`
- `runtime/missed_step.md`
- `recovery/repeated_missed_step.md`
- `runtime/command_failed.md`
- `runtime/missing_required_output.md`
- `recovery/validation_failed.md`

### Durable evidence

- session events
- nudge events
- failure summaries when the session reports one durably

### Exit or handoff

- back into ordinary execution
- back into next-stage bootstrap
- fail safely
- pause for user

### Structural status

- duplicated and corrective rather than canonical
- currently split across several overlapping prompt families

---

## Stage 10: Recovery, Resume, And Replacement

### Entry conditions

- stale, lost, detached, or interrupted session state

### Main commands

- `session show-current`
- `session show --node <id>`
- `session attach --node <id>`
- `session resume --node <id>`
- `session recover --node <id>`
- `session provider-resume --node <id>`
- `node recovery-status --node <id>`
- `node recovery-provider-status --node <id>`

### Prompt surfaces

- `runtime/resume_existing_session.md`
- `runtime/replacement_session_bootstrap.md`
- `recovery/recover_interrupted_session.md`
- `recovery/resume_existing_session.md`
- `recovery/replacement_session_bootstrap.md`

### Durable evidence

- recovery classification
- session history
- replacement session rows
- prompt history and current run state

### Exit or handoff

- back into stage bootstrap and context loading

### Structural status

- daemon and tmux specs are fairly explicit
- prompt family boundaries are overlapping and should later collapse into a clearer lifecycle surface

---

## Stage 11: Child Session Delegation And Merge-Back

### Entry conditions

- current subtask pushes bounded delegated work into a child session

### Main commands

- `session push --node <id> --reason <reason>`
- `session pop --session <id> --summary-file <path>`
- `session result show`

### Prompt surfaces

- `runtime/delegated_child_session.md`
- child-session lifecycle surfaces in runtime and tmux notes

### Durable evidence

- child session rows
- child session result artifacts
- parent cursor context

### Exit or handoff

- back to parent stage
- possibly into reconcile or merge handling

### Structural status

- present in specs and CLI
- still has known runtime rough edges in live flows

---

## Stage 12: Terminal Completion

### Entry conditions

- no next subtask remains
- run closes at the daemon level

### Main commands

- currently often inferred through:
  - successful final `workflow advance`
  - or awkwardly through `404 active node run not found` when another low-level mutation is attempted

### Prompt surfaces

- no single canonical terminal-completion prompt surface yet

### Durable evidence

- run status `COMPLETE`
- lifecycle state `COMPLETE`
- final summaries, quality-gate history, docs, provenance, and session history

### Exit or handoff

- none; run is complete

### Structural status

- daemon completion itself is clear
- AI-facing completion UX is not yet a clean first-class lifecycle stage

---

## Major Structural Inconsistencies

### 1. One lifecycle is authored in multiple systems

The lifecycle is currently spread across:

- prompt markdown files
- workflow-rendered Python strings
- synthesized runtime prompt text
- runtime and tmux specs

That makes it hard to see one canonical lifecycle without a dedicated note.

### 2. Some stages are composite while neighboring stages are low-level rituals

Examples:

- `workflow start` is composite
- `review run` is composite
- `node quality-chain` is composite
- ordinary execution is still a low-level ritual

### 3. Ordinary, corrective, and recovery flows are not clearly partitioned in prompts

Examples:

- `runtime/*` and `recovery/*` overlap heavily
- `pause/*` and `runtime/pause_for_user.md` overlap
- idle and missed-step prompts have parallel variants

### 4. Quality-related prompt families are not structurally uniform

Examples:

- `review/*` is operational
- `quality/*` is analytical
- `testing/*` is analytical
- docs prompt is output-oriented but not clearly tied to one explicit command system

### 5. Parent lifecycle stages are partly hidden in Python-rendered prose

The parent decomposition loop is not defined only in prompt files or only in specs. Important lifecycle behavior lives in rendered strings in `workflows.py`.

---

## Lifecycle-Note Outline

The future full AI command lifecycle note should contain these sections:

1. Purpose and scope
2. Lifecycle families
3. Primary happy-path stages
4. Quality-gate stages
5. Parent/child and child-session branches
6. Corrective and recovery branches
7. Terminal completion semantics
8. Command ownership model by stage
9. Durable evidence and operator surfaces by stage
10. Current weird or transitional systems
11. Relationship to existing runtime, tmux, CLI, and prompt specs

---

## Recommended Source-Note Relationship

If the full lifecycle note is authored later:

- `runtime_command_loop_spec_v2.md` should remain the runtime contract source
- `tmux_session_lifecycle_spec_v1.md` should remain the session/recovery transport source
- `cli_surface_spec_v2.md` should remain the command inventory source
- `prompt_library_plan.md` should remain the prompt-pack source
- the new lifecycle note should become the cross-source map that explains how those surfaces fit together for AI execution

---

## Result

The review is now structurally complete enough to author a dedicated full AI command lifecycle note.

The main conclusion is that the repository does not yet have one coherent lifecycle document because the lifecycle itself is currently split across multiple command systems, prompt families, and ownership models. That split is now mapped stage by stage rather than only described as “messy.”
