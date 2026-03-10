# Automated Full-Tree Cat Runtime Preimplementation Note

## Purpose

This note freezes the preimplementation design surface for the requested automated full-tree runtime narrative:

- start with an automated `epic`
- let parent AI/runtime behavior create `phase`, `plan`, and `task` descendants
- execute the leaf task through the real tmux/Codex path
- produce a minimal sample program that recreates the basic `cat` command behavior

This note exists because the repository already has nearby runtime features, but the exact end-to-end narrative requested here was not previously defined tightly enough to justify implementation work.

Related documents:

- `plan/tasks/2026-03-10_automated_full_tree_cat_runtime_preimplementation_planning.md`
- `plan/tasks/2026-03-10_automated_full_tree_cat_runtime_e2e.md`
- `notes/contracts/parent_child/child_materialization_and_scheduling.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/catalogs/audit/flow_coverage_checklist.md`
- `notes/catalogs/checklists/feature_checklist_backfill.md`

---

## Narrative Boundary

The requested runtime narrative is not:

- operator-issued `node materialize-children --node <id>` at each tier
- a fake child scheduler
- a direct DB mutation that inserts descendants
- a synthetic prompt, summary, or result injection path

The requested runtime narrative is:

1. start a top-level `epic` from a user request for a minimal `cat`-like program
2. bind a real primary tmux/Codex session for that epic
3. let the parent workflow generate an effective child layout
4. let runtime child materialization use that generated layout as the authoritative child source for this narrative
5. let the daemon admit and bind ready child work automatically when policy allows
6. repeat the same parent-owned decomposition pattern until a leaf `task` is reached
7. let the leaf task execute through the real tmux/Codex path in the workspace
8. prove the produced sample program behaves like a basic `cat` implementation for the declared narrow scope

---

## Minimal Product Target

The sample program scope for this narrative should stay intentionally narrow.

Required leaf outcome:

- read one or more file paths from argv
- print file contents in order to stdout
- return non-zero on unreadable input

Deliberate non-goals for the first narrative:

- full GNU `cat` parity
- streaming stdin behavior unless the leaf implementation already arrives there naturally
- line numbering, squeezing, or other option flags
- performance benchmarking as part of the first runtime proof

The first real E2E should prove only a basic bounded `cat`-like command, not a production-grade clone.

---

## Core Invariants

### 1. Generated layout authority must be explicit

If a parent workflow in this narrative writes `layouts/generated_layout.yaml`, that file must be the effective materialization input for the next child-creation step.

Rules:

- generated layout authority is scoped to this runtime narrative or scoped policy path
- built-in packaged layouts remain the fallback when no generated layout exists
- materialization must not silently ignore a generated layout while claiming parent-driven decomposition

### 2. Child auto-start must remain daemon-owned

Once children exist, ready child admission and session binding must be performed by the daemon, not by hidden operator-side commands in the E2E harness.

Rules:

- the daemon decides readiness from durable child state
- the daemon records durable run/session evidence for auto-started children
- blocked children remain blocked until dependencies clear

### 3. Parent decomposition selection must be scoped

The global built-in `epic`, `phase`, and `plan` ladders must not be silently changed just to satisfy this one narrative.

Rules:

- the automated full-tree narrative must use a scoped project/override/profile path
- the default built-in parent ladders remain unchanged unless a broader note explicitly revises that posture
- compile-time inspection must make the selected scoped ladder visible

### 4. The proof must remain durable and inspectable

The final E2E cannot rely only on terminal text.

Required durable checkpoints:

- node creation and lineage at epic, phase, plan, and task depth
- compiled workflow/task/subtask inspection at each tier
- child materialization evidence
- child run/session admission evidence
- leaf summary and completion evidence
- final workspace behavior of the sample program

---

## Canonical Runtime Flow For This Narrative

### Stage A: Top-level startup

1. `workflow start --kind epic --prompt ...`
2. admit the top-level run
3. bind the primary session
4. retrieve the authoritative parent prompt/context through the CLI bootstrap path

### Stage B: Parent decomposition

1. parent session runs a scoped decomposition ladder
2. parent produces `layouts/generated_layout.yaml`
3. runtime materializes children from that generated layout
4. daemon inspects child readiness
5. daemon auto-starts ready children when policy permits

### Stage C: Recursive descent

1. each parent tier repeats the same decomposition pattern
2. the tree descends until a leaf `task` node is produced
3. dependency-blocked siblings wait durably rather than being started speculatively

### Stage D: Leaf execution

1. the leaf task receives the concrete request to implement the minimal `cat`-like program
2. the leaf session performs real workspace edits
3. the leaf session records summary/progress through the CLI runtime loop
4. the leaf node completes durably

### Stage E: First-proof stop point

The first real automated full-tree `cat` E2E may stop once all of the following are true:

- automated descent from epic to task is proven durably
- the leaf task completes through the real tmux/Codex path
- the resulting program passes the bounded behavior check for the minimal `cat` scope

Mergeback, regeneration, and upward rectification remain adjacent later layers, not part of the first proof target here.

---

## Proving Ladder

### Phase 0: Planning/spec completion

Required outputs:

- this note
- task-plan gating for the later runtime phases
- checklist/gap/flow updates that honestly describe the current missing implementation

### Phase 1: Generated-layout materialization

Required proof:

- bounded materialization tests prove generated layout preference and built-in fallback

### Phase 2: Daemon child auto-run

Required proof:

- bounded integration tests prove the daemon auto-starts ready children and leaves blocked siblings alone

### Phase 3: Scoped parent decomposition

Required proof:

- compile/flow tests prove the scoped decomposition ladder is selected for this narrative without mutating the default path

### Phase 4: Real E2E

Required proof:

- one real tmux/Codex-driven E2E proves automated descent plus leaf completion for the minimal `cat` target

---

## Document Surfaces That Must Change Before Runtime Coding Continues

The following surfaces must acknowledge this narrative explicitly:

- `notes/catalogs/traceability/cross_spec_gap_matrix.md`
- `notes/catalogs/checklists/feature_checklist_backfill.md`
- `notes/catalogs/audit/flow_coverage_checklist.md`
- the development log for the planning task

The following runtime/spec surfaces should only be updated as each later implementation phase lands:

- `notes/contracts/parent_child/child_materialization_and_scheduling.md`
- `notes/specs/runtime/runtime_command_loop_spec_v2.md`
- `notes/specs/cli/cli_surface_spec_v2.md`

That sequencing matters because those specs should describe real implemented behavior, not a wish list.

---

## Current Honest Status

As of March 10, 2026:

- the repository has real proof for top-level startup, explicit child materialization, and real leaf-task execution
- the repository does not yet have real proof for parent-driven generated-layout child creation
- the repository does not yet have daemon-owned child auto-start for this narrative
- the repository does not yet have a scoped compiled parent decomposition ladder for this narrative

So the automated full-tree `cat` runtime narrative is currently:

- planned at the preimplementation level
- not yet implemented
- not yet E2E-covered
