# AI Workflow Command Surface Phase 1 Evidence Note

## Purpose

This note records the Phase 1 evidence for `plan/tasks/2026-03-10_ai_workflow_command_surface_review_discovery.md`.

The goal of this note is not to propose fixes yet. It freezes the concrete problems exposed by the latest real tmux/Codex `cat` runtime flow so later design work can distinguish:

- transcript noise that is acceptable session reasoning
- true workflow-contract violations
- daemon tolerance that is currently masking protocol misuse
- prompt/runtime surfaces that are forcing the AI through too many low-level steps

Related documents:

- `plan/tasks/2026-03-10_ai_workflow_command_surface_review_discovery.md`
- `notes/logs/reviews/2026-03-10_ai_workflow_command_surface_review_discovery.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `notes/specs/prompts/prompt_library_plan.md`
- `notes/logs/e2e/2026-03-10_automated_full_tree_cat_runtime_e2e.md`

---

## Evidence Sources

Phase 1 findings are based on:

- the latest real full-tree `cat` tmux/Codex transcript captured during the passing E2E
- the current authored prompt contracts in the default prompt pack
- the current documented runtime command loop
- the current documented CLI mutation surface

The relevant transcript excerpts showed the session doing all of the following in one successful run:

- completing the leaf implementation stage
- advancing into validation stages
- retrying `workflow advance` after repeated daemon conflicts
- submitting review outcomes
- issuing another `workflow advance`
- finally observing `404 active node run not found` after the daemon had already closed the run

---

## Transcript Inventory

### T1. Leaf implementation stage

Observed transcript pattern:

- the session wrote the code
- ran the targeted tests
- wrote the implementation summary
- completed the subtask
- then advanced the workflow

Representative transcript line:

- `The leaf subtask is recorded as complete. I’m advancing the workflow now...`

Cross-reference:

- `src/aicoding/resources/prompts/packs/default/execution/implement_leaf_task.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`

Assessment:

- This stage broadly followed the intended low-level sequence.
- The chatter here is not the main problem.
- The main issue begins at the stage-transition handoff after completion.

Classification:

- acceptable transcript noise: yes
- workflow-contract violation: not from the quoted leaf-complete line alone

### T2. Validation stage handoff required explicit prompt fetch

Observed transcript pattern:

- after `workflow advance`, the session had to detect that another subtask existed
- it then fetched the next prompt and started the next stage manually

Representative transcript line:

- `The workflow advanced into a validation subtask rather than ending the run. I’m fetching the live prompt for this next stage...`

Cross-reference:

- `src/aicoding/resources/prompts/packs/default/execution/implement_leaf_task.md`
- `src/aicoding/daemon/run_orchestration.py`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`

Assessment:

- This is currently documented behavior, not a transcript mistake.
- It is still evidence that the AI-facing workflow remains overly manual.
- One successful stage currently expands into at least:
  - `summary register`
  - `subtask complete`
  - `workflow advance`
  - `subtask current`
  - `subtask prompt`

Classification:

- acceptable transcript noise: no
- workflow-contract problem: yes, but at the product-surface level rather than a prompt-disobedience level

### T3. Repeated `workflow advance` conflict retries

Observed transcript pattern:

- the session completed a stage
- immediately called `workflow advance`
- received a daemon conflict
- retried the advance after the state settled
- repeated this pattern more than once

Representative transcript lines:

- `The completion recorded correctly; the advance call raced and hit a daemon conflict...`
- `The same race happened on the immediate advance call...`
- `The advance raced the review submission again...`

Cross-reference:

- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `plan/features/47_F10_ai_cli_progress_and_stage_transition_commands.md`

Assessment:

- This is a real workflow problem, not harmless chatter.
- The runtime currently exposes a low-level sequence that is easy to mis-time.
- A passing run now commonly depends on recoverable conflict retries.
- That is evidence that the AI-facing happy path is not actually one clean authoritative mutation.

Classification:

- acceptable transcript noise: no
- workflow-contract problem: yes
- daemon tolerance masking misuse: yes

### T4. Review stage treated as `review run` plus `workflow advance`

Observed transcript pattern:

- the session described review submission
- then separately described a follow-up advance

Representative transcript lines:

- `I’m submitting a passing review and advancing...`
- `The actual review subtask prompt matches the hook review... I’m submitting that and advancing the workflow again.`

Cross-reference:

- `src/aicoding/resources/prompts/packs/default/review/review_layout_against_request.md`
- `src/aicoding/resources/prompts/packs/default/review/review_node_output.md`
- `src/aicoding/daemon/workflows.py`
- `tests/unit/test_workflows.py`

Documented prompt contract:

- the review prompts say to submit the review with `review run`
- the review prompts explicitly say `do not call subtask complete or workflow advance after review run`

Assessment:

- This is a direct prompt-contract violation by the session.
- The daemon currently tolerates enough surrounding state that the overall run still finishes.
- That tolerance is useful for recovery but is obscuring that the session did not follow the documented review protocol.

Classification:

- acceptable transcript noise: no
- workflow-contract problem: yes
- daemon tolerance masking misuse: yes

### T5. Terminal `404 active node run not found`

Observed transcript pattern:

- after the workflow had already reached completion, the session tried another `workflow advance`
- the daemon responded with `404 active node run not found`

Representative transcript line:

- `the final workflow advance attempt returned 404 active node run not found because the daemon had already closed the run`

Cross-reference:

- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/cli/cli_surface_spec_v2.md`

Assessment:

- The session should not need to probe terminal completion through another mutating command.
- From the product perspective, this is evidence that the terminal success contract is too awkward.
- The daemon response is technically correct for the low-level command, but it is a poor AI-facing completion outcome.

Classification:

- acceptable transcript noise: no
- workflow-contract problem: yes
- likely future idempotency or higher-level command candidate: yes

---

## Noise Versus Real Problems

### Acceptable session reasoning noise

The following observed behavior is not itself a defect:

- the session narrating what stage it is on
- the session saying it is fetching the next prompt
- the session summarizing test results before recording them durably
- the session explaining that a later stage exists

These lines reflect the model thinking in public. They are noisy, but they are not the main design problem.

### Actual workflow problems

The following patterns are real command-surface or protocol problems:

1. The happy path still requires too many serialized low-level commands.
2. `workflow advance` is easy to call too early and appears in the happy path as a retried race.
3. Review stages are explicitly documented as self-routing via `review run`, yet the runtime still allows sloppy follow-up mutation attempts to coexist with overall success.
4. Terminal completion is discoverable through an awkward low-level error rather than a clean AI-facing completion outcome.

---

## Current Contract Pressure Points

### Prompt layer pressure

The authored prompts are already compensating for workflow fragmentation by spelling out long command rituals:

- leaf execution prompts require summary registration, completion, advance, then next-stage discovery
- layout prompts require generated-file registration, completion, then advance
- command-only stages require result JSON writing, completion, then advance
- review prompts have to warn the model not to call extra commands after `review run`

This is evidence that the prompt layer is carrying workflow complexity that should eventually move into daemon-owned operations.

### Daemon/CLI pressure

The daemon and CLI currently expose the correct low-level primitives for inspection and mutation, but the live transcript shows the AI-facing happy path is not well-shaped:

- stage success is fragmented across multiple commands
- retryable conflicts are too easy to hit
- correct review behavior is too easy to violate
- terminal success is not surfaced as a simple authoritative outcome from the command the session actually wants to use

---

## Phase 1 Findings

Phase 1 evidence supports the following discovery conclusions:

1. The passing full-tree `cat` E2E proves survivability of the current low-level workflow loop, not cleanliness of the AI-facing command protocol.
2. The largest problem is not session chatter. The larger problem is that the current happy path forces the AI to serialize too many low-level daemon mutations correctly.
3. At least one transcript behavior was a direct prompt-contract violation:
   - calling or attempting `workflow advance` around review handling after `review run`
4. At least two transcript behaviors expose product-shape problems even when the session is trying to comply:
   - repeated `workflow advance` races after stage completion
   - terminal completion surfacing as `404 active node run not found`
5. Later design work should preserve low-level commands for operators and debugging, but the current evidence justifies exploring a smaller AI-facing command surface.

---

## Out Of Scope For Phase 1

This note does not yet decide:

- which new higher-level commands should exist
- which current low-level commands should become AI-internal or operator-only
- which misuse cases should become hard daemon errors versus idempotent success responses
- which prompt families should be rewritten first

Those are Phase 2 through Phase 4 questions in the governing review/discovery task.
