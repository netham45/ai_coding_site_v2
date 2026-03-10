# Provenance Identity Strategy

## Purpose

This document defines how the system should identify code entities over time for provenance, rationale tracking, and documentation generation.

The current design already includes:

- `code_entities`
- `node_entity_changes`
- `code_relations`

But one of the biggest unresolved issues is stable identity:

- how to recognize the "same" entity after edits
- how to handle renames
- how to handle moves across files
- how to handle signature changes
- how to represent uncertainty when identity cannot be known perfectly

This note defines a practical strategy that is accurate enough for useful provenance without pretending identity is always perfect.

Related documents:

- `notes/specs/database/database_schema_spec_v2.md`
- `notes/planning/expansion/review_testing_docs_yaml_plan.md`
- `notes/catalogs/audit/auditability_checklist.md`
- `notes/catalogs/traceability/cross_spec_gap_matrix.md`

---

## Core Rule

Entity identity should be stable when possible, probabilistic when necessary, and never silently assumed when evidence is weak.

That means:

- use durable entity IDs
- use deterministic matching when possible
- use heuristic matching when necessary
- record confidence when identity is inferred
- prefer explicit uncertainty over false certainty

---

## What Counts As A Code Entity

The provenance model should support at least:

- file
- module
- class
- function
- method
- variable
- type
- endpoint
- test

The exact initial implementation may support fewer types, but the model should allow the broader set.

---

## Identity Problem Cases

The strategy must handle at least these scenarios.

## Case 1: Same entity, body changed

Example:

- function name unchanged
- signature unchanged
- implementation changed

Desired behavior:

- keep same entity identity

## Case 2: Same entity, renamed

Example:

- function renamed
- body largely similar

Desired behavior:

- preserve lineage if confidence is high enough

## Case 3: Same entity, moved files

Example:

- class moved from one file to another
- structure and name mostly preserved

Desired behavior:

- preserve lineage if confidence is high enough

## Case 4: Same conceptual entity, signature changed

Example:

- function gets new parameters or return type

Desired behavior:

- often preserve identity, but confidence may be lower

## Case 5: Entity split or merge

Example:

- one function split into two
- two helper functions collapsed into one

Desired behavior:

- treat this as ambiguous
- allow one-to-many or many-to-one provenance history where useful
- avoid pretending perfect identity continuity

## Case 6: Uncertain or conflicting match

Desired behavior:

- record low confidence
- avoid claiming a deterministic identity match if evidence is weak

---

## Recommended Identity Model

Use a layered identity approach.

## Layer 1: Durable entity row

Each entity gets:

- `entity_id`
- `entity_type`
- `canonical_name`
- `file_path`
- `signature`
- `stable_hash`

The row is the durable database identity.

## Layer 2: Current structural fingerprint

For each extraction pass, compute a fingerprint from stable-ish structure such as:

- normalized AST shape
- normalized signature
- surrounding lexical or structural context

This fingerprint should help detect continuity even when line numbers change.

## Layer 3: Match confidence

When matching extracted entities to existing entities, assign confidence based on evidence:

- exact signature match
- exact canonical name match
- same file path
- similar normalized body or AST
- relation neighborhood similarity

If confidence is weak, do not silently overwrite prior identity assumptions.

---

## Matching Strategy

The recommended matching order is:

## Step 1: Exact structural identity match

If all of the following align strongly:

- entity type
- canonical name
- file path
- signature or normalized fingerprint

Then:

- treat as same entity with high confidence

## Step 2: Strong rename/move candidate match

If exact identity fails, look for:

- same entity type
- similar normalized body/fingerprint
- nearby relation graph similarity
- likely rename or move pattern

Then:

- treat as same entity with medium/high confidence if strong enough

## Step 3: Weak heuristic candidate match

If exact and strong match fail but there is a plausible candidate:

- keep the match only with explicit lower confidence
- make it queryable as inferred, not certain

## Step 4: No safe match

If confidence is too weak:

- create a new entity row
- keep the old entity as historical

This avoids corrupting provenance history through aggressive guessing.

---

## Current Bounded Implementation

The current implementation is intentionally narrower than the full target model.

- supported entity types today are `module`, `class`, `function`, and `method`
- supported relation types today are `contains` and `calls`
- supported source languages today are:
  - Python (`.py`)
  - JavaScript (`.js`, `.jsx`)
  - TypeScript (`.ts`, `.tsx`)
- exact matches require the same entity type, canonical name, file path, and signature
- heuristic rename/move matches require the same entity type, normalized signature, and stable hash while allowing the canonical name or file path to change
- heuristic matches are currently recorded with `match_confidence = medium`
- new entities and exact matches are currently recorded with `match_confidence = high`
- ambiguous split/merge cases still fall back to new durable entity rows rather than attempting many-to-one or one-to-many identity preservation

Stable hashes are deliberately code-owned rather than YAML-owned policy.

- Python hashes are derived from normalized AST structure
- JavaScript/TypeScript hashes are currently derived from normalized declaration text with declaration names removed before hashing where possible

Extraction scope is also bounded:

- when the daemon refreshes provenance without an explicit workspace root, it first uses the configured runtime workspace root when one exists
- otherwise it scans the repository `src/` tree when present
- when a caller provides an explicit workspace root, that tree is scanned directly

This keeps the default refresh path focused on the active runtime workspace instead of the whole repository while preserving deterministic behavior for explicit test or tool workspaces.

Still deferred in the current slice:

- variables
- types/interfaces
- endpoints/routes
- tests as first-class provenance entities
- richer non-Python relation families such as imports or route bindings

---

## Stable Hash Guidance

`stable_hash` should not just be a hash of raw text.

It should be derived from normalized structure where possible.

Better candidates:

- normalized AST
- normalized signature plus normalized body structure
- normalized declaration shape

Poor candidates:

- raw line ranges
- raw whitespace-sensitive source text

Reason:

- provenance should survive formatting changes and minor mechanical edits better than raw text hashes do

---

## Confidence Model

The provenance system should expose confidence explicitly.

Recommended rough confidence bands:

- `high`
- `medium`
- `low`

Or numeric scores if preferred.

Confidence should be influenced by:

- name continuity
- signature continuity
- fingerprint similarity
- file-path continuity
- relation-neighborhood similarity

When confidence is low:

- avoid presenting lineage as certain fact in docs or rationale views
- label it as inferred or likely

---

## Entity History Model

The system should support the idea that one durable entity can have multiple observed versions over time.

That suggests one of two practical approaches.

## Option A: Keep one `code_entities` row and update metadata over time

Pros:

- simple

Cons:

- historical structural detail is lost unless separately stored

## Option B: Add entity-observation history

Possible future table:

- `code_entity_observations`

Potential fields:

- `id`
- `entity_id`
- `node_version_id`
- `file_path`
- `signature`
- `start_line`
- `end_line`
- `stable_hash`
- `match_confidence`
- `observed_at`

Recommended direction:

- strongly consider an observation/history table if provenance becomes a major product feature

For an initial implementation, the simpler current table may be enough, but the design should acknowledge the limitation.

---

## Split And Merge Handling

Split and merge scenarios are inherently ambiguous.

Recommended treatment:

- do not force a perfect one-to-one identity when one entity splits into many or many collapse into one
- record relation-like lineage when useful
- prefer explicit ambiguity over false certainty

Potential future concept:

- `entity_lineage_events`

Examples:

- `renamed_from`
- `moved_from`
- `split_from`
- `merged_from`

This may be too heavy for first implementation, but the design should leave room for it.

---

## DB Implications

The current DB model can support part of this, but implementation should consider:

### Possible additions

- confidence on `node_entity_changes`
- confidence and match_source on `code_relations`
- `code_entity_observations`
- possibly `entity_lineage_events`

### Current-table implications

`code_entities` should not be treated as a perfect immutable truth of all observed historical shapes.

It is more realistic to treat it as:

- current durable entity identity anchor

and add observation history later if needed.

---

## Runtime/Extraction Implications

The provenance update step should:

1. extract current entities from code
2. compare them to known entity anchors
3. match exact identities first
4. apply rename/move heuristics second
5. create new entities where safe match is not available
6. record confidence and rationale for inferred matches

This should be deterministic enough to reproduce, but not so rigid that simple refactors destroy history continuity.

---

## CLI And Docs Implications

CLI and docs should reflect confidence honestly.

Examples:

- high-confidence identity continuity can be presented normally
- lower-confidence lineage should be presented as inferred
- ambiguous cases should be inspectable, not hidden

Likely useful CLI capabilities:

- show entity current identity
- show entity history
- show relation confidence
- show why a lineage match was made

Potential useful addition:

- `ai-tool entity explain-match --name <canonical_name>`

---

## Auditability Rule

If the provenance engine inferred identity rather than proving it, that should be visible.

The system should be able to answer:

- why this entity was considered the same as a prior one
- what evidence supported that decision
- what confidence level was assigned

If it cannot answer those, provenance becomes too opaque to trust.

---

## Recommended Default Strategy

For the first serious implementation, use this default:

1. high-confidence exact matching first
2. limited rename/move heuristics second
3. explicit confidence recording
4. create new entity when in doubt

This is conservative, auditable, and good enough to start without pretending perfect semantic identity resolution.

---

## Open Decisions Still Remaining

### D01. Numeric vs categorical confidence

Recommended default:

- start with categorical confidence for simplicity

### D02. Observation history in first implementation

Recommended default:

- optional, but likely worth adding if provenance is central early

### D03. Lineage event model

Recommended default:

- defer unless split/merge lineage becomes immediately important

---

## Recommended Next Follow-On Work

The next docs that should absorb this logic are:

1. `notes/specs/database/database_schema_spec_v2.md`
2. future provenance/docs spec work
3. `notes/catalogs/traceability/cross_spec_gap_matrix.md`

Then reduce the severity of the provenance-identity gap.

---

## Exit Criteria

This note is complete enough when:

- identity strategy is explicit
- uncertainty handling is explicit
- rename/move handling is explicit
- DB and runtime implications are identified

At that point, provenance identity is no longer a vague hidden assumption.
