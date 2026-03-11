# AI Workflow Prompt Migration Phase 3 Protocol Hardening Targets Note

## Purpose

This note completes Phase 3 of `plan/tasks/2026-03-10_ai_workflow_prompt_migration_and_protocol_hardening.md`.

It freezes the concrete protocol-hardening targets that remain after the composite command rollout and the first prompt-migration slices.

## Source surfaces reviewed

- prompt-pack markdown under `src/aicoding/resources/prompts/packs/default/`
- Python-rendered parent workflow guidance in `src/aicoding/daemon/workflows.py`
- runtime and CLI ownership notes
- bounded, integration, and E2E tests touching workflow advancement and terminal outcomes

## Main finding

The main prompt-migration problem is no longer “everything teaches the low-level ritual.”

The remaining hardening work is more specific:

1. stop corrective/recovery prompts from becoming alternate workflow manuals
2. tighten post-composite outcome behavior so AI sessions do not probe low-level state unnecessarily
3. make the retained low-level/operator paths clearly separate from the AI happy path in tests and notes

## Hardening target list

### Target 1: No redundant post-review advancement

Current state:

- review prompts teach `review run`
- parent workflow prompts explicitly say not to call `subtask complete` or `workflow advance` after `review run`
- bounded tests already defend that wording

Remaining issue:

- this is still mostly a prompt-level defense
- the user-facing command surface still leaves room for sessions to “try” `workflow advance` afterward and learn through conflict or terminal absence

Hardening goal:

- keep `review run` as the only AI-taught review completion path
- make future AI-facing guidance treat the routed review outcome as final for that stage
- avoid any prompt text that implies a second advancement probe is expected after review routing

### Target 2: No ordinary success-path fallback to low-level choreography

Current state:

- leaf execution, synthesized command subtasks, and parent layout generation now use composite commands
- some notes and older test/docs surfaces still mention `workflow advance` or other low-level paths as if they are normal AI continuation steps

Hardening goal:

- AI-facing prompts should teach composite commands wherever those commands exist
- low-level `summary register`, `subtask complete`, and `workflow advance` should remain available but be documented as operator/recovery primitives rather than default AI happy-path steps

### Target 3: No post-completion probing through low-level commands

Observed symptom:

- live tmux/Codex runs learned terminal completion through `404 active node run not found`

Current state:

- composite prompts now talk about routed outcomes
- some E2E and helper surfaces still tolerate terminal “not found” as part of session-level success narratives

Hardening goal:

- AI-facing prompts should stop after a routed `completed` outcome instead of probing the closed run
- tests should prefer proving the composite routed outcome and durable run completion, not a tolerated post-close low-level error

### Target 4: Corrective prompts must refer back to the active stage contract

Current state:

- corrective prompts are still largely standalone prose
- if left unchecked, they can regrow alternate workflow instructions

Hardening goal:

- corrective prompts should tell the AI to restate the active stage, identify the correction, and continue within the existing stage contract
- they should not reintroduce old success choreography where composite commands exist

### Target 5: Recovery prompts should emphasize durable reconstruction, not restart a new workflow authoring path

Current state:

- recovery prompts already point at durable state
- duplicate runtime/recovery bootstrap surfaces still exist

Hardening goal:

- retarget duplicated runtime bootstrap/resume prompts toward the stronger recovery-family contract
- keep recovery prompts focused on reconstructing state and resuming the active stage, not on teaching a new generic workflow loop

## Required proof layers for the hardening phase

### Bounded prompt/workflow proof

Need assertions for:

- no review prompt teaches post-`review run` advancement
- composite-enabled prompt families do not teach `workflow advance` as the happy path
- corrective prompts do not teach full alternate success rituals

### Integration proof

Need assertions for:

- composite endpoints remain the AI-facing primary path for covered stages
- low-level commands remain available for operator/recovery use where intentionally retained

### E2E proof

Need at least one real AI-session narrative that proves:

- the session closes ordinary success and command stages via composite commands
- the session does not need post-completion probing to discover terminal success
- the session does not regress into low-level retry choreography during a normal success path

## Recommendation for the next implementation order

1. Retarget or narrow the duplicated resume/replacement runtime prompts.
2. Retarget generic pause prompting to one canonical generic pause family.
3. Tighten prompt/test expectations around routed `completed` outcomes so post-close probing is no longer treated as normal.
4. Only after that, consider daemon-side UX hardening for low-level misuse responses that still confuse AI sessions.
