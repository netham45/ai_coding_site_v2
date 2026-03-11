# Operator Questionnaire And Requirement Capture

## Purpose

Design a better question set for operators with limited UI-design experience so collaborative design produces useful requirements instead of vague preference chatter.

This is a working note, not a final questionnaire.

## Core Principle

Ask questions the operator can answer concretely.

Do not assume the operator can produce professional design terminology.

## Questionnaire Sections

The future system should probably group questions into a few stable buckets.

### 1. Page Purpose

Ask:

- what must this page let the user do
- who the page is for
- what the single most important action is

### 2. Required Structure

Ask:

- which sections must exist
- which fields must exist exactly
- which buttons or actions must exist
- what must be visible without scrolling

### 3. Visual Direction

Ask:

- which 2-4 adjectives best fit the desired feel
- whether the page should feel more minimal, dense, bold, conservative, playful, or technical
- whether there are examples that feel close

### 4. Avoidances

Ask:

- what should not appear
- what felt wrong in the current draft
- whether anything felt cluttered, childish, sterile, or confusing

### 5. Device Priority

Ask:

- whether mobile, desktop, or both matter most
- whether any content must stay above the fold on a specific device size

### 6. Open Questions

Ask:

- what the operator is unsure about
- which parts should be treated as provisional

## Good Answer Translation

The future system should convert free-form answers into a structured artifact with:

- normalized required sections
- normalized field names
- normalized action list
- prioritized content list
- style adjectives
- avoidances
- device priorities
- unresolved questions

## Confirmation Step

The AI should summarize the interpreted requirements before revising.

Example confirmation structure:

- "I believe the required sections are ..."
- "The must-have fields are ..."
- "The desired style direction is ..."
- "I will avoid ..."

Then the operator should confirm or correct that summary.

## Anti-Patterns

Avoid future questionnaire designs that:

- ask twenty open-ended questions in one block
- assume the operator knows design jargon
- optimize for stylistic nuance before required fields and actions are clear
- skip the confirmation step

## Possible Advanced Later Inputs

Later versions might also accept:

- screenshot markup
- URL references
- component-level comments
- before/after preference ranking

But those should be optional enhancements, not prerequisites.
