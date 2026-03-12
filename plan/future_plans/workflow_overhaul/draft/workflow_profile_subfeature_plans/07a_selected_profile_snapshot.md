# Workflow Profile Subfeature Plan 07a: Selected Profile Snapshot

## Parent Area

- `07 Compile-Context Profile Freezing`

## Parent Slice

- `draft_feature_plans/04_compiled_profile_context_and_brief_generation.md`

## Goal

Freeze selected-profile identity and descriptive metadata into compiled workflow state.

## Implementation Subtasks

- persist selected profile id, label, kind applicability, and compact description in compile context
- define which selected-profile fields are immutable after compile versus recomputed on recompile
- expose the snapshot through compile inspection and failure reads
