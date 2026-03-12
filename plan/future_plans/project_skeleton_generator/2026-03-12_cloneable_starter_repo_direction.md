# Cloneable Starter Repo Direction

## Purpose

Record the current preferred delivery direction for the project-skeleton work.

The strongest near-term path is no longer "build the generator first and only then expose the skeleton."

The stronger immediate path is:

1. define a starter repository people can clone directly
2. review and refine that starter repository as a concrete artifact
3. optionally automate its rendering later with a generator once the starter shape is stable

## Why This Direction Is Better Right Now

- A cloneable starter repo is easier to evaluate than an abstract rendering pipeline.
- Users can start with it immediately without waiting for generator implementation.
- The starter repo becomes the review surface for doctrine, folder shape, starter notes, and checklist ergonomics.
- Later generator work can target a known-good artifact instead of generating from theory.

## Practical Implication

The `project_skeleton_generator` future-plan bundle should now treat:

- the starter-repo draft under `draft_repo/`

as the primary reviewable output shape.

Generator-oriented notes still matter, but they should now support the cloneable starter repo rather than replacing it.

## What The Starter Repo Must Preserve

Even as a separate repo, the starter should carry forward the current repository's core operational concepts:

- explicit multi-system thinking
- notes as implementation assets
- lifecycle-stage governance
- required task plans
- required development logs
- required checklist discipline
- bounded-test to real-E2E progression
- authoritative document-family consistency checks
- explicit verification commands
- honest completion vocabulary
- post-v1 continuation guidance

## Current Review Surface

The concrete draft now lives at:

- `plan/future_plans/project_skeleton_generator/draft_repo/`

That folder should be treated as the best current approximation of the future standalone repository layout and content.
