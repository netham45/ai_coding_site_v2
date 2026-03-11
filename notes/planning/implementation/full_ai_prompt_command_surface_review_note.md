# Full AI Prompt Command Surface Review Note

## Purpose

This note records the broader review requested in `plan/tasks/2026-03-10_full_ai_prompt_command_surface_review.md`.

It expands beyond the single full-tree `cat` transcript and reviews the entire prompt-driven AI command surface across:

- authored prompt files in the packaged default prompt pack
- workflow-rendered parent guidance in `src/aicoding/daemon/workflows.py`
- synthesized command-subtask prompts in `src/aicoding/daemon/run_orchestration.py`

This note is still review only. It does not start remediation.

Related documents:

- `plan/tasks/2026-03-10_full_ai_prompt_command_surface_review.md`
- `notes/logs/reviews/2026-03-10_full_ai_prompt_command_surface_review.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/specs/prompts/prompt_library_plan.md`
- `notes/planning/implementation/ai_workflow_command_surface_phase1_evidence_note.md`
- `notes/planning/implementation/ai_workflow_command_surface_phase2_inventory_note.md`
- `notes/planning/implementation/ai_workflow_command_surface_phase3_ownership_error_policy_note.md`
- `notes/planning/implementation/ai_workflow_command_surface_phase4_recommendations_note.md`

---

## Review Boundary

The default prompt pack currently contains these prompt families:

- `execution`
- `review`
- `quality`
- `testing`
- `docs`
- `layouts`
- `runtime`
- `recovery`
- `pause`

The command surface taught to AI sessions does not come only from those files.

Two non-file systems also teach command behavior directly:

1. `src/aicoding/daemon/workflows.py`
   - workflow-rendered parent guidance
2. `src/aicoding/daemon/run_orchestration.py`
   - synthesized command-subtask prompts

That means the full AI-facing command surface is already split across at least three authoring systems:

- packaged prompt markdown
- workflow-rendered Python strings
- synthesized runtime prompt text

This split is itself one of the weird systems.

---

## Major Prompt-Taught Command Systems

### System 1: Ordinary low-level stage completion ritual

Taught in:

- `execution/implement_leaf_task.md`
- `layouts/generate_phase_layout.md`
- `layouts/generate_plan_layout.md`
- `layouts/generate_task_layout.md`
- `src/aicoding/daemon/workflows.py`
- `src/aicoding/daemon/run_orchestration.py`

Command shape:

1. `subtask current`
2. `subtask start`
3. `subtask context`
4. do work
5. `summary register` or write `command_result.json`
6. `subtask complete` or `subtask fail`
7. `workflow advance`
8. `subtask current`
9. `subtask prompt`

Why it is weird:

- one logical stage success expands into a large ritual
- the same ritual is duplicated in multiple prompt sources
- the ritual mixes read, write, and cursor-advance steps tightly
- the ritual is not packaged as one daemon-owned AI-facing outcome even though the system already has examples of composite commands elsewhere

### System 2: Composite review-routing system

Taught in:

- `review/review_layout_against_request.md`
- `review/review_node_output.md`
- `src/aicoding/daemon/workflows.py`

Command shape:

- `review run --node ... --status ... --summary ...`

Special rule:

- prompts explicitly say not to call `subtask complete` or `workflow advance` after `review run`

Why it is weird:

- this subsystem already uses the cleaner composite daemon-owned shape
- it is inconsistent with the ordinary success ritual taught almost everywhere else
- prompts need a defensive warning because neighboring subsystems teach the opposite pattern

### System 3: Command-subtask reporting system

Taught in:

- `src/aicoding/daemon/run_orchestration.py`

Command shape:

1. `subtask current`
2. `subtask start`
3. `subtask context`
4. run the command once
5. write `summaries/command_result.json`
6. `subtask complete --result-file ...` or `subtask fail --summary-file ... --result-file ...`
7. `workflow advance`
8. optionally `subtask prompt`

Why it is weird:

- this is not authored in a prompt file; it is synthesized in Python
- it is another custom completion ritual parallel to the ordinary implementation and layout rituals
- it carries its own file contract and continuation logic

### System 4: Parent workflow rendered guidance system

Taught in:

- `src/aicoding/daemon/workflows.py`

Command shape:

- summary registration and completion for parent subtask
- `workflow advance`
- then repeated `subtask current` and `subtask prompt`
- poll-like repetition until `node child-materialization` shows created or materialized children or the run stops

Why it is weird:

- this is a separate command-teaching system outside the prompt pack
- it teaches a structural workflow loop, not just stage completion
- it introduces `node child-materialization` as part of the AI continuation logic
- it tells the AI to repeat until a structural condition becomes true, which feels closer to operator orchestration than ordinary AI stage execution

### System 5: Parent layout registration system

Taught in:

- all three `layouts/generate_*_layout.md` prompts

Command shape:

- write `layouts/generated_layout.yaml`
- `node register-layout --node ... --file layouts/generated_layout.yaml`
- then return to the ordinary low-level success ritual

Why it is weird:

- this is actually one of the cleaner subsystems because it represents a real structural handoff
- the weirdness is that it is embedded inside the same low-level completion ritual rather than separated cleanly as “structural mutation” versus “stage success”

### System 6: Runtime bootstrap and generic CLI-discipline system

Taught in:

- `runtime/cli_bootstrap.md`
- `runtime/session_bootstrap.md`
- `runtime/replacement_session_bootstrap.md`
- `runtime/resume_existing_session.md`
- `recovery/recover_interrupted_session.md`
- `recovery/replacement_session_bootstrap.md`
- `recovery/resume_existing_session.md`

Command shape:

- inspect the current session
- inspect workflow/subtask state
- reload durable context
- continue from the durable checkpoint

Why it is weird:

- most of these prompts describe the same family of actions with different wording but not one canonical command sequence
- the repo has both `runtime/*` and `recovery/*` prompts for overlapping bootstrap/resume/replacement concepts
- some variants name exact surfaces like `session show-current` or `session show --node ...`
- others only imply the same recovery ritual generically

### System 7: Idle and missed-step corrective system

Taught in:

- `runtime/idle_nudge.md`
- `recovery/idle_nudge.md`
- `runtime/missed_step.md`
- `recovery/repeated_missed_step.md`

Command shape:

- mostly prose behavior correction rather than exact CLI commands

Why it is weird:

- there are parallel `runtime/*` and `recovery/*` versions of what is functionally the same corrective surface
- the variants differ in specificity and tone
- one emphasizes a short update, another emphasizes restating the exact current subtask and either heartbeating or failing
- this looks like two overlapping corrective subsystems rather than one canonical one

### System 8: Pause and intervention explanation system

Taught in:

- `runtime/pause_for_user.md`
- `pause/pause_for_user.md`
- `runtime/parent_pause_for_user.md`
- `runtime/parent_local_replan.md`

Command shape:

- mostly explanatory rather than mutating

Why it is weird:

- there are two separate generic pause prompt families, `runtime/pause_for_user.md` and `pause/pause_for_user.md`
- the difference is subtle and not obviously justified by a strong system boundary
- the parent-specific pause and replan prompts add yet another branch-specific explanatory subsystem

### System 9: Analysis-only quality/testing/docs system

Taught in:

- `quality/review_node_against_requirements.md`
- `testing/interpret_test_results.md`
- `docs/build_node_docs.md`

Why it is weird:

- these prompts describe important stage thinking, but they do not teach a clear CLI mutation path in the way the review prompts do
- that creates another inconsistency:
  - some review-like prompts are executional and command-bearing
  - some review/testing/docs prompts are analytical and non-operational
- the family boundary between “think about quality” and “record a quality-gate outcome” is not obvious from filenames alone

---

## Cross-Surface Weirdness Beyond The Transcript

### 1. The AI command surface is authored in three different places

- markdown prompt files
- Python-rendered workflow strings
- Python-synthesized runtime prompts

This is more important than it looks because command-system consistency can drift in three different places.

### 2. `runtime/*` and `recovery/*` are partially duplicate families

Overlapping pairs already visible:

- `runtime/idle_nudge.md` and `recovery/idle_nudge.md`
- `runtime/resume_existing_session.md` and `recovery/resume_existing_session.md`
- `runtime/replacement_session_bootstrap.md` and `recovery/replacement_session_bootstrap.md`
- `runtime/pause_for_user.md` and `pause/pause_for_user.md`

This suggests the repo has multiple overlapping “corrective runtime guidance” systems rather than one clearly partitioned one.

### 3. Some prompts teach exact command rituals while adjacent prompts teach only behavior

Examples:

- `review/review_node_output.md` teaches `review run`
- `quality/review_node_against_requirements.md` teaches judgment behavior only
- `testing/interpret_test_results.md` teaches interpretation behavior only
- `docs/build_node_docs.md` teaches output behavior only

That makes it unclear which prompt families are supposed to be action-driving versus analysis-driving.

### 4. Parent workflows have their own hidden command system

`src/aicoding/daemon/workflows.py` is not just rendering prompt variables. It is teaching a whole parent-owned orchestration loop involving:

- stage success
- repeated next-prompt fetches
- `node child-materialization`
- structural wait conditions

That is a distinct subsystem and should be reviewed as such.

### 5. Command-subtask prompts are a separate command DSL

`src/aicoding/daemon/run_orchestration.py` teaches:

- JSON result-file contracts
- one-shot command execution expectations
- continuation rules

This is not just another prompt variant. It is effectively a separate AI command DSL synthesized at runtime.

### 6. The prompt library is carrying runtime ownership inconsistencies directly

The prompts themselves are full of defensive language that exists because the runtime command shapes are inconsistent:

- “do not call `workflow advance` after `review run`”
- “do not assume the daemon will discover `layouts/generated_layout.yaml`”
- “after a successful `workflow advance`, do not stop while the node still has a current compiled subtask”

Those warnings are not incidental prompt polish. They are evidence of weird systems bleeding directly into prompt authoring.

---

## Initial Comprehensive Findings

The broader review already supports these stronger conclusions:

1. The earlier transcript findings are important, but they are only one symptom of a larger problem.
2. The repository currently has multiple parallel AI command systems, not one unified command surface.
3. The biggest weird systems are:
   - the ordinary low-level stage-completion ritual
   - the composite review-routing system
   - the synthesized command-subtask reporting system
   - the workflow-rendered parent orchestration system
   - the overlapping `runtime/*`, `recovery/*`, and `pause/*` corrective guidance systems
4. The prompt pack is not just teaching commands. It is also compensating for unclear runtime ownership boundaries, and that compensation shows up as duplicated prompt families, defensive warnings, and mixed explicit-versus-implicit command guidance.

---

## Next Review Steps

This note is only the first comprehensive pass.

The next review pass should add:

1. a command-by-command matrix of which prompt families teach which commands
2. a clearer map of which prompt files are executional versus analytical
3. a direct comparison of each weird subsystem against the documented CLI/runtime specs
4. an explicit list of prompt families that should probably merge or be renamed later so the system boundaries are obvious
