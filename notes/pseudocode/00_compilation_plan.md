# Pseudocode Compilation Plan

## Objective

Convert the existing `notes/*.md` corpus into a structured pseudocode package that can be logically reviewed and pseudotested by AI before implementation begins.

---

## Working assumptions

- `notes/` remains the prose-spec source of truth
- `notes/pseudocode/` becomes the logic-compilation layer
- pseudocode artifacts must be traceable back to specific source notes
- every important flow needs both control logic and test scenarios
- contradictions should be surfaced explicitly rather than silently resolved

---

## Phase 1: Build the compilation index

Goal:

Create a source-to-artifact map so the notes corpus can be converted systematically.

Tasks:

1. classify each note as one or more of:
   - runtime module
   - flow
   - state machine
   - schema/compiler rule
   - policy/decision table
   - traceability/gap analysis
2. mark whether the note is canonical, revised, appendix, or planning-only
3. identify duplicate or superseded sources
4. choose the canonical sources for first-pass pseudocode generation

Deliverable:

- `catalog/source_to_artifact_map.md`

Exit criteria:

- every markdown note in `notes/` has a category
- every v2 spec has at least one planned pseudocode output

---

## Phase 2: Compile the runtime spine

Goal:

Define the smallest set of modules that make the orchestration runtime logically runnable on paper.

Priority modules:

1. `compile_workflow(...)`
2. `admit_node_run(...)`
3. `run_node_loop(...)`
4. `execute_compiled_subtask(...)`
5. `handle_subtask_failure(...)`
6. `recover_interrupted_run(...)`

For each module:

1. extract inputs, outputs, and required state
2. write ordered pseudocode
3. list durable writes explicitly
4. define all loop exits
5. define failure, pause, retry, and recovery paths
6. attach unresolved questions

Implementation note:

- the live system now exposes a daemon-backed `workflow source-discovery` inspection surface for the first compile stage, returning deterministic discovered source order plus resolved-document inventory for one compiled workflow
- the live system also exposes explicit inspection reads for later compile stages through `workflow schema-validation`, `workflow override-resolution`, `workflow hook-policy`, and `workflow rendering`

Deliverables:

- module files under `modules/`
- first runtime pseudotest file under `pseudotests/`

Exit criteria:

- a full happy path exists from compile to recovery
- the runtime spine has no hidden state transitions

---

## Phase 3: Compile orchestration edges

Goal:

Make tree orchestration, dependency handling, and parent/child escalation explicit.

Priority areas:

1. child materialization
2. sibling dependency readiness
3. invalid dependency rejection
4. parent failure handling
5. manual-tree and auto-tree reconciliation
6. regeneration triggers and rebuild scope

Deliverables:

- flow files under `flows/`
- state machines for dependency and escalation behavior
- pseudotests for invalid graph and blocked-progress cases

Exit criteria:

- dependency legality is testable
- regeneration behavior is explicit
- parent/child responsibilities are unambiguous

---

## Phase 4: Compile git, audit, and operator logic

Goal:

Ensure the system is inspectable, reproducible, and safely rectifiable.

Priority areas:

1. branch and merge flow
2. rectification from seed
3. upstream rebuild behavior
4. provenance update logic
5. CLI-visible introspection expectations
6. audit trail completeness

Deliverables:

- rectification and provenance modules
- auditability pseudotests
- operator-query expectation docs

Exit criteria:

- every critical mutation has a corresponding inspection path
- rebuild and merge behavior can be reasoned about without code

---

## Phase 5: Run contradiction and completeness review

Goal:

Use the pseudocode layer to identify what the prose specs still leave underspecified.

Review questions:

1. does every loop have a termination or escalation condition?
2. does every state mutation have persistence semantics?
3. does every failure class map to a parent or operator-visible outcome?
4. does every CLI action map to a runtime and DB behavior?
5. do any source notes impose conflicting rules?

Deliverables:

- `catalog/open_questions.md`
- `catalog/contradictions.md`
- updated traceability notes if needed

Exit criteria:

- remaining gaps are explicit and prioritized
- implementation can begin from pseudocode instead of prose alone

---

## Recommended first week of work

1. build `catalog/source_to_artifact_map.md`
2. write `modules/compile_workflow.md`
3. write `modules/run_node_loop.md`
4. write `modules/execute_compiled_subtask.md`
5. write `pseudotests/runtime_core_tests.md`
6. review those artifacts against `cross_spec_gap_matrix.md` and `spec_traceability_matrix.md`

This sequence should expose the highest-value ambiguities early.

---

## Review standard for each pseudocode artifact

An artifact is ready when it answers all of these:

- what starts it
- what inputs it reads
- what state it assumes
- what durable records it writes
- what conditions advance it
- what conditions block it
- what conditions fail it
- what conditions pause it
- how it resumes
- how another actor can inspect it

If any of those are missing, the artifact is still prose, not usable pseudocode.
