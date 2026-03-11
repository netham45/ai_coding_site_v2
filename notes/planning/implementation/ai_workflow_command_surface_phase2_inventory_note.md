# AI Workflow Command Surface Phase 2 Inventory Note

## Purpose

This note records the Phase 2 command-surface inventory for `plan/tasks/2026-03-10_ai_workflow_command_surface_review_discovery.md`.

Phase 1 established that the main problem is not session chatter; it is the shape of the AI-facing command loop. Phase 2 inventories that loop and groups the current commands by role so later design work can decide which commands should remain exposed to AI sessions and which should remain operator/debug tools.

Related documents:

- `plan/tasks/2026-03-10_ai_workflow_command_surface_review_discovery.md`
- `notes/planning/implementation/ai_workflow_command_surface_phase1_evidence_note.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/cli/cli_surface_spec_v2.md`
- `src/aicoding/cli/parser.py`
- `src/aicoding/cli/handlers.py`

---

## Inventory Boundary

This inventory is limited to the command surfaces that participate in or closely surround the current AI-facing runtime loop.

The purpose is not to list every CLI command in the repository. The purpose is to identify:

- which commands the prompts currently expect AI sessions to use directly
- which commands are primarily operator or debugging reads
- which mutations appear to be overexposed to AI sessions
- which commands already represent daemon-owned higher-level operations

---

## Group A: Current AI-Facing Stage Loop Commands

These are the commands currently used directly by prompts or by the documented canonical runtime loop.

### Stage discovery and prompt retrieval

- `workflow start --kind <kind> --prompt <prompt>`
- `session bind --node <id>`
- `subtask current --node <id>`
- `subtask prompt --node <id>`
- `subtask context --node <id>`
- `subtask environment --node <id>`

Current role:

- active AI-session bootstrap and next-stage discovery

Observations:

- these are legitimate AI-facing commands
- `subtask current` and `subtask prompt` are currently part of the happy path after successful stage advancement, not only recovery or inspection
- the need to call both after each stage is evidence that stage closure is too fragmented

### Stage execution and progress mutation

- `subtask start --node <id> --compiled-subtask <id>`
- `subtask heartbeat --node <id> --compiled-subtask <id>`
- `summary register --node <id> --file <path> --type <type>`
- `subtask complete --node <id> --compiled-subtask <id> [--summary ...] [--result-file ...]`
- `subtask fail --node <id> --compiled-subtask <id> [--summary-file ...] [--result-file ...]`
- `workflow advance --node <id>`

Current role:

- low-level stage mutation loop

Observations:

- this is the most overloaded AI-facing cluster
- successful stage closure often requires several commands in strict sequence
- `workflow advance` is especially sensitive to timing and is implicated directly in the repeated race evidence from Phase 1
- `summary register` plus `subtask complete` plus `workflow advance` is currently a common “one logical action, three mutating commands” pattern

### Review, validation, and testing stage execution

- `review run --node <id> --status ... --summary ...`
- `node validate --node <id>`
- `testing run --node <id>`
- command-subtask flow using:
  - `subtask start`
  - local command execution
  - `subtask complete --result-file ...`
  - `workflow advance`

Current role:

- quality-gate and stage-specific mutation paths

Observations:

- `review run` is already closer to the desired shape because it is documented as recording and routing the review outcome itself
- the prompts still need to warn the AI not to follow `review run` with `workflow advance`
- that warning is evidence that the surrounding command surface is too easy to misuse
- validation and testing still often reduce to the generic low-level completion loop rather than one obvious higher-level success/failure mutation

### Parent decomposition and child creation

- `node register-layout --node <id> --file <path>`
- `node materialize-children --node <id>`
- `workflow advance --node <id>`

Current role:

- parent-authored child-plan handoff and child-creation progression

Observations:

- `node register-layout` is an appropriate explicit AI-facing handoff because it turns a workspace artifact into durable authoritative state
- `node materialize-children` is more ambiguous:
  - it is currently a real workflow mutation used by parent flows
  - it also feels operational and structural rather than purely “complete this stage”
- later design work should decide whether this remains directly AI-facing or becomes an internal step behind a parent-stage success command

---

## Group B: Commands That Are Primarily Operator Or Debug Reads

These commands are important and should remain available, but they do not appear to belong in the normal AI happy path.

### Run, workflow, and hierarchy inspection

- `node show --node <id>`
- `node run show --node <id>`
- `node runs --node <id>`
- `workflow show --node <id>`
- `workflow chain --node <id>`
- `workflow current --node <id>`
- `node children --node <id>`
- `node child-materialization --node <id>`
- `node child-results --node <id>`
- `node reconcile --node <id>`
- `node audit --node <id>`
- `node run audit --node <id>`

### Session and recovery inspection

- `session show --node <id>`
- `session list --node <id>`
- `session events --session <id>`
- `node recovery-status --node <id>`
- `node recovery-provider-status --node <id>`

### History and evidence reads

- `summary history --node <id>`
- `summary show --summary <id>`
- `prompts history --node <id>`
- `review show --node <id>`
- `review results --node <id>`
- `validation show --node <id>`
- `validation results --node <id>`
- `testing show --node <id>`
- `testing results --node <id>`

Observations:

- these reads are crucial for operator diagnosis, auditability, and recovery
- they should remain inspectable even if the AI-facing mutation surface is collapsed later
- several of them are currently used in E2E and debugging, but they are not required in the intended AI happy path

---

## Group C: Commands That Already Behave Like Higher-Level Daemon-Owned Operations

These commands already bundle multiple concerns and are useful examples for later design work.

- `workflow start --kind <kind> --prompt <prompt>`
- `review run --node <id> --status ... --summary ...`
- `node quality-chain --node <id>`
- `session recover --node <id>`
- `session provider-resume --node <id>`
- `node register-layout --node <id> --file <path>`

Why they matter:

- they already prove the daemon can own multi-step workflow mutations safely
- they reduce the need for the AI to stitch together low-level state transitions
- they still leave durable inspection surfaces intact afterward

Observations:

- `node quality-chain` is especially notable because it already embodies the “one command owns a larger workflow slice” pattern
- the current messy AI loop is therefore not a global repository limitation; it is a narrower design gap in the stage-completion surface

---

## Group D: Commands That Are Likely Overexposed To AI Sessions

These commands are valuable low-level tools, but the current evidence suggests they should not all remain part of the normal AI happy path.

### `workflow advance`

Why it is overexposed:

- it appears in the normal success path for ordinary stages
- it is easy to call too early
- it frequently races immediately after another accepted mutation
- terminal completion currently surfaces through misuse of this command

Likely future role:

- remain available as a low-level operator/debug or explicit recovery tool
- no longer be required after every normal successful stage mutation

### `summary register` in ordinary success paths

Why it is overexposed:

- it is often just one required sub-step of “succeed this stage”
- the AI has to coordinate summary persistence separately from stage completion
- prompts repeatedly spell out this ritual

Likely future role:

- remain available as an explicit artifact-registration tool
- may no longer need to be a required separate success-path step for common stage types

### `subtask current` and `subtask prompt` after every success path

Why they are overexposed:

- they are legitimate discovery tools
- they are currently also part of the ordinary continuation path after `workflow advance`
- that turns stage continuation into explicit command choreography rather than one daemon-owned transition outcome

Likely future role:

- remain the read-side tools for recovery, attach, manual debugging, and explicit inspection
- no longer be required just to keep an ordinary successful session moving

### `node materialize-children`

Why it is ambiguous:

- it is a meaningful explicit parent-structure mutation
- but in the current parent flow it acts like a workflow-progress step rather than a pure operator action

Likely future role:

- needs a later design decision
- it may remain AI-facing for parent workflows, or be subsumed by a parent-stage success command once the child plan is registered

---

## Group E: Commands That Should Remain Low-Level Even If The AI Surface Shrinks

These commands appear worth preserving as explicit low-level primitives regardless of later simplification.

- `subtask fail`
- `subtask retry`
- `summary register`
- `session nudge`
- `session attach`
- `session recover`
- `node register-layout`
- `node materialize-children`
- `workflow compile`
- `workflow chain`
- `node audit`
- `session events`

Rationale:

- they support recovery, diagnosis, explicit operator intervention, or structural workflow mutations
- later design work can reduce how often AI sessions need them directly without removing their value

---

## Phase 2 Findings

Phase 2 supports the following conclusions:

1. The actual AI happy path is concentrated in a much smaller command set than the full CLI.
2. The main overexposure is not “too many commands in the repo.” It is “too many low-level mutating commands required for one ordinary stage success.”
3. The most problematic command in the current happy path is `workflow advance`, because it acts as both:
   - a required ordinary continuation step
   - a fragile low-level cursor mutation
4. `review run` already demonstrates a better command shape than the ordinary leaf-validation-testing loop, because it claims responsibility for routing its own outcome.
5. The repository already contains examples of higher-level daemon-owned commands, so later simplification work can align with existing patterns instead of inventing a new philosophy.

---

## Questions Carried Into Phase 3

Phase 2 does not yet decide final redesign semantics. It narrows the next review questions to:

1. Which misuse cases should become hard daemon rejections?
2. Which low-level commands should remain available but no longer appear in ordinary prompts?
3. Which stage-success clusters should collapse into one authoritative daemon-owned mutation?
4. Which commands must stay explicit because they create durable artifacts or structural state rather than merely advancing a stage?
